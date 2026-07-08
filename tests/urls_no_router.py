"""A router-less root URLconf.

Used by tests that exercise *legacy* dispatch behavior (e.g. path-binding at
mint), which only applies when the ``/hx/<name>/`` router is not installed.
"""

urlpatterns = []
