"""Unit tests for hx_requests.utils: serialization, URL building, csrf."""

import datetime
from urllib.parse import parse_qs, urlparse

import pytest
from django.test import RequestFactory
from test_app.models import Gadget, Widget

from hx_requests.utils import (
    HX_TOKEN_PARAM,
    deserialize,
    deserialize_kwargs,
    get_hx_payload,
    get_hx_request_name,
    get_url,
    is_htmx_request,
    is_hx_request,
    parse_model_ref,
    resolve_model_ref,
    serialize,
    serialize_kwargs,
    sign_hx_payload,
    unsign_hx_payload,
)
from tests.helpers import make_context

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


def test_serialize_unsaved_instance_fails_loudly():
    # An unsaved instance has pk=None; serializing it produced '...__None',
    # which later blew up in queryset.get(pk="None"). Fail at serialize time
    # with a clear error instead.
    widget = Widget(name="unsaved")
    assert widget.pk is None
    with pytest.raises(ValueError, match="unsaved"):
        serialize(widget)


@pytest.mark.django_db()
def test_deserialize_uses_default_manager():
    # Resolution goes through the *default* manager, so anything the default
    # manager hides (soft-delete / tenant scoping) cannot be resolved. A
    # visible row still resolves fine.
    gadget = Gadget.objects.create(name="visible")
    assert deserialize(serialize(gadget)).pk == gadget.pk

    archived = Gadget.all_objects.create(name="archived", archived=True)
    with pytest.raises(Gadget.DoesNotExist):
        deserialize(serialize(archived))


# --------------------------------------------------------------------------
# parse_model_ref / resolve_model_ref
# --------------------------------------------------------------------------


@pytest.mark.django_db()
def test_parse_model_ref_splits_a_model_reference(widget):
    assert parse_model_ref(serialize(widget)) == ("test_app", "widget", str(widget.pk))


@pytest.mark.parametrize("value", ['"hello"', "5", "true", "null", '{"a": 1}'])
def test_parse_model_ref_returns_none_for_non_model_values(value):
    assert parse_model_ref(value) is None


def test_parse_model_ref_pk_may_contain_double_underscore():
    # A string PK containing '__' is legitimate (server-minted). Splitting
    # without a maxsplit produced too many segments -> ValueError -> 500.
    # App label and model name never contain '__', so a left split with
    # maxsplit 2 keeps the whole tail as the pk.
    assert parse_model_ref("model_instance__test_app__widget__a__b") == (
        "test_app",
        "widget",
        "a__b",
    )


@pytest.mark.django_db()
def test_resolve_model_ref_uses_default_manager_by_default():
    gadget = Gadget.objects.create(name="visible")
    ref = ("test_app", "gadget", str(gadget.pk))
    assert resolve_model_ref(*ref) == gadget


@pytest.mark.django_db()
def test_resolve_model_ref_honors_a_scoped_queryset(widget):
    other = Widget.objects.create(name="out-of-scope")
    scoped = Widget.objects.filter(pk=widget.pk)
    # In-scope pk resolves...
    assert resolve_model_ref("test_app", "widget", str(widget.pk), queryset=scoped) == widget
    # ...out-of-scope pk is not found (the object-authz boundary).
    with pytest.raises(Widget.DoesNotExist):
        resolve_model_ref("test_app", "widget", str(other.pk), queryset=scoped)


# --------------------------------------------------------------------------
# serialize_kwargs / deserialize_kwargs
# --------------------------------------------------------------------------


def test_serialize_kwargs_keys_are_unprefixed():
    assert serialize_kwargs(flavor="spicy") == {"flavor": '"spicy"'}


def test_deserialize_kwargs_deserializes_every_entry():
    result = deserialize_kwargs(flavor='"spicy"', count="3")
    assert result == {"flavor": "spicy", "count": 3}


@pytest.mark.django_db()
def test_kwargs_round_trip_with_model_instance(widget):
    serialized = serialize_kwargs(widget=widget, count=3)
    result = deserialize_kwargs(**serialized)
    assert result == {"widget": widget, "count": 3}


def test_none_kwarg_round_trip():
    assert deserialize_kwargs(**serialize_kwargs(maybe=None)) == {"maybe": None}


def test_kwarg_name_containing_prefix_sequence_round_trips():
    # A kwarg whose name contains the '___' sequence must survive the
    # serialize -> deserialize round trip unchanged. The old prefix-strip
    # (str.replace) removed *every* occurrence, silently renaming
    # 'foo___bar' -> 'foobar'.
    serialized = serialize_kwargs(**{"foo___bar": "x"})
    assert deserialize_kwargs(**serialized) == {"foo___bar": "x"}


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
# sign_hx_payload / unsign_hx_payload
# --------------------------------------------------------------------------


@pytest.mark.django_db()
def test_sign_payload_round_trips_name_object_and_kwargs(widget):
    token = sign_hx_payload("edit_widget", widget, flavor="spicy")
    payload = unsign_hx_payload(token)
    assert payload["name"] == "edit_widget"
    assert deserialize(payload["object"]) == widget
    assert deserialize_kwargs(**payload["kwargs"]) == {"flavor": "spicy"}


def test_sign_payload_without_object_or_kwargs():
    payload = unsign_hx_payload(sign_hx_payload("simple_get"))
    assert payload == {"name": "simple_get", "object": None, "kwargs": {}}


def test_tampered_token_fails_verification():
    from django.core import signing

    token = sign_hx_payload("simple_get")
    with pytest.raises(signing.BadSignature):
        unsign_hx_payload(token[:-3] + "xxx")


def test_handler_name_is_bound_to_the_signature():
    # The name lives inside the signed payload, so it cannot be swapped for
    # another handler without invalidating the token (this is why a per-name
    # salt is unnecessary). The token is base64, so a naive str.replace never
    # touches the name -- decode the payload, swap the name, re-encode with the
    # original signature, and assert loads() rejects it.
    import json

    from django.core import signing

    token = sign_hx_payload("view_user")
    payload_b64, signed_rest = token.split(":", 1)  # "<payload>:<timestamp>:<sig>"
    payload = json.loads(signing.b64_decode(payload_b64.encode()))
    assert payload["name"] == "view_user"

    payload["name"] = "delete_user"
    forged_b64 = signing.b64_encode(json.dumps(payload).encode()).decode()
    forged = f"{forged_b64}:{signed_rest}"

    assert forged != token  # the swap really changed the token
    with pytest.raises(signing.BadSignature):
        unsign_hx_payload(forged)


# --------------------------------------------------------------------------
# get_hx_payload / get_hx_request_name (public introspection accessors)
# --------------------------------------------------------------------------


@pytest.mark.django_db()
def test_get_hx_payload_returns_verified_contents(widget):
    token = sign_hx_payload("edit_widget", widget, flavor="spicy")
    request = RequestFactory().get("/", data={HX_TOKEN_PARAM: token})
    payload = get_hx_payload(request)
    assert payload["name"] == "edit_widget"
    assert deserialize(payload["object"]) == widget
    assert deserialize_kwargs(**payload["kwargs"]) == {"flavor": "spicy"}


def test_get_hx_payload_none_without_token():
    assert get_hx_payload(RequestFactory().get("/")) is None


def test_get_hx_payload_none_on_bad_signature():
    request = RequestFactory().get("/", data={HX_TOKEN_PARAM: "not-a-real-token"})
    assert get_hx_payload(request) is None


def test_get_hx_request_name_reads_name_from_token():
    request = RequestFactory().get("/", data={HX_TOKEN_PARAM: sign_hx_payload("simple_get")})
    assert get_hx_request_name(request) == "simple_get"


def test_get_hx_request_name_none_for_plain_htmx():
    # The plain-htmx fall-through check: no token -> not an hx handler.
    assert get_hx_request_name(RequestFactory().get("/?page=2")) is None


def test_is_hx_request_true_with_valid_token():
    request = RequestFactory().get("/", data={HX_TOKEN_PARAM: sign_hx_payload("simple_get")})
    assert is_hx_request(request) is True


def test_is_hx_request_false_without_token():
    assert is_hx_request(RequestFactory().get("/?page=2")) is False


def test_is_hx_request_false_on_bad_signature():
    request = RequestFactory().get("/", data={HX_TOKEN_PARAM: "garbage"})
    assert is_hx_request(request) is False


# --------------------------------------------------------------------------
# get_url
# --------------------------------------------------------------------------


def token_from_url(url):
    query = parse_qs(urlparse(url).query)
    return unsign_hx_payload(query[HX_TOKEN_PARAM][0])


def test_get_url_basic():
    url = get_url(make_context(), "simple_get", None)
    assert url.startswith("/page/?")
    payload = token_from_url(url)
    assert payload["name"] == "simple_get"
    assert payload["object"] is None


@pytest.mark.django_db()
def test_get_url_includes_serialized_object(widget):
    url = get_url(make_context(), "simple_get", widget)
    assert deserialize(token_from_url(url)["object"]) == widget


def test_get_url_appends_serialized_kwargs():
    url = get_url(make_context(), "simple_get", None, flavor="spicy")
    assert deserialize_kwargs(**token_from_url(url)["kwargs"]) == {"flavor": "spicy"}


def test_get_url_use_full_path_carries_existing_params():
    context = make_context("/page/?q=search&page=1&page=2")
    url = get_url(context, "simple_get", None, use_full_path=True)
    query = parse_qs(urlparse(url).query)
    assert query["q"] == ["search"]
    assert query["page"] == ["1", "2"]  # multi-value params preserved
    assert token_from_url(url)["name"] == "simple_get"


def test_get_url_use_full_path_filters_internal_params():
    context = make_context("/page/?q=search&hx_request_name=old&object=x&extra=keep")
    url = get_url(context, "new_name", None, use_full_path=True)
    query = parse_qs(urlparse(url).query)
    assert query["q"] == ["search"]
    # Stale framework params from the current URL are not re-emitted loose.
    assert "hx_request_name" not in query
    assert "object" not in query
    # Ordinary loose params (page filters etc.) are carried forward untouched.
    # There is no longer any '___'-prefixed "framework kwarg" notion: kwargs
    # travel only inside the signed token, so nothing on the query string is
    # treated as special beyond the token param and the two legacy names above.
    assert query["extra"] == ["keep"]
    assert token_from_url(url)["name"] == "new_name"
