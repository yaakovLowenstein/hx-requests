import importlib
import inspect
import os
import threading

from django.apps import apps

from hx_requests.hx_requests import BaseHxRequest


class HxRequestRegistry:
    _registry = {}
    _initialized = False
    _lock = threading.Lock()  # Lock to ensure thread safety
    _processed_classes = set()  # Keep track of processed classes

    @classmethod
    def initialize(cls):
        if cls._initialized:
            return

        with cls._lock:  # Ensure that only one thread can initialize at a time
            if cls._initialized:
                return  # Another thread might have finished initializing while we were waiting

            # Proceed with initialization
            for app in apps.get_app_configs():
                # Process hx_requests.py in the root directory of the app
                try:
                    module = importlib.import_module(f"{app.label}.hx_requests")
                    cls._process_module(module)
                except ModuleNotFoundError:
                    pass

                # Check if hx_requests directory exists in the root of the app
                hx_requests_dir = os.path.join(app.path, "hx_requests")
                if os.path.isdir(hx_requests_dir):
                    cls._process_hx_requests_directory(hx_requests_dir, app.label)

            cls._initialized = True

    @classmethod
    def _process_hx_requests_directory(cls, directory_path, app_label):
        """Process all modules in the hx_requests directory, including nested subdirectories."""
        for root, _, files in os.walk(directory_path):
            # Calculate the relative path from the hx_requests directory
            rel_path = os.path.relpath(root, directory_path)

            for file in files:
                if file.endswith(".py") and file != "__init__.py":
                    # Build the module name based on the relative path
                    if rel_path == ".":
                        module_name = f"{app_label}.hx_requests.{os.path.splitext(file)[0]}"
                    else:
                        # Convert path separators to dots for module path
                        subpackage = rel_path.replace(os.sep, ".")
                        module_name = f"{app_label}.hx_requests.{subpackage}.{os.path.splitext(file)[0]}"

                    try:
                        module = importlib.import_module(module_name)
                        cls._process_module(module)
                    except ModuleNotFoundError:
                        continue

    @classmethod
    def _process_module(cls, module):
        """Process a given module to register its HxRequest classes."""
        clsmembers = inspect.getmembers(module, inspect.isclass)
        for _, obj in clsmembers:
            if obj in cls._processed_classes:
                continue
            cls._processed_classes.add(obj)

            if issubclass(obj, BaseHxRequest) and getattr(obj, "name", None):
                cls.register_hx_request(obj.name, obj)

    @classmethod
    def register_hx_request(cls, name, hx_request_class):
        if name in cls._registry:
            raise Exception(f"Duplicate HxRequest name found: {name}")
        cls._registry[name] = hx_request_class

    @classmethod
    def get_hx_request(cls, name):
        cls.initialize()
        return cls._registry.get(name)

    @classmethod
    def get_all_hx_requests(cls):
        cls.initialize()
        return cls._registry
