"""Unit tests for the pure helpers in hx_requests.security_utils."""

import pytest

from hx_requests.security_utils import (
    app_label_for_object,
    app_label_from_module,
    is_allowed_by_spec,
    is_globally_allowed,
    is_unauthenticated_allowed,
)


class TestIsAllowedBySpec:
    def test_empty_spec_denies(self):
        assert is_allowed_by_spec(None, "test_app", "simple_get") is False
        assert is_allowed_by_spec([], "test_app", "simple_get") is False
        assert is_allowed_by_spec({}, "test_app", "simple_get") is False

    @pytest.mark.parametrize("spec", [["test_app"], ("test_app",), {"test_app"}])
    def test_sequence_spec_allows_whole_app(self, spec):
        assert is_allowed_by_spec(spec, "test_app", "anything") is True
        assert is_allowed_by_spec(spec, "other_app", "anything") is False

    def test_dict_spec_all_allows_whole_app(self):
        spec = {"test_app": "__all__"}
        assert is_allowed_by_spec(spec, "test_app", "anything") is True
        assert is_allowed_by_spec(spec, "other_app", "anything") is False

    def test_dict_spec_name_list_allows_only_listed_names(self):
        spec = {"test_app": ["simple_get", "widget_form"]}
        assert is_allowed_by_spec(spec, "test_app", "simple_get") is True
        assert is_allowed_by_spec(spec, "test_app", "unlisted") is False

    def test_dict_spec_with_invalid_rule_denies(self):
        assert is_allowed_by_spec({"test_app": "simple_get"}, "test_app", "simple_get") is False

    def test_invalid_spec_type_raises(self):
        with pytest.raises(ValueError, match="Invalid allow_spec"):
            is_allowed_by_spec("not-a-collection", "test_app", "simple_get")

    def test_wrapper_functions_share_semantics(self):
        spec = {"test_app": "__all__"}
        assert is_globally_allowed(spec, "test_app", "x") is True
        assert is_unauthenticated_allowed(spec, "test_app", "x") is True


class TestAppLabelResolution:
    def test_module_inside_an_app(self):
        assert app_label_from_module("test_app.hx_requests") == "test_app"

    def test_top_level_app_module(self):
        assert app_label_from_module("hx_requests.utils") == "hx_requests"

    def test_unknown_module_returns_none(self):
        assert app_label_from_module("nonexistent.module.xyz") is None

    def test_app_label_for_class(self):
        from test_app.hx_requests import SimpleGetHx

        assert app_label_for_object(SimpleGetHx) == "test_app"

    def test_app_label_for_class_in_nested_module(self):
        from test_app_two.hx_requests.nested.deep import DeepHx

        assert app_label_for_object(DeepHx) == "test_app_two"
