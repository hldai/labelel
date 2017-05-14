from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

app_name = "yelp"
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/yelp/login/'}, name='logout'),
    url(r'^review/(?P<rev_idx>[0-9]+)$', views.show_review, name='review')
]
