from typing import Dict

from django import template

from hx_requests.utils import get_csrf_token, get_url

register = template.Library()


@register.simple_tag(takes_context=True)
def render_hx(
    context: Dict,
    hx_request_name: str,
    method: str = "get",
    object=None,
    use_full_path=False,
    **kwargs,
) -> str:
    """
    Renders out the hx-post or hx-get with the correct url along with all kwargs
    turned into GET params.
    """
    url = get_url(context, hx_request_name, object, use_full_path, **kwargs)
    return f"hx-{method}={url}"


@register.simple_tag(takes_context=True)
def hx_get(
    context: Dict, hx_request_name: str, object=None, use_full_path=False, **kwargs
) -> str:
    """
    Same as render_hx EXCEPT that it is specifically for 'get' requests.
    """
    return render_hx(
        context,
        hx_request_name,
        method="get",
        object=object,
        use_full_path=use_full_path,
        **kwargs,
    )


@register.simple_tag(takes_context=True)
def hx_post(
    context: Dict, hx_request_name: str, object=None, use_full_path=False, **kwargs
) -> str:
    """
    Same as render_hx EXCEPT that it is specifically for 'post' requests.
    """
    hx_attrs = render_hx(
        context,
        hx_request_name,
        method="post",
        object=object,
        use_full_path=use_full_path,
        **kwargs,
    )
    token = get_csrf_token(context)
    if token:
        hx_attrs += f' hx-headers={{"X-CSRFTOKEN":"{token}"}}'
    return hx_attrs
