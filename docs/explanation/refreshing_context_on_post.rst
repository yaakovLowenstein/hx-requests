Refreshing Context on POST
--------------------------

After a POST request, when a template is returned, you typically want it to
have the updated context. However, by default, the context is not updated.
This happens because context is fetched when the view is first called,
which occurs before the POST method executes and the form is saved.

There are ways to refresh the context, but it’s also important to know when it’s not necessary.

If you need to refresh the context on POST, you can override
:code:`get_post_context_data` or set :code:`refresh_views_context_on_post` to :code:`True`.
See :ref:`Adding Context Only On POST` for details.

However, you don’t need to refresh the context if the only updated object is
the :code:`hx_object` and its name matches the object name in the view.
By default, :code:`hx_object` is always refreshed, ensuring the template
receives the latest data. But if :code:`hx_object_name` does not match
the view’s object name, the updated object won’t appear in the context.
See :ref:`Step 8: Create The HxRequest` for an example of setting :code:`hx_object_name`.

For example, if the object is named :code:`object` in the view,
the template accesses it with :code:`object.username`.
Therefore, if the :code:`hx_object` name is not :code:`object`,
the template won’t reflect the changes because the :code:`object` var in the context
was never updated.

Another case where refreshing the context is not needed
is when the only updated context is a queryset. Querysets in Django are
lazy-loaded, meaning they aren’t evaluated when the view is first called.
Instead, they fetch data when accessed in the template, ensuring they
reflect the latest state even if the context was fetched before the update was made.

However, if the context includes a list instead of a queryset,
it must be refreshed. Unlike querysets, lists are evaluated immediately
when the view is called and won’t reflect changes made on POST.
