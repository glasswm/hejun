__author__ = 'glasswm'

from django.conf.urls import patterns, url

from homework import views

urlpatterns = patterns('',
    url(r'^$', views.index2, name='index2'),
    url(r'^main/$', views.index, name='index'),
    url(r'^class/(?P<class_id>\d+)/$', views.kclass, name='kclass'),
    url(r'^student/(?P<student_id>\d+)/$', views.student, name='student'),
    url(r'^studentwithbbsid/(?P<bbs_id>\w+)/$', views.student_by_bbs_id, name='student_by_bbs_id'),
    url(r'^thread/(?P<thread_id>\d+)/$', views.thread, name='thread'),
    url(r'^updateall/$', views.updateAll, name='updateAll'),
    url(r'^updateallwithpage/(?P<start_page>\d+)/(?P<end_page>\d+)/$', views.updateAllwithpage, name='updateAllwithpage'),
    url(r'^update/(?P<thread_id>\d+)/$', views.update, name='update'),
    url(r'^updatewithpage/(?P<thread_id>\d+)/(?P<start_page>\d+)/(?P<end_page>\d+)/$', views.updatewithpage, name='updatewithpage'),
)