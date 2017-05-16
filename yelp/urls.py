from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

app_name = "yelp"
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/yelp/login/'}, name='logout'),
    url(r'^review/(?P<rev_idx>[0-9]+)$', views.show_review, name='review'),
    url(r'^search/$', views.search_candidates, name='search'),
    url(r'^label/(?P<rev_idx>[0-9]+)$', views.label, name='label'),
    url(r'^deletelabel/(?P<rev_idx>[0-9]+)/(?P<mention_id>[0-9]+)$', views.delete_label, name='deletelabel'),
    url(r'^test/$', views.test, name='test'),
    url(r'^testaj/$', views.test_aj, name='testaj'),
    url(r'^testsub/$', views.test_sub, name='testsub')
]
