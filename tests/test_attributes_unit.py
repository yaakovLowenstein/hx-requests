"""Guard tests for the documented class-attribute defaults."""

from django.test import RequestFactory, override_settings

from hx_requests.hx_requests import (
    BaseHxRequest,
    DeleteHxRequest,
    FormHxRequest,
    FormModalHxRequest,
    ModalHxRequest,
)


def test_base_hx_request_defaults():
    assert BaseHxRequest.name == ""
    assert BaseHxRequest.hx_object_name == "hx_object"
    assert BaseHxRequest.GET_template == ""
    assert BaseHxRequest.POST_template == ""
    assert BaseHxRequest.GET_block == ""
    assert BaseHxRequest.POST_block == ""
    assert BaseHxRequest.refresh_page is False
    assert BaseHxRequest.redirect is None
    assert BaseHxRequest.return_empty is False
    assert BaseHxRequest.no_swap is False
    assert BaseHxRequest.show_messages is True
    assert BaseHxRequest.get_views_context is True
    assert BaseHxRequest.kwargs_as_context is True
    assert BaseHxRequest.refresh_views_context_on_POST is False
    assert BaseHxRequest.use_current_url is False


def test_form_hx_request_defaults():
    assert FormHxRequest.form_class is None
    assert FormHxRequest.add_form_errors_to_error_message is False
    assert FormHxRequest.set_initial_from_kwargs is False
    assert FormHxRequest.show_form_invalid_message is True


def test_modal_hx_request_defaults():
    assert ModalHxRequest.title == ""
    assert ModalHxRequest.modal_size_classes == ""


def test_form_modal_defaults_and_inheritance():
    assert FormModalHxRequest.close_modal_on_save is True
    assert issubclass(FormModalHxRequest, ModalHxRequest)
    assert issubclass(FormModalHxRequest, FormHxRequest)
    assert issubclass(DeleteHxRequest, BaseHxRequest)


def make_hx(**attrs):
    hx = BaseHxRequest()
    hx.request = RequestFactory().get("/")
    for key, value in attrs.items():
        setattr(hx, key, value)
    return hx


@override_settings(HX_REQUESTS_USE_HX_MESSAGES=True)
def test_use_messages_follows_setting_and_show_messages():
    assert make_hx().use_messages is True
    assert make_hx(show_messages=False).use_messages is False


@override_settings(HX_REQUESTS_USE_HX_MESSAGES=False)
def test_use_messages_disabled_by_setting():
    assert make_hx().use_messages is False


def test_hx_object_to_str(db):
    from test_app.models import Widget

    hx = make_hx()
    hx.hx_object = None
    assert hx.hx_object_to_str() == ""
    hx.hx_object = Widget(name="x")
    assert hx.hx_object_to_str() == "Widget"


def test_setup_exposes_args_and_kwargs_like_django_view_setup():
    # Mirror Django's View.setup: the resolved positional/keyword args are
    # available on the handler as self.args / self.kwargs after setup, so a
    # hook can read them without every hook re-threading **kwargs.
    class _ViewStub:
        template_name = "simple.html"

    hx = BaseHxRequest()
    hx.view = _ViewStub()
    hx._setup_hx_request(RequestFactory().get("/"), "posarg", flavor="spicy")
    assert hx.args == ("posarg",)
    assert hx.kwargs == {"flavor": "spicy"}


def test_preset_hx_object_is_not_overwritten_at_setup():
    # A pre-set hx_object (assigned before setup) is left untouched -- setup
    # only resolves it from the token when it has not already been provided.
    class _ViewStub:
        template_name = "simple.html"

    hx = BaseHxRequest()
    hx.view = _ViewStub()
    sentinel = object()
    hx.hx_object = sentinel
    hx._setup_hx_request(RequestFactory().get("/"))
    assert hx.hx_object is sentinel
