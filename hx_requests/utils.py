from django.apps import apps
from django.db import models


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


def get_url(context, hx_request_name, object, **kwargs):
    url = context["request"].path
    if not "?" in url:
        url += f"?hx_request_name={hx_request_name}"
    else:
        url += f"&hx_request_name={hx_request_name}"
    url += (
        f"&object={object._meta.app_label}_{object._meta.model.__name__}_{object.pk}"
        if object
        else ""
    )
    serialized_kwargs = serialize_kwargs(**kwargs)
    extra_params = ""
    for k, v in serialized_kwargs.items():
        extra_params += f"&{k}={v}"
    url += extra_params
    return url


def get_csrf_token(context):
    token = (
        context["request"].headers.get("cookie").split("csrftoken=")[1].split(";")[0]
    )
    return token
