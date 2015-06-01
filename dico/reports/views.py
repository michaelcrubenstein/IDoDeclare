from django.conf import settings
from django.contrib import admin
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.db import connection
from django.db.utils import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.template import RequestContext, loader, TemplateDoesNotExist
from django.views.decorators.csrf import requires_csrf_token

import traceback
import json
import uuid

from dico.models import Issue, Constituent, ConstituentInterest, ContactMethod, \
    Petition, PetitionManager, PetitionIssue, PetitionVote, \
    Argument, ArgumentManager, ArgumentRating, Note, NoteManager, Story, StoryManager, MC
from dico.titlecase import titlecase

# Create your views here.

@requires_csrf_token
def totals(request):
    try:
        template = loader.get_template('dico/reports/totals.html')
        backURL = request.GET.get('back', '/dico/')
    
        with connection.cursor() as c:
            sql = "SELECT COUNT(*) FROM dico_constituent"
            c.execute(sql, [])
            userCount = c.fetchone()[0]
          
        with connection.cursor() as c:
            sql = "SELECT COUNT(*) FROM dico_issue"
            c.execute(sql, [])
            issueCount = c.fetchone()[0]
          
        with connection.cursor() as c:
            sql = "SELECT COUNT(*) FROM dico_constituentinterest"
            c.execute(sql, [])
            interestCount = c.fetchone()[0]
          
        with connection.cursor() as c:
            sql = "SELECT COUNT(*) FROM dico_petition"
            c.execute(sql, [])
            actionCount = c.fetchone()[0]
          
        with connection.cursor() as c:
            sql = "SELECT COUNT(*) FROM dico_petitionvote"
            c.execute(sql, [])
            voteCount = c.fetchone()[0]
          
        with connection.cursor() as c:
            sql = "SELECT COUNT(*) FROM dico_note"
            c.execute(sql, [])
            noteCount = c.fetchone()[0]
          
        with connection.cursor() as c:
            sql = "SELECT COUNT(*) FROM dico_argument"
            c.execute(sql, [])
            argumentCount = c.fetchone()[0]
          
        with connection.cursor() as c:
            sql = "SELECT COUNT(*) " + \
                  " FROM dico_story"
            c.execute(sql, [])
            storyCount = c.fetchone()[0]
          
        context = RequestContext(request, {
            'userCount' : userCount,
            'issueCount': issueCount,
            'interestCount': interestCount,
            'actionCount' : actionCount,
            'voteCount': voteCount,
            'noteCount': noteCount,
            'argumentCount': argumentCount,
            'storyCount': storyCount,
        })
        return HttpResponse(template.render(context))
    except TemplateDoesNotExist as e:
        return HttpResponse("Template does not exist: " + str(e))
    except Exception as e:
        return HttpResponse("Error: " + str(e))

def getTotals(request):
    try:
        totals = [ {"name": "Users", "sql": "SELECT COUNT(*) FROM dico_constituent"},
                   {"name": "Issues", "sql": "SELECT COUNT(*) FROM dico_issue"},
                   {"name": "User Interests", "sql": "SELECT COUNT(*) FROM dico_constituentinterest"},
                   {"name": "Actions", "sql": "SELECT COUNT(*) FROM dico_petition"},
                   {"name": "Votes", "sql": "SELECT COUNT(*) FROM dico_petitionvote"},
                   {"name": "Notes", "sql": "SELECT COUNT(*) FROM dico_note"},
                   {"name": "Action Issues", "sql": "SELECT COUNT(*) FROM dico_petitionissue"},
                   {"name": "Arguments", "sql": "SELECT COUNT(*) FROM dico_argument"},
                   {"name": "Stories", "sql": "SELECT COUNT(*) FROM dico_story"},
                   ]
        
        for a in totals:
            with connection.cursor() as c:
                c.execute(a["sql"], [])
                a["count"] = c.fetchone()[0]
                del a["sql"]
          
        results = {'success':True, 'totals': totals}
    except Exception as e:
        with open('exception.log', 'a') as log:
            log.write("%s\n" % traceback.format_exc())
            log.flush()
        results = {'success':False, 'error': str(e)}
            
    return JsonResponse(results)

