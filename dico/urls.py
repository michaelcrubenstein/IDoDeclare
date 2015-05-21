from django.conf.urls import patterns, url

from dico import views

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='home'),
    # ex: /dico/signin/
    url(r'^signin/', views.signin, name='signin'),
    # ex: /dico/submitsignin/
    url(r'^submitsignin/', views.submitsignin, name='submitSignin'),
    # ex: /dico/submitFacebookSignin
    url(r'^submitfacebooksignin/', views.submitFacebookSignin, name='submitFacebookSignin'),
    # ex: /dico/signout/
    url(r'^signout/', views.signout, name='signout'),
    # ex: /dico/editinterests/
    url(r'^editinterests/', views.editInterests, name='editInterests'),
    # ex: /dico/account/
    url(r'^account/', views.account, name='account'),
    # ex: /dico/constituentsettings/
    url(r'^constituentsettings/', views.constituentSettings, name='constituentSettings'),
    # ex: /dico/password/
    url(r'^password/', views.password, name='password'),
    # ex: /dico/forgotpassword/
    url(r'^forgotpassword/', views.forgotPassword, name='forgotPassword'),
    # ex: /dico/resetpassword/
    url(r'^resetpassword/', views.resetPassword, name='resetPassword'),
    # ex: /dico/passwordreset/
    url(r'^passwordreset/', views.passwordReset, name='passwordReset'),
    # ex: /dico/passwordreset/
    url(r'^setresetpassword/', views.setResetPassword, name='setResetPassword'),
    # ex: /dico/issues/
    url(r'^issues/', views.issues, name='issues'),
    # ex: /dico/issue/issue=5
    url(r'^issue/', views.issue, name='issue'),
    # ex: /dico/petition/5/
    url(r'^(?P<petition_id>\d+)/petition/', views.petition, name='petition'),
    # ex: /dico/createPetition/
    url(r'^createpetition/', views.createPetition, name='createPetition'),
    # ex: /dico/addpetitionissue/5/
    url(r'^(?P<petition_id>\d+)/addpetitionissue/', views.addPetitionIssue, name='addPetitionIssue'),
    # ex: /dico/newinterest/
    url(r'^newinterest/', views.newInterest, name='newInterest'),
    # ex: /dico/submitdeleteinterest/
    url(r'^submitdeleteinterest/', views.submitdeleteinterest, name='deleteInterest'),
    # ex: /dico/createConstituent/
    url(r'^createConstituent/', views.createConstituent, name='createConstituent'),
    # ex: /dico/newconstituent/
    url(r'^newconstituent/', views.newConstituent, name='newConstituent'),
    # ex: /dico/updateconstituent/
    url(r'^updateconstituent/', views.updateConstituent, name='updateConstituent'),
    # ex: /dico/updatepassword/
    url(r'^updatepassword/', views.updatePassword, name='updatePassword'),
    # ex: /dico/getissuepetitions/
    url(r'^getissuepetitions/', views.getIssuePetitions, name='getIssuePetitions'),
    # ex: /dico/newpetition/
    url(r'^newpetition/', views.newPetition, name='newPetition'),
    # ex: /dico/deletepetition/
    url(r'^deletepetition/', views.deletePetition, name='deletePetition'),
    # ex: /dico/updatepetition/
    url(r'^updatepetition/', views.updatePetition, name='updatePetition'),
    # ex: /dico/getpetitionissues/
    url(r'^getpetitionissues/', views.getPetitionIssues, name='getPetitionIssues'),
    # ex: /dico/getpetitionarguments/
    url(r'^getpetitionarguments/', views.getPetitionArguments, name='getPetitionArguments'),
    # ex: /dico/newpetitionissue/
    url(r'^newpetitionissue/', views.newPetitionIssue, name='newPetitionIssue'),
    # ex: /dico/deletepetitionissue/
    url(r'^deletepetitionissue/', views.deletePetitionIssue, name='deletePetitionIssue'),
    # ex: /dico/newpetitionvote/
    url(r'^newpetitionvote/', views.newPetitionVote, name='newPetitionVote'),
    # ex: /dico/deletepetitionvote/
    url(r'^deletepetitionvote/', views.deletePetitionVote, name='deletePetitionVote'),
    # ex: /dico/newargument/
    url(r'^newargument/', views.newArgument, name='newArgument'),
    # ex: /dico/deleteargument/
    url(r'^deleteargument/', views.deleteArgument, name='deleteArgument'),
    # ex: /dico/newstory/
    url(r'^newstory/', views.newStory, name='newStory'),
    # ex: /dico/deletestory/
    url(r'^deletestory/', views.deleteStory, name='deleteStory'),
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
    # ex: /dico/getissues -- Get all of the issues with a specified minimum level of interest.
    url(r'^getissues/', views.getIssues, name='getIssues'),
    # ex: /dico/getissueinterests -- Get the interest in a particular issue ID.
    url(r'^getissueinterests/', views.getIssueInterests, name='getIssueInterests'),
    # ex: /dico/getmyinterests -- Get all of the interests of the current logged-in user.
    url(r'^getmyinterests/', views.getMyInterests, name='getMyInterests'),
    # ex: /dico/getmynews -- Get all of the news items of the current logged-in user.
    url(r'^getmynews/', views.getMyNews, name='getMyNews'),
    # ex: /dico/getmymembers -- Get information about all of the members for the current logged-in user.
    url(r'^getmymembers/', views.getMyMembers, name='getMyMembers'),
    #
    # from the petition.html page
    # ex: /dico/getpetitionvotetotals/
    url(r'^getpetitionvotetotals/', views.getPetitionVoteTotals, name='getPetitionVoteTotals'),
    # ex: dico/5/getpetitionvotesbyscope/
    url(r'^getpetitionvotesbyscope/', views.getPetitionVotesByScope, name='getPetitionVotesByScope'),
    # ex: /dico/getpetitionstories/
    url(r'^getpetitionstories/', views.getPetitionStories, name='getPetitionStories'),
    # ex: /dico/rateargument/
    url(r'^rateargument/', views.rateArgument, name='rateArgument'),
    # ex: /dico/unrateargument/
    url(r'^unrateargument/', views.unrateArgument, name='unrateArgument'),
    # ex: /dico/addsupportingargument/5/
    url(r'^addsupportingargument/', views.addSupportingArgument, name='addSupportingArgument'),
    # ex: /dico/addopposingargument/5/
    url(r'^addopposingargument/', views.addOpposingArgument, name='addOpposingArgument'),
    # ex: /dico/addstory/
    url(r'^addstory/', views.addStory, name='addStory'),
    #
    # documentation urls.
    # ex: /dico/doctermsofuse
    url(r'^doctermsofuse/', views.docTermsOfUse, name='docTermsOfUse'),
    # ex: /dico/docratings
    url(r'^docratings/', views.docRatings, name='docRatings'),
    # ex: /dico/docyourinterests
    url(r'^docyourinterests/', views.docYourInterests, name='docYourInterests'),
    
)
