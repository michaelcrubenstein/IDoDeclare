import csv
import random
import traceback
from pygeocoder import Geocoder
from sunlight import congress
from dico import models
from dico.models import Constituent, Issue, ConstituentInterest
from custom_user.models import AuthUser

class ConstituentReader:
    streetnames = ["Second", \
        "Third", \
        "First", \
        "Fourth", \
        "Park", \
        "Fifth", \
        "Main", \
        "Sixth", \
        "Oak", \
        "Seventh", \
        "Pine", \
        "Maple", \
        "Cedar", \
        "Eighth", \
        "Elm", \
        "View", \
        "Washington", \
        "Ninth", \
        "Lake", \
        "Hill"]
        
    streettypes =   ["Ave", "St", "Dr", "Lane", "Rd"]
    
    def loaduser(email, password, firstname, lastname):
        isvalidaddress = False
        while not isvalidaddress:
            streetname = random.choice(ConstituentReader.streetnames)
            if streetname == "Main":
                streettype = "St"
            elif streetname in ["First", "Second", "Third", "Fourth", "Fifth", "Sixth", "Seventh", "Eighth", "Ninth"]:
                streettype = random.choice(["Ave", "St"])
            else:
                streettype = random.choice(ConstituentReader.streettypes)
            streetaddress = str(random.randint(10, 1000)) + " " + \
            streetname + " " + streettype
            zipcode = "%05d" % random.randint(1, 99999)
            with open('exception.log', 'a') as log:
                log.write(streetaddress + " " + zipcode + "\n")
                log.flush()
            results = Geocoder.geocode(streetaddress + " " + zipcode)
            isvalidaddress = results.valid_address
            if isvalidaddress:
                coordinates = results[0].coordinates
                districtInfo = congress.locate_districts_by_lat_lon(coordinates[0], coordinates[1])
                if districtInfo is None:
                    isvalidaddress = False
                elif districtInfo[0] is None:
                    isvalidaddress = False
                    
        Constituent.objects.create_constituent("Default User", password, email, firstname, lastname, streetaddress, zipcode, districtInfo[0]["district"], districtInfo[0]["state"])
    
    def loadinterests(minTestUser, maxTextUser, numInterests):
        
        try:
            issues = Issue.objects.all()
            issueList = []
            for issue in issues:
                issueList.append(issue)
                
            with open('exception.log', 'a') as log:
                log.write("TestUser Interest count: %s\n" % (ConstituentInterest.objects.filter(constituent__user__email__startswith='testuser').count()))
                log.write("ConstituentInterest count: %s\n" % (ConstituentInterest.objects.all().count()))
                log.write("numInterests: %s\n" % (numInterests))
                log.flush()

                numCreated = 0
                while numCreated < numInterests:    
                    userindex = random.randint(minTestUser, maxTextUser)
                    email = "testuser%s@idodeclare.org" % userindex
                    user = AuthUser.objects.filter(email=email).get()
                    constituent = Constituent.get_constituent(user)
                    issue = random.choice(issueList)
                    obj, created = ConstituentInterest.objects.get_or_create(constituent=constituent, issue=issue)
                    if created:
                        numCreated += 1
                        log.write("Create interest for %4d: %s (%4d/%4d)\n" % (userindex, issue.name, numCreated, numInterests))
                        log.flush()
                log.write("ConstituentInterest count: %s\n" % (ConstituentInterest.objects.all().count()))
                log.flush()
        except Exception as e:
            with open('exception.log', 'a') as log:
                log.write("%s\n" % traceback.format_exc())
                log.flush()
            
    def loadUsers(minTestUser, maxTestUser):
        try:
            with open('exception.log', 'a') as log:
                for i in range(minTestUser, maxTestUser):
                    email = "testuser%s@idodeclare.org" % i
                    if AuthUser.objects.filter(email=email).count() == 0:
                        password = "testuser%s" % i
                        ConstituentReader.loaduser(email, password, "Test", "User")
                log.write("loaduser(%4d,%4d) complete\n" % (minTestUser, maxTestUser))
                log.flush()
        except Exception as e:
            with open('exception.log', 'a') as log:
                log.write("%s\n" % traceback.format_exc())
                log.flush()
                
