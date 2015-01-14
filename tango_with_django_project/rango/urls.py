__author__ = 'usrsjx'

from django.conf.urls import patterns, url
from rango import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       url(r'^about', views.about, name='about'),
                       url(r'^add_category/$', views.add_category, name='add_category'),
                       url(r'^category/(?P<category_name_slug>[\w\-]+)/add_page/$', views.add_page, name='add_page'),
                       url(r'^category/(?P<category_name_slug>[\w\-]+)/$', views.category, name='category'),
                       url(r'^restricted/$', views.restricted, name='restricted'),
                       url(r'^search/$', views.search, name='search'),
                       url(r'^goto/$', views.track_url, name='goto'),
                       url(r'^add_profile/(?P<user_id>[\w\-]+)/$', views.register_profile, name='add_profile'),
                       url(r'^profile/(?P<user_id>[\w\-]+)/$', views.profile, name='profile'),
                       url(r'^profiles/$', views.profiles, name='profiles'),
                       url(r'^like_category/$', views.like_category, name='like_category'),
                       url(r'^category_suggest/$', views.suggest_category, name='category_suggest'),
                       url(r'^auto_add_page/$', views.auto_add_page, name='auto_add_page'),)