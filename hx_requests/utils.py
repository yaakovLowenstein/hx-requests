import json
from urllib.parse import urlencode

from django.apps import apps
from django.core import signing
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.middleware.csrf import get_token

MODEL_INSTANCE_PREFIX = "model_instance__"
KWARG_PREFIX = "___"
__ = "__"

# Query param that carries the signed round-trip token, and the signing salt.
# The salt only namespaces the signature; secrecy comes from SECRET_KEY. A
# per-name salt is intentionally NOT used: the handler name lives inside the
# signed payload, so a token minted for one handler cannot be replayed against
# another (tampering the name invalidates the signature).
HX_TOKEN_PARAM = "hx"
HX_SIGNING_SALT = "hx-requests"


def serialize(value):
    if isinstance(value, models.Model):
        return (
            f"{MODEL_INSTANCE_PREFIX}{value._meta.app_label}{__}{value._meta.model_name}{__}{value.pk}"
        )
    return json.dumps(value, cls=DjangoJSONEncoder)


def parse_model_ref(value):
    """
    If ``value`` is a serialized model-instance reference
    (``model_instance__<app>__<model>__<pk>``), return ``(app_label,
    model_name, pk)``; otherwise return ``None``. Uses a length-based slice
    (not ``str.replace``) so a pk/label that happens to contain the prefix
    can't be mangled.
    """
    if isinstance(value, str) and value.startswith(MODEL_INSTANCE_PREFIX):
        app_label, model_name, pk = value[len(MODEL_INSTANCE_PREFIX) :].split(__)
        return app_label, model_name, pk
    return None


def deserialize(value):
    ref = parse_model_ref(value)
    if ref is not None:
        return resolve_model_ref(*ref)
    return json.loads(value)


def resolve_model_ref(app_label, model_name, pk, queryset=None):
    """
    Fetch a model instance from a parsed reference. Resolution goes through
    ``queryset`` when one is supplied (the object-scoping seam -- see
    ``BaseHxRequest.get_queryset``); otherwise it falls back to the model's
    ``_default_manager``.

    The default manager (not ``_base_manager``) is deliberate: soft-delete and
    tenant scoping expressed on the default manager are respected automatically,
    so an object hidden by the default manager cannot be resolved unless a
    handler explicitly widens the queryset. Raises the model's
    ``DoesNotExist`` when the pk is absent from the resolved queryset.
    """
    if queryset is None:
        queryset = apps.get_model(app_label, model_name)._default_manager.all()
    return queryset.get(pk=pk)


def is_htmx_request(request):
    return "HX-Request" in request.headers


def serialize_kwargs(**kwargs):
    serialized_kwargs = {}
    for k, v in kwargs.items():
        prefixed_k = KWARG_PREFIX + k
        serialized_kwargs[prefixed_k] = serialize(v)
    return serialized_kwargs


def deserialize_kwargs(**kwargs):
    deserialized_kwargs = {}
    for k, v in kwargs.items():
        if not k.startswith(KWARG_PREFIX):
            continue
        prefixed_k = k.replace(KWARG_PREFIX, "")
        deserialized_kwargs[prefixed_k] = deserialize(v)
    return deserialized_kwargs


def sign_hx_payload(hx_request_name, obj=None, **kwargs):
    """
    Pack everything the template tag controls -- the handler name, the object,
    and the extra kwargs -- into a single HMAC-signed token. The client can
    read the token (it is base64-encoded JSON) but cannot forge it without
    ``SECRET_KEY``, which closes the object/kwarg/name tampering vectors.
    """
    payload = {
        "name": hx_request_name,
        "object": serialize(obj) if obj is not None else None,
        "kwargs": serialize_kwargs(**kwargs),
    }
    return signing.dumps(payload, salt=HX_SIGNING_SALT)


def unsign_hx_payload(token):
    """
    Verify and unpack a signed token. Raises ``signing.BadSignature`` (a base
    class covering tampered/truncated/hand-crafted tokens) on any failure.
    """
    return signing.loads(token, salt=HX_SIGNING_SALT)


def get_hx_payload(request):
    """
    Return the *verified* contents of the signed ``hx`` token on ``request`` as
    ``{"name": ..., "object": ..., "kwargs": ...}``, or ``None`` if the request
    carries no token or the signature is invalid.

    This is the supported way for view code to introspect an inbound
    hx-requests request (detect it, read its name/object/kwargs) *without*
    going through ``HtmxViewMixin`` dispatch. The ``object`` and ``kwargs``
    values are still in serialized form -- pass them through :func:`deserialize`
    / :func:`deserialize_kwargs` to get live values.
    """
    token = request.GET.get(HX_TOKEN_PARAM)
    if not token:
        return None
    try:
        return unsign_hx_payload(token)
    except signing.BadSignature:
        return None


def get_hx_request_name(request):
    """
    Return the :code:`HxRequest` name from the signed ``hx`` token, or ``None``
    if the request isn't a (valid) hx-requests request.

    Replaces reading ``request.GET["hx_request_name"]`` directly, which no
    longer exists on the query string now that routing data is signed.
    """
    payload = get_hx_payload(request)
    return payload["name"] if payload else None


def is_hx_request(request):
    """
    Return ``True`` if ``request`` is an hx-requests request -- i.e. it carries
    a valid signed ``hx`` token bound for a registered handler.

    This is distinct from :func:`is_htmx_request`, which only checks the
    ``HX-Request`` header (*any* htmx request). Use it to tell a plain htmx
    request (sort / filter / paginate) apart from one routed to an
    :code:`HxRequest`::

        if is_htmx_request(request) and not is_hx_request(request):
            ...  # plain htmx -- let the underlying view handle it
    """
    return get_hx_payload(request) is not None


def get_url(context, hx_request_name, obj, use_full_path=False, **kwargs):
    request = context["request"]

    # Non-framework params (page filters/pagination) stay as ordinary loose
    # query params -- they are untrusted runtime input the view already reads.
    # Only the framework's routing/deserialization data is signed.
    params = {}
    if use_full_path:
        for k, v in request.GET.lists():
            if k in (HX_TOKEN_PARAM, "hx_request_name", "object") or k.startswith(KWARG_PREFIX):
                continue
            params[k] = v[0] if len(v) == 1 else v

    params[HX_TOKEN_PARAM] = sign_hx_payload(hx_request_name, obj, **kwargs)

    return f"{request.path}?{urlencode(params, doseq=True)}"


def get_csrf_token(context):
    # Delegate to Django rather than hand-splitting the Cookie header: get_token
    # handles CSRF_USE_SESSIONS, token masking/rotation, and custom cookie names,
    # and always returns a usable token (minting one on the request if needed) so
    # a POST is never left without its CSRF header.
    return get_token(context["request"])
