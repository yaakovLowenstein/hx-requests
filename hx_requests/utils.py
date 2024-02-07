from urllib.parse import quote_plus

from django.apps import apps
from django.db import models
from urllib.parse import urlencode, quote_plus


def is_htmx_request(request):
    return "HX-Request" in request.headers


def serialize_kwargs(**kwargs):
    for k, v in kwargs.items():
        if isinstance(v, models.Model):
            kwargs[k] = f"___{v._meta.app_label}_{v._meta.model.__name__}_{v.pk}"
    return kwargs


def deserialize_kwargs(**kwargs):
    for k, v in kwargs.items():
        if v.startswith("___"):
            app_label, model, pk = v.replace("___", "").split("_")
            model = apps.get_model(app_label, model)
            instance = model.objects.get(pk=pk)
            kwargs[k] = instance
    return kwargs


def get_url(context, hx_request_name, obj, use_full_path=False, **kwargs):
    request = context["request"]
    url = request.path

    params = {"hx_request_name": hx_request_name}

    if use_full_path:
        params.update(
            {
                k: v
                for k, v in request.GET.items()
                if k not in ["hx_request_name", "object"]
            }
        )

    if obj:
        params["object"] = f"{obj._meta.app_label}_{obj._meta.model.__name__}_{obj.pk}"

    url += f"?{urlencode(params)}"

    serialized_kwargs = serialize_kwargs(**kwargs)
    url += "".join(f"&{k}={quote_plus(str(v))}" for k, v in serialized_kwargs.items())

    return url


def get_csrf_token(context):
    cookie = context["request"].headers.get("cookie")
    if cookie and "csrftoken" in cookie:
        token = cookie.split("csrftoken=")[1].split(";")[0]
        return token
