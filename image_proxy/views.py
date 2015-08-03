
import requests
import mimetypes

from urlparse import urljoin
from django.http import StreamingHttpResponse
from django.views import generic
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core.files.storage import FileSystemStorage, get_storage_class
from django.views.generic import View
from django.conf import settings

from image_proxy import processors

from PIL import Image


class ThumbnailMixin(object):

    @property
    def base_url(self):
        return getattr(settings, "IMAGE_PROXY_URL", getattr(self, "url", "localhost"))

    @property
    def if_cache(self):
        return getattr(settings, "IMAGE_PROXY_CACHE", True)

    @property
    def thumbnail_path(self):
        return getattr(settings, "THUMBNAILS_DIR", "thumbnails")

    @property
    def file_extension(self):
        return getattr(settings, "THUMBNAILS_FORMAT", "PNG")

    @property
    def image(self):
        try:
            r = requests.get(self.remote_path)
        except Exception as e:
            raise Exception('Exception %s raised '
                            'during loading image %s' % (e, self.remote_path))

        if self.storage.exists(self.full_name) and self.if_cache:
            im = Image.open(self.storage.path(self.full_name))
            im = processors.save_image(im, format=self.file_extension)
        else:
            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(r.content)
            img_temp.flush()
            im = Image.open(img_temp.name)
            if not self.final_size is None:
                im = processors.scale_and_crop(
                    im,
                    self.final_size,
                    self.method)
            im = processors.colorspace(im)
            im = processors.save_image(im, format=self.file_extension)
            self.storage.save(self.full_name, im)

        return im

    @property
    def content_type(self):
        mimetype = "image/png"
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
    def final_size_string(self):
        if self.final_size:
            return "x".join(self.final_size)
        return str(self.final_size)

    @property
    def final_size(self):
        try:
            size = self.kwargs["size"]
            size = size.split("x")
        except KeyError:
            size = None
        return size

    @property
    def method(self):
        try:
            method = self.kwargs["method"]
        except KeyError:
            method = "crop"
        return method

    @property
    def remote_path(self):
        return urljoin(self.base_url, self.kwargs["id"])

    @property
    def name(self):
        return self.kwargs["id"].split("/")[-1]

    @property
    def full_name(self):
        return "%s/%s_%s" % (self.thumbnail_path, self.final_size_string, self.name)

    @property
    def storage(self):
        return get_storage_class()()


class ThumbnailView(View, ThumbnailMixin):

    def get(self, request, *args, **kwargs):

        response = StreamingHttpResponse(self.image, content_type=self.content_type)

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
