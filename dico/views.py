from django.conf import settings
from django.contrib import admin
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.db import transaction
from django.db.utils import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.template import RequestContext, loader
from django.views.decorators.csrf import requires_csrf_token
from pygeocoder import Geocoder
from sunlight import congress
from dico.emailer import Emailer

import traceback
import json
import uuid

from custom_user.models import PasswordReset
from dico.models import Issue, Constituent, ConstituentInterest, ContactMethod, \
    Petition, PetitionManager, PetitionIssue, PetitionVote, \
    Frequency, Via, \
    Argument, ArgumentManager, ArgumentRating, Note, NoteManager, Story, StoryManager, MC
from dico.titlecase import titlecase

# Create your views here.

def index(request):
    if request.user.is_authenticated():
        constituent = Constituent.get_constituent(request.user)
        if constituent is None:
            # log out the current user so that the landing page is clean.
            logout(request)
        else:
            template = loader.get_template('dico/home.html')
            context = RequestContext(request, {
                'user': request.user,
                'member_list': Constituent.get_members(request.user),
                'news_list': Constituent.get_news(request.user),
            })
            return HttpResponse(template.render(context))
            
    template = loader.get_template('dico/index.html')
    context = RequestContext(request, {
        'facebookAppID': settings.FACEBOOK_APP_ID, 
    })
        
    return HttpResponse(template.render(context))

@requires_csrf_token
def signin(request):
    template = loader.get_template('dico/signin.html')
    
    backURL = request.GET.get(u'backURL', "/dico/")
        
    context = RequestContext(request, {
        'backURL' : backURL,
    })
    return HttpResponse(template.render(context))

def submitsignin(request):
    try:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                results = {'success':True}
            else:
                raise Exception('This account is disabled.')
        else:
            raise Exception('This login is invalid.');
    except Exception as e:
        with open('exception.log', 'a') as log:
            log.write("%s\n" % traceback.format_exc())
            log.flush()
        results = {'success':False, 'error': str(e)}
            
    return JsonResponse(results)
    
def submitFacebookSignin(request):
    try:
        accessToken = request.POST['accessToken']
        user = authenticate(accessToken=accessToken)
        if user is not None:
            if user.is_active:
                login(request, user)
                setupRequired = (Constituent.get_constituent(user) is None)
                results = {'success':True,
                           'setupRequired': setupRequired,
                           'accessToken':accessToken}
            else:
                raise Exception('This account is disabled.')
        else:
            raise Exception('This Facebook login is invalid.');
    except Exception as e:
        with open('exception.log', 'a') as log:
            log.write("%s\n" % traceback.format_exc())
            log.flush()
        results = {'success':False, 'error': str(e)}
            
    return JsonResponse(results)

def signout(request):
    logout(request)
    return redirect('/dico/')
    
def editInterests(request):
    if not request.user.is_authenticated:
        return signin(request)
    
    template = loader.get_template('dico/editinterests.html')
    backURL = request.GET.get('back', '/dico/')
        
    context = RequestContext(request, {
        'user': request.user,
        'backURL': backURL,
    })
    return HttpResponse(template.render(context))

def account(request):
    if not request.user.is_authenticated:
        return signin(request)
    
    template = loader.get_template('dico/account.html')
    backURL = request.GET.get('back', '/dico/')
    constituent = Constituent.get_constituent(request.user)
    if constituent is None:
        return index(request)
    contactMethod = ContactMethod.get_contact_method(request.user)
        
    context = RequestContext(request, {
        'user': request.user,
        'constituent': constituent,
        'backURL': backURL,
        'contactMethod': contactMethod
    })
    return HttpResponse(template.render(context))

def constituentSettings(request):
    if not request.user.is_authenticated:
        return signin(request)
    
    template = loader.get_template('dico/constituentsettings.html')
    backURL = request.GET.get('back', '/dico/')
    nextURL = request.GET.get('next', '/dico/')
    accessToken = request.GET.get('accessToken', None)
    constituent = Constituent.get_constituent(request.user)
    contactMethod = ContactMethod.get_contact_method(request.user)
        
    context = RequestContext(request, {
        'user': request.user,
        'constituent': constituent,
        'backURL': backURL,
        'nextURL': nextURL,
        'accessToken': accessToken,
        'contactMethod': contactMethod
    })
    return HttpResponse(template.render(context))

def password(request):
    if not request.user.is_authenticated:
        return signin(request)
    
    template = loader.get_template('dico/password.html')
    backURL = request.GET.get('back', '/dico/')
        
    context = RequestContext(request, {
        'user': request.user,
        'backURL': backURL,
    })
    return HttpResponse(template.render(context))

# Displays a web page in which a user can specify an email address for 
# resetting their password.
def forgotPassword(request):
    if not request.user.is_authenticated:
        return signin(request)
    
    template = loader.get_template('dico/forgotpassword.html')
    backURL = request.GET.get('backURL', '/dico/')
    nextURL = request.GET.get('nextURL', '/dico/')
        
    context = RequestContext(request, {
        'backURL': backURL,
        'nextURL': nextURL,
    })
    return HttpResponse(template.render(context))

# Displays a web page in which a user can specify a new password based on a key.
def passwordReset(request):
    if not request.user.is_authenticated:
        return signin(request)
    
    template = loader.get_template('dico/passwordreset.html')
    resetKey = request.GET.get('key', "")
        
    context = RequestContext(request, {
        'resetkey': resetKey
    })
    return HttpResponse(template.render(context))

# Displays a web page in which a user can create a new petition for the specified issue.
def createPetition(request):
    if not request.user.is_authenticated:
        return signin(request)
    
    template = loader.get_template('dico/createPetition.html')
    backURL = request.GET.get('backURL', '/dico/');    
    backName = request.GET.get('backName', 'Home')
        
    allIssues = []
    if 'issue' in request.GET:
        issueID = request.GET['issue']
        issue = Issue.objects.filter(pk=issueID).get()
    else:
        issue = None
        for i in Issue.get_issues():
            allIssues += [i]

    context = RequestContext(request, {
        'user': request.user,
        'backURL': backURL,
        'backName': backName,
        'issue': issue,
        'allIssues': allIssues,
    })
    return HttpResponse(template.render(context))

# Displays a web page in which a user can edit the description of an action.
def editPetition(request):
    if not request.user.is_authenticated:
        return signin(request)
    
    template = loader.get_template('dico/editPetition.html')
    backURL = request.GET.get('back', '/dico/')
    petition_id = request.GET.get('petition', 0)
    
    if petition_id == 0:
        raise Exception('The petition is not specified')
        
    petition = Petition.objects.get(pk=petition_id)
    if petition.constituent.user != request.user and not (request.user.is_superuser):
        raise Exception('The current login does not have permission to change this action');
       
    voteCount = petition.get_vote_count()
    context = RequestContext(request, {
        'user': request.user,
        'petition': petition,
        'backURL': backURL,
        'voteCount': voteCount,
    })
    return HttpResponse(template.render(context))

def hasIssue(issues, issue):
    testName = issue['name']
    for i in issues:
        if i.name == testName:
            return True
    return False
    
# Displays a web page for adding an issue to a petition.
def addPetitionIssue(request, petition_id):
    if not request.user.is_authenticated:
        return signin(request)
    
    template = loader.get_template('dico/addpetitionissue.html')
        
    petition = Petition.objects.filter(pk=petition_id).select_related().get()
    backURL = request.GET.get('backURL', '/dico/');    
    backName = request.GET.get('backName', 'Home')
    
    petitionIssues = petition.issues.all();
    allIssues = []
    for i in Issue.get_issues():
        if (not hasIssue(petitionIssues, i)):
            allIssues += [i]

    context = RequestContext(request, {
        'user': request.user,
        'petition': petition,
        'allIssues': allIssues,
        'backURL': backURL,
        'backName': backName,
    })
    return HttpResponse(template.render(context))

# Creates a record so that a user can reset their password via email.
def resetPassword(request):
    results = {'success':False, 'error': u'request format invalid'}
    try:
        if request.method != "POST":
            raise Exception("newInterest only responds to POST requests")

        POST = request.POST
        email = request.POST['email']
        
        if get_user_model().objects.filter(email=email).count() == 0:
            raise Exception("This email address is not recognized.");
            
        newKey = str(uuid.uuid4())
        
        query_set = PasswordReset.objects.filter(email=email)
        if query_set.count() == 0:
            PasswordReset.objects.create(email=email, reset_key=newKey)
        else:
            pr = query_set.get()
            pr.reset_key = newKey
            pr.save()
        
        Emailer.sendResetPasswordEmail(email, settings.PASSWORD_RESET_URL + "?key=" + newKey)
        
        # Set the new issue to titlecase and remove extraneous spaces.
        results = {'success':True}
    except Exception as e:
        log = open('exception.log', 'a')
        log.write("%s\n" % traceback.format_exc())
        log.flush()
        results = {'success':False, 'error': str(e)}
            
    return JsonResponse(results)

# Resets the password for the specified email address based on the key.
def setResetPassword(request):
    results = {'success':False, 'error': u'request format invalid'}
    try:
        if request.method != "POST":
            raise Exception("newInterest only responds to POST requests")

        POST = request.POST
        resetKey = request.POST['resetkey']
        email = request.POST['email']
        password = request.POST['password']
        
        if get_user_model().objects.filter(email=email).count() == 0:
            raise Exception("This email address is not recognized.");
        
        query_set = PasswordReset.objects.filter(reset_key=resetKey)
        if query_set.count() == 0:  
            raise Exception("This reset key is not recognized.");
        
        pr = query_set.get()
        pr.updatePassword(email, password)
        
        user = authenticate(username=email, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                results = {'success':True}
            else:
                raise Exception('This account is disabled.')
        else:
            raise Exception('This login is invalid.');

        results = {'success':True}
    except Exception as e:
        log = open('exception.log', 'a')
        log.write("%s\n" % traceback.format_exc())
        log.flush()
        results = {'success':False, 'error': str(e)}
            
    return JsonResponse(results)

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
        with open('exception.log', 'a') as log:
            log.write("%s\n" % traceback.format_exc())
            log.flush()
        results = {'success':False, 'error': str(e)}
            
    return JsonResponse(results)

def signup(request):
    template = loader.get_template('dico/signup.html')

    backURL = request.GET.get('backURL', '/dico/')
    nextURL = request.GET.get('nextURL', '/dico/')

    context = RequestContext(request, {
        'backURL' : backURL,
        'nextURL' : nextURL,
    })
    return HttpResponse(template.render(context))
    
def getDistrict(address):
    results = Geocoder.geocode(address)
    if not results.valid_address:
        raise ValueError("the street address and zip code are not recognized")
    
    coordinates = results[0].coordinates
    
    #Get the list of legislators for these coordinates.
    return congress.locate_districts_by_lat_lon(coordinates[0], coordinates[1])
    
def checkUnusedEmail(request):
    results = {'success':False, 'error': 'checkEmail failed'}
    try:
        if request.method != "POST":
            raise Exception("checkEmail only responds to POST requests")

        email = request.POST['email']
        
        manager = get_user_model().objects
        if manager.filter(email=manager.normalize_email(email)).count() > 0:
            results = {'success':False, 'error': 'That email address has already been used to sign up.'}
        else:
            results = {'success':True}
    except Exception as e:
        with open('exception.log', 'a') as log:
            log.write("%s\n" % traceback.format_exc())
            log.flush()
        results = {'success':False, 'error': str(e)}
    
    return JsonResponse(results)

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

        contactFrequency = request.POST.get('contactFrequency', 1)
        contactVia = request.POST.get('contactVia', 2)
        contactPhoneNumber = request.POST['contactPhone']
        
        newFrequency = Frequency.objects.filter(pk=contactFrequency).get()
        newVia = Via.objects.filter(pk=contactVia).get()
        
        with transaction.atomic():
            constituent = Constituent.objects.create_constituent(username='Default user', password=password, email=username,
                                                                 firstname = firstName, lastname = lastName,
                                                                 streetaddress=streetAddress, zipcode=zipCode,
                                                                 district=districtInfo[0]["district"], state = districtInfo[0]["state"]
                                                                 )
                                                             
            contactMethod = ContactMethod.objects.create(user=constituent.user, 
                                                         frequency=newFrequency,
                                                         via=newVia, 
                                                         phonenumber = contactPhoneNumber)
                                                     
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
        with open('exception.log', 'a') as log:
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
        newFirstName = POST.get('newFirstName', '')
        newLastName = POST.get('newLastName', '')
        newStreetAddress = POST.get('newStreetAddress', '')
        newZipCode = POST.get('newZipcode', '')
        if 'newContactFrequency' in POST:
            newFrequency = Frequency.objects.filter(pk=POST['newContactFrequency']).get()
        else:
            newFrequency = None
        if 'newContactVia' in POST:
            newVia = Via.objects.filter(pk=POST['newContactVia']).get()
        else:
            newVia = None
        newPhoneNumber = POST.get('newContactPhone', '')
        
        constituent = Constituent.get_constituent(request.user)          
        with transaction.atomic():
            if constituent is None:
                districtInfo = getDistrict(newStreetAddress + " " + newZipCode)
                constituent = Constituent.objects.create(user=request.user, 
                                          streetAddress=newStreetAddress, 
                                          zipCode=newZipCode,
                                          district=districtInfo[0]["district"], 
                                          state=districtInfo[0]["state"])
            else:
                if len(newStreetAddress) == 0:
                    newStreetAddress = constituent.streetAddress
                if len(newZipCode) == 0:
                    newZipCode = constituent.zipCode
                districtInfo = getDistrict(newStreetAddress + " " + newZipCode)
                constituent.update_fields(newUsername, 
                                          newFirstName, newLastName, newStreetAddress, newZipCode, 
                                          districtInfo[0]["state"], districtInfo[0]["district"])
        
            contactMethod = ContactMethod.get_contact_method(request.user)
            if contactMethod is None:
                if newFrequency is None:
                    newFrequency = Frequency.objects.filter(pk=1).get()
                if newVia is None:
                    newVia = Via.objects.filter(pk=2).get()
                ContactMethod.objects.create(frequency=newFrequency, 
                                             via=newVia, 
                                             phonenumber=newPhoneNumber)
            else:
                contactMethod.update_fields(newFrequency, 
                                            newVia, 
                                            newPhoneNumber)

        results = {'success':True}
    except IntegrityError as e:
        results = {'success':False, 'error': 'That email address has already been used to identify someone.'}
    except Exception as e:
        log = open('exception.log', 'a')
        log.write("%s\n" % traceback.format_exc())
        log.flush()
        results = {'success':False, 'error': str(e)}
    
    return JsonResponse(results)

def updatePassword(request):
    results = {'success':False, 'error': 'updatePassword failed'}
    try:
        if request.method != "POST":
            raise Exception("UpdatePassword only responds to POST requests")
        if not request.user.is_authenticated:
            raise Exception("The current login is invalid")
            
        POST = request.POST;
        oldPassword = POST.get('oldPassword', '')
        newPassword = POST.get('newPassword', '')
        
        testUser = authenticate(username=request.user.email, password=oldPassword)
        if testUser is not None:
            if testUser.is_active:
                testUser.set_password(newPassword)
                testUser.save(using=get_user_model().objects._db)
            else:
                raise Exception('This account is disabled.');
                # Return a 'disabled account' error message
        else:
            raise Exception('This login is invalid.')

        results = {'success':True}
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
        
        issues = request.POST.getlist('issue[]');
        
        # Do the model operation
        with transaction.atomic():
            petition = Petition.objects.create_petition(constituent, description)
            for s in issues:
                petition.add_issue_by_name(s, constituent)
        
        # Return the results.
        results = {'success':True, 'petition':petition.id}
    except Exception as e:
        with open('exception.log', 'a') as log:
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
        petition_id = request.POST['petition']
        description = request.POST['description']

        constituent = Constituent.get_constituent(request.user)
        if constituent is None:
            raise Exception('The current login is not a constituent');
            
        petition = Petition.objects.get(pk=petition_id)
        if petition.constituent != constituent and not (request.user.is_superuser):
            raise Exception('The current login does not have permission to change this action');
            
        # Do the model operation
        with transaction.atomic():
            petition.update_description(description);
        
        # Return the results.
        results = {'success':True, 'petition':petition_id}
    except Exception as e:
        with open('exception.log', 'a') as log:
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

# Displays a web page for adding a story to a petition.
def addNote(request):
    if not request.user.is_authenticated:
        return signin(request)
    
    template = loader.get_template('dico/addnote.html')
        
    petition_id = request.GET.get('petition', 0)
    petition = Petition.objects.filter(pk=petition_id).select_related().get()
    backURL = request.GET.get(u'backURL', '/dico/')
    backName = request.GET.get('backName', 'Home')
    
    context = RequestContext(request, {
        'user': request.user,
        'petition': petition,
        'backURL': backURL,
        'backName': backName,
    })
    return HttpResponse(template.render(context))

# Displays a web page for adding a supporting argument to a petition.
def addSupportingArgument(request):
    if not request.user.is_authenticated:
        return signin(request)
    
    template = loader.get_template('dico/addargument.html')
        
    petition_id = request.GET.get('petition', 0)
    petition = Petition.objects.filter(pk=petition_id).select_related().get()
    backURL = request.GET.get(u'backURL', '/dico/')
    backName = request.GET.get('backName', 'Home')
    
    context = RequestContext(request, {
        'user': request.user,
        'petition': petition,
        'backURL': backURL,
        'backName': backName,
        'argumentVote': 1,
        'voteLabel': "Supporting",
    })
    return HttpResponse(template.render(context))

# Displays a web page for adding a supporting argument to a petition.
def addOpposingArgument(request):
    if not request.user.is_authenticated:
        return signin(request)
    
    template = loader.get_template('dico/addargument.html')
        
    petition_id = request.GET.get('petition', 0)
    petition = Petition.objects.filter(pk=petition_id).select_related().get()
    backURL = request.GET.get(u'backURL', '/dico/')
    backName = request.GET.get('backName', 'Home')
    
    context = RequestContext(request, {
        'user': request.user,
        'petition': petition,
        'backURL': backURL,
        'backName': backName,
        'argumentVote': 0,
        'voteLabel': "Opposing",
    })
    return HttpResponse(template.render(context))

# Displays a web page for adding a story to a petition.
def addStory(request):
    if not request.user.is_authenticated:
        return signin(request)
    
    template = loader.get_template('dico/addstory.html')
        
    petition_id = request.GET.get('petition', 0)
    petition = Petition.objects.filter(pk=petition_id).select_related().get()
    backURL = request.GET.get(u'backURL', '/dico/')
    backName = request.GET.get('backName', 'Home')
    
    context = RequestContext(request, {
        'user': request.user,
        'petition': petition,
        'backURL': backURL,
        'backName': backName,
    })
    return HttpResponse(template.render(context))

# Displays a web page for showing the documentation for ratings.
def docRatings(request):
    if not request.user.is_authenticated:
        return signin(request)
    
    template = loader.get_template('doc/ratings.html')
        
    petition_id = request.GET.get('petition', 0)
    petition = Petition.objects.filter(pk=petition_id).select_related().get()
    backURL = request.GET.get(u'backURL', '/dico/')
    backName = request.GET.get('backName', 'Home')
    
    context = RequestContext(request, {
        'user': request.user,
        'petition': petition,
        'backURL': backURL,
        'backName': backName,
    })
    return HttpResponse(template.render(context))

# Displays a web page for adding a supporting argument to a petition.
def docTermsOfUse(request):
    template = loader.get_template('doc/termsofuse.html')
        
    context = RequestContext(request, {
    })
    return HttpResponse(template.render(context))

# Displays a web page for adding a supporting argument to a petition.
def docYourInterests(request):
    template = loader.get_template('doc/yourInterests.html')
        
    context = RequestContext(request, {
    })
    return HttpResponse(template.render(context))

def newNote(request):
    results = {'success':False, 'error': 'newNote failed'}
    try:
        if request.method != "POST":
            raise Exception("newNote only responds to POST requests")
        if not request.user.is_authenticated:
            raise Exception("The current login is invalid")

        constituent = Constituent.get_constituent(request.user)
        if constituent is None:
            raise Exception('The current login is not a constituent');

        # Get the petition info.
        petition_id = request.POST['petition']
        description = request.POST['description']
        link = request.POST['link']
        
        # Do the model operation
        note = Note.objects.create(petition_id=petition_id, \
                                               constituent_id=constituent.user.id, \
                                               description=description,
                                               link=link)
        
        # Return the results.
        results = {'success':True, 'story': {'creationTime': note.creationTime}}
    except Exception as e:
        with open('exception.log', 'a') as log:
            log.write("%s\n" % traceback.format_exc())
            log.flush()
        results = {'success':False, 'error': str(e)}
    
    return JsonResponse(results)

def deleteNote(request):
    results = {'success':False, 'error': 'deleteNote failed'}
    try:
        if request.method != "POST":
            raise Exception("deleteNote only responds to POST requests")
        if not request.user.is_authenticated:
            raise Exception("The current login is invalid")

        # Get the petition info.
        id = request.POST['id']
        
        constituent = Constituent.get_constituent(request.user)
        if constituent is None:
            raise Exception('The current login is not a constituent');

        # Do the model operation
        Note.objects.filter(pk=id).delete()
        
        # Return the results.
        results = {'success':True}
    except Exception as e:
        with open('exception.log', 'a') as log:
            log.write("%s\n" % traceback.format_exc())
            log.flush()
        results = {'success':False, 'error': str(e)}
    
    return JsonResponse(results)

def newArgument(request):
    results = {'success':False, 'error': 'newArgument failed'}
    try:
        if request.method != "POST":
            raise Exception("newArgument only responds to POST requests")
        if not request.user.is_authenticated:
            raise Exception("The current login is invalid")

        constituent = Constituent.get_constituent(request.user)
        if constituent is None:
            raise Exception('The current login is not a constituent');

        # Get the petition info.
        petition_id = request.POST['petition']
        vote = request.POST['vote']
        description = request.POST['description']
        
        # Do the model operation
        argument = Argument.objects.create(petition_id=petition_id, \
                                               constituent_id=constituent.user.id, \
                                               vote=int(vote), \
                                               description=description)
        
        # Return the results.
        results = {'success':True, 'argument': {'description': argument.description, \
                                                'creationTime': argument.creationTime}}
    except Exception as e:
        log = open('exception.log', 'a')
        log.write("%s\n" % traceback.format_exc())
        log.flush()
        results = {'success':False, 'error': str(e)}
    
    return JsonResponse(results)

def deleteArgument(request):
    results = {'success':False, 'error': 'deleteArgument failed'}
    try:
        if request.method != "POST":
            raise Exception("deleteArgument only responds to POST requests")
        if not request.user.is_authenticated:
            raise Exception("The current login is invalid")

        # Get the petition info.
        argument_id = request.POST['argument']
        
        constituent = Constituent.get_constituent(request.user)
        if constituent is None:
            raise Exception('The current login is not a constituent');

        # Do the model operation
        Argument.objects.filter(pk=argument_id).delete()
        
        # Return the results.
        results = {'success':True}
    except Exception as e:
        log = open('exception.log', 'a')
        log.write("%s\n" % traceback.format_exc())
        log.flush()
        results = {'success':False, 'error': str(e)}
    
    return JsonResponse(results)

def rateArgument(request):
    results = {'success':False, 'error': 'rateArgument failed'}
    try:
        if request.method != "POST":
            raise Exception("rateArgument only responds to POST requests")
        if not request.user.is_authenticated:
            raise Exception("The current login is invalid")

        # Get the petition info.
        argument_id = request.POST['argument']
        vote = request.POST['rating']
        
        constituent = Constituent.get_constituent(request.user)
        if constituent is None:
            raise Exception('The current login is not a constituent');

        # Do the model operation
        query_set = ArgumentRating.objects.filter(argument_id=argument_id, constituent_id=constituent.user.id)
        if query_set.count() == 0:
            ar = ArgumentRating.objects.create(argument_id=argument_id, constituent_id=constituent.user.id, vote=int(vote))
        else:
            ar = query_set.get()
            ar.vote = int(vote)
            ar.save()
        
        # Return the results.
        results = {'success':True}
    except Exception as e:
        log = open('exception.log', 'a')
        log.write("%s\n" % traceback.format_exc())
        log.flush()
        results = {'success':False, 'error': str(e)}
    
    return JsonResponse(results)

def unrateArgument(request):
    results = {'success':False, 'error': 'unrateArgument failed'}
    try:
        if request.method != "POST":
            raise Exception("unrateArgument only responds to POST requests")
        if not request.user.is_authenticated:
            raise Exception("The current login is invalid")

        # Get the petition info.
        argument_id = request.POST['argument']
        
        constituent = Constituent.get_constituent(request.user)
        if constituent is None:
            raise Exception('The current login is not a constituent');

        # Do the model operation
        query_set = ArgumentRating.objects.filter(argument_id=argument_id, constituent_id=constituent.user.id)
        if query_set.count() > 0:
            query_set.delete()
        
        # Return the results.
        results = {'success':True}
    except Exception as e:
        log = open('exception.log', 'a')
        log.write("%s\n" % traceback.format_exc())
        log.flush()
        results = {'success':False, 'error': str(e)}
    
    return JsonResponse(results)

def newStory(request):
    results = {'success':False, 'error': 'newStory failed'}
    try:
        if request.method != "POST":
            raise Exception("newStory only responds to POST requests")
        if not request.user.is_authenticated:
            raise Exception("The current login is invalid")

        constituent = Constituent.get_constituent(request.user)
        if constituent is None:
            raise Exception('The current login is not a constituent');

        # Get the petition info.
        petition_id = request.POST['petition']
        description = request.POST['description']
        link = request.POST['link']
        
        # Do the model operation
        story = Story.objects.create(petition_id=petition_id, \
                                               constituent_id=constituent.user.id, \
                                               description=description,
                                               link=link)
        
        # Return the results.
        results = {'success':True, 'story': {'creationTime': story.creationTime}}
    except Exception as e:
        log = open('exception.log', 'a')
        log.write("%s\n" % traceback.format_exc())
        log.flush()
        results = {'success':False, 'error': str(e)}
    
    return JsonResponse(results)

def deleteStory(request):
    results = {'success':False, 'error': 'deleteStory failed'}
    try:
        if request.method != "POST":
            raise Exception("deleteStory only responds to POST requests")
        if not request.user.is_authenticated:
            raise Exception("The current login is invalid")

        # Get the petition info.
        story_id = request.POST['story']
        
        constituent = Constituent.get_constituent(request.user)
        if constituent is None:
            raise Exception('The current login is not a constituent');

        # Do the model operation
        Story.objects.filter(pk=story_id).delete()
        
        # Return the results.
        results = {'success':True}
    except Exception as e:
        log = open('exception.log', 'a')
        log.write("%s\n" % traceback.format_exc())
        log.flush()
        results = {'success':False, 'error': str(e)}
    
    return JsonResponse(results)

def issues(request):
    template = loader.get_template('dico/issues.html')
    backURL = request.GET.get(u'backURL', '/dico/')
    backName = request.GET.get('backName', 'Home')
    if request.user.is_authenticated:
        defaultPanel = 'vote'
    else:
        defaultPanel = 'debate'
    actionPanel = request.GET.get('actionPanel', defaultPanel);
    
    helpTexts = { 'vote': 'Select an issue that is related to the action you want to vote on.', \
                  'debate': 'Select the issue that you want to explore.', \
                  'maps': 'Select an issue that is related to the action you want to analyze.', \
                  'story': 'Select the issue that is related to the action you want to create a story for.' }
    titleTexts = {'vote': 'Explore an Issue', \
                  'debate': 'Explore an Issue', \
                  'story': 'Share Your Story' }
    if actionPanel in helpTexts:
        helpText = helpTexts[actionPanel]
    else:
        helpText = 'Select an issue that is related to the action you want.'
        
    if actionPanel in titleTexts:
        titleText = titleTexts[actionPanel]
    else:
        titleText = 'Select Issue'
        
    context = RequestContext(request, {
        'user': request.user,
        'backURL': backURL,
        'backName': backName,
        'actionPanel': actionPanel,
        'helpText': helpText,
        'titleText': titleText,
    })
    return HttpResponse(template.render(context))

def search(request):
    template = loader.get_template('dico/search.html')
    query = request.GET.get('query', "");
    if request.user.is_authenticated:
        defaultPanel = 'vote'
    else:
        defaultPanel = 'debate'
    actionPanel = request.GET.get('actionPanel', defaultPanel);
    
    context = RequestContext(request, {
        'user': request.user,
        'query': query,
        'actionPanel': actionPanel,
    })
    return HttpResponse(template.render(context))

def issue(request):
    template = loader.get_template('dico/issuePetitions.html')
    issue_id = int(request.GET.get('issue', 0));
    filter = Issue.objects.filter(id=issue_id)
    if request.user.is_authenticated:
        defaultPanel = 'vote'
    else:
        defaultPanel = 'debate'
    actionPanel = request.GET.get('actionPanel', defaultPanel);
    
    helpTexts = { 'vote': 'Select the action you want to vote on.', \
                  'debate': 'Select the action you want to learn about.', \
                  'issues': 'Select the action you want to label.', \
                  'maps': 'Select the action you want to analyze.', \
                  'story': 'Select the action you want to create a story for.' }
    if actionPanel in helpTexts:
        helpText = helpTexts[actionPanel]
    else:
        helpText = 'Select the action you want.'
        
    context = RequestContext(request, {
        'user': request.user,
        'issue': filter.get(),
        'actionPanel': actionPanel,
        'helpText': helpText,
    })
    return HttpResponse(template.render(context))

def votingHistory(request):
    template = loader.get_template('dico/votingHistory.html')
    if request.user.is_authenticated:
        defaultPanel = 'vote'
    else:
        defaultPanel = 'debate'
    actionPanel = request.GET.get('actionPanel', defaultPanel);
    
    context = RequestContext(request, {
        'user': request.user,
        'actionPanel': actionPanel,
    })
    return HttpResponse(template.render(context))

# Displays a web page for a petition.
def petition(request, petition_id):
    template = loader.get_template('dico/petition.html')
    
    backURL = request.GET.get(u'backURL', '/dico/')
    backName = request.GET.get('backName', 'Home')
    initialTab = request.GET.get('tab', 'vote')
    
    if initialTab == 'debate':
        initialButton = "#id_debateButton"
    elif initialTab == 'maps':
        initialButton = "#id_mapsButton"
    elif initialTab == 'story':
        initialButton = "#id_storyButton"
    else:
        initialButton = "#id_voteButton"
        
    inEditMode = int('edit' in request.GET)
        
    if 'showNext' in request.GET:
        nextPetitionID = Petition.objects.get_next_petition_id(petition_id=petition_id, user=request.user)
        showDoneVoting = True
    else:
        nextPetitionID = None
        showDoneVoting = False
    
    vote = Constituent.get_vote(request.user, petition_id) 
    
    filter = Petition.objects.filter(id=petition_id)
    petition = filter.get()
    
    canEditDescription = request.user.is_superuser or request.user == petition.constituent.user

    context = RequestContext(request, {
        'user': request.user,
        'petition': petition,
        'backURL' : backURL,
        'backName': backName,
        'initialButton': initialButton,
        'nextPetitionID': nextPetitionID,
        'inEditMode': inEditMode,
        'showDoneVoting': showDoneVoting,
        'facebookAppID': settings.FACEBOOK_APP_ID,
        'vote': vote, 
        'canEditDescription': canEditDescription,
    })
    return HttpResponse(template.render(context))
    
# Displays a web page for a petition.
def vote(request):
    template = loader.get_template('dico/petition.html')
    
    backURL = request.GET.get(u'backURL', '/dico/')
    backName = request.GET.get('backName', 'Home')
    
    if 'id' not in request.GET:
        raise Exception('The action to vote on is not specified')
    id = int(request.GET['id'])
    
    initialButton = "#id_voteButton"
        
    nextPetition = None
    showDoneVoting = False
        
    vote = Constituent.get_vote(request.user, id) 
    
    filter = Petition.objects.filter(id=id)
    petition = filter.get()
    
    canEditDescription = request.user.is_superuser or request.user == petition.constituent.user

    context = RequestContext(request, {
        'user': request.user,
        'petition': petition,
        'backURL' : backURL,
        'backName': backName,
        'initialButton': initialButton,
        'nextPetition': nextPetition,
        'showDoneVoting': showDoneVoting,
        'facebookAppID': settings.FACEBOOK_APP_ID, 
        'vote': vote, 
        'canEditDescription': canEditDescription,
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

def member(request):
    response = "You're looking at member %s."
    bioguide_id = request.GET.get('bioguide_id')
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
def getIssueInterests(request):
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
    
# Handles a GET request to get all of the issues for which there is at least 
# the specified minimum interest.
# Returns: JsonResponse with results. 
# Return element success: True if the operation is successful, False otherwise.
# Return element error: Present if there was an error with a text description of the error.
# Return element interests: Present if there was no error. Contains an array of dictionaries
# where each dictionary describes an issue with the following fields: name, id. 
def getIssues(request):
    results = {'success':False}
    if request.method == u'GET':
        GET = request.GET
        try:
            issueList = Issue.get_issues()
            results = {'success':True}
            results['issues'] = issueList
        except Exception as e:
            results = {'success':False, 'error': str(e)}

    return JsonResponse(results)
    
def getSearchResults(request):
    results = {'success':False, 'error': 'getSearchResults failed'}
    try:
        if 'query' not in request.GET:
            raise Exception('the query is not specified')
        query = request.GET['query'];
        results = {'searchResults' : Constituent.get_search_results(request.user, query), 'success':True}
    except Exception as e:
        with open('exception.log', 'a') as log:
            log.write("%s\n" % traceback.format_exc())
            log.flush()
        results = {'success':False, 'error': str(e)}
            
    return JsonResponse(results)

    
    
# Responds to a Json request to get the issues of the currently logged-in user.
# Returns: JsonResponse with results. 
# Return element success: True if the operation is successful, False otherwise.
# Return element myIssues: Present if there was no error. Contains an array of dictionaries
# where each dictionary describes an issue with the following fields: name, id, petition_count. 
# The petition_count is the number of petitions associated with that issue for which the
# currently logged-in user has not voted.
def getMyInterests(request):
    results = {'success':False, 'error': 'getMyInterests failed'}
    try:
        if not request.user.is_authenticated:
            raise Exception("The current login is invalid")
        
        myIssues = Constituent.get_interests(request.user)

        results = {'success':True}
        results['myIssues'] = myIssues
    except Exception as e:
        with open('exception.log', 'a') as log:
            log.write("%s\n" % traceback.format_exc())
            log.flush()
        results = {'success':False, 'error': str(e)}
            
    return JsonResponse(results)
    
def getMyNews(request):
    results = {'success':False}
    try:
        if not request.user.is_authenticated:
            raise Exception("The current login is invalid")
        
        results = {'myNews' : Constituent.get_news(request.user), 'success':True}
    except Exception as e:
        with open('exception.log', 'a') as log:
            log.write("%s\n" % traceback.format_exc())
            log.flush()
        results = {'success':False, 'error': str(e)}
            
    return JsonResponse(results)

def getMyMembers(request):    
    results = {'success':False}
    try:
        if not request.user.is_authenticated:
            raise Exception("The current login is invalid")
        
        results = {'myMembers' : Constituent.get_members(request.user), 'success':True}
    except Exception as e:
        with open('exception.log', 'a') as log:
            log.write("%s\n" % traceback.format_exc())
            log.flush()
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
        petitions = PetitionManager.get_petitions(issue_id, user=request.user);
        for p in petitions:
            p['isEditable'] = (int(p['constituent_id']) == request.user.id or \
                               request.user.is_superuser)
        
        # Return the results.
        results = {'success':True, 'petitions' : petitions}
    except Exception as e:
        with open('exception.log', 'a') as log:
            log.write("%s\n" % traceback.format_exc())
            log.flush()
        results = {'success':False, 'error': str(e)}
    
    return JsonResponse(results)

def getVotingHistory(request):
    results = {'success':False, 'error': 'getIssuePetitions failed'}
    try:
        # Do the model operation
        petitions = Constituent.get_voting_history(user=request.user);
        
        # Return the results.
        results = {'success':True, 'actions' : petitions}
    except Exception as e:
        with open('exception.log', 'a') as log:
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
        petitionIssues = Petition.get_issues(petition_id);
        for i in petitionIssues:
            i['isEditable'] = i['constituent_id'] == request.user.id or \
                              request.user.is_superuser
        
        # Return the results.
        results = {'success':True, 'issues' : petitionIssues}
    except Exception as e:
        log = open('exception.log', 'a')
        log.write("%s\n" % traceback.format_exc())
        log.flush()
        results = {'success':False, 'error': str(e)}
    
    return JsonResponse(results)

# Returns a json response containing the arguments associated with the specified petition. 
def getPetitionArguments(request):
    results = {'success':False, 'error': 'getPetitionArguments failed'}
    try:
        if request.method != "POST":
            raise Exception("getPetitionArguments only responds to POST requests")
            
        if request.user.is_authenticated:
            request_user_id = request.user.id
        else:
            request_user_id = None

        # Get the petition info.
        petition_id = request.POST['petition']

        # Do the model operation
        supportingArguments = ArgumentManager.get_arguments(petition_id, request_user_id, 1)
        opposingArguments = ArgumentManager.get_arguments(petition_id, request_user_id, 0)
        
        for a in supportingArguments:
            a['isEditable'] = (int(a['constituent_id']) == request_user_id or \
                               request.user.is_superuser)
        
        for a in opposingArguments:
            a['isEditable'] = (int(a['constituent_id']) == request_user_id or \
                               request.user.is_superuser)
        
        # Return the results.
        results = {'success':True, 'supportingArguments' : supportingArguments, 'opposingArguments' : opposingArguments}
    except Exception as e:
        log = open('exception.log', 'a')
        log.write("%s\n" % traceback.format_exc())
        log.flush()
        results = {'success':False, 'error': str(e)}
    
    return JsonResponse(results)

def getPetitionVoteTotals(request):
    results = {'success':False, 'error': 'getPetitionVoteTotals failed'}
    try:
        # Get the petition info.
        if request.method == "POST":
            qs = request.POST
        else:
            qs = request.GET
        petition_id = int(qs['petition'])
        voteCounts = Petition.get_vote_totals(petition_id)
        # Return the results.
        results = {'success':True, 'votes':voteCounts}
        
        vote = Constituent.get_vote(request.user, petition_id)
        if (vote != -2):
            results['userVote'] = vote
            
    except Exception as e:
        log = open('exception.log', 'a')
        log.write("%s\n" % traceback.format_exc())
        log.flush()
        results = {'success':False, 'error': str(e)}
    
    return JsonResponse(results)
        
# Returns a json response containing the notes associated with the specified petition. 
def getPetitionNotes(request):
    results = {'success':False, 'error': 'getPetitionNotes failed'}
    try:
        if request.method == "POST":
            petition_id = request.POST['id']
        else:
            petition_id = request.GET['id']
            
        if request.user.is_authenticated:
            request_user_id = request.user.id
        else:
            request_user_id = None

        # Do the model operation
        notes = NoteManager.get_notes(petition_id)
        
        for a in notes:
            constituentID = a['constituent_id']
            a['isEditable'] = (constituentID == request_user_id or \
                               request.user.is_superuser)
            creator = get_user_model().objects.get(pk=constituentID)
            creatorConstituent = Constituent.objects.filter(pk=constituentID).select_related().get()
            a['heading'] = 'From ' + creatorConstituent.user.get_initials() + " in " + creatorConstituent.state + "-" + ("%d" % creatorConstituent.district) 
        
        # Return the results.
        results = {'success':True, 'notes' : notes}
    except Exception as e:
        with open('exception.log', 'a') as log:
            log.write("%s\n" % traceback.format_exc())
            log.flush()
        results = {'success':False, 'error': str(e)}
    
    return JsonResponse(results)

# Returns a json response containing the stories associated with the specified petition. 
def getPetitionStories(request):
    results = {'success':False, 'error': 'getPetitionStories failed'}
    try:
        if request.method == "POST":
            petition_id = request.POST['id']
        else:
            petition_id = request.GET['id']
            
        if request.user.is_authenticated:
            request_user_id = request.user.id
        else:
            request_user_id = None

        # Do the model operation
        stories = StoryManager.get_stories(petition_id)
        
        for a in stories:
            constituentID = a['constituent_id']
            a['isEditable'] = (constituentID == request_user_id or \
                               request.user.is_superuser)
            creator = get_user_model().objects.get(pk=constituentID)
            creatorConstituent = Constituent.objects.filter(pk=constituentID).select_related().get()
            a['heading'] = 'From ' + creatorConstituent.user.get_initials() + " in " + creatorConstituent.state + "-" + ("%d" % creatorConstituent.district) 
        
        # Return the results.
        results = {'success':True, 'stories' : stories}
    except Exception as e:
        with open('exception.log', 'a') as log:
            log.write("%s\n" % traceback.format_exc())
            log.flush()
        results = {'success':False, 'error': str(e)}
    
    return JsonResponse(results)

# Handles a GET request to get the votes based on specific petition.
# Request GET element pk: the primary key of the petition
# Request GET element scope: 'district' for the counts at the district level or 'state' for counts
# at the state level. Default is 'district'.
# Returns: JsonResponse with results. 
# Return element success: True if the operation is successful, False otherwise.
# Return element error: Present if there was an error with a text description of the error.
# Return element interests: Present if there was no error. Contains an array of dictionaries 
# for each scope that contains at least one interested constituent. Each dictionary 
# contains a 'state', a 'district' and a 'support_count' and an 'oppose_count' for district scope; each
# dictionary contains a 'state' and a 'support_count' and an 'oppose_count' for state scope.
def getPetitionVotesByScope(request):
    results = {'success':False, 'error': 'getPetitionVotesByScope failed'}
    try:
        if request.method == u'GET':
            qs = request.GET
        else:
            qs = request.POST
        pk = int(qs['petition'])
        scope = qs.get('scope', 'district')
        if pk != 0:
            try:
                petition = Petition.objects.get(pk=pk)
                try:
                    votes = petition.get_votes(scope=scope)
                    voteList = []
                    if scope == 'district':
                        for i in votes:
                            voteList.append({'state': i[0], 'district': i[1], 'support_count':i[2], 'oppose_count':i[3]})
                    else:
                        for i in votes:
                            voteList.append({'state': i[0], 'support_count':i[1], 'oppose_count':i[2]})
                    results = {'success':True, 'votes':voteList}
                except Exception as ex:
                    results = {'success':False, 'error': str(ex)}
            except Exception as ex:
                results = {'success':False, 'error': 'Petition was not found'}
    except Exception as e:
        results = {'success':False, 'error': str(e)}

    return JsonResponse(results)
    
