import importlib
import inspect
import threading

from django.apps import apps

from hx_requests.hx_requests import BaseHXRequest


class HXRequestRegistry:
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
                try:
                    module = importlib.import_module(f"{app.label}.hx_requests")
                    clsmembers = inspect.getmembers(module, inspect.isclass)
                    for _, obj in clsmembers:
                        # Check if the class has already been processed
                        if obj in cls._processed_classes:
                            continue
                        cls._processed_classes.add(obj)

                        if issubclass(obj, BaseHXRequest) and getattr(obj, "name", None):
                            cls.register_hx_request(obj.name, obj)
                except ModuleNotFoundError:
                    continue

            cls._initialized = True

    @classmethod
    def register_hx_request(cls, name, hx_request_class):
        if name in cls._registry:
            raise Exception(f"Duplicate HXRequest name found: {name}")
        cls._registry[name] = hx_request_class

    @classmethod
    def get_hx_request(cls, name):
        cls.initialize()
        return cls._registry.get(name)

    @classmethod
    def get_all_hx_requests(cls):
        cls.initialize()
        return cls._registry
