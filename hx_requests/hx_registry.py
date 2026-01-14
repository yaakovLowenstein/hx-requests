"""
HxRequest Registry using AST parsing + lazy module import.

Behavior:
- initialize(): scans installed apps for hx_requests.py and hx_requests/ packages,
  parses files with AST to find classes with class attribute `name = "..."`,
  and stores name -> (module_path, class_name).
- get_hx_request(name): lazily imports the module and returns the class.
- get_all_hx_requests(): forces loading all discovered requests (imports all modules).

Notes:
- This approach intentionally does NOT validate BaseHxRequest inheritance at parse time.
  That only becomes known at import time.
"""

import ast
import importlib
import os
import threading
from typing import Dict, Optional, Tuple, Type, Union

from django.apps import apps

from hx_requests.hx_requests import BaseHxRequest


class HxRequestRegistry:
    # name -> class OR (module_path, class_name)
    _registry: Dict[str, Union[Type[BaseHxRequest], Tuple[str, str]]] = {}
    _initialized = False
    _lock = threading.Lock()

    @classmethod
    def initialize(cls):
        if cls._initialized:
            return

        with cls._lock:
            if cls._initialized:
                return

            for app in apps.get_app_configs():
                # 1) hx_requests.py at the root of the app
                hx_requests_file = os.path.join(app.path, "hx_requests.py")
                if os.path.isfile(hx_requests_file):
                    module_name = f"{app.label}.hx_requests"
                    cls._parse_file(hx_requests_file, module_name)

                # 2) hx_requests/ directory at the root of the app
                hx_requests_dir = os.path.join(app.path, "hx_requests")
                if os.path.isdir(hx_requests_dir):
                    cls._process_hx_requests_directory(hx_requests_dir, app.label)

            cls._initialized = True

    @classmethod
    def _process_hx_requests_directory(cls, directory_path: str, app_label: str):
        """Process all modules in hx_requests/ (including nested subdirectories) via AST."""
        for root, _, files in os.walk(directory_path):
            rel_path = os.path.relpath(root, directory_path)

            for file in files:
                if not (file.endswith(".py") and file != "__init__.py"):
                    continue

                file_path = os.path.join(root, file)
                mod_base = os.path.splitext(file)[0]

                if rel_path == ".":
                    module_name = f"{app_label}.hx_requests.{mod_base}"
                else:
                    subpackage = rel_path.replace(os.sep, ".")
                    module_name = f"{app_label}.hx_requests.{subpackage}.{mod_base}"

                cls._parse_file(file_path, module_name)

    @classmethod
    def _parse_file(cls, file_path: str, module_name: str):
        """
        Parse a Python file with AST to find class definitions containing
        a string literal class attribute called `name`.
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(source, filename=file_path)

            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    hx_name = cls._get_class_name_attribute(node)
                    if not hx_name:
                        continue

                    if hx_name in cls._registry:
                        raise Exception(f"Duplicate HxRequest name found: {hx_name}")

                    # Store for lazy loading: (module_path, class_name)
                    cls._registry[hx_name] = (module_name, node.name)

        except (OSError, SyntaxError):
            # Skip unreadable or unparsable files
            return

    @classmethod
    def _get_class_name_attribute(cls, class_node: ast.ClassDef) -> Optional[str]:
        """
        Extract the `name` class attribute from a class definition.

        Supports:
            name = "my_request"
            name: str = "my_request"
        Only returns when the value is a string literal.
        """
        for stmt in class_node.body:
            # name = "..."
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Name) and target.id == "name":
                        val = stmt.value
                        if isinstance(val, ast.Constant) and isinstance(val.value, str):
                            return val.value

            # name: str = "..."
            if isinstance(stmt, ast.AnnAssign):
                target = stmt.target
                if isinstance(target, ast.Name) and target.id == "name":
                    val = stmt.value
                    if isinstance(val, ast.Constant) and isinstance(val.value, str):
                        return val.value

        return None

    @classmethod
    def register_hx_request(cls, name: str, hx_request_class: Type[BaseHxRequest]):
        """
        Manual registration
        """
        if name in cls._registry:
            raise Exception(f"Duplicate HxRequest name found: {name}")
        cls._registry[name] = hx_request_class

    @classmethod
    def get_hx_request(cls, name: str):
        """
        Retrieve a single HxRequest class by name.
        Lazily imports the defining module if needed.
        """
        cls.initialize()

        entry = cls._registry.get(name)
        if entry is None:
            return None

        # already loaded
        if isinstance(entry, type):
            return entry

        module_name, class_name = entry

        try:
            module = importlib.import_module(module_name)
            hx_class = getattr(module, class_name, None)
            if hx_class is None:
                return None

            # Optional safety check: must still be a BaseHxRequest subclass
            # (keeps behavior sane if something else had `name = "..."`)
            if not (isinstance(hx_class, type) and issubclass(hx_class, BaseHxRequest)):
                return None

            # Cache loaded class
            cls._registry[name] = hx_class
            return hx_class

        except ModuleNotFoundError:
            return None

    @classmethod
    def get_all_hx_requests(cls):
        """
        Return all HxRequest entries as a dict of name -> class.

        This will import all discovered modules/classes (not lazy anymore).
        Not used but can be useful for debugging or admin views.
        """
        cls.initialize()

        for name, entry in list(cls._registry.items()):
            if isinstance(entry, tuple):
                cls.get_hx_request(name)

        # By now, any entries that failed to import or failed subclass check
        # may still be tuples. Filter them out to match typical expectation.
        return {k: v for k, v in cls._registry.items() if isinstance(v, type)}

    @classmethod
    def reset(cls):
        """Reset the registry state. Useful for tests."""
        cls._registry = {}
        cls._initialized = False
