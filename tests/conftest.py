import pytest


@pytest.fixture()
def widget(db):
    from test_app.models import Widget

    return Widget.objects.create(name="gizmo", description="a widget")


@pytest.fixture()
def user(db):
    from django.contrib.auth.models import User

    return User.objects.create_user(username="tester", password="pw")


@pytest.fixture()
def clean_registry():
    """
    Save and restore the global HxRequestRegistry state around tests that
    mutate it (reset, manual registration, parsing scratch files).
    """
    from hx_requests.hx_registry import HxRequestRegistry

    saved_registry = dict(HxRequestRegistry._registry)
    saved_initialized = HxRequestRegistry._initialized
    yield HxRequestRegistry
    HxRequestRegistry._registry = saved_registry
    HxRequestRegistry._initialized = saved_initialized
