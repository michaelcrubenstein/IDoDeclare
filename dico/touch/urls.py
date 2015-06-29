from django.conf.urls import patterns, url

from dico.touch import views

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='touchHome'),
    # ex: /dico/touch/createmailbag/
    url(r'^createmailbag/', views.createMailbag, name='createMailbag'),
    # ex: /dico/touch/newmailbag/
    url(r'^newmailbag/', views.newMailbag, name='newMailbag'),
    # ex: /dico/getmessagesearchresults -- Get message search results.
    url(r'^getmessagesearchresults/', views.getMessageSearchResults, name='getMessageSearchResults'),
    # ex: /dico/getusersearchresults -- Get message search results.
    url(r'^getusersearchresults/', views.getUserSearchResults, name='getUserSearchResults'),
    # ex: /dico/touch/createmessage/
    url(r'^createmessage/', views.createMessage, name='createMessage'),
    # ex: /dico/touch/newmessage/
    url(r'^newmessage/', views.newMessage, name='newMessage'),
    # ex: /dico/sendmailbags -- Get the html page to send mailbags.
    url(r'^sendmailbags/', views.sendMailbags, name='sendMailbags'),
    # ex: /dico/getunsentmailbags -- Get A list of all of the unsent mailbags.
    url(r'^getunsentmailbags/', views.getUnsentMailbags, name='getUnsentMailbags'),
    # ex: /dico/deletemailbags -- Get A list of all of the unsent mailbags.
    url(r'^deletemailbags/', views.deleteMailbags, name='deleteMailbags'),
    # ex: /dico/dropmailbags -- drop the specified mailbags to the server that sends messages.
    url(r'^dropmailbags/', views.dropMailbags, name='dropMailbags'),
)
