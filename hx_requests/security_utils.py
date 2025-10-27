from __future__ import annotations

from typing import Any

from django.apps import apps

# ---------- App & URL helpers (pure) ----------


def app_label_from_module(module_name: str) -> str | None:
    """
    Resolve a Django app label from a module path.
    Uses apps.get_containing_app_config with a light fallback.
    """
    cfg = apps.get_containing_app_config(module_name)
    if cfg:
        return cfg.label
    top = module_name.split(".", 1)[0]
    try:
        return apps.get_app_config(top).label
    except Exception:
        return None


def app_label_for_object(obj: Any) -> str | None:
    mod = getattr(obj, "__module__", None)
    return app_label_from_module(mod) if mod else None


def is_globally_allowed(global_allow_spec, hx_app: str | None, hx_name: str) -> bool:
    """
    Global allow semantics:
      - list-form: any Hx from listed apps is globally allowed
      - dict-form: only listed Hx names (or __all__) from that app are globally allowed
    """
    if not global_allow_spec:
        return False

    # list-form: apps
    if isinstance(global_allow_spec, (list, tuple, set)):
        return bool(hx_app and hx_app in set(global_allow_spec))

    # dict-form: app -> ["__all__", "HxNameA", ...]
    if isinstance(global_allow_spec, dict):
        if not (hx_app and hx_app in global_allow_spec):
            return False
        rule = global_allow_spec[hx_app]
        if rule == "__all__":
            return True
        return hx_name in set(rule)

    return False
