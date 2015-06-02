from django.conf.urls import patterns, url

from dico.reports import views

urlpatterns = patterns(
    '',
    url(r'^$', views.totals, name='reportsHome'),
    # ex: /dico/totals/
    url(r'^totals/', views.totals, name='totals'),
    url(r'^gettotals/', views.getTotals, name='getTotals'),
)
