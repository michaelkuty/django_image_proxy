
from django.conf.urls import *

from .views import ThumbnailView, ThumbnailPreView

urlpatterns = patterns('image_proxy',
   	
   	url(r'^image/preview(?P<id>.*)$', ThumbnailPreView.as_view(), name='proxy_image_preview'),
   	url(r'^image(?P<id>.*)$', ThumbnailView.as_view(), name='proxy_image'),

)
