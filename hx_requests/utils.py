from urllib.parse import quote_plus, urlparse

from django.apps import apps
from django.db import models
from urllib.parse import urlencode, quote_plus

KWARG_PREFIX = "___"
def is_htmx_request(request):
    return "HX-Request" in request.headers


def serialize_kwargs(**kwargs):
    serialize_kwargs = {}
    for k, v in kwargs.items():
        prefixed_k = KWARG_PREFIX + k
        if isinstance(v, models.Model):
            serialize_kwargs[prefixed_k] = f"{KWARG_PREFIX}{v._meta.app_label}_{v._meta.model.__name__}_{v.pk}"
        else:
            serialize_kwargs[prefixed_k] = v
    return serialize_kwargs


def deserialize_kwargs(**kwargs):
    deserialize_kwargs = {}
    for k, v in kwargs.items():
        prefixed_k = k.replace(KWARG_PREFIX, "")
        if v.startswith(KWARG_PREFIX):
            app_label, model, pk = v.replace(KWARG_PREFIX, "").split("_")
            model = apps.get_model(app_label, model)
            instance = model.objects.get(pk=pk)
            deserialize_kwargs[prefixed_k] = instance
        else:
            deserialize_kwargs[prefixed_k] = v
    return deserialize_kwargs


def get_url(context, hx_request_name, obj, use_full_path=False, **kwargs):
    request = context["request"]
    url = request.path

    params = {"hx_request_name": hx_request_name}

    if use_full_path:
        get_params = {}
        for k, v in request.GET.lists():
            if k not in ["hx_request_name", "object"] and not k.startswith(KWARG_PREFIX):
                get_params[k] = v[0] if len(v) == 1 else v
        params.update(get_params)

    if obj:
        params["object"] = f"{obj._meta.app_label}_{obj._meta.model.__name__}_{obj.pk}"

    # Parse the URL to check if there are existing query parameters
    parsed_url = urlparse(url)
    if parsed_url.query:  # If there are existing query parameters
        url += "&"  # Append using "&"
    else:
        url += "?"  # Otherwise, start with "?"

    url += urlencode(params)

    serialized_kwargs = serialize_kwargs(**kwargs)
    url += "".join(f"&{k}={quote_plus(str(v))}" for k, v in serialized_kwargs.items())

    return url

def get_csrf_token(context):
    cookie = context["request"].headers.get("cookie")
    if cookie and "csrftoken" in cookie:
        token = cookie.split("csrftoken=")[1].split(";")[0]
        return token