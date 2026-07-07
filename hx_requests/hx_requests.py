from __future__ import annotations

import contextlib
import json
import logging
from functools import partial

from django.conf import settings
from django.contrib import messages
from django.contrib.messages import get_messages
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.forms import Form
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseNotAllowed
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.functional import cached_property
from django.utils.html import format_html, strip_tags
from render_block import render_block_to_string

from hx_requests.utils import deserialize, parse_model_ref, resolve_model_ref

logger = logging.getLogger(__name__)

# Leading keywords of DML statements that mutate rows. Used by the
# GET-must-not-mutate guard to spot a write executed during a handler's get().
_WRITE_SQL_VERBS = ("insert", "update", "delete")


@contextlib.contextmanager
def _warn_on_get_writes(handler_name):
    """
    Best-effort guard around a handler's ``get()``.

    Mutations belong on POST: a GET that writes to the database is replayable
    cross-site (``<img src>``, prefetch, ``<link>``) because GETs are not
    CSRF-protected -- a gap independent of the signed round-trip token. This
    logs a WARNING (it never blocks) when a DML write runs on the default
    database connection while ``get()`` executes.

    Best-effort by design: it watches the default connection (the common case)
    and matches on the leading SQL verb; it is a nudge toward the right pattern,
    not an airtight sandbox.
    """
    from django.db import connection

    warned = False

    def wrapper(execute, sql, params, many, context):
        nonlocal warned
        if not warned and sql.lstrip()[:6].lower() in _WRITE_SQL_VERBS:
            warned = True
            logger.warning(
                "hx_requests: %s wrote to the database during a GET. Mutations "
                "belong on POST -- a GET that writes is replayable cross-site "
                "(GETs aren't CSRF-protected). Move the write to post(), or set "
                "allow_writes_on_get = True on the handler to silence this if the "
                "write is known-safe (e.g. idempotent bookkeeping).",
                handler_name,
            )
        return execute(sql, params, many, context)

    with connection.execute_wrapper(wrapper):
        yield


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
    #: Optional model used to scope object resolution. When set, the default
    #: :meth:`get_queryset` resolves the round-trip object through this model's
    #: default manager. Mirrors Django's ``SingleObjectMixin.model``.
    model = None
    hx_object_name: str = "hx_object"
    GET_template: str | list = ""
    POST_template: str | list = ""
    GET_block: str | list = ""
    POST_block: str | list | dict[str, str] = ""
    refresh_page: bool = False
    redirect: str | None = None
    return_empty: bool = False
    no_swap = False
    show_messages: bool = True
    get_views_context: bool = True
    kwargs_as_context: bool = True
    refresh_views_context_on_POST: bool = False
    use_current_url: bool = False

    #: Per-handler authorization, checked in :meth:`dispatch` before ``get`` /
    #: ``post`` run. This is *the* authorization seam: a handler is responsible
    #: for deciding whether the current user may run it, regardless of which view
    #: or template triggered it.
    #:
    #: - ``login_required`` (default ``True``): an anonymous user gets a 404
    #:   (bodiless, so nothing about the handler leaks).
    #: - ``permission_required``: a permission string or list of them; an
    #:   authenticated user missing any of them gets a 403.
    #: - Override :meth:`has_permission` for arbitrary per-user/per-object logic.
    login_required: bool = True
    permission_required: str | list[str] | None = None

    #: Mutations belong on POST. By default the framework warns (never blocks)
    #: when a handler's ``get()`` writes to the database, because a GET that
    #: writes is replayable cross-site (GETs aren't CSRF-protected). Set this to
    #: ``True`` on a handler whose GET write is known-safe (e.g. idempotent
    #: bookkeeping) to silence that warning.
    allow_writes_on_get: bool = False

    #: Maps the friendly phase keys accepted in a dict return from
    #: :meth:`get_triggers` to their HTMX response-header names.
    trigger_header_map: dict[str, str] = {
        "trigger": "HX-Trigger",
        "after_settle": "HX-Trigger-After-Settle",
        "after_swap": "HX-Trigger-After-Swap",
    }

    @cached_property
    def is_post_request(self):
        """
        **Property** : Returns True if it is a POST request
        """
        return self.request.method == "POST"

    @cached_property
    def use_messages(self):
        return getattr(settings, "HX_REQUESTS_USE_HX_MESSAGES", False) and self.show_messages

    def get_context_data(self, **kwargs) -> dict:
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

    def get_context_on_GET(self, **kwargs) -> dict:
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

    def get_queryset(self):
        """
        The object-scoping seam. Return the queryset the round-trip object is
        resolved through, or ``None`` to fall back to the object's own model
        default manager.

        This is the idiomatic slot for row-level authorization -- the way
        Django CBVs teach ``get_queryset`` for the URL-pk trust boundary.
        Override it (or set :attr:`model`) to scope resolution to objects the
        current user may act on; a pk outside the queryset raises ``Http404``
        rather than silently loading someone else's row::

            def get_queryset(self):
                return Invoice.objects.filter(owner=self.request.user)
        """
        if self.model is not None:
            return self.model._default_manager.all()
        return None

    def get_hx_object(self, request, **kwargs):
        """
        Resolve the object carried by the (verified) round-trip token.

        Model instances are resolved through :meth:`get_queryset` when it is
        provided, so ownership scoping is honored; otherwise they fall back to
        the model's default manager. A pk that is absent from the resolved
        queryset raises ``Http404`` (object-level authorization), not a 500.
        Non-model values are deserialized as plain JSON.
        """
        serialized = request.GET.get("object")
        if not serialized:
            return None

        ref = parse_model_ref(serialized)
        if ref is None:
            return deserialize(serialized)

        queryset = self.get_queryset()
        try:
            return resolve_model_ref(*ref, queryset=queryset)
        except ObjectDoesNotExist:
            raise Http404(f"No {ref[1]} matches the given query for HxRequest '{self.name}'.")

    @cached_property
    def view_response(self):
        # Runs the page view's get() to harvest its context_data. Backed by a
        # cached_property so it runs at most once; assigning view_response
        # directly (as some unit tests do) pre-populates the cache and skips the
        # call. Normally triggered eagerly in _setup_hx_request when the context
        # will be rendered -- see _renders_view_context.
        return self.view.get(self.request, *self._view_get_args, **self._view_get_kwargs)

    def _renders_view_context(self) -> bool:
        # A POST that renders nothing from the view (refresh_page / redirect /
        # return_empty) discards the view context, so it need not be harvested.
        # Every other case -- all GETs, and POSTs that render a template -- uses
        # it, and on POST it must be captured *before* post() runs to preserve
        # the pre-mutation ("stale") context semantics.
        if self.is_post_request and (self.refresh_page or self.redirect or self.return_empty):
            return False
        return True

    def _setup_hx_request(self, request, *args, **kwargs):
        self.request = request
        self._view_get_args = args
        self._view_get_kwargs = kwargs
        self.renderer = Renderer()
        self.GET_template = self.GET_template or self.view.template_name
        self.POST_template = self.POST_template or self.view.template_name

        if not hasattr(self, "hx_object"):
            self.hx_object = self.get_hx_object(request, **kwargs)

        # Harvest the page view's context up front when it will be rendered, so
        # that on POST it reflects state captured before post() mutates anything
        # (the documented stale-context behavior). When the POST renders nothing
        # from the view, the harvest -- and the page view's query cost -- is
        # skipped entirely.
        if self.get_views_context and self._renders_view_context():
            _ = self.view_response

    def hx_object_to_str(self) -> str:
        if not self.hx_object:
            return ""
        # Use the model's verbose_name rather than str.capitalize() on the class
        # name -- capitalize() lower-cased the tail of CamelCase names ("MyModel"
        # -> "Mymodel"). Upper-case only the first character so the name reads as
        # a proper noun at the start of the success/error messages.
        verbose_name = str(self.hx_object._meta.verbose_name)
        return verbose_name[:1].upper() + verbose_name[1:]

    def get_headers(self, **kwargs) -> dict:
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

        headers.update(self.get_trigger_headers(**kwargs))
        return headers

    def get_triggers(self, **kwargs) -> list[str | dict] | dict[str, list]:
        """
        Override to set the triggers for the response.

        Return either:

        - A **list** of triggers, emitted on the ``HX-Trigger`` header (fired
          as soon as the response is received). Each item can be:

          - A string for a simple trigger (e.g. ``"myEvent"``).
          - A dict to pass details with the trigger
            (e.g. ``{"showMessage": {"level": "info", "message": "Saved!"}}``).

        - A **dict** keyed by trigger phase to target the full set of HTMX
          trigger headers, where each value is a list of the same shape::

              {
                  "trigger": ["eventA"],  # HX-Trigger
                  "after_settle": ["eventB"],  # HX-Trigger-After-Settle
                  "after_swap": [{"eventC": {...}}],  # HX-Trigger-After-Swap
              }

        Within any list, when a dict trigger is present the header value is
        formatted as a JSON object per the `HX-Trigger response header spec
        <https://htmx.org/headers/hx-trigger/>`_.
        """
        return []

    def get_trigger_headers(self, **kwargs) -> dict[str, str]:
        """
        Build the HTMX trigger response headers from :meth:`get_triggers`.

        Returns a ``{header_name: header_value}`` dict covering ``HX-Trigger``,
        ``HX-Trigger-After-Settle`` and ``HX-Trigger-After-Swap`` as needed.
        Phases with no triggers are omitted.
        """
        triggers = self.get_triggers(**kwargs)
        # A plain list keeps the historical behavior: everything on HX-Trigger.
        if not isinstance(triggers, dict):
            triggers = {"trigger": triggers}

        headers = {}
        for key, header_name in self.trigger_header_map.items():
            value = self._format_trigger_value(triggers.get(key) or [])
            if value:
                headers[header_name] = value
        return headers

    def format_triggers(self, **kwargs) -> str:
        """
        Format the ``HX-Trigger`` header value from :meth:`get_triggers`.

        Retained for backwards compatibility; only covers the ``HX-Trigger``
        header. For the full set of trigger headers see
        :meth:`get_trigger_headers`.
        """
        triggers = self.get_triggers(**kwargs)
        if isinstance(triggers, dict):
            triggers = triggers.get("trigger") or []
        return self._format_trigger_value(triggers)

    @staticmethod
    def _format_trigger_value(triggers: list[str | dict]) -> str:
        """
        Format a single list of triggers into one header value.

        If all triggers are plain strings, they are comma-separated. If any
        trigger carries details (dict), the value is JSON-encoded.
        """
        has_details = any(isinstance(t, dict) for t in triggers)
        if not has_details:
            return ", ".join(triggers)

        merged = {}
        for trigger in triggers:
            if isinstance(trigger, str):
                merged[trigger] = True
            elif isinstance(trigger, dict):
                merged.update(trigger)
        return json.dumps(merged)

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

        # Case: Single template, single block (or no block). A falsy block name
        # renders the whole template, so `None` and `""` both mean "no block".
        if isinstance(templates, str) and (blocks is None or isinstance(blocks, str)):
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

        # No branch matched: the template/block types are unsupported. Fail loud
        # instead of silently returning an empty partial (which surfaces later as
        # a mystifying blank swap).
        raise ValueError(
            f"Unsupported template/block combination: templates={templates!r}, blocks={blocks!r}. "
            "templates must be a str or list; blocks must be a str, list, dict, or None."
        )

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

    def has_permission(self, request: HttpRequest) -> bool:
        """
        Whether the current user may run this handler. Called by
        :meth:`check_permissions` only for *authenticated* users (the
        ``login_required`` gate runs first).

        The default enforces :attr:`permission_required`. Override for custom
        row-level or role logic::

            def has_permission(self, request):
                return self.hx_object.owner_id == request.user.pk
        """
        if not self.permission_required:
            return True
        perms = (
            [self.permission_required]
            if isinstance(self.permission_required, str)
            else list(self.permission_required)
        )
        return request.user.has_perms(perms)

    def check_permissions(self, request: HttpRequest) -> None:
        """
        Enforce per-handler authorization before routing to ``get`` / ``post``.

        - Anonymous user + auth needed -> ``Http404`` (bodiless; leaks nothing).
        - Authenticated user failing :meth:`has_permission` -> ``PermissionDenied``
          (403), the honest response for "logged in but not allowed".
        """
        user = getattr(request, "user", None)
        authenticated = bool(user and user.is_authenticated)

        if not authenticated:
            if self.login_required or self.permission_required:
                raise Http404(f"HxRequest '{self.name}' requires an authenticated user.")
            return

        if not self.has_permission(request):
            raise PermissionDenied(f"Not permitted to run HxRequest '{self.name}'.")

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Entry point for a resolved HxRequest, mirroring Django's
        ``View.dispatch``.

        Checks per-handler authorization (:meth:`check_permissions`), then
        routes the request to ``get`` or ``post`` based on the request method.
        Override this to run additional per-handler logic (setup, logging)
        before the method handler runs, calling ``super().dispatch(...)`` to
        continue routing.
        """
        self.check_permissions(request)
        method = request.method.lower()
        handler = getattr(self, method, None)
        if handler is None:
            return HttpResponseNotAllowed(["GET", "POST"])
        if method == "get" and not self.allow_writes_on_get:
            # Nudge writes onto POST -- see _warn_on_get_writes.
            with _warn_on_get_writes(type(self).__name__):
                return handler(request, *args, **kwargs)
        return handler(request, *args, **kwargs)

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
    show_form_invalid_message : bool
        If True (default) sets an error message on form_invalid. Set to False to suppress it
        (useful when the form already renders inline field errors).
    """

    form_class: Form = None
    add_form_errors_to_error_message: bool = False
    set_initial_from_kwargs: bool = False
    show_form_invalid_message: bool = True

    def get_context_data(self, **kwargs) -> dict:
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

        Builds the response from ``_get_response`` unless ``form_valid`` /
        ``form_invalid`` return their own ``HttpResponse``.
        """
        self.form = self.form_class(**self.get_form_kwargs(**kwargs))

        response = self.form_valid(**kwargs) if self.form.is_valid() else self.form_invalid(**kwargs)

        return response if response is not None else self._get_response(**kwargs)

    def form_valid(self, **kwargs) -> HttpResponse | None:
        """
        Saves the form and sets a success message.

        Return ``None`` (default) to let ``post`` build the standard response,
        or return an ``HttpResponse`` to short-circuit with custom output.
        """
        self.form.save()
        messages.success(self.request, self.get_success_message(**kwargs))

    def form_invalid(self, **kwargs) -> HttpResponse | None:
        """
        Sets an error message unless ``show_form_invalid_message`` is False.

        Return ``None`` (default) to let ``post`` build the standard response,
        or return an ``HttpResponse`` to short-circuit with custom output.
        """
        if self.show_form_invalid_message:
            messages.error(self.request, self.get_error_message(**kwargs))

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
        if self.hx_object:
            message = format_html("<b>{} did not save successfully.</b>", self.hx_object_to_str())
        else:
            message = format_html("<b>{}</b>", "Did not save successfully")
        if self.add_form_errors_to_error_message:
            # format_html escapes each interpolated part and returns a SafeString;
            # <br> is the valid line break (the old code emitted the invalid </br>).
            message = format_html("{}<br>{}", message, self.get_form_errors(**kwargs))
        return message

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

        Builds the response from ``_get_response`` unless ``delete`` returns
        its own ``HttpResponse``.
        """
        response = self.delete(**kwargs)
        return response if response is not None else self._get_response(**kwargs)

    def delete(self, **kwargs) -> HttpResponse | None:
        """
        Deletes the hx_object and sets a success message.

        Return ``None`` (default) to let ``post`` build the standard response,
        or return an ``HttpResponse`` to short-circuit with custom output.
        """
        self.hx_object.delete()
        messages.success(self.request, self.get_success_message(**kwargs))

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
            # Support both the list return and the phase-keyed dict return.
            if isinstance(triggers, dict):
                triggers.setdefault("trigger", []).append("closeHxModal")
            else:
                triggers.append("closeHxModal")
        return triggers

    def get_headers(self, **kwargs) -> dict:
        """
        If the form is invalid, headers are set to retarget the innerHTML of the modal body.
        This is done to show the form errors.
        """
        headers = super().get_headers(**kwargs)
        if self.is_post_request and self.form.is_valid() is False:
            headers["HX-Retarget"] = self.modal_body_selector
            headers["HX-Reswap"] = "innerHTML"
        return headers
