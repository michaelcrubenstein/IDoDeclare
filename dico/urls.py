from django.conf.urls import patterns, url

from dico import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    # ex: /dico/signin/
    url(r'^signin/', views.signin, name='signin'),
    # ex: /dico/submitsignin/
    url(r'^submitsignin/', views.submitsignin, name='submitsignin'),
    # ex: /dico/signout/
    url(r'^signout/', views.signout, name='signout'),
    # ex: /dico/submitnewissue/
    url(r'^submitnewissue/', views.submitnewissue, name='submitnewissue'),
    # ex: /dico/createConstituent/
    url(r'^createConstituent/', views.createConstituent, name='createConstituent'),
    # ex: /dico/submitcreateconstituent/
    url(r'^submitcreateconstituent/', views.submitCreateConstituent, name='submitcreateconstituent'),
    # ex: /dico/issue/5/
    url(r'^(?P<issue_id>\d+)/issue/$', views.issue, name='issue'),
    # ex: /dico/5/
    url(r'^(?P<constituent_id>\d+)/$', views.dashboard, name='dashboard'),
    # ex: /dico/5/addissue/
    url(r'^(?P<constituent_id>\d+)/addissue/$', views.addissue, name='addissue'),
    # ex: /dico/5/mcdashboard/
    url(r'^(?P<mc_id>\d+)/mcdashboard/$', views.mcdashboard, name='mcdashboard'),
    # ex: /dico/5/mcaddissue/
    url(r'^(?P<mc_id>\d+)/mcaddissue/$', views.mcaddissue, name='mcaddissue'),
    # ex: /dico/member/?bioguide_id=.../
    url(r'^member/', views.member, name='member'),
	# ex: /dico/getInterests -- Get the interest in a particular issue ID.
	url(r'^getinterests/', views.getInterests, name='getInterests'),
	# ex: /dico/getMyIssues -- Get all of the interests of the current logged-in user..
	url(r'^getmyissues/', views.getMyIssues, name='getMyIssues'),
)
