
==================
Django Image Proxy
==================

Small django toolkit for loading images from remote hosts. Supports custom sizes and simple caching for less API calls.

Supports
--------

* Django 1.7 +
* Pillow 2.3.0

Installation
------------

.. code-block:: bash

    pip install django_image_proxy

Settings
--------

Specify your remote host.

.. code-block:: python

    INSTALLED_APPS += ('image_proxy',)

    IMAGE_PROXY_URL = 'http://localhost:9753/images'

Optionaly you can set some common properties.

.. code-block:: python

    THUMBNAILS_DIR = "thumbnails"

    # disable caching
    IMAGE_PROXY_CACHE = False
    
    # change thumbnail format
    THUMBNAILS_FORMAT = "PNG"

urls.py

.. code-block:: python

    urlpatterns = patterns('',
        ...
        url(r'^images/', include('image_proxy.urls')),
        ...
    )

Usage
-----

As url

.. code-block:: html
    
    <img src="{% url 'proxy_image' '/media/anotherdjangoapp.png' %}"/>
    <img src="{% url 'proxy_image_preview' '/media/anotherdjangoapp.png' %}"/>
    <img src="{% url 'proxy_image_size' 'my_image_name' '100x100' %}"/>
    <img src="{% url 'proxy_image_full' 'my_image_id' '100x100' 'scale' %}"/>

As templatetag

.. code-block:: html

    {% load thumnail %}
    {% thumbnail product.image %}
    {% thumbnail product.image '400x400' %}
    {% thumbnail product.image '400x400' 'crop' %}

If you have clash between your favourite thumbnail provider and proxy thumbanil tags use ``{% load thumbnail from proxy_thumbnail %}``.

Custom size and method

.. code-block:: python

    http://<hostname>/<path_to_source_file>/<size>/<method>/

.. code-block:: python

    # simple using Django Rest Framework Serializer
    # for image paths return something like this
    images = ["/media/image.jpg", "/media/image01.jpg"]
    
    for image in images:

        print reverse("proxy_image", args=[image])
        /images/image/media/image.jpg # this url download image from original url and returns it !        


Usage with Openstack Horizon Dashboard
--------------------------------------

Requires installed horizon.

Image in modal dialog.

.. code-block:: python
    
    <a href="{% url 'proxy_image_preview' image %}" class="ajax-modal">
      <img src="{% thumbnail product.image '100x100' 'crop' %}" class="center-block" width="100px" />
    </a>

Override
--------

.. code-block:: python

    from image_proxy.views import ThumbnailView

    class MyThumbnailView(ThumbnailView)

        def get(self, request, *args, **kwargs):

            response = http.HttpResponse(self.image, content_type=self.content_type)

            return response


Contribution
------------

* Check for open issues or open a fresh issue to start a discussion around a feature idea or a bug.
* Fork https://github.com/michaelkuty/django_image_proxy on GitHub to start making your changes to the **master** branch.
* Send a pull request
