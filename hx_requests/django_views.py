from django.http import Http404
from django.utils.translation import gettext_lazy as _


def list_view_get(self, request, *args, **kwargs):
    self.object_list = self.get_queryset()
    allow_empty = self.get_allow_empty()

    if not allow_empty:
        # When pagination is enabled and object_list is a queryset,
        # it's better to do a cheap query than to load the unpaginated
        # queryset in memory.
        if self.get_paginate_by(self.object_list) is not None and hasattr(self.object_list, "exists"):
            is_empty = not self.object_list.exists()
        else:
            is_empty = not self.object_list
        if is_empty:
            raise Http404(
                _("Empty list and “%(class_name)s.allow_empty” is False.")
                % {
                    "class_name": self.__class__.__name__,
                }
            )


def update_view_get(self, request, *args, **kwargs):
    self.object = self.get_object()


def create_view_get(self, request, *args, **kwargs):
    self.object = None


def detail_view_get(self, request, *args, **kwargs):
    self.object = self.get_object()


def delete_view_get(self, request, *args, **kwargs):
    self.object = self.get_object()


def date_view_get(self, request, *args, **kwargs):
    self.date_list, self.object_list, extra_context = self.get_dated_items()
    return {
        "object_list": self.object_list,
        "date_list": self.date_list,
        **extra_context,
    }
