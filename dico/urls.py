from django.conf.urls import patterns, url

from dico import views

urlpatterns = patterns(
	'',
    url(r'^$', views.index, name='index'),
    # ex: /dico/signin/
    url(r'^signin/', views.signin, name='signin'),
    # ex: /dico/submitsignin/
    url(r'^submitsignin/', views.submitsignin, name='submitsignin'),
    # ex: /dico/signout/
    url(r'^signout/', views.signout, name='signout'),
    # ex: /dico/editinterests/
    url(r'^editinterests/', views.editinterests, name='editinterests'),
    # ex: /dico/account/
    url(r'^account/', views.account, name='account'),
	# ex: /dico/issue/5/
	url(r'^(?P<issue_id>\d+)/issue/$', views.issue, name='issue'),
	# ex: /dico/petition/5/
	url(r'^(?P<petition_id>\d+)/petition/$', views.petition, name='petition'),
	# ex: /dico/createPetition/
	url(r'^createpetition/$', views.createPetition, name='createPetition'),
	# ex: /dico/addpetitionissue/5/
	url(r'^(?P<petition_id>\d+)/addpetitionissue/$', views.addpetitionissue, name='addpetitionissue'),
    # ex: /dico/newinterest/
    url(r'^newinterest/', views.newInterest, name='newInterest'),
    # ex: /dico/submitdeleteinterest/
    url(r'^submitdeleteinterest/', views.submitdeleteinterest, name='deleteinterest'),
	# ex: /dico/createConstituent/
    url(r'^createConstituent/', views.createConstituent, name='createConstituent'),
	# ex: /dico/newconstituent/
	url(r'^newconstituent/', views.newConstituent, name='newConstituent'),
	# ex: /dico/updateconstituent/
	url(r'^updateconstituent/', views.updateConstituent, name='updateConstituent'),
    # ex: /dico/getissuepetitions/
    url(r'^getissuepetitions/', views.getIssuePetitions, name='getissuepetitions'),
    # ex: /dico/newpetition/
    url(r'^newpetition/', views.newPetition, name='newpetition'),
    # ex: /dico/deletepetition/
    url(r'^deletepetition/', views.deletePetition, name='deletepetition'),
    # ex: /dico/updatepetition/
    url(r'^updatepetition/', views.updatePetition, name='updatepetition'),
    # ex: /dico/getpetitionissues/
    url(r'^getpetitionissues/', views.getPetitionIssues, name='getpetitionissues'),
    # ex: /dico/getpetitionarguments/
    url(r'^getpetitionarguments/', views.getPetitionArguments, name='getpetitionarguments'),
    # ex: /dico/newpetitionissue/
    url(r'^newpetitionissue/', views.newPetitionIssue, name='newpetitionissue'),
    # ex: /dico/deletepetitionissue/
    url(r'^deletepetitionissue/', views.deletePetitionIssue, name='deletepetitionissue'),
    # ex: /dico/getpetitionvotes/
    url(r'^getpetitionvotes/', views.getPetitionVotes, name='getpetitionvotes'),
    # ex: /dico/newpetitionvote/
    url(r'^newpetitionvote/', views.newPetitionVote, name='newpetitionvote'),
    # ex: /dico/deletepetitionvote/
    url(r'^deletepetitionvote/', views.deletePetitionVote, name='deletepetitionvote'),
    # ex: /dico/updatepetitionvote/
    url(r'^updatepetitionvote/', views.updatePetitionVote, name='updatepetitionvote'),
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
	# ex: /dico/getactiveissues -- Get all of the issues with a specified minimum level of interest.
	url(r'^getactiveissues/', views.getActiveIssues, name='getActiveIssues'),
	# 	# ex: /dico/getInterests -- Get the interest in a particular issue ID.
	url(r'^getinterests/', views.getInterests, name='getInterests'),
	# ex: /dico/getMyIssues -- Get all of the interests of the current logged-in user.
	url(r'^getmyissues/', views.getMyIssues, name='getMyIssues'),
)
