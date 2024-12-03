import json
from urllib.parse import quote_plus, urlencode, urlparse

from django.apps import apps
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models

MODEL_INSTANCE_PREFIX = "model_instance__"
KWARG_PREFIX = "___"
__ = "__"


def serialize(value):
    if isinstance(value, models.Model):
        return (
            f"{MODEL_INSTANCE_PREFIX}{value._meta.app_label}{__}{value._meta.model_name}{__}{value.pk}"
        )
    return json.dumps(value, cls=DjangoJSONEncoder)


def deserialize(value):
    if value.startswith(MODEL_INSTANCE_PREFIX):
        value = value.replace(MODEL_INSTANCE_PREFIX, "")
        app_label, model_name, pk = value.split(__)
        model = apps.get_model(app_label, model_name)
        manager = model._base_manager
        return manager.get(pk=pk)
    return json.loads(value)


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
        params["object"] = serialize(obj)

    # Parse the URL to check if there are existing query parameters
    parsed_url = urlparse(url)
    if parsed_url.query:  # If there are existing query parameters
        url += "&"  # Append using "&"
    else:
        url += "?"  # Otherwise, start with "?"

    url += urlencode(params, doseq=True)

    serialized_kwargs = serialize_kwargs(**kwargs)
    url += "".join(f"&{k}={quote_plus(str(v))}" for k, v in serialized_kwargs.items())

    return url


def get_csrf_token(context):
    cookie = context["request"].headers.get("cookie")
    if cookie and "csrftoken" in cookie:
        token = cookie.split("csrftoken=")[1].split(";")[0]
        return token
