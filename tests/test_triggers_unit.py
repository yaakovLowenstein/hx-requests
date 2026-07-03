"""Unit tests for HX-Trigger formatting."""

import json

from django.test import RequestFactory

from hx_requests.hx_requests import BaseHxRequest


def make_hx(triggers, method="get"):
    class TriggeredHx(BaseHxRequest):
        def get_triggers(self, **kwargs):
            return triggers

    hx = TriggeredHx()
    hx.request = getattr(RequestFactory(), method)("/")
    return hx


class TestFormatTriggers:
    def test_empty_list(self):
        assert make_hx([]).format_triggers() == ""

    def test_single_string(self):
        assert make_hx(["eventA"]).format_triggers() == "eventA"

    def test_strings_are_comma_separated(self):
        assert make_hx(["a", "b", "c"]).format_triggers() == "a, b, c"

    def test_dict_triggers_become_json(self):
        value = make_hx([{"eventA": {"x": 1}}]).format_triggers()
        assert json.loads(value) == {"eventA": {"x": 1}}

    def test_mixed_strings_and_dicts_merge_into_json(self):
        value = make_hx(["plain", {"detailed": {"x": 1}}]).format_triggers()
        assert json.loads(value) == {"plain": True, "detailed": {"x": 1}}


class TestTriggersInHeaders:
    def test_triggers_land_on_the_hx_trigger_header(self):
        assert make_hx(["a", "b"]).get_headers() == {"HX-Trigger": "a, b"}

    def test_no_triggers_means_no_header(self):
        assert make_hx([]).get_headers() == {}

    def test_details_are_json_encoded_in_the_header(self):
        headers = make_hx([{"e": {"k": "v"}}]).get_headers()
        assert json.loads(headers["HX-Trigger"]) == {"e": {"k": "v"}}
