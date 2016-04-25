# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.contrib.auth.views import login, logout
from django.views.generic import TemplateView
import views

urlpatterns = patterns(
    '',
    url(r'^signin/$', login, name='login',
        kwargs={"template_name": "account/login.html"}),
    url(r'^signup/$', views.UserCreateView.as_view(), name='signup'),
    url(r'^logout_confirm/$',
        TemplateView.as_view(template_name='account/logout.html'),
        name="logout_confirm"),
    url(r'^logout/$', logout, name='logout'),
)
