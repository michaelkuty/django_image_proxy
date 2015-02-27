
import requests
import mimetypes

from urlparse import urljoin
from django.http import HttpResponse
from django.views import generic
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

from django.views.generic import View
from django.conf import settings

from image_proxy import processors

from PIL import Image


class ThumbnailMixin(object):

    @property
    def base_url(self):
        return getattr(settings, "IMAGE_PROXY_URL", getattr(self, "url", "localhost"))

    @property
    def remote_path(self):
        return urljoin(self.base_url, self.kwargs["id"])

    @property
    def image(self):
        r = requests.get(self.remote_path)

        img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(r.content)
        img_temp.flush()
        return Image.open(img_temp.name)

    @property
    def content_type(self):
        mimetype = "image/jpeg"
        try:
            mimetype = mimetypes.guess_type(self.remote_path)[0]
        except Exception, e:
            raise e
        return mimetype

    def get_context_data(self, **kwargs):
        context = super(ThumbnailPreView, self).get_context_data(**kwargs)

        context["image"] = self.kwargs["id"]

        return context

    @property
    def final_size(self):
        try:
            size = self.kwargs["size"]
        except KeyError:
            size = "100x100" 
        return size.split("x")

    @property
    def method(self):
        try:
            method = self.kwargs["method"]
        except KeyError:
            method = "crop" 
        return method

    def get_image(self):
        im = processors.scale_and_crop(
            self.image,
            self.final_size,
            self.method)
        im = processors.colorspace(im)
        im = processors.save_image(im)
        return im

class ThumbnailView(View, ThumbnailMixin):

    def get(self, request, *args, **kwargs):

        response = HttpResponse(self.get_image(), content_type=self.content_type)

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
