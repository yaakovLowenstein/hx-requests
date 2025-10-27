import contextlib
from functools import partial
from typing import Dict, Union

from django.conf import settings
from django.contrib import messages
from django.contrib.messages import get_messages
from django.core.exceptions import ObjectDoesNotExist
from django.forms import Form
from django.http import HttpRequest, HttpResponse
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.functional import cached_property
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from render_block import render_block_to_string

from hx_requests.utils import deserialize


class Renderer:
    def render(self, template_name, block_name, context, request):
        if block_name:
            return render_block_to_string(template_name, block_name, context, request)
        return render_to_string(template_name, context, request)


class BaseHxRequest:
    """
    Base class for HxRequests. Class to be used for basic GET and POST requests.

    Attributes
    ----------
    name : str
         Unique name that needs to be matched in the template tag rendering the HxRequest
    hx_object_name : str, optional
        Name that the hx_object is passed into the context with
    GET_template : str,list, optional
        Template rendered for a GET request. If a list is passed in, all the templates are rendered
        If unset, the views template_name is used
    POST_template : str,list, optional
        Template rendered for a POST request. If a list is passed in, all the templates are rendered
        If unset, the views template_name is used
    GET_block : str,list, optional
        Block of the GET_template to be used instead of rendering the whole template
        If a list is passed in, all the blocks are rendered per the GET_template
        If a dict is passed in, the keys are the templates and the values are the blocks
    POST_block : str,list, optional
        Block of the POST_block to be used instead of rendering the whole template
        If a list is passed in, all the blocks are rendered per the POST_template
        If a dict is passed in, the keys are the templates and the values are the blocks
    refresh_page : bool
        If True the page will refresh after a POST request
    redirect : str, optional
        URL to redirect to after a POST request
    return_empty : bool
        If True, returns an empty HTTPResponse after a POST request
    no_swap : bool
        If True, does not do a swap
    show_messages: bool
        If True and there is a message set and settings.HX_REQUESTS_USE_HX_MESSAGES is True
        then the set message is displayed
    get_views_context: bool
        If True, the context from the view is added to the context of the HxRequest
        If False, only the context from the HxRequest is used, potentially improving performance
        by not needing to call the view's get_context_data method.
    kwargs_as_context: bool
        If True, the kwargs are added into the context directly.
        If False, the kwargs are added into the context as hx_kwargs.
    refresh_views_context_on_POST: bool
        If True, the view's context is refreshed on a POST request.
        Useful if the context needs to be updated after the POST.
    use_current_url: bool (Experimental)
        If True, the request adds the GET params from the current browser URL to the request.
        The GET params submitted with the request (I.e via hx-vals) override the ones in the
        current URL.




    **Note**: Cannot use blocks with a list of templates

    """

    name: str = ""
    hx_object_name: str = "hx_object"
    GET_template: Union[str, list] = ""
    POST_template: Union[str, list] = ""
    GET_block: Union[str, list] = ""
    POST_block: Union[str, list, dict[str, str]] = ""
    refresh_page: bool = False
    redirect: str = None
    return_empty: bool = False
    no_swap = False
    show_messages: bool = True
    get_views_context: bool = True
    kwargs_as_context: bool = True
    refresh_views_context_on_POST: bool = False
    use_current_url: bool = False

    @cached_property
    def is_post_request(self):
        """
        **Property** : Returns True if it is a POST request
        """
        return self.request.method == "POST"

    @cached_property
    def use_messages(self):
        return getattr(settings, "HX_REQUESTS_USE_HX_MESSAGES", False) and self.show_messages

    def get_context_data(self, **kwargs) -> Dict:
        """
        Adds the context from the view and additionally adds:

            | kwargs as hx_kwargs
            | hx_object as {self.hx_object_name} (default is hx_object)
            | self as hx_request
        """
        context = RequestContext(self.request)
        if self.get_views_context and hasattr(self.view_response, "context_data"):
            context.update(self.view_response.context_data)
        if self.kwargs_as_context:
            context.update(kwargs)
        else:
            context["hx_kwargs"] = kwargs
        context[self.hx_object_name] = self.hx_object
        context["request"] = self.request
        context["hx_request"] = self
        if self.is_post_request:
            context.update(self.get_context_on_POST(**kwargs))
        else:
            context.update(self.get_context_on_GET(**kwargs))
        # Turn into dict for template rendering which expects a dict
        return context.flatten()

    def get_context_on_GET(self, **kwargs) -> Dict:
        """
        Adds extra context to the context data only on GET.
        """
        return {}

    def get_context_on_POST(self, **kwargs):
        """
        Adds extra context to the context data only on POST.
        """
        context = {}
        # Refresh the object in case it was updated.
        if self.hx_object and self.hx_object.pk:
            with contextlib.suppress(ObjectDoesNotExist):
                self.hx_object.refresh_from_db()
        if self.refresh_views_context_on_POST:
            if hasattr(self.view, "object") and self.view.object:
                self.view.object.refresh_from_db()
                context["object"] = self.view.object
            context.update(self.view.get_context_data(**kwargs))
        context[self.hx_object_name] = self.hx_object

        return context

    def get_hx_object(self, request):
        """
        If an 'object' was passed in, deserialize it.
        """
        if request.GET.get("object"):
            return deserialize(request.GET.get("object"))

    def _setup_hx_request(self, request, *args, **kwargs):
        if self.get_views_context:
            self.view_response = self.view.get(request, *args, **kwargs)
        self.request = request
        self.renderer = Renderer()
        self.GET_template = self.GET_template or self.view.template_name
        self.POST_template = self.POST_template or self.view.template_name

        if not hasattr(self, "hx_object"):
            self.hx_object = self.get_hx_object(request)

    def hx_object_to_str(self) -> str:
        return self.hx_object._meta.model.__name__.capitalize() if self.hx_object else ""

    def get_headers(self, **kwargs) -> Dict:
        """
        Prepare the headers for the response.
        """
        headers = {}
        if self.is_post_request:
            if self.refresh_page:
                headers["HX-Refresh"] = "true"
            elif self.redirect:
                headers["HX-Redirect"] = self.redirect
        if self.no_swap:
            headers["HX-Reswap"] = "none"

        triggers = self.get_triggers(**kwargs)
        if triggers:
            headers["HX-Trigger"] = ", ".join(triggers)
        return headers

    def get_triggers(self, **kwargs) -> list:
        """
        Override to set the triggers for the response.
        """
        return []

    def get_response_html(self, **kwargs) -> str:
        """
        Prepare the HTML for the response.
        """
        if self.is_post_request:
            if self.refresh_page or self.redirect or self.return_empty:
                html = ""
            else:
                html = self._render_templates(self.POST_template, self.POST_block, **kwargs)

        else:
            html = self._render_templates(self.GET_template, self.GET_block, **kwargs)

        return html

    def _render_templates(self, templates, blocks, **kwargs) -> str:
        """
        Renders templates and blocks into HTML based on different input cases.
        """
        context = self.get_context_data(**kwargs)
        render_with_context = partial(self.renderer.render, context=context, request=self.request)
        html = []

        # Case: Single template, single block
        if isinstance(templates, str) and isinstance(blocks, str):
            return render_with_context(templates, blocks)

        # Case: Multiple templates and blocks provided as a dictionary
        if isinstance(blocks, dict):
            for template, block in blocks.items():
                if isinstance(block, list):
                    html.extend(render_with_context(template, b) for b in block)
                else:
                    html.append(render_with_context(template, block))

            if isinstance(templates, str):
                html.append(render_with_context(templates, None))
            elif isinstance(templates, list):
                html.extend(render_with_context(template, None) for template in templates)

            return "".join(html)

        # Case: Multiple templates, no blocks
        if isinstance(templates, list):
            if blocks:
                raise ValueError("When using multiple templates, blocks must be a dictionary or empty.")
            return "".join(render_with_context(template, None) for template in templates)

        # Case: Single template, multiple blocks
        if isinstance(blocks, list):
            if isinstance(templates, list):
                raise ValueError(
                    "When using multiple blocks with multiple templates, blocks must be a dictionary."
                )
            return "".join(render_with_context(templates, block) for block in blocks)

        return ""

    def _get_messages_html(self, **kwargs) -> str:
        messages = get_messages(self.request)
        if messages:
            return render_to_string(
                settings.HX_REQUESTS_HX_MESSAGES_TEMPLATE,
                {"messages": messages},
                self.request,
            )
        return ""

    def _get_response(self, **kwargs):
        """
        Gets the response.
        """
        html = self.get_response_html(**kwargs)
        if self.use_messages and not (self.refresh_page or self.redirect):
            html += self._get_messages_html(**kwargs)

        return HttpResponse(
            html,
            headers=self.get_headers(**kwargs),
        )

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Method that all GET requests hit.
        """
        return self._get_response(**kwargs)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Method that all POST requests hit.
        """
        return self._get_response(**kwargs)


class FormHxRequest(BaseHxRequest):
    """
    HxRequests class to be used for forms that helps with some of the boiler plate.
    It's loosely based on Django's FormView and UpdateView.

    Every FormHxRequest must have a form associated with it. The form is
    passed into the context and is also accessible within the class as
    self.form.

    Override form_valid to form_invalid to inject custom behavior. By
    default form_valid saves the form and sets a success message. By
    default form_invalid sets an error message.

    Add kwargs into the form using get_form_kwargs

    If there is an hx_object it is passed into the form as the form
    instance.

    Attributes
    ----------
    form_class : Form
        Class of the form attached to the FormHxRequest
    add_form_errors_to_error_message : bool
        If True adds the form's validation errors to the error message on form_invalid
    set_initial_from_kwargs : bool
        If True sets the initial values in the form from the kwargs as long as the key
        matches a field in the form
    """

    form_class: Form = None
    add_form_errors_to_error_message: bool = False
    set_initial_from_kwargs: bool = False

    def get_context_data(self, **kwargs) -> Dict:
        """
        Additionally adds the form into the context.
        """
        context = super().get_context_data(**kwargs)
        context["form"] = self.form
        return context

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Instantiates the form.
        """
        self.form = self.form_class(**self.get_form_kwargs(**kwargs))
        return self._get_response(**kwargs)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        If the form is valid form_valid.
        If invalid calls form_invalid.
        """
        self.form = self.form_class(**self.get_form_kwargs(**kwargs))

        if self.form.is_valid():
            return self.form_valid(**kwargs)
        else:
            return self.form_invalid(**kwargs)

    def form_valid(self, **kwargs) -> HttpResponse:
        """
        Saves the form and sets a success message.
        Returns self._get_response. Override to add custom behavior.
        """
        self.form.save()
        messages.success(self.request, self.get_success_message(**kwargs))
        return self._get_response(**kwargs)

    def form_invalid(self, **kwargs) -> HttpResponse:
        """
        Sets an error message.
        Returns self._get_response. Override to add custom behavior.
        """
        messages.error(self.request, self.get_error_message(**kwargs))
        return self._get_response(**kwargs)

    def get_response_html(self, **kwargs):
        """
        On POST if the form is invalid instead of returning the
        POST_template the GET_template is returned (the form
        now contains the validation errors.)
        """
        if self.is_post_request and self.form.is_valid() is False:
            return self._render_templates(self.GET_template, self.GET_block, **kwargs)
        return super().get_response_html(**kwargs)

    def get_form_kwargs(self, **kwargs):
        """
        Return the keyword arguments for instantiating the form.
        Override to add more kwargs into the form.
        """
        form_kwargs = {"initial": self.get_initial(**kwargs)}
        if self.request.method in ("POST", "PUT"):
            form_kwargs.update(
                {
                    "data": self.request.POST,
                    "files": self.request.FILES,
                }
            )
        if self.hx_object:
            form_kwargs.update({"instance": self.hx_object})
        return form_kwargs

    def get_initial(self, **kwargs):
        """
        Override to set initial values in the form.
        """
        initial = {}

        if self.set_initial_from_kwargs:
            form_fields = self.form_class.base_fields
            for key, value in kwargs.items():
                if key in form_fields:
                    initial[key] = value

        return initial

    def get_success_message(self, **kwargs) -> str:
        """
        Message set when the form is valid. Override to set
        a custom message.
        """
        message = (
            f"{self.hx_object_to_str()} Saved Successfully." if self.hx_object else "Saved Successfully"
        )
        return message

    def get_error_message(self, **kwargs) -> str:
        """
        Message set when the form is invalid. Override to set
        a custom message.
        """
        message = (
            f"<b>{self.hx_object_to_str()} did not save  successfully.</b>"
            if self.hx_object
            else "<b>Did not save successfully</b>"
        )
        if self.add_form_errors_to_error_message:
            message += mark_safe("</br>") + self.get_form_errors(**kwargs)
        return mark_safe(message)

    def get_form_errors(self, **kwargs) -> str:
        """
        concatenates the form errors into an easily readable string.
        """
        errors = ""
        for k, v in self.form.errors.items():
            errors += f"{k}: {strip_tags(v)}" if k != "__all__" else strip_tags(v)
        return errors


class DeleteHxRequest(BaseHxRequest):
    """
    HxRequest for deleting objects.

    The object passed into a DeleteHxRequest is deleted.
    Override handle_delete for custom behavior.
    """

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Calls delete on the hx_object.
        """
        return self.delete(**kwargs)

    def delete(self, **kwargs) -> str:
        """
        Deletes the hx_object and sets a success message.
        Override to add custom behavior.
        """
        self.hx_object.delete()
        messages.success(self.request, self.get_success_message(**kwargs))
        return self._get_response(**kwargs)

    def get_success_message(self, **kwargs) -> str:
        """
        Message set when the object is deleted. Override to set
        a custom message.
        """
        message = (
            f"{self.hx_object_to_str()} deleted successfully."
            if self.hx_object
            else "Deleted successfully"
        )
        return message


class ModalHxRequest(BaseHxRequest):
    """
    A generic modal that can be used without needing to create a class that inherits from this one.
    It can be used by passing in title and body into the template tag as kwargs and passing in
    'hx-modal' as the name.

    Attributes
    ----------
    title : str
        Title of the modal, can be passed in as a kwarg and the kwarg will override this attribute
    modal_size_classes : str
        Classes to set the size of the modal, can be passed in as a kwarg and the kwarg will override this attribute
    """

    title: str = ""
    modal_size_classes: str = ""

    @cached_property
    def modal_container_id(self):
        return getattr(settings, "HX_REQUESTS_MODAL_CONTAINER_ID", "hx_modal_container")

    @cached_property
    def modal_template(self):
        modal_template = getattr(settings, "HX_REQUESTS_MODAL_TEMPLATE", None)
        if not modal_template:
            raise Exception("HX_REQUESTS_MODAL_TEMPLATE needs to be set in settings to use HXModal")
        return modal_template

    def get_response_html(self, **kwargs) -> str:
        """
        If it is a GET request, the entire modal template is returned with the body, title and `modal_size_classes`
        of the modal instead of just the `GET_template`.
        """
        if self.is_post_request is False:
            return self._get_modal_html(kwargs)
        return super().get_response_html(**kwargs)

    def _get_modal_html(self, kwargs):
        # Turn the GET_template into the body of the modal
        body_html = super().get_response_html(**kwargs)

        # Add the body to the context of the modal template
        modal_context = {
            "modal_size_classes": kwargs.get("modal_size_classes", self.modal_size_classes),
            "title": kwargs.get("title", self.title),
            "body": body_html,
        }
        return render_to_string(self.modal_template, modal_context, self.request)


class FormModalHxRequest(ModalHxRequest, FormHxRequest):
    """
    A modal to be used with a form.
    You need to create an HxRequest class that inherits from this one
    and set the needed attributes for a FormHxRequest.

    If the form is invalid the modal stays open and the form contains the validation
    errors. If the form is valid the modal will close.

    Attributes
    ----------
    close_modal_on_save : bool
        Close modal when form is valid. Set to False to keep the modal open even after
        the form saves.
    """

    close_modal_on_save = True

    @cached_property
    def modal_body_selector(self):
        return getattr(settings, "HX_REQUESTS_MODAL_BODY_ID", "#hx_modal_body")

    def get_triggers(self, **kwargs) -> list:
        """
        If the form is valid and the modal is set to close on save, closeHxModal is added to the triggers.
        """
        triggers = super().get_triggers(**kwargs)
        if self.is_post_request and self.form.is_valid() and self.close_modal_on_save:
            triggers.append("closeHxModal")
        return triggers

    def get_headers(self, **kwargs) -> Dict:
        """
        If the form is invalid, headers are set to retarget the innerHTML of the modal body.
        This is done to show the form errors.
        """
        headers = super().get_headers(**kwargs)
        if self.is_post_request and self.form.is_valid() is False:
            headers["HX-Retarget"] = self.modal_body_selector
            headers["HX-Reswap"] = "innerHTML"
        return headers
