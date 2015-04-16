from django.conf.urls import patterns, url

from data import views

urlpatterns = patterns(
	'',
    # ex: /data/loadusers/
    url(r'^loadinterests/', views.loadInterests, name='loadInterests'),
    url(r'^loadusers/', views.loadUsers, name='loadUsers'),
)
