"""Tests for HxRequestRegistry: AST discovery, lazy loading, manual registration."""

import logging

import pytest

from hx_requests.hx_registry import DuplicateHxRequestNameError, HxRequestRegistry
from hx_requests.hx_requests import BaseHxRequest

# --------------------------------------------------------------------------
# Discovery
# --------------------------------------------------------------------------


def test_discovers_file_style_hx_requests():
    from test_app.hx_requests import SimpleGetHx

    assert HxRequestRegistry.get_hx_request("simple_get") is SimpleGetHx


def test_discovers_directory_style_hx_requests():
    from test_app_two.hx_requests.widgets import OtherAppHx

    assert HxRequestRegistry.get_hx_request("other_app_hx") is OtherAppHx


def test_discovers_nested_directory_modules_and_annotated_names():
    from test_app_two.hx_requests.nested.deep import DeepHx

    assert HxRequestRegistry.get_hx_request("deep_hx") is DeepHx


def test_unknown_name_returns_none():
    assert HxRequestRegistry.get_hx_request("no_such_hx_request") is None


def test_class_with_name_but_not_an_hx_request_is_filtered_out():
    assert HxRequestRegistry.get_hx_request("not_an_hx_request") is None


def test_get_all_hx_requests_loads_everything(clean_registry):
    all_requests = HxRequestRegistry.get_all_hx_requests()
    assert "simple_get" in all_requests
    assert "other_app_hx" in all_requests
    assert "deep_hx" in all_requests
    assert "not_an_hx_request" not in all_requests
    assert all(isinstance(cls, type) for cls in all_requests.values())


# --------------------------------------------------------------------------
# Lazy loading
# --------------------------------------------------------------------------


def test_entries_are_lazy_until_first_access(clean_registry):
    HxRequestRegistry.reset()
    HxRequestRegistry.initialize()
    assert isinstance(HxRequestRegistry._registry["simple_get"], tuple)

    cls = HxRequestRegistry.get_hx_request("simple_get")
    assert issubclass(cls, BaseHxRequest)
    # The loaded class is cached back into the registry.
    assert HxRequestRegistry._registry["simple_get"] is cls


def test_missing_module_returns_none(clean_registry):
    HxRequestRegistry._registry["ghost"] = ("nonexistent_module_xyz", "Ghost")
    assert HxRequestRegistry.get_hx_request("ghost") is None


def test_missing_class_in_module_returns_none(clean_registry):
    HxRequestRegistry._registry["ghost"] = ("test_app.hx_requests", "NoSuchClass")
    assert HxRequestRegistry.get_hx_request("ghost") is None


# --------------------------------------------------------------------------
# AST parsing
# --------------------------------------------------------------------------


def test_parse_file_registers_string_name_classes(clean_registry, tmp_path):
    HxRequestRegistry.reset()
    source = tmp_path / "scratch.py"
    source.write_text("class Foo:\n    name = 'scratch_foo'\n")
    HxRequestRegistry._parse_file(str(source), "scratch.module")
    assert HxRequestRegistry._registry["scratch_foo"] == ("scratch.module", "Foo")


def test_parse_file_registers_annotated_name(clean_registry, tmp_path):
    HxRequestRegistry.reset()
    source = tmp_path / "scratch.py"
    source.write_text("class Foo:\n    name: str = 'scratch_annotated'\n")
    HxRequestRegistry._parse_file(str(source), "scratch.module")
    assert "scratch_annotated" in HxRequestRegistry._registry


def test_parse_file_ignores_non_string_names(clean_registry, tmp_path):
    HxRequestRegistry.reset()
    source = tmp_path / "scratch.py"
    source.write_text("class Foo:\n    name = 123\n\nclass Bar:\n    pass\n")
    HxRequestRegistry._parse_file(str(source), "scratch.module")
    assert HxRequestRegistry._registry == {}


def test_parse_file_skips_unparsable_files_with_warning(clean_registry, tmp_path, caplog):
    HxRequestRegistry.reset()
    source = tmp_path / "scratch.py"
    source.write_text("def broken(:\n")
    with caplog.at_level(logging.WARNING, logger="hx_requests.hx_registry"):
        HxRequestRegistry._parse_file(str(source), "scratch.module")
    assert HxRequestRegistry._registry == {}
    # The file is skipped, but loudly -- a silent skip resurfaces as a 404.
    assert "could not parse" in caplog.text
    assert "scratch.py" in caplog.text


def test_parse_file_skips_unreadable_file_with_warning(clean_registry, caplog):
    # A file that cannot be read (missing / unreadable) is skipped loudly
    # rather than blowing up discovery for the whole app.
    HxRequestRegistry.reset()
    with caplog.at_level(logging.WARNING, logger="hx_requests.hx_registry"):
        HxRequestRegistry._parse_file("/no/such/hx_requests_file.py", "scratch.missing")
    assert HxRequestRegistry._registry == {}
    assert "could not read it" in caplog.text


def test_duplicate_names_raise(clean_registry, tmp_path):
    HxRequestRegistry.reset()
    source = tmp_path / "scratch.py"
    source.write_text("class Foo:\n    name = 'dup_name'\n")
    HxRequestRegistry._parse_file(str(source), "scratch.module")
    with pytest.raises(DuplicateHxRequestNameError, match="Duplicate HxRequest name found: dup_name"):
        HxRequestRegistry._parse_file(str(source), "scratch.other_module")


# --------------------------------------------------------------------------
# Manual registration and reset
# --------------------------------------------------------------------------


def test_manual_registration(clean_registry):
    class ManualHx(BaseHxRequest):
        pass

    HxRequestRegistry.register_hx_request("manual_hx", ManualHx)
    assert HxRequestRegistry.get_hx_request("manual_hx") is ManualHx


def test_manual_registration_rejects_duplicates(clean_registry):
    class ManualHx(BaseHxRequest):
        pass

    HxRequestRegistry.register_hx_request("manual_dup", ManualHx)
    with pytest.raises(DuplicateHxRequestNameError, match="Duplicate HxRequest name found: manual_dup"):
        HxRequestRegistry.register_hx_request("manual_dup", ManualHx)


def test_reset_clears_state_and_allows_reinitialization(clean_registry):
    HxRequestRegistry.reset()
    assert HxRequestRegistry._registry == {}
    assert HxRequestRegistry._initialized is False
    # get_hx_request re-initializes on demand.
    assert HxRequestRegistry.get_hx_request("simple_get") is not None
