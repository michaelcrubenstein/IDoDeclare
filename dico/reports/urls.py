from django.conf.urls import patterns, url

from dico.reports import views

urlpatterns = patterns(
    '',
    url(r'^$', views.totals, name='home'),
    # ex: /dico/totals/
    url(r'^totals/', views.totals, name='totals'),
)
