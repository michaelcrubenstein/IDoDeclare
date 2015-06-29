from django.conf import settings
from django.contrib import admin
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.db import connection, transaction
from django.db.utils import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.template import RequestContext, loader, TemplateDoesNotExist
from django.views.decorators.csrf import requires_csrf_token
from django.core.mail import send_mail

import traceback
import json
import uuid

from dico.models import Issue, Constituent, ConstituentInterest, ContactMethod, \
    Petition, PetitionManager, PetitionIssue, PetitionVote, \
    Argument, ArgumentManager, ArgumentRating, Note, NoteManager, Story, StoryManager, \
    Message, Mailbag, Envelope, MC
from dico.titlecase import titlecase

# Create your views here.

@requires_csrf_token
def index(request):
    try:
        if not request.user.is_authenticated:
            raise Exception("The current login is invalid")
        if not request.user.is_staff:
            raise Exception("The current login is invalid")

        template = loader.get_template('dico/touch/index.html')
        backURL = request.GET.get('back', '/dico/')
    
        context = RequestContext(request, {
        })
        return HttpResponse(template.render(context))
    except TemplateDoesNotExist as e:
        return HttpResponse("Template does not exist: " + str(e))
    except Exception as e:
        return HttpResponse("Error: " + str(e))

# Displays a web page in which a user can create a new mailbag.
def createMailbag(request):
    try:
        if not request.user.is_authenticated:
            raise Exception("The current login is invalid")
        if not request.user.is_staff:
            raise Exception("The current login is invalid")
    
        template = loader.get_template('dico/touch/createMailbag.html')
        backURL = request.GET.get('backURL', '/dico/');    
        backName = request.GET.get('backName', 'Home')
        
        context = RequestContext(request, {
            'user': request.user,
            'backURL': backURL,
            'backName': backName,
        })
        return HttpResponse(template.render(context))
    except TemplateDoesNotExist as e:
        return HttpResponse("Template does not exist: " + str(e))
    except Exception as e:
        return HttpResponse("Error: " + str(e))

def getMessageSearchResults(request):
    results = {'success':False, 'error': 'getMessageSearchResults failed'}
    try:
        if not request.user.is_authenticated:
            raise Exception("The current login is invalid")
        if not request.user.is_staff:
            raise Exception("The current login is invalid")

        if 'query' not in request.GET:
            raise Exception('the query is not specified')
        query = request.GET['query'];
        results = {'searchResults' : Message.get_search_results(query), 'success':True}
    except Exception as e:
        with open('exception.log', 'a') as log:
            log.write("%s\n" % traceback.format_exc())
            log.flush()
        results = {'success':False, 'error': str(e)}
            
    return JsonResponse(results)

def getUserSearchResults(request):
    results = {'success':False, 'error': 'getUserSearchResults failed'}
    try:
        if not request.user.is_authenticated:
            raise Exception("The current login is invalid")
        if not request.user.is_staff:
            raise Exception("The current login is invalid")

        if 'query' not in request.GET:
            raise Exception('the query is not specified')
        query = request.GET['query'];
        message_id = int(request.GET['message_id'])
        results = {'searchResults' : Message.get_message_search_results(message_id, query), 'success':True}
    except Exception as e:
        with open('exception.log', 'a') as log:
            log.write("%s\n" % traceback.format_exc())
            log.flush()
        results = {'success':False, 'error': str(e)}
            
    return JsonResponse(results)

def newMailbag(request):
    results = {'success':False, 'error': 'newMailbag failed'}
    try:
        if request.method != "POST":
            raise Exception("newMailbag only responds to POST requests")
        if not request.user.is_authenticated:
            raise Exception("The current login is invalid")
        if not request.user.is_staff:
            raise Exception("The current login is invalid")

        # Get the petition info.
        message_id = int(request.POST['message_id'])
            
        user_ids = request.POST.getlist('user_id[]')
        users = get_user_model().objects.filter(id__in=user_ids)
        message = Message.objects.get(pk=message_id)
        via = message.via
        
        # Do the model operation
        with transaction.atomic():
            mailbag = Mailbag.objects.create(message_id = message_id,
                                             via=via)
            for user in users:
                if via==1:
                    address = ContactMethod.objects.get(pk=user.id).phonenumber
                else:
                    address = user.email
                envelope = Envelope.objects.create(mailbag=mailbag,
                                                   constituent_id = user.id)
        
        # Return the results.
        results = {'success':True, 'count':len(users) }
    except Exception as e:
        with open('exception.log', 'a') as log:
            log.write("%s\n" % traceback.format_exc())
            log.flush()
        results = {'success':False, 'error': str(e)}
    
    return JsonResponse(results)

def getUnsentMailbags(request):
    results = {'success':False, 'error': 'getUnsentMailbags failed'}
    try:
        if not request.user.is_authenticated:
            raise Exception("The current login is invalid")
        if not request.user.is_staff:
            raise Exception("The current login is invalid")

        results = {'mailbags' : Mailbag.get_unsent_mailbags(), 'success':True}
    except Exception as e:
        with open('exception.log', 'a') as log:
            log.write("%s\n" % traceback.format_exc())
            log.flush()
        results = {'success':False, 'error': str(e)}
            
    return JsonResponse(results)

def sendMailbags(request):
    try:
        if not request.user.is_authenticated:
            raise Exception("The current login is invalid")
        if not request.user.is_staff:
            raise Exception("The current login is invalid")
    
        template = loader.get_template('dico/touch/sendMailbags.html')
        backURL = request.GET.get('backURL', '/dico/');    
        backName = request.GET.get('backName', 'Home')
        
        context = RequestContext(request, {
            'user': request.user,
            'backURL': backURL,
            'backName': backName,
        })
        return HttpResponse(template.render(context))
    except TemplateDoesNotExist as e:
        return HttpResponse("Template does not exist: " + str(e))
    except Exception as e:
        return HttpResponse("Error: " + str(e))

def dropMailbags(request):
    results = {'success':False, 'error': 'dropMailbags failed'}
    try:
        if request.method != "POST":
            raise Exception("dropMailbags only responds to POST requests")
        if not request.user.is_authenticated:
            raise Exception("The current login is invalid")
        if not request.user.is_staff:
            raise Exception("The current login is invalid")

        # Get the petition info.            
        envelope_ids = request.POST.getlist('envelope_id[]')
        envelopes = Envelope.objects.filter(id__in=envelope_ids)
        
        for envelope in envelopes:
            sendMessage(envelope.message, envelope.constituent);
            
        # Do the model operation
        with transaction.atomic():
            for envelope in envelopes:
                cm = ContactMethod.objects.updateLastContactTime(envelope.constituent.id)
        
        # Return the results.
        results = {'success':True, 'count':len(envelopes) }
    except Exception as e:
        with open('exception.log', 'a') as log:
            log.write("%s\n" % traceback.format_exc())
            log.flush()
        results = {'success':False, 'error': str(e)}
    
    return JsonResponse(results)

def deleteMailbags(request):
    results = {'success':False, 'error': 'deleteMailbags failed'}
    try:
        if request.method != "POST":
            raise Exception("deleteMailbags only responds to POST requests")
        if not request.user.is_authenticated:
            raise Exception("The current login is invalid")
        if not request.user.is_staff:
            raise Exception("The current login is invalid")

        # Get the petition info.            
        mailbag_ids = request.POST.getlist('mailbag_id[]')
        mailbags = Mailbag.objects.filter(id__in=mailbag_ids)
        numMailbags = mailbags.count()
        
        # Do the model operation
        mailbags.delete()
        
        # Return the results.
        results = {'success':True, 'count':numMailbags }
    except Exception as e:
        with open('exception.log', 'a') as log:
            log.write("%s\n" % traceback.format_exc())
            log.flush()
        results = {'success':False, 'error': str(e)}
    
    return JsonResponse(results)

# Displays a web page in which a user can create a new message.
def createMessage(request):
    try:
        if not request.user.is_authenticated:
            raise Exception("The current login is invalid")
        if not request.user.is_staff:
            raise Exception("The current login is invalid")
    
        template = loader.get_template('dico/touch/createMessage.html')
        backURL = request.GET.get('backURL', '/dico/');    
        backName = request.GET.get('backName', 'Home')
        
        context = RequestContext(request, {
            'user': request.user,
            'backURL': backURL,
            'backName': backName,
        })
        return HttpResponse(template.render(context))
    except TemplateDoesNotExist as e:
        return HttpResponse("Template does not exist: " + str(e))
    except Exception as e:
        return HttpResponse("Error: " + str(e))

def newMessage(request):
    results = {'success':False, 'error': 'newMessage failed'}
    try:
        if request.method != "POST":
            raise Exception("newMessage only responds to POST requests")
        if not request.user.is_authenticated:
            raise Exception("The current login is invalid")
        if not request.user.is_staff:
            raise Exception("The current login is invalid")

        # Get the petition info.
        subject = request.POST['subject']
        body = request.POST['body']
        petition_id = int(request.POST['petition_id'])
        constituent_id = request.user.id
        via = request.POST['via']
        
        # Do the model operation
        message = Message.objects.create(subject=subject, \
                                         body=body, \
                                         petition_id=petition_id, \
                                         constituent_id=request.user.id, \
                                         via_id=int(via))
        
        # Return the results.
        results = {'success':True, 'message': {'creationTime': message.creationTime}}
    except Exception as e:
        with open('exception.log', 'a') as log:
            log.write("%s\n" % traceback.format_exc())
            log.flush()
        results = {'success':False, 'error': str(e)}
    
    return JsonResponse(results)
