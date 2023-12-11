from django.urls import path, re_path

from . import views


app_name = 'malkoDB'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    re_path(r'^(?P<project>[\w\-]+)/$', views.IndexdVuView.as_view(), name='indexN'),
    re_path(r'^(?P<project>[\w\-]+)/(?P<N>\d+\.\d+)/$', views.VisNView.as_view(), name='VisN'),
    re_path(r'^(?P<project>[\w\-]+)/(?P<N>[0-9]+)/$', views.VisNView.as_view(), name='VisN'),
]
