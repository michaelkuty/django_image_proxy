
from django import http
from django.views import generic
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

from django.views.generic import View
from django.conf import settings

import requests
import mimetypes


class ThumbnailMixin(object):


    @property
    def base_url(self):
        return getattr(settings, "IMAGE_PROXY_URL", getattr(self, "url", "localhost"))

    @property
    def remote_path(self):
        return self.base_url + self.kwargs["id"]

    @property
    def image(self):
        r = requests.get(self.remote_path)

        img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(r.content)
        img_temp.flush()
        return File(img_temp)

    @property
    def content_type(self):
        mimetype = "image/jpeg"
        try:
            mimetype =  mimetypes.guess_type(self.remote_path)[0]
        except Exception, e:
            raise e
        return mimetype

    def get_context_data(self, **kwargs):
        context = super(ThumbnailPreView, self).get_context_data(**kwargs)

        context["image"] = self.kwargs["id"]

        return context


class ThumbnailView(View, ThumbnailMixin):

    def get(self, request, *args, **kwargs):

        response = http.HttpResponse(self.image, content_type=self.content_type)

        return response


class ThumbnailPreView(generic.TemplateView, ThumbnailMixin):
    """implementation without Horizon
    """

    template_name = "image_proxy/image_preview.html"

    def get_context_data(self, **kwargs):
        context = super(ThumbnailPreView, self).get_context_data(**kwargs)

        context["image"] = self.kwargs["id"]

        return context


try:
    from horizon import forms
    HORIZON = True
except ImportError:
    HORIZON = False

if HORIZON:

    class FakeForm(forms.SelfHandlingForm):

        def handle(self, request, data):
            pass

    class ThumbnailPreView(forms.ModalFormView, ThumbnailMixin):
        
        template_name = "image_proxy/image_preview.html"
        form_class = FakeForm

        def get_context_data(self, **kwargs):
            context = super(ThumbnailPreView, self).get_context_data(**kwargs)

            context["image"] = self.kwargs["id"]

            return context
