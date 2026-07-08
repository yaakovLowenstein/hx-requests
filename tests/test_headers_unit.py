"""Unit tests for BaseHxRequest.get_headers precedence and method handling."""

from tests.helpers import make_hx


def test_no_flags_no_headers():
    assert make_hx().get_headers() == {}


def test_refresh_page_on_post():
    assert make_hx("post", refresh_page=True).get_headers() == {"HX-Refresh": "true"}


def test_redirect_on_post():
    headers = make_hx("post", redirect="/next/").get_headers()
    assert headers == {"HX-Redirect": "/next/"}


def test_refresh_page_takes_precedence_over_redirect():
    headers = make_hx("post", refresh_page=True, redirect="/next/").get_headers()
    assert headers == {"HX-Refresh": "true"}


def test_refresh_and_redirect_ignored_on_get():
    assert make_hx("get", refresh_page=True, redirect="/next/").get_headers() == {}


def test_no_swap_applies_on_get_and_post():
    assert make_hx("get", no_swap=True).get_headers() == {"HX-Reswap": "none"}
    assert make_hx("post", no_swap=True).get_headers() == {"HX-Reswap": "none"}


def test_trigger_headers_are_merged_in():
    hx = make_hx("post", refresh_page=True)
    hx.get_triggers = lambda **kwargs: ["evt"]
    assert hx.get_headers() == {"HX-Refresh": "true", "HX-Trigger": "evt"}


def test_is_post_request_property():
    assert make_hx("post").is_post_request is True
    assert make_hx("get").is_post_request is False
