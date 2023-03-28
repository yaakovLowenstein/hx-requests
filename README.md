# hx-requests
<br>

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Code style: djlint](https://img.shields.io/badge/html%20style-djlint-blue.svg)](https://www.djlint.com)

## Overview

A package to simplify the usage of HTMX with Django. Easily add HTMX reuqests witout needing additional urls, and reduce clutter in views by offloading all responsibility to an <em>hx_request</em>.

<br>

## Why use?


- Avoid cluttering up urls with endpoints for HTMX
- Reduce clutter in views by avoiding if/elses that are checking if the incoming request is an HTMX request
- Built in functionality for HTMX requests that handle forms.

<br>

## How to use


- ### **Installation**
       pip install simple-django-htmx
    - Add simple_django_htmx to your list of installed apps
    - You will also need to have HTMX installed. See https://htmx.org/

<br>

- ### **Quick Example**

<br>

1. Create an HXRequest:

        class EditUserHxRequest(FormHXRequest):
            name = "edit_user"
            GET_template = "update_user.html"
            POST_template = "user_row.html"
            form_class = EditUserForm

2. Create the template where this HXRequest will be used. Notice how the template tag is used to render the HXRequest.
   <br>

    user_list.html

        {% load hx_tags %}
        <tr >
            <td>
                {{user.name}}
            </td>
            <td>
                {{user.email}}
            </td>
            <td>
                {{user.address}}
            </td>
            <td>
                <button {% render_hx  'edit_user' 'get' object=user %} hx-target="closest tr" hx-swap="outerHTML">Edit</button>
            </td>
        </tr>

3. Load the HXRequest into the view that it's being used in. The view needs to inherit from HtmxViewMixin and the view needs to provide a list of hx_requests that will be used in the view.

         class UserListView(HtmxVIewMixin, ListView):
            template_name = "user_list.html"
            model = User
            hx_requests = [
               EditUserHxRequest
            ]

4. Voila! on the click of the Edit button the GET_template from EditUserHxRequest will be loaded.

   - The view is neat and clean and there was no need to create a url for the edit button to hit.


<br>

## A Deeper Dive


### **---HXRequest Classes---**

<br>

### **HXRequest**

---

<br>

A wrapper for HTMX requests. Instead of the GET/POST getting dircted to a view, it goes to an HXRequest.

- **Attributes**
     - name: Unique string that is used to identify which HXRequest the HTMX reuqest should direct to
     - GET_template: The template that an <em>hx-get</em> fetches
     - POST_template: The template an <em>hx-post</em> fetches
     - hx_object_name: Default is hx_object. If an object is passed into the `render_hx` template tag the obejct is put into the context of the GET/POST templates. The hx_object_name is the key in the contedxt for this object.

<br>

- **Methods**
    - get_context_data: Same as a view's get_context_data. HXRequest's add in a few additional items into the context.
        - hx_kwargs -> These are any kwargs passed into `render_hx`
        - hx_object (or the name given to it using `hx_object_name`) -> The object passed into `render_hx`. In the `FormHXRequest` this object acts like the object of a Django UpdateView.
        - hx_request: The HXRequest

<br>

### **FormHXRequest**

---

<br>

Acts like a a Django UpdateView. When a form is valid it saves the form and by default returns the POST_template of the HXRequest. If the form is invalid it returns the GET_temlate by default. Can customize what the view returns by overriding `form_valid` or `form_invalid` and return anything from those functions.

- **Attributes**
  - form_class: This is passed into the context as form and is instantiated with the object passed into `render_hx`. On POST it is instantiated with the request.POST as well.


<br>

- **Methods**

  - form_valid: Method called when the form is valid. By default it just calls `form.save()`. Has access to kwargs sent in through the `render_hx` template tag.
  - form_invalid: Method called when the form is invalid. No default. Has access to kwargs sent in through the `render_hx` template tag.
  - get_form_kwargs: Injects kwargs into the form. Can override to put items into the form. i.e. to set initial values. Has access to kwargs sent in through the `render_hx` template tag.

<br>

### **DeleteHXRequest**

---

<br>

Deletes the object passed into `render_hx`. Can override `handle_delete` for custom functionality.

<br>

### **---Other---**

<br>

### **HtmxVIewMixin** -> The mixin intercepts the GET and POST and if it finds hx_request in the GET params it redircts to the HXRequest's GET and POST methods.

<br>

### **render_hx** -> Template tag to use for HXReuqests. Takes in:
- Name of the HXReqest
- Type of reuqest, get or post
- object (optional), the object that is used by the request. It is treated just like the object of an UpdateView
- kwargs, addional params that can be passed in. These kwargs can be used in get_form_kwargs, form_valid, of form_invalid.
    - Example -> The template has a user and is looping through the contact methods of the user. There is an HXRequest on each contact method that lets you edit the contact method. Would need to pass in the contact method as the object. Addionally the page has an add new button which allows you to add a new contact method to this user, you would need to pass an addional kwarg for the user because when saving the new contact method, the back end needs to know which user we are saving this for.

            <button {% hx_request_name='render_hx create_update_contact_method' method="get" object="contact_method" user=user %} hx-target="closest tr" ></button>

<br>

## Future Features


- Aysnchronous messaging.
- Auto filling initial of form fields with kwargs if the kwarg key matches the form field.
