import json
from email import header
from typing import Dict

from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.forms import Form
from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string
from django.utils.functional import cached_property
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe

from hx_requests.hx_messages import HXMessages


class BaseHXRequest:
    """
    Base class for HXRequests. Class to be used for basic GET and POST requests.

    Attributes
    ----------
    name : str
         Unique name that needs to be matched in the template tag rendering the HXRequest
    hx_object_name : str, optional
        Name that the hx_object is passed into the context with
    GET_template : str, optional
        Template rendered for a GET request
    POST_template : str, optional
        Template rendered for a POST request
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
    """

    name: str = ""
    hx_object_name: str = "hx_object"
    messages: HXMessages
    GET_template: str = ""
    POST_template: str = ""
    refresh_page: bool = False
    redirect: str = None
    return_empty: bool = False
    no_swap = False
    show_messages: bool = True

    @cached_property
    def is_post_request(self):
        """
        **Property** : Returns True if it is a POST request
        """
        return self.request.method == "POST"

    @cached_property
    def use_messages(self):
        return (
            getattr(settings, "HX_REQUESTS_USE_HX_MESSAGES", False)
            and self.show_messages
        )

    def get_context_data(self, **kwargs) -> Dict:
        """ "
        Adds the context from the view and additionally adds:
            | kwargs as hx_kwargs
            | hx_object as {self.hx_object_name} (default is hx_object)
            | self as hx_request
        """
        context = self.view.get_context_data()
        context["hx_kwargs"] = kwargs

        # TODO move the next 2 lines to either form valid or somewhere else..
        if self.hx_object and self.hx_object.pk:
            self.hx_object.refresh_from_db()

        context[self.hx_object_name] = self.hx_object

        context["request"] = self.request
        context["hx_request"] = self
        if self.is_post_request:
            context.update(self.get_post_context_data(**kwargs))
        return context

    def get_post_context_data(self, **kwargs):
        """
        Adds extra context to the context data only on POST.
        """
        return {}

    def get_hx_object(self, request):
        """
        If an 'object' was passed in, deserialize it.
        """
        if request.GET.get("object"):
            serialized_hx_object = request.GET.get("object")
            app_label, model, pk = serialized_hx_object.split("_")
            model = apps.get_model(app_label, model)
            return model.objects.get(pk=pk)

    def setup_hx_request(self, request):
        self.request = request
        self.messages = HXMessages()
        # TODO maybe remove this line (why is it there?)
        if not hasattr(self, "hx_object"):
            self.hx_object = self.get_hx_object(request)

    def hx_object_to_str(self) -> str:
        return (
            self.hx_object._meta.model.__name__.capitalize() if self.hx_object else ""
        )

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
        if self.use_messages:
            headers.update(self.get_message_headers(**kwargs))
        return headers

    def get_response_html(self, **kwargs) -> str:
        """
        Prepare the HTML for the response.
        """
        if self.is_post_request:
            if self.refresh_page or self.redirect or self.return_empty:
                html = ""
                if self.use_messages:
                    self.set_synchronous_messages(**kwargs)
            else:
                html = render_to_string(
                    self.POST_template, self.get_context_data(**kwargs), self.request
                )

        else:
            html = render_to_string(
                self.GET_template, self.get_context_data(**kwargs), self.request
            )
        return html

    def get_response(self, **kwargs):
        """
        Gets the response.
        """
        html = self.get_response_html(**kwargs)
        return HttpResponse(
            html,
            headers=self.get_headers(**kwargs),
        )

    def get_message_headers(self, **kwargs) -> Dict:
        headers = {}
        if self.messages.get_message():
            headers["HX-Trigger"] = json.dumps(
                {
                    "showMessages": {
                        "message": self.messages.get_message()[0],
                        "tag": self.messages.get_message()[1],
                    }
                }
            )
        return headers

    def set_synchronous_messages(self, **kwargs):
        # TODO this should really match what message type it is (might need 2nd part of tuple to be tuple of actual tag and then class)
        messages.success(self.request, self.messages.get_message()[0])

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Method that all GET requests hit.
        """
        return self.get_response(**kwargs)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Method that all POST requests hit.
        """
        return self.get_response(**kwargs)


class FormHXRequest(BaseHXRequest):
    """
    Adds in form to context.
    On POST if the form is valid returns form_valid OR the POST_template.
    If the form is invalid returns form_invalid or the GET_template.

    form_invalid and form_valid can be overriden for custom behavior.
    Can override get_template_kwargs to add custom kwargs into the form.
    """

    form_class: Form = None
    add_form_errors_to_error_message: bool = False

    def get_context_data(self, **kwargs) -> Dict:
        context = super().get_context_data(**kwargs)
        context["form"] = self.form
        return context

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.form = self.form_class(**self.get_form_kwargs(**kwargs))
        return self.get_response(**kwargs)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.form = self.form_class(**self.get_form_kwargs(**kwargs))

        if self.form.is_valid():
            self.messages.success(self.get_success_message(**kwargs))
            return self.form_valid(**kwargs)

        else:
            self.messages.error(self.get_error_message(**kwargs))
            return self.form_invalid(**kwargs)

    def form_valid(self, **kwargs) -> str:
        self.form.save()
        return self.get_response(**kwargs)

    def form_invalid(self, **kwargs) -> str:
        return self.get_response(**kwargs)

    def get_response_html(self, **kwargs):
        if self.is_post_request and self.form.is_valid() is False:
            return render_to_string(
                self.GET_template, self.get_context_data(**kwargs), self.request
            )
        return super().get_response_html(**kwargs)

    def get_form_kwargs(self, **kwargs):
        """Return the keyword arguments for instantiating the form."""
        form_kwargs = {"initial": self.get_initial(**kwargs)}
        if self.request.method in ("POST", "PUT"):
            form_kwargs.update(
                {
                    "data": self.request.POST,
                    "files": self.request.FILES,
                }
            )
        if getattr(self, "hx_object"):
            form_kwargs.update({"instance": self.hx_object})
        return form_kwargs

    def get_initial(self, **kwargs):
        return {}

    def get_success_message(self, **kwargs) -> str:
        message = (
            f"{self.hx_object_to_str()} Saved Successfully."
            if self.hx_object
            else "Saved Successfully"
        )
        return message

    def get_error_message(self, **kwargs) -> str:
        message = (
            f"<b>{self.hx_object_to_str()} did not save  successfully.</b>"
            if self.hx_object
            else "<b>Did not save successfully</b>"
        )
        if self.add_form_errors_to_error_message:
            message += mark_safe("</br>") + self.get_form_errors(**kwargs)
        return mark_safe(message)

    def get_form_errors(self, **kwargs) -> str:
        errors = ""
        for k, v in self.form.errors.items():
            errors += f"{k}: {strip_tags(v)}" if k != "__all__" else strip_tags(v)
        return errors


class DeleteHXRequest(BaseHXRequest):
    """
    HXRequest for deleting objects. Can override handle_delete
    for custom behavior.
    """

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.messages.success(self.get_success_message(**kwargs))
        return self.handle_delete(**kwargs)

    def handle_delete(self, **kwargs) -> str:
        self.hx_object.delete()
        return self.get_response(**kwargs)

    def get_success_message(self, **kwargs) -> str:
        message = (
            f"{self.hx_object_to_str()} deleted successfully."
            if self.hx_object
            else "Deleted successfully"
        )
        return message


class HXModal(BaseHXRequest):
    name = "hx_modal"

    @cached_property
    def modal_container_id(self):
        return getattr(settings, "HX_REQUSTS_MODAL_CONTAINER_ID", "hx_modal_container")

    @cached_property
    def modal_template(self):
        return getattr(settings, "HX_REQUSTS_MODAL_TEMPLATE", "hx_requests/modal.html")

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.set_modal_body(**kwargs)
        return super().get(request, *args, **kwargs)

    def set_modal_body(self, **kwargs):
        self.body = kwargs.get("body")
        if self.GET_template != self.modal_template:
            self.body = self.GET_template
            self.GET_template = self.modal_template

    def get_context_data(self, **kwargs) -> Dict:
        context = super().get_context_data(**kwargs)
        body = getattr(self, "body", None) or kwargs.get("body", self.GET_template)
        context["title"] = kwargs.get("title", self.hx_object)
        context["modal_container_id"] = self.modal_container_id
        context["body"] = (
            render_to_string(body, context=context)
            if body.split(".")[-1] == "html"
            else body
        )
        return context


class HXFormModal(HXModal, FormHXRequest):
    @cached_property
    def modal_body_selector(self):
        return getattr(settings, "HX_REQUSTS_MODAL_BODY_SELECTOR", ".modal-body")

    def form_invalid(self, **kwargs) -> str:
        self.set_modal_body()
        return self.get_response(**kwargs)

    def get_headers(self, **kwargs) -> Dict:
        headers = super().get_headers(**kwargs)
        if self.is_post_request:
            if self.form.is_valid():
                headers["HX-Trigger"] = "modalFormValid"
            else:
                headers["HX-Retarget"] = self.modal_body_selector
        return headers


class HXMessagesRequest(BaseHXRequest):
    name = "hx_messages"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.GET_template = getattr(settings, "HX_REQUESTS_HX_MESSAGES_TEMPLATE")
        if not self.GET_template:
            raise Exception(
                "HX_REQUESTS_HX_MESSAGES_TEMPLATE is not set in settings.py. Define a template to be used for messages."
            )
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["message"] = self.request.GET.get("message")
        context["tag"] = self.request.GET.get("tag")
        return context
