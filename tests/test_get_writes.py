"""Tests for the GET-must-not-mutate guard.

Mutations belong on POST. A GET that writes to the database is replayable
cross-site (via ``<img src>`` etc.) because GETs aren't CSRF-protected -- a gap
independent of the signed-token work. The guard is best-effort: it wraps the
default DB connection while a handler's ``get()`` runs and logs a WARNING if a
DML write executes. It never raises, and ``allow_writes_on_get`` opts out.
"""

import logging

import pytest
from test_app.hx_requests import (
    GetWritesAllowedHx,
    GetWritesHx,
    SimpleGetHx,
)
from test_app.models import Widget
from test_app.views import BaseView

from hx_requests.hx_requests import BaseHxRequest
from tests.helpers import hx_get

pytestmark = pytest.mark.django_db

GUARD_LOGGER = "hx_requests.hx_requests"


def test_default_forbids_writes_on_get():
    assert BaseHxRequest.allow_writes_on_get is False


def test_write_during_get_logs_a_warning(caplog):
    with caplog.at_level(logging.WARNING, logger=GUARD_LOGGER):
        response = hx_get(GetWritesHx, BaseView)

    # The write still happens (guard warns, never blocks) ...
    assert response.status_code == 200
    assert Widget.objects.filter(name="written-during-get").exists()
    # ... and it is surfaced, naming the offending handler.
    assert "GetWritesHx" in caplog.text
    assert "GET" in caplog.text


def test_read_only_get_does_not_warn(caplog):
    with caplog.at_level(logging.WARNING, logger=GUARD_LOGGER):
        response = hx_get(SimpleGetHx, BaseView)

    assert response.status_code == 200
    assert caplog.text == ""


def test_allow_writes_on_get_silences_the_guard(caplog):
    with caplog.at_level(logging.WARNING, logger=GUARD_LOGGER):
        response = hx_get(GetWritesAllowedHx, BaseView)

    assert response.status_code == 200
    assert Widget.objects.filter(name="written-during-get").exists()
    assert caplog.text == ""
