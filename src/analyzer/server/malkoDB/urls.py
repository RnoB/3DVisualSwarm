from django.urls import path, re_path

from . import views


app_name = 'malkoDB'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    re_path(r'^(?P<project>[\w\-]+)/$', views.ProjectView.as_view(), name='indexProject'),
    re_path(r'^(?P<project>[\w\-]+)/(?P<experiment>[\w\-]+)/$', views.ExperimentView.as_view(), name='indexExperiment'),
    re_path(r'^(?P<project>[\w\-]+)/(?P<experiment>[\w\-]+)/(?P<p0>[\w\-]+)/(?P<value0>[\d+\.\d+]+)/$', views.ExperimentView.as_view(), name='indexExperiment'),
    #re_path(r'^(?P<project>[\w\-]+)/(?P<N>[0-9]+)/$', views.VisNView.as_view(), name='VisN'),
]
