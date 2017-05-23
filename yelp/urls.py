from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.contrib import admin

from . import views

app_name = "yelp"
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', auth_views.login, {'template_name': 'login.html'}, name='login'),
    # url(r'^logout/$', auth_views.logout, {'next_page': '/yelp/login/'}, name='logout'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^review/(?P<username>\w+)/(?P<user_rev_idx>[0-9]+)/$', views.show_review, name='review'),
    url(r'^search/$', views.search_candidates, name='search'),
    url(r'^label/(?P<user_rev_idx>[0-9]+)/$', views.label, name='label'),
    url(r'^deletelabel/(?P<user_rev_idx>[0-9]+)/(?P<mention_id>[0-9]+)/$', views.delete_label, name='deletelabel')
]
