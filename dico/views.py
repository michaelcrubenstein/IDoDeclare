from django.conf import settings
from django.contrib import admin
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.db.utils import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.template import RequestContext, loader
from django.views.decorators.csrf import requires_csrf_token
from pygeocoder import Geocoder
from sunlight import congress

import urllib
import json

from dico.models import Issue, Constituent, ConstituentInterest, MC
from dico.titlecase import titlecase

# Create your views here.

def index(request):
    template = loader.get_template('dico/index.html')
    issue_list = Issue.objects.order_by('name')
    il = []
    for i in issue_list:
        il = il + [{'name': i.name, 'id': i.id}]
        
    member_list = Constituent.get_members(request.user)
            
    context = RequestContext(request, {
    	'user': request.user,
        'issue_list': json.dumps(il),
        'member_list': member_list,
    })
    return HttpResponse(template.render(context))

@requires_csrf_token
def signin(request):
    template = loader.get_template('dico/signin.html')
    if 'authentication_error' in request.GET:
    	authenticationError = request.GET['authentication_error']
    else:
    	authenticationError = None
    	
    context = RequestContext(request, {
    	'authentication_error' : authenticationError,
    })
    return HttpResponse(template.render(context))

def submitsignin(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            return redirect('/dico/')
        else:
            return redirect('/dico/signin/?authentication_error=disabled_account')
            # Return a 'disabled account' error message
    else:
        return redirect('/dico/signin/?authentication_error=invalid_login')
        # Return an 'invalid login' error message.

def signout(request):
    logout(request)
    return redirect('/dico/')
    
def editinterests(request):
    if not request.user.is_authenticated:
    	return signin(request)
    
    template = loader.get_template('dico/editinterests.html')
        
    context = RequestContext(request, {
    	'user': request.user,
    })
    return HttpResponse(template.render(context))

def submitnewissue(request):
    results = {'success':False, 'error': u'request format invalid'}

    if request.method == u'POST':
        try:
            POST = request.POST
            newissue = request.POST['newissue']
            
            # Set the new issue to titlecase and remove extraneous spaces.
            newissue = titlecase(newissue)
            newissue = ' '.join(newissue.split())
            Constituent.add_interest(request.user, newissue)
            results = {'success':True}
        except Exception as e:
            results = {'success':False, 'error': str(e)}
            
    return JsonResponse(results)

def submitdeleteinterest(request):
    results = {'success':False, 'error': 'request format invalid'}
    if request.method == u'POST':
        try:
            POST = request.POST
            oldinterest = request.POST['oldinterest']
            Constituent.delete_interest(request.user, oldinterest)
            results = {'success':True}
        except Exception as e:
            results = {'success':False, 'error': str(e)}
            
    return JsonResponse(results)

def createConstituent(request):
    template = loader.get_template('dico/createConstituent.html')

    if 'error_message' in request.GET:
    	errorMessage = request.GET['error_message']
    else:
    	errorMessage = None

    context = RequestContext(request, {
    	'error_message' : errorMessage
    })
    return HttpResponse(template.render(context))
    
def getDistrict(address):
    results = Geocoder.geocode(address)
    if not results.valid_address:
        raise ValueError("the street address and zip code are not recognized")
    
    coordinates = results[0].coordinates
    
    #Get the list of legislators for these coordinates.
    return congress.locate_districts_by_lat_lon(coordinates[0], coordinates[1])
    
def newConstituent(request):
    results = {'success':False, 'error': 'newConstituent failed'}
    try:
        username = request.POST['username']
        password = request.POST['password']
        firstName = request.POST['firstName']
        lastName = request.POST['lastName']
        streetAddress = request.POST['streetAddress']
        zipCode = request.POST['zipcode']
        
        districtInfo = getDistrict(streetAddress + " " + zipCode)

        constituent = Constituent.objects.create_constituent(username='Default user', password=password, email=username,
                                                             firstname = firstName, lastname = lastName,
                                                             streetaddress=streetAddress, zipcode=zipCode,
                                                             district=districtInfo[0]["district"], state = districtInfo[0]["state"]
                                                             ) 
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                if request.user is None:
                	results = {'success':False, 'error': 'user login failed.'}
                else:
                	results = {'success':True}
            else:
                results = {'success':False, 'error': 'this user is disabled.'}
                # Return a 'disabled account' error message
        else:
            results = {'success':False, 'error': 'This login is invalid.'}
    except IntegrityError as e:
        results = {'success':False, 'error': 'That email address has already been used to sign up.'}
    except Exception as e:
        log = open('newConstituent.log', 'a')
        log.write("Error: %s\n" % type(e))
        log.write("  Message: %s\n" % str(e))
        log.flush()
        results = {'success':False, 'error': str(e)}
    
    return JsonResponse(results)

def issue(request, issue_id):
    o = Issue.objects
    filter = o.filter(id=issue_id)
    return HttpResponse("You're looking at the dashboard for issue %s." % filter.get())

def dashboard(request, constituent_id):
    return HttpResponse("You're looking at the dashboard for constituent %s." % constituent_id)

def addissue(request, constituent_id):
    return HttpResponse("You're adding an issue as constituent %s." % constituent_id)

def mcdashboard(request, mc_id):
    response = "You're looking at the dashboard for mc %s."
    return HttpResponse(response % mc_id)

def mcaddissue(request, mc_id):
    response = "You're adding an issue as mc %s."
    return HttpResponse(response % mc_id)

def member(request, bioguide_id):
    response = "You're looking at member %s."
    return HttpResponse(response % bioguide_id)

# Handles a GET request to get the interests based on specific issue.
# Request GET element pk: the primary key of the issue
# Request GET element scope: 'district' for the counts at the district level or 'state' for counts
# at the state level. Default is 'district'.
# Returns: JsonResponse with results. 
# Return element success: True if the operation is successful, False otherwise.
# Return element error: Present if there was an error with a text description of the error.
# Return element interests: Present if there was no error. Contains an array of dictionaries 
# for each scope that contains at least one interested constituent. Each dictionary 
# contains a 'state', a 'district' and a 'constituent_count' for district scope; each
# dictionary contains a 'state' and a 'constituent_count' for state scope.
def getInterests(request):
    results = {'success':False}
    if request.method == u'GET':
        GET = request.GET
        try:
            pk = int(GET.get(u'pk', 0))
            if pk != 0:
                try:
                    issue = Issue.objects.get(pk=pk)
                    try:
                        scope = GET.get('scope', 'district')
                        interests = issue.get_interests(scope=scope)
                        interestList = []
                        if scope == 'district':
                            for i in interests:
                                interestList.append({'state': i[0], 'district': i[1], 'constituent_count':i[2]})
                        else:
                            for i in interests:
                                interestList.append({'state': i[0], 'constituent_count':i[1]})
                        results = {'success':True}
                        results['interests'] = interestList
                    except Exception as ex:
                        results = {'success':False, 'error': str(ex)}
                except Exception as ex:
                    results = {'success':False, 'error': 'Issue was not found'}
        except Exception as e:
            results = {'success':False, 'error': str(e)}

    return JsonResponse(results)
    
def getActiveIssues(request):
    results = {'success':False}
    if request.method == u'GET':
        GET = request.GET
        try:
            minInterestCount = int(GET.get(u'minInterestCount', 1))
            issueList = Issue.get_active_issues(minInterestCount)
            results = {'success':True}
            results['issues'] = issueList
        except Exception as e:
            results = {'success':False, 'error': str(e)}

    return JsonResponse(results)
	

def getMyIssues(request):
    results = {'success':False}
    if request.method == u'POST':
        try:
            POST = request.POST
            myIssues = []
            if request.user.is_authenticated:
                interests = Constituent.get_interests(request.user)
                for i in interests:
                    myIssues.append({'id': i.issue.id, 'name': i.issue.name})

            issue_list = Issue.objects.order_by('name')
            allIssues = []
            for i in issue_list:
                allIssues.append({'id': i.id, 'name': i.name})
				
            results = {'success':True}
            results['myIssues'] = myIssues
            results['allIssues'] = allIssues
        except Exception as e:
            results = {'success':False, 'error': str(e)}
            
    return JsonResponse(results)
