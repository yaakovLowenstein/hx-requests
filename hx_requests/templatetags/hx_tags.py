from __future__ import annotations

import json

from django import template
from django.utils.html import format_html

from hx_requests.utils import get_csrf_token, get_url

register = template.Library()


@register.simple_tag(takes_context=True)
def hx_get(context: dict, hx_request_name: str, object=None, use_full_path=False, **kwargs) -> str:
    """
    Renders the proper HTML attributes for an HX GET request.
    And includes the hx_request_name, object, and any additional kwargs.
    """
    url = get_url(context, hx_request_name, object, use_full_path, **kwargs)
    return format_html('hx-get="{}"', url)


@register.simple_tag(takes_context=True)
def hx_post(context: dict, hx_request_name: str, object=None, use_full_path=False, **kwargs) -> str:
    """
    Renders the proper HTML attributes for an HX POST request.
    And includes the hx_request_name, object, and any additional kwargs.
    Also includes the CSRF token if available.
    """
    url = get_url(context, hx_request_name, object, use_full_path, **kwargs)
    hx_attrs = format_html('hx-post="{}"', url)
    token = get_csrf_token(context)
    if token:
        # Single-quote the attribute so the JSON's double quotes survive; they
        # are HTML-escaped by format_html and decoded by the browser at parse time.
        hx_attrs += format_html(" hx-headers='{}'", json.dumps({"X-CSRFTOKEN": token}))
    return hx_attrs


@register.simple_tag(takes_context=True)
def hx_url(context: dict, hx_request_name: str, object=None, use_full_path=False, **kwargs) -> str:
    """
    Returns the URL for an HX request. Can be used when you need to manually set the URL in a template.
    Useful if the hx-get or hx-post tags are not flexible enough for your use case.
    For example:

    ```
    hx-get="{% hx_url 'my-hx-request' object %}"

    ```
    """
    return get_url(context, hx_request_name, object, use_full_path, **kwargs)
