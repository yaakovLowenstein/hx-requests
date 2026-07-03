"""Unit tests for hx_requests.utils: serialization, URL building, csrf."""

import datetime

import pytest
from django.test import RequestFactory
from test_app.models import Widget

from hx_requests.utils import (
    deserialize,
    deserialize_kwargs,
    get_csrf_token,
    get_url,
    is_htmx_request,
    serialize,
    serialize_kwargs,
)

# --------------------------------------------------------------------------
# serialize / deserialize
# --------------------------------------------------------------------------


@pytest.mark.django_db()
def test_model_instance_round_trip(widget):
    serialized = serialize(widget)
    assert serialized == f"model_instance__test_app__widget__{widget.pk}"
    assert deserialize(serialized) == widget


@pytest.mark.parametrize(
    ("value", "serialized"),
    [
        ("hello", '"hello"'),
        (5, "5"),
        (True, "true"),
        (None, "null"),
        ({"a": 1}, '{"a": 1}'),
        ([1, 2], "[1, 2]"),
    ],
)
def test_json_values_round_trip(value, serialized):
    assert serialize(value) == serialized
    assert deserialize(serialized) == value


def test_dates_serialize_via_django_json_encoder():
    assert serialize(datetime.date(2020, 1, 2)) == '"2020-01-02"'


@pytest.mark.django_db()
def test_deserialize_uses_base_manager():
    # Objects hidden by a default manager would still resolve; at minimum the
    # base manager must be able to fetch a plain instance by pk.
    widget = Widget.objects.create(name="managed")
    assert deserialize(serialize(widget)).pk == widget.pk


# --------------------------------------------------------------------------
# serialize_kwargs / deserialize_kwargs
# --------------------------------------------------------------------------


def test_serialize_kwargs_prefixes_keys():
    assert serialize_kwargs(flavor="spicy") == {"___flavor": '"spicy"'}


def test_deserialize_kwargs_strips_prefix_and_ignores_other_keys():
    result = deserialize_kwargs(___flavor='"spicy"', plain="ignored", hx_request_name="x")
    assert result == {"flavor": "spicy"}


@pytest.mark.django_db()
def test_kwargs_round_trip_with_model_instance(widget):
    serialized = serialize_kwargs(widget=widget, count=3)
    result = deserialize_kwargs(**serialized)
    assert result == {"widget": widget, "count": 3}


def test_none_kwarg_round_trip():
    assert deserialize_kwargs(**serialize_kwargs(maybe=None)) == {"maybe": None}


# --------------------------------------------------------------------------
# is_htmx_request
# --------------------------------------------------------------------------


def test_is_htmx_request_detects_header():
    request = RequestFactory().get("/", HTTP_HX_REQUEST="true")
    assert is_htmx_request(request) is True


def test_is_htmx_request_without_header():
    request = RequestFactory().get("/")
    assert is_htmx_request(request) is False


# --------------------------------------------------------------------------
# get_url
# --------------------------------------------------------------------------


def make_context(path="/page/", **extra):
    return {"request": RequestFactory().get(path, **extra)}


def test_get_url_basic():
    url = get_url(make_context(), "simple_get", None)
    assert url == "/page/?hx_request_name=simple_get"


@pytest.mark.django_db()
def test_get_url_includes_serialized_object(widget):
    url = get_url(make_context(), "simple_get", widget)
    assert f"object=model_instance__test_app__widget__{widget.pk}" in url


def test_get_url_appends_serialized_kwargs():
    url = get_url(make_context(), "simple_get", None, flavor="spicy")
    assert "&___flavor=%22spicy%22" in url


def test_get_url_use_full_path_carries_existing_params():
    context = make_context("/page/?q=search&page=1&page=2")
    url = get_url(context, "simple_get", None, use_full_path=True)
    assert "q=search" in url
    assert url.count("page=") >= 2  # multi-value params preserved


def test_get_url_use_full_path_filters_internal_params():
    context = make_context("/page/?q=search&hx_request_name=old&object=x&___junk=%22y%22")
    url = get_url(context, "new_name", None, use_full_path=True)
    assert "q=search" in url
    assert "old" not in url
    assert "junk" not in url
    assert "object=" not in url


# --------------------------------------------------------------------------
# get_csrf_token
# --------------------------------------------------------------------------


def test_get_csrf_token_reads_cookie():
    context = make_context(HTTP_COOKIE="csrftoken=tok123; other=1")
    assert get_csrf_token(context) == "tok123"


def test_get_csrf_token_with_leading_cookies():
    context = make_context(HTTP_COOKIE="a=b; csrftoken=tok456")
    assert get_csrf_token(context) == "tok456"


def test_get_csrf_token_missing_returns_none():
    assert get_csrf_token(make_context(HTTP_COOKIE="a=b")) is None
    assert get_csrf_token(make_context()) is None
