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

import traceback
import urllib
import json

from dico.models import Issue, Constituent, ConstituentInterest, \
    Petition, PetitionIssue, PetitionVote, MC
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

def account(request):
    if not request.user.is_authenticated:
        return signin(request)
    
    template = loader.get_template('dico/account.html')
    constituent = Constituent.get_constituent(request.user)
    if constituent is None:
        return index(request)
        
    context = RequestContext(request, {
        'user': request.user,
        'constituent': constituent
    })
    return HttpResponse(template.render(context))

def createPetition(request):
    if not request.user.is_authenticated:
        return signin(request)
    
    template = loader.get_template('dico/createPetition.html')
        
    if 'next' in request.GET:
        next = request.GET['next']
    else:
        next = request.META.HTTP_REFERER
        
    if 'issue' in request.GET:
        issueID = request.GET['issue']
        issue = Issue.objects.filter(pk=issueID).get()

    context = RequestContext(request, {
        'user': request.user,
        'next': next,
        'issue': issue,
    })
    return HttpResponse(template.render(context))

def hasIssue(issues, issue):
    testName = issue['name']
    for i in issues:
        if i.name == testName:
            return True
    return False
    
# Displays a web page for adding an issue to a petition.
def addpetitionissue(request, petition_id):
    if not request.user.is_authenticated:
        return signin(request)
    
    template = loader.get_template('dico/addpetitionissue.html')
        
    petition = Petition.objects.filter(pk=petition_id).select_related().get()
    
    petitionIssues = petition.issues.all();
    allIssues = []
    for i in Issue.get_active_issues(1):
        if (not hasIssue(petitionIssues, i)):
            allIssues += [i]

    context = RequestContext(request, {
        'user': request.user,
        'petition': petition,
        'allIssues': allIssues,
    })
    return HttpResponse(template.render(context))

def newInterest(request):
    results = {'success':False, 'error': u'request format invalid'}
    try:
        if request.method != "POST":
            raise Exception("newInterest only responds to POST requests")

        POST = request.POST
        newissue = request.POST['newissue']
        
        # Set the new issue to titlecase and remove extraneous spaces.
        newissue = titlecase(newissue)
        newissue = ' '.join(newissue.split())
        Constituent.add_interest(request.user, newissue)
        results = {'success':True}
    except Exception as e:
        log = open('exception.log', 'a')
        log.write("%s\n" % traceback.format_exc())
        log.flush()
        results = {'success':False, 'error': str(e)}
            
    return JsonResponse(results)

def submitdeleteinterest(request):
    results = {'success':False, 'error': 'request format invalid'}
    try:
        if request.method != "POST":
            raise Exception("submitdeleteinterest only responds to POST requests")

        POST = request.POST
        oldinterest = request.POST['oldinterest']
        Constituent.delete_interest(request.user, oldinterest)
        results = {'success':True}
    except Exception as e:
        log = open('exception.log', 'a')
        log.write("%s\n" % traceback.format_exc())
        log.flush()
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
        if request.method != "POST":
            raise Exception("newConstituent only responds to POST requests")

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
        log = open('exception.log', 'a')
        log.write("%s\n" % traceback.format_exc())
        log.flush()
        results = {'success':False, 'error': str(e)}
    
    return JsonResponse(results)

def updateConstituent(request):
    results = {'success':False, 'error': 'updateConstituent failed'}
    try:
        if request.method != "POST":
            raise Exception("UpdateConstituent only responds to POST requests")
        if not request.user.is_authenticated:
            raise Exception("The current login is invalid")
            
        POST = request.POST;
        newUsername = POST.get('newUsername', '')
        oldPassword = POST.get('oldPassword', '')
        newPassword = POST.get('newPassword', '')
        newFirstName = POST.get('newFirstName', '')
        newLastName = POST.get('newLastName', '')
        newStreetAddress = POST.get('newStreetAddress', '')
        newZipCode = POST.get('newZipcode', '')
        
        constituent = Constituent.get_constituent(request.user)
        if constituent is None:
            return
        
        if len(newStreetAddress) == 0:
            newStreetAddress = constituent.streetAddress
        if len(newZipCode) == 0:
            newZipCode = constituent.zipCode
            
        districtInfo = getDistrict(newStreetAddress + " " + newZipCode)
        
        constituent.update_fields(newUsername, newPassword, 
                                  newFirstName, newLastName, newStreetAddress, newZipCode, 
                                  districtInfo[0]["state"], districtInfo[0]["district"])

        results = {'success':True}
    except IntegrityError as e:
        results = {'success':False, 'error': 'That email address has already been used to sign up.'}
    except Exception as e:
        log = open('exception.log', 'a')
        log.write("%s\n" % traceback.format_exc())
        log.flush()
        results = {'success':False, 'error': str(e)}
    
    return JsonResponse(results)

def newPetition(request):
    results = {'success':False, 'error': 'newPetition failed'}
    try:
        if request.method != "POST":
            raise Exception("newPetition only responds to POST requests")
        if not request.user.is_authenticated:
            raise Exception("The current login is invalid")

        # Get the petition info.
        description = request.POST['description']

        constituent = Constituent.get_constituent(request.user)
        if constituent is None:
            raise Exception('The current login is not a constituent');
        
        # Do the model operation
        petition = Petition.objects.create_petition(constituent, description)
        issueName = request.POST.get('issue', '')
        if len(issueName) != 0:
            query_set = Issue.objects.filter(name=issueName)
            if query_set.count() == 0:
                raise ValueError('the issue "{}" is not recognized'.format(issueName))
            else:
                issue = query_set.get()
            pi = PetitionIssue(petition=petition, issue=issue, constituent=constituent)
            pi.save()
        
        # Return the results.
        results = {'success':True, 'petition':petition.id}
    except Exception as e:
        log = open('exception.log', 'a')
        log.write("%s\n" % traceback.format_exc())
        log.flush()
        results = {'success':False, 'error': str(e)}
    
    return JsonResponse(results)

def deletePetition(request):
    results = {'success':False, 'error': 'deletePetition failed'}
    try:
        if request.method != "POST":
            raise Exception("deletePetition only responds to POST requests")
        if not request.user.is_authenticated:
            raise Exception("The current login is invalid")

        # Get the petition info.
        petition_id = request.POST['petition_id']

        # Do the model operation
        Petition.objects.filter(id=petition_id).delete();
        
        # Return the results.
        results = {'success':True}
    except Exception as e:
        log = open('exception.log', 'a')
        log.write("%s\n" % traceback.format_exc())
        log.flush()
        results = {'success':False, 'error': str(e)}
    
    return JsonResponse(results)

def updatePetition(request):
    results = {'success':False, 'error': 'updatePetition failed'}
    try:
        if request.method != "POST":
            raise Exception("updatePetition only responds to POST requests")
        if not request.user.is_authenticated:
            raise Exception("The current login is invalid")

        # Get the petition info.
        petition_id = request.POST['id']
        description = request.POST['description']

        # Do the model operation
        
        # Return the results.
        results = {'success':True}
    except Exception as e:
        log = open('exception.log', 'a')
        log.write("%s\n" % traceback.format_exc())
        log.flush()
        results = {'success':False, 'error': str(e)}
    
    return JsonResponse(results)

def newPetitionIssue(request):
    results = {'success':False, 'error': 'newPetitionIssue failed'}
    try:
        if request.method != "POST":
            raise Exception("newPetitionIssue only responds to POST requests")
        if not request.user.is_authenticated:
            raise Exception("The current login is invalid")

        # Get the petition issue info.
        petition_id = request.POST['petition']
        issue_id = request.POST['issue']
        
        constituent = Constituent.get_constituent(request.user)
        if constituent is None:
            raise Exception('The current login is not a constituent');
        
        # Do the model operation
        petition = Petition.objects.filter(pk=petition_id).get();
        issue = Issue.objects.filter(pk=issue_id).get();
        
        petition.add_issue(issue, constituent)

        # Return the results.
        results = {'success':True}
    except Exception as e:
        log = open('exception.log', 'a')
        log.write("%s\n" % traceback.format_exc())
        log.flush()
        results = {'success':False, 'error': str(e)}
    
    return JsonResponse(results)

def deletePetitionIssue(request):
    results = {'success':False, 'error': 'deletePetitionIssue failed'}
    try:
        if request.method != "POST":
            raise Exception("deletePetitionIssue only responds to POST requests")
        if not request.user.is_authenticated:
            raise Exception("The current login is invalid")

        # Get the petition info.
        petition_id = request.POST['petition_id']
        issue_id = request.POST['issue_id']

        # Do the model operation
        PetitionIssue.delete_petition_issue(petition_id, issue_id)
        
        # Return the results.
        results = {'success':True}
    except Exception as e:
        log = open('exception.log', 'a')
        log.write("%s\n" % traceback.format_exc())
        log.flush()
        results = {'success':False, 'error': str(e)}
    
    return JsonResponse(results)

def getPetitionVotes(request):
    results = {'success':False, 'error': 'newPetitionVote failed'}
    try:
        if request.method != "POST":
            raise Exception("newPetitionVote only responds to POST requests")
            
        # Get the petition info.
        petition_id = request.POST['petition']
        voteCounts = Petition.get_votes(petition_id)
        # Return the results.
        results = {'success':True, 'votes':voteCounts}
        
        if request.user.is_authenticated:
            constituent = Constituent.get_constituent(request.user)
            if constituent is not None:
                query_set = PetitionVote.objects.filter(petition_id=petition_id). \
                    filter(constituent_id=constituent.user.id)
                if (query_set.count() > 0):
                    results['userVote'] = query_set.get().vote
            
    except Exception as e:
        log = open('exception.log', 'a')
        log.write("%s\n" % traceback.format_exc())
        log.flush()
        results = {'success':False, 'error': str(e)}
    
    return JsonResponse(results)
        
def newPetitionVote(request):
    results = {'success':False, 'error': 'newPetitionVote failed'}
    try:
        if request.method != "POST":
            raise Exception("newPetitionVote only responds to POST requests")
        if not request.user.is_authenticated:
            raise Exception("The current login is invalid")

        constituent = Constituent.get_constituent(request.user)
        if constituent is None:
            raise Exception('The current login is not a constituent');

        # Get the petition info.
        petition_id = request.POST['petition']
        vote = request.POST['vote']
        
        # Do the model operation
        query_set = PetitionVote.objects.filter(petition_id=petition_id, constituent_id=constituent.user.id)
        if query_set.count() == 0:
            petitionVote = PetitionVote.objects.create(petition_id=petition_id, constituent_id=constituent.user.id, vote=int(vote))
        else:
            petitionVote = query_set.get()
            petitionVote.vote = int(vote)
            petitionVote.save()
        
        # Return the results.
        results = {'success':True}
    except Exception as e:
        log = open('exception.log', 'a')
        log.write("%s\n" % traceback.format_exc())
        log.flush()
        results = {'success':False, 'error': str(e)}
    
    return JsonResponse(results)

def deletePetitionVote(request):
    results = {'success':False, 'error': 'deletePetitionVote failed'}
    try:
        if request.method != "POST":
            raise Exception("deletePetitionVote only responds to POST requests")
        if not request.user.is_authenticated:
            raise Exception("The current login is invalid")

        # Get the petition info.
        petition_id = request.POST['petition']
        
        constituent = Constituent.get_constituent(request.user)
        if constituent is None:
            raise Exception('The current login is not a constituent');

        # Do the model operation
        PetitionVote.objects.filter(petition_id=petition_id, constituent_id=constituent.user.id).delete()
        
        # Return the results.
        results = {'success':True}
    except Exception as e:
        log = open('exception.log', 'a')
        log.write("%s\n" % traceback.format_exc())
        log.flush()
        results = {'success':False, 'error': str(e)}
    
    return JsonResponse(results)

def updatePetitionVote(request):
    results = {'success':False, 'error': 'updatePetitionVote failed'}
    try:
        if request.method != "POST":
            raise Exception("updatePetitionVote only responds to POST requests")
        if not request.user.is_authenticated:
            raise Exception("The current login is invalid")

        # Get the petition info.
        petition_vote_id = request.POST['id']
        vote = request.POST['vote']

        # Do the model operation
        
        # Return the results.
        results = {'success':True}
    except Exception as e:
        log = open('exception.log', 'a')
        log.write("%s\n" % traceback.format_exc())
        log.flush()
        results = {'success':False, 'error': str(e)}
    
    return JsonResponse(results)

def issue(request, issue_id):
    template = loader.get_template('dico/issuePetitions.html')
    filter = Issue.objects.filter(id=issue_id)
    context = RequestContext(request, {
        'user': request.user,
        'issue': filter.get(),
    })
    return HttpResponse(template.render(context))

def petition(request, petition_id):
    template = loader.get_template('dico/petition.html')
    
    issueID = int(request.GET.get(u'backIssue', 0))
    if (issueID != 0):
        issue = Issue.objects.filter(pk=issueID).get()
        backName = issue.name
        backURL = "/dico/" + str(issueID) + "/issue/"
    else:
        backName = ""
        backURL = ""
        
    filter = Petition.objects.filter(id=petition_id)
    context = RequestContext(request, {
        'user': request.user,
        'petition': filter.get(),
        'backName' : backName,
        'backURL' : backURL,
    })
    return HttpResponse(template.render(context))

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
    
def getIssuePetitions(request):
    results = {'success':False, 'error': 'getIssuePetitions failed'}
    try:
        if request.method != "POST":
            raise Exception("getIssuePetitions only responds to POST requests")

        # Get the petition info.
        issue_id = request.POST['issue']

        # Do the model operation
        petitionIssues = PetitionIssue.objects.filter(issue_id=issue_id).select_related('petition')
        petitions = []
        for i in petitionIssues:
            petitions.append({'id': i.petition.id, 'description': i.petition.description})
        
        # Return the results.
        results = {'success':True, 'petitions' : petitions}
    except Exception as e:
        log = open('exception.log', 'a')
        log.write("%s\n" % traceback.format_exc())
        log.flush()
        results = {'success':False, 'error': str(e)}
    
    return JsonResponse(results)

def getPetitionIssues(request):
    results = {'success':False, 'error': 'getPetitionIssues failed'}
    try:
        if request.method != "POST":
            raise Exception("getPetitionIssues only responds to POST requests")

        # Get the petition info.
        petition_id = request.POST['petition']

        # Do the model operation
        petitionIssues = PetitionIssue.objects.filter(petition_id=petition_id).select_related('issue')
        issues = []
        for i in petitionIssues:
            issues.append({'id': i.issue.id, 'name': i.issue.name})
        
        # Return the results.
        results = {'success':True, 'issues' : issues}
    except Exception as e:
        log = open('exception.log', 'a')
        log.write("%s\n" % traceback.format_exc())
        log.flush()
        results = {'success':False, 'error': str(e)}
    
    return JsonResponse(results)

def getPetitionArguments(request):
    results = {'success':False, 'error': 'getPetitionArguments failed'}
    try:
        if request.method != "POST":
            raise Exception("getPetitionArguments only responds to POST requests")

        # Get the petition info.
        petition_id = request.POST['petition']

        supportingArguments = [];
        opposingArguments = [];
        # Do the model operation
        # TODO: 
        
        # Return the results.
        results = {'success':True, 'supportingArguments' : supportingArguments, 'opposingArguments' : opposingArguments}
    except Exception as e:
        log = open('exception.log', 'a')
        log.write("%s\n" % traceback.format_exc())
        log.flush()
        results = {'success':False, 'error': str(e)}
    
    return JsonResponse(results)

