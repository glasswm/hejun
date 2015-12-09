from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls.static import static
from hejun import settings

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'hejun.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^managehejun/', include(admin.site.urls)),
    url(r'^homework/', include('homework.urls', namespace='homework')),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
