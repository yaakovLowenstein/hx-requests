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
    return is_allowed_by_spec(global_allow_spec, hx_app, hx_name)


def is_unauthenticated_allowed(spec, hx_app: str | None, hx_name: str | None) -> bool:
    """
    Unauthenticated allowlist semantics (separate from is_globally_allowed):
      - list/tuple/set: any Hx from listed apps is allowed unauthenticated
      - dict:
          app -> "__all__"                 # all Hx in that app
          app -> ["HxNameA", "HxNameB"]    # only these Hx names in that app
    """
    return is_allowed_by_spec(spec, hx_app, hx_name)


def is_allowed_by_spec(allow_spec, hx_app: str | None, hx_name: str) -> bool:
    """
    General allowlist semantics:
      - list/tuple/set: any Hx from listed apps is allowed
      - dict:
          app -> "__all__"                 # all Hx in that app
          app -> ["HxNameA", "HxNameB"]    # only these Hx names in that app
    """
    if not allow_spec:
        return False

    if isinstance(allow_spec, (list, tuple, set)):
        return hx_app in set(allow_spec)

    if isinstance(allow_spec, dict):
        if hx_app not in allow_spec:
            return False
        rule = allow_spec[hx_app]
        if rule == "__all__":
            return True
        if isinstance(rule, (list, tuple, set)):
            return hx_name in set(rule)
        return False

    if not isinstance(allow_spec, (list, tuple, set, dict)):
        raise ValueError("Invalid allow_spec format. Must be list, tuple, set, or dict.")

    return False
