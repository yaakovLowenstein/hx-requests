from typing import Dict

from django.apps import apps
from django.forms import Form
from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string

from hx_requests.views import MessagesMixin


class HXRequest:
    """
    HXRequest is the base class for Htmx requests.
    """

    name: str = ""
    GET_template: str = ""
    POST_template: str = ""
    hx_object_name: str = "hx_object"
    refresh_page: bool = False
    redirect: str = None

    def get_context_data(self, **kwargs) -> Dict:
        context = self.view.get_context_data()
        context["hx_kwargs"] = kwargs
        context[self.hx_object_name] = self.hx_object
        context["request"] = self.request
        context["hx_request"] = self
        return context

    def get_hx_object(self, request):
        if request.GET.get("object"):
            serialized_hx_object = request.GET.get("object")
            app_label, model, pk = serialized_hx_object.split("_")
            model = apps.get_model(app_label, model)
            return model.objects.get(pk=pk)

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.setup_hx_request(request)
        html = self.get_response(self.GET_template, **kwargs)
        return HttpResponse(html, headers=self.get_GET_headers(**kwargs))

    def setup_hx_request(self, request):
        self.request = request
        if not hasattr(self, "hx_object"):
            self.hx_object = self.get_hx_object(request)

    def get_GET_headers(self, **kwargs) -> Dict:
        return {}

    def get_response(self, template, **kwargs):
        return render_to_string(template, self.get_context_data(**kwargs), self.request)


class FormHXRequest(MessagesMixin, HXRequest):
    """
    Adds in form to context.
    On POST if the form is valid returns form_valid OR the POST_template.
    If the form is invalid returns form_invalid or the GET_template.

    form_invalid and form_valid can be overriden for custom behavior.
    Can override get_template_kwargs to add custom kwargs into the form.
    """

    form_class: Form = None
    _is_valid: bool

    def get_context_data(self, **kwargs) -> Dict:
        context = super().get_context_data(**kwargs)
        if self.request.method == "GET":
            context.update(self.get_GET_context_data(**kwargs))
        else:  # POST
            context.update(self.get_POST_context_data(**kwargs))
        context["form"] = self.form
        return context

    def get_GET_context_data(self, **kwargs) -> dict:
        return {}

    def get_POST_context_data(self, **kwargs) -> dict:
        return {}

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.setup_hx_request(request)
        self.form = self.form_class(**self.get_form_kwargs(**kwargs))
        return super().get(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.setup_hx_request(request)

        self.form = (
            self.form_class(**self.get_form_kwargs(**kwargs))
            if self.form_class
            else None
        )
        if not self.form_class or self.form.is_valid():
            response = self.form_valid(self.form, **kwargs)
            message, level = self.get_success_message(request, **kwargs), "success"

        else:
            response = self.form_invalid(self.form, **kwargs)
            message, level = self.get_error_message(request, **kwargs), "danger"

        return HttpResponse(
            response,
            headers=self.get_POST_headers(message=message, level=level, **kwargs),
        )

    def form_valid(self, form, **kwargs) -> str:
        form.save()
        # if refreshing page, no need for a post template
        # TODO for refresh and redirect. if either of them set new attr and check that here
        post_template = (
            self.POST_template
            if not self.refresh_page or self.redirect
            else self.GET_template
        )
        return self.get_response(post_template, **kwargs)

    def form_invalid(self, form, **kwargs) -> str:
        return self.get_response(self.GET_template, **kwargs)

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

    def get_success_message(self, request, **kwargs) -> str:
        object_name = (
            self.hx_object._meta.model.__name__.capitalize() if self.hx_object else None
        )
        message = (
            self.success_message or f"{object_name} saved successfully."
            if object_name
            else "Saved Successfully"
        )
        return message

    def get_error_message(self, request, **kwargs) -> str:
        object_name = (
            self.hx_object._meta.model.__name__.capitalize() if self.hx_object else None
        )
        message = (
            self.error_message or f"{object_name} did not save  successfully."
            if object_name
            else "Did not save successfully"
        )
        return message

    def get_POST_headers(self, **kwargs) -> Dict:
        headers = super().get_POST_headers(**kwargs)
        if self.refresh_page:
            headers["HX-Refresh"] = "true"
        elif self.redirect:
            headers["HX-Redirect"] = self.redirect
        return headers


class DeleteHXRequest(HXRequest, MessagesMixin):
    """
    HXRequest for deleting objects. Can override handle_delete
    for custom behavior.
    """

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.setup_hx_request(request)
        response = self.handle_delete(**kwargs)
        message, level = self.get_success_message(request, **kwargs), "success"
        return HttpResponse(
            response,
            headers=self.get_POST_headers(message=message, level=level, **kwargs),
        )

    def handle_delete(self, **kwargs) -> str:
        self.hx_object.delete()
        return self.get_response(self.POST_template, **kwargs)

    def get_success_message(self, request, **kwargs) -> str:
        object_name = (
            self.hx_object._meta.model.__name__.capitalize() if self.hx_object else None
        )
        message = (
            self.error_message or f"{object_name} deleted successfully."
            if object_name
            else "Deleted successfully"
        )
        return message

    def get_POST_headers(self, **kwargs) -> Dict:
        headers = super().get_POST_headers(**kwargs)
        if self.refresh_page:
            headers["HX-Refresh"] = "true"
        elif self.redirect:
            headers["HX-Redirect"] = self.redirect
        return headers
