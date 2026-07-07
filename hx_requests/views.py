from __future__ import annotations

from urllib.parse import parse_qs, urlparse

from django.conf import settings
from django.http import Http404, HttpRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie

from hx_requests.constants import HX_TOKEN_PARAM, KWARG_PREFIX
from hx_requests.hx_registry import HxRequestRegistry
from hx_requests.security_utils import (
    app_label_for_object,
    is_globally_allowed,
    is_unauthenticated_allowed,
)
from hx_requests.utils import (
    deserialize_kwargs,
    get_hx_payload,
    is_htmx_request,
)


@method_decorator(ensure_csrf_cookie, name="dispatch")
class HtmxViewMixin:
    """
    Mixin to be added to views that are using HxRequests.
    Hijacks the get and post to route them to the proper
    HxRequest.
    """

    allowed_hx_requests: list[str]
    use_global_hx_rules: bool = True  # True by default

    def dispatch(self, request, *args, **kwargs):
        # HTMX requests are handed off to the resolved HxRequest's own dispatch.
        # super().dispatch() is deliberately NOT called on this path: it would
        # route to the page view's own get/post and defeat the handoff. As a
        # consequence the page view's dispatch-based auth mixins
        # (LoginRequiredMixin, PermissionRequiredMixin, ...) only gate this path
        # when they sit *before* HtmxViewMixin in the MRO -- otherwise the
        # handoff runs first and skips them. `check_auth_mixin_ordering`
        # (checks.py) warns at startup when an auth mixin is ordered after this
        # mixin; enforce per-handler authorization on the HxRequest itself.
        if is_htmx_request(request) and request.method.lower() in self.http_method_names:
            request = self._resolve_hx_token(request)
            kwargs.update(self.get_hx_extra_kwargs(request))
            hx_request = self._setup_hx_request(request, *args, **kwargs)

            # Use request from hx_request, in case use_current_url is set to True
            return hx_request.dispatch(hx_request.request, *args, **kwargs)

        # Non-HTMX requests (full page loads, plain-htmx the view handles
        # itself) chain through super().dispatch() so the page view's own
        # mixins run normally instead of being short-circuited.
        return super().dispatch(request, *args, **kwargs)

    def get_hx_request(self, request):
        hx_request_name = request.GET.get("hx_request_name")
        if not hx_request_name:
            raise Http404("Missing required query param 'hx_request_name' for HTMX request.")

        hx_request_class = HxRequestRegistry.get_hx_request(hx_request_name)
        if not hx_request_class:
            raise Http404(f"No HxRequest found with the name '{hx_request_name}'.")

        if not self.is_hx_allowed(hx_request_class, request):
            raise Http404(f"HxRequest '{hx_request_name}' is not allowed here.")

        return hx_request_class()

    def _resolve_hx_token(self, request):
        """
        Verify the signed ``hx`` token and rebuild ``request.GET`` so the rest
        of the chain reads *trusted* framework data. Everything the framework
        controls (name, object, kwargs) comes from the signed token; any
        client-supplied framework params on the raw query string are dropped so
        they cannot shadow or forge the verified values. Non-framework params
        (page filters, runtime hx-vals) are left untouched.
        """
        if not request.GET.get(HX_TOKEN_PARAM):
            raise Http404("Missing required query param 'hx' for HTMX request.")
        payload = get_hx_payload(request)
        if payload is None:
            raise Http404("Invalid or tampered hx token.")

        # A path-bound token (bind_to_path handler) only verifies on the path it
        # was minted for -- replaying it against another view's path is rejected.
        # The global HX_REQUESTS_BIND_TOKEN_TO_PATH switch disables the check so
        # already-minted bound tokens stop 404ing the moment it is turned off.
        bound_path = payload.get("path")
        binding_enabled = getattr(settings, "HX_REQUESTS_BIND_TOKEN_TO_PATH", True)
        if binding_enabled and bound_path is not None and bound_path != request.path:
            raise Http404("hx token is bound to a different path.")

        sanitized = request.GET.copy()
        for key in list(sanitized.keys()):
            if key in (HX_TOKEN_PARAM, "hx_request_name", "object") or key.startswith(KWARG_PREFIX):
                del sanitized[key]
        sanitized["hx_request_name"] = payload["name"]
        if payload.get("object"):
            sanitized["object"] = payload["object"]

        request.GET = sanitized
        # Verified, serialized kwargs from the token -- the only source of
        # kwargs-as-context. Raw query params never feed this again.
        request._hx_kwargs = payload.get("kwargs", {})
        return request

    def get_hx_extra_kwargs(self, request):
        return deserialize_kwargs(**getattr(request, "_hx_kwargs", {}))

    def _setup_hx_request(self, request, *args, **kwargs):
        hx_request = self.get_hx_request(request)
        hx_request.view = self

        if getattr(hx_request, "use_current_url", False):
            request = self._use_current_url(request)
        hx_request._setup_hx_request(request, *args, **kwargs)
        return hx_request

    def is_hx_allowed(self, hx_cls: type, request: HttpRequest) -> bool:
        hx_name = getattr(hx_cls, "name", None)
        if not hx_name:
            return False

        hx_app = app_label_for_object(hx_cls)
        view_app = app_label_for_object(self.__class__)

        # --- auth settings ---
        require_auth = getattr(settings, "HX_REQUESTS_REQUIRE_AUTH", True)
        unauth_allow_spec = getattr(settings, "HX_REQUESTS_UNAUTHENTICATED_ALLOW", None)

        # --- policy settings ---
        enforce_same_app = getattr(settings, "HX_REQUESTS_ENFORCE_SAME_APP", True)
        global_allow_spec = getattr(settings, "HX_REQUESTS_GLOBAL_ALLOW", None)
        view_allow_list = set(getattr(self, "allowed_hx_requests", []) or [])
        use_global_hx_rules = bool(getattr(self, "use_global_hx_rules", True))

        # --- auth gate ---
        user_is_authed = bool(getattr(request, "user", None) and request.user.is_authenticated)
        if (
            require_auth
            and not user_is_authed
            and not is_unauthenticated_allowed(unauth_allow_spec, hx_app, hx_name)
        ):
            return False

        # --- policy signals ---
        same_app_ok = bool(hx_app and view_app and hx_app == view_app)
        global_ok = is_globally_allowed(global_allow_spec, hx_app, hx_name)

        # No view list and same-app enforcement is OFF -> allow all
        if not view_allow_list and not enforce_same_app:
            return True

        # If there is a view allow list and the hx_name is in it -> allow
        if hx_name in view_allow_list:
            return True

        # If additive = False it must be in the view allow list to be allowed
        if view_allow_list and use_global_hx_rules is False and hx_name not in view_allow_list:
            return False

        # View list present + additive=True -> list OR policy
        if view_allow_list and use_global_hx_rules:
            return global_ok or same_app_ok

        # No view list -> policy
        return global_ok or (enforce_same_app and same_app_ok)

    def _use_current_url(self, request):
        # Start with the current GET params
        merged_get = request.GET.copy()

        # Check if HX-Current-URL is in the headers
        hx_current_url = request.headers.get("HX-Current-URL")
        if hx_current_url:
            # Parse the URL and extract its query parameters
            parsed_url = urlparse(hx_current_url)
            additional_params = parse_qs(parsed_url.query)

            # Add each HX param only if not already present. Framework params
            # (name/object/kwargs/token) are never merged from the current URL:
            # those are trusted only via the signed token, not raw query input.
            for key, values in additional_params.items():
                if key in (HX_TOKEN_PARAM, "hx_request_name", "object") or key.startswith(KWARG_PREFIX):
                    continue
                if key not in merged_get:
                    merged_get.setlist(key, values)

        # Now override request.GET
        request.GET = merged_get
        return request
