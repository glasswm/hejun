from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'hejun.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^managehejun/', include(admin.site.urls)),
    url(r'^homework/', include('homework.urls', namespace='homework')),
)
