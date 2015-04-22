from django.db import connection, models, transaction
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser, PermissionsMixin)
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.conf import settings

from sunlight import congress

# Create your models here.
_max_name_length = 50

class Issue(models.Model):
    name = models.CharField(max_length=50, unique=True, db_index=True)

    def __str__(self):
        return self.name
        
    # Returns a list of arrays containing the state, district and constituent_count
    # for this issue.
    # Scope can be by district or by name.
    def get_interests(self, scope='district'):
        with connection.cursor() as c:
            if scope == 'district':
                sql = "SELECT state, district, COUNT(*) as constituent_count" + \
                      " FROM dico_issue, dico_constituentinterest, dico_constituent" + \
                      " WHERE dico_issue.name = %s" + \
                      " AND   dico_issue.id = dico_constituentinterest.issue_id" + \
                      " AND   dico_constituentinterest.constituent_id = dico_constituent.user_id" + \
                      " GROUP BY state, district" + \
                      " ORDER BY state, district";
            else:
                sql = "SELECT state, COUNT(*) as constituent_count" + \
                      " FROM dico_issue, dico_constituentinterest, dico_constituent" + \
                      " WHERE dico_issue.name = %s" + \
                      " AND   dico_issue.id = dico_constituentinterest.issue_id" + \
                      " AND   dico_constituentinterest.constituent_id = dico_constituent.user_id" + \
                      " GROUP BY state" + \
                      " ORDER BY state"
            c.execute(sql, [self.name])
            return c.fetchall()
            
    def get_issues():
        with connection.cursor() as c:
            sql = "SELECT name, id FROM " + \
                  " dico_issue" + \
                  " ORDER BY name"
            c.execute(sql)
            active_issues = []
            for i in c.fetchall():
                active_issues.append({'name': i[0], 'id': i[1]})
            return active_issues
    
class ConstituentManager(models.Manager):
    def create_constituent(self, username, password, email, firstname, lastname, streetaddress, zipcode, district, state):
        if email is None:
            raise ValueException('email is not specified')
            
        if firstname is None:
            raise ValueException('firstname is not specified')
            
        if lastname is None:
            raise ValueException('lastname is not specified')
            
        manager = get_user_model().objects
        user = manager.create_user(username=username, password=password, email=email)
        user.first_name = firstname
        user.last_name = lastname
        user.save(using=manager._db)
        
        try:
            constituent = self.create(user=user, streetAddress=streetaddress, zipCode=zipcode,
                                      district=district, state=state)
            
            return constituent
        except Exception as e:
            try:
                manager.delete(user)
            except Exception:
                pass
            raise e
            
class ContactMethod(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, primary_key=True);
    frequency = models.PositiveSmallIntegerField(db_index=True, default=0) # 0 - never, 1 - daily, 2 - weekly
    via = models.PositiveSmallIntegerField(db_index=True, null=True) # 1 - email, 2 - sms, 3 - app
    phonenumber = models.CharField(max_length=25, null=True)
    
    def get_contact_method(user):
        if user is None or not user.is_active:
            return None
            
        query_set = ContactMethod.objects.filter(user_id=user.id)
        if query_set.count() == 0:
            return ContactMethod.objects.create(user=user, frequency=1, via=2)
        else:
            return query_set.get()
    
    # Update the properties of this constituent.    
    def update_fields(self, newFrequency, newVia, newPhoneNumber):
        
        if newFrequency is None:
            newFrequency = self.frequency
        if newVia is None:
            newVia = self.via
        if newPhoneNumber is None or len(newPhoneNumber) == 0:
            newPhoneNumber = self.phonenumber
        
        ContactMethod.objects.filter(user_id=self.user.id) \
            .update(frequency=newFrequency, via=newVia, phonenumber=newPhoneNumber)

    def __str__(self):
        return str(self.user)

class Constituent(models.Model):
    fiveCharacterValidator = RegexValidator(r'^.....$', message='Zip codes are five digits only.')
    zipcodeValidator = RegexValidator(r'^[0-9][0-9][0-9][0-9][0-9]$', message='Zip codes are five digits only.')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, primary_key=True);
    
    ### Our own class fields ###
    streetAddress = models.CharField(max_length=100, db_column='street_address')
    zipCode = models.CharField(max_length=5, db_column='zip_code', validators=[fiveCharacterValidator, zipcodeValidator])
    district = models.IntegerField(db_index=True)
    state = models.CharField(max_length=2, db_index=True)
    
    objects = ConstituentManager()
    def __str__(self):
        return str(self.user)
    
    def get_constituent(user):
        if user is None or not user.is_active:
            return None
            
        query_set = Constituent.objects.filter(user_id=user.id)
        if query_set.count() == 0:
            return None
        else:    
            return query_set.get()
        
    def get_interests(user):
        constituent = Constituent.get_constituent(user)
        if constituent is None:
            return []
            
        with connection.cursor() as c:
            sql = "SELECT i.id, i.name, " + \
                  " (SELECT COUNT(*) FROM dico_petitionissue pi " + \
                  "  WHERE pi.issue_id = i.id" + \
                  "  AND NOT EXISTS(SELECT * FROM dico_petitionvote pv" + \
                                  " WHERE pv.petition_id = pi.petition_id" + \
                                  " AND pv.constituent_id = %s)) " + \
                  " FROM dico_issue i, dico_constituentinterest ci" + \
                  " WHERE ci.constituent_id = %s" + \
                  " AND ci.issue_id = i.id" + \
                  " ORDER BY i.name"
            c.execute(sql, [user.id, user.id])
            interests = []
            for i in c.fetchall():
                interests.append({'id': i[0], 'name': i[1], 'petition_count': i[2]})
            return interests

    # First, get a list of all of the petitions that the current user hasn't voted on,
    # Ordered in descending order by creation date.
    def get_news(user):
        constituent = Constituent.get_constituent(user)
        if constituent is None:
            return []
            
        with connection.cursor() as c:
            sql = "SELECT p.id, p.description, p.creation_time" + \
                  " FROM dico_petition p" + \
                  " WHERE EXISTS(SELECT * FROM dico_constituentinterest ci, dico_petitionissue pi" + \
                                  " WHERE ci.issue_id = pi.issue_id" + \
                                  " AND pi.petition_id = p.id" + \
                                  " AND ci.constituent_id = %s)" + \
                  " AND NOT EXISTS(SELECT * FROM dico_petitionvote pv WHERE pv.petition_id = p.id AND pv.constituent_id = %s)" + \
                  " ORDER BY p.creation_time DESC"
            c.execute(sql, [user.id, user.id])
            petitions = []
            for i in c.fetchall():
                petitions.append({'section': 'petition', 'id': i[0], 'description': i[1], 'creation_time': i[2]})
            return petitions

    def get_members(user):
        constituent = Constituent.get_constituent(user)
        if constituent is None:
            return []
            
        state = constituent.state
        district = constituent.district
        
        try:
            senators = congress.legislators(state=state, chamber='senate')
            reps = congress.legislators(state=state, district=district)
            if senators is None:
                senators=[]
            if reps is None:
                reps=[]
        # Catch URLError if the system is not online.
        except Exception:
            senators = [];
            reps = [];
            
        return senators + reps
        
    # Update the properties of this constituent.    
    def update_fields(self, newUsername, newPassword, newFirstName, newLastName, newStreetAddress, newZipCode, newState, newDistrict):
         
        with transaction.atomic():
            manager = get_user_model().objects    
            manager.update_user(self.user, newUsername, newPassword, newFirstName, newLastName)
            
            if len(newStreetAddress) == 0:
                newStreetAddress = self.streetAddress
            if len(newZipCode) == 0:
                newZipCode = self.zipCode
            if len(newState) == 0:
                newState = self.state
            if newDistrict < 0:
                newDistrict = self.district
            
            Constituent.objects.filter(user_id=self.user.id) \
                .update(streetAddress=newStreetAddress, zipCode=newZipCode, state=newState, district=newDistrict)
        
    # Add an interest to the named issue for the specified user.
    # If the user is already interested, return that interest.    
    def add_interest(user, name):
        constituent = Constituent.get_constituent(user)
        if constituent is None:
            return None
        
        interest = ConstituentInterest.get_interest(constituent, name)
        if interest is None:
            interest = ConstituentInterest.create_interest(constituent, name)
        return interest
            
    # Remove an interest to the named issue for the specified user.
    # If the user is not interested, return an exception.    
    def delete_interest(user, name):
        constituent = Constituent.get_constituent(user)
        if constituent is None:
            return None
        
        interest = ConstituentInterest.get_interest(constituent, name)
        if interest is None:
            raise ValueError("the specified user is not currently interested in the issue '%s'" % name);
        
        ConstituentInterest.delete_interest(constituent, name)
            
class PetitionManager(models.Manager):
    def create_petition(self, constituent, description):
        petition = self.create(constituent=constituent, description=description)
        return petition
    
    def get_petitions(issue_id, user=None):
        with connection.cursor() as c:
            petitions = []
            if (user == None):
                sql = "SELECT dico_petition.id, description, dico_petition.constituent_id, creation_time FROM " + \
                      " dico_petition, dico_petitionissue" + \
                      " WHERE dico_petitionissue.issue_id = %s" + \
                      " AND dico_petition.id = dico_petitionissue.petition_id" + \
                      " ORDER BY creation_time DESC"
                c.execute(sql, [issue_id])
                for i in c.fetchall():
                    petitions.append({'id': i[0], 'description': i[1], 'constituent_id': i[2], 'creation_time': i[3]})
            else:
                sql = "SELECT p.id, p.description, p.constituent_id, p.creation_time, pv.vote" + \
                      " FROM dico_petitionissue pi, dico_petition p" + \
                      "      LEFT JOIN dico_petitionvote pv ON (pv.petition_id = p.id AND pv.constituent_id = %s)" + \
                      " WHERE pi.issue_id = %s" + \
                      " AND p.id = pi.petition_id" + \
                      " ORDER BY p.creation_time DESC"
                c.execute(sql, [user.id, issue_id])
                for i in c.fetchall():
                    petitions.append({'id': i[0], 'description': i[1], 'constituent_id': i[2], 'creation_time': i[3], 'vote': i[4]})

            return petitions

class Petition(models.Model):
    description = models.TextField()
    constituent = models.ForeignKey(Constituent, db_index=True, db_column='constituent_id')
    creationTime = models.DateTimeField(db_column='creation_time', db_index=True, auto_now_add=True)
    issues = models.ManyToManyField(Issue, through='PetitionIssue');
    
    objects = PetitionManager()
    
    def add_issue(self, issue, constituent):
        pi = PetitionIssue(petition=self, issue=issue, constituent=constituent)
        pi.save()

    def get_votes(petition_id):
        with connection.cursor() as c:
            sql = "SELECT vote, COUNT(*) as vote_count" + \
                  " FROM dico_petitionvote" + \
                  " WHERE dico_petitionvote.petition_id = %s" + \
                  " GROUP BY vote" + \
                  " ORDER BY vote";
            c.execute(sql, [petition_id]);
            countList = []
            for vc in c.fetchall():
                countList.append({'vote': vc[0], 'count': vc[1]})
            return countList
    
    # Gets an array of dictionaries that have the id, name and the constituent_id of
    # the user who connected the issue to the specified petition.
    def get_issues(petition_id):
        with connection.cursor() as c:
            sql = "SELECT dico_issue.id, dico_issue.name, dico_petitionissue.constituent_id" + \
                  " FROM dico_issue, dico_petitionissue" + \
                  " WHERE dico_petitionissue.petition_id = %s" + \
                  " AND dico_issue.id = dico_petitionissue.issue_id" + \
                  " ORDER BY dico_issue.name";
            c.execute(sql, [petition_id]);
            countList = []
            for vc in c.fetchall():
                countList.append({'id': vc[0], 'name': vc[1], 'constituent_id' : vc[2]})
            return countList
    
    def __str__(self):
        return self.description

class PetitionIssue(models.Model):
    petition = models.ForeignKey(Petition, db_index=True, db_column='petition_id')
    issue = models.ForeignKey(Issue, db_index=True, db_column='issue_id')
    constituent = models.ForeignKey(Constituent, db_index=True, db_column='constituent_id')
    
    def delete_petition_issue(petition_id, issue_id):
        query_set = PetitionIssue.objects.filter(petition_id=petition_id). \
            filter(issue_id=issue_id)
        query_set.delete()
            
    def __str__(self):
        return self.issue.name + ": " + self.petition.description

class PetitionVote(models.Model):
    petition = models.ForeignKey(Petition, db_index=True, db_column='petition_id')
    constituent = models.ForeignKey(Constituent, db_index=True, db_column='constituent_id')
    vote = models.IntegerField(db_index=True)
    creationTime = models.DateTimeField(db_column='creation_time', db_index=True, auto_now_add=True)
    lastModifiedTime = models.DateTimeField(db_column='last_modified_time', db_index=True, auto_now=True)
    
    def __str__(self):
        return self.constituent.user.email + "/" + self.petition.description + ": " + str(self.vote)

class ArgumentManager(models.Manager):
    def get_arguments(petition_id, rating_constituent_id, vote):
        with connection.cursor() as c:
            sql = "SELECT a.id, a.description, a.constituent_id, a.creation_time, ar.vote " + \
                  " FROM dico_argument a" + \
                  " LEFT JOIN dico_argumentrating ar" + \
                  " ON a.id = ar.argument_id AND ar.constituent_id = %s" + \
                  " WHERE a.petition_id = %s" + \
                  " AND a.vote = %s" + \
                  " ORDER BY a.creation_time DESC"
            c.execute(sql, [rating_constituent_id, petition_id, vote])
            arguments = []
            for i in c.fetchall():
                arguments.append({'id': i[0], 'description': i[1], 'constituent_id': i[2], \
                                  'creation_time': i[3], 'rating_vote': i[4]})
            return arguments
    
class Argument(models.Model):
    petition = models.ForeignKey(Petition, db_index=True, db_column='petition_id')
    constituent = models.ForeignKey(Constituent, db_index=True, db_column='constituent_id')
    description = models.TextField()
    vote = models.IntegerField(db_index=True)
    creationTime = models.DateTimeField(db_column='creation_time', db_index=True, auto_now_add=True)
    
    objects = ArgumentManager()
    
    def __str__(self):
        return self.description

class ArgumentRating(models.Model):
    argument = models.ForeignKey(Argument, db_index=True, db_column='argument_id')
    constituent = models.ForeignKey(Constituent, db_index=True, db_column='constituent_id')
    vote = models.IntegerField(db_index=True)
    creationTime = models.DateTimeField(db_column='creation_time', db_index=True, auto_now_add=True)
    lastModifiedTime = models.DateTimeField(db_column='last_modified_time', db_index=True, auto_now=True)

    def __str__(self):
        return str(self.constituent) + ": " + str(self.vote)

class MC(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, primary_key=True, db_column='user_id');
    
    ### Our own class fields ###
    district = models.IntegerField(null=True, db_index=True)
    state = models.CharField(max_length=2, db_index=True)

    def __str__(self):
        return str(self.user)
    
class Event(models.Model):
    description = models.TextField()
    link = models.URLField()
    eventTime = models.DateTimeField(db_column='event_time', db_index=True)
    mc = models.ForeignKey(MC, db_index=True, db_column='mc_id')
    
    def __str__(self):
        return self.description

class ConstituentInterest(models.Model):
    constituent = models.ForeignKey(Constituent, db_index=True, db_column='constituent_id')
    issue = models.ForeignKey(Issue, db_index=True, db_column='issue_id')
    
    def get_interest(constituent, name):
        query_set = ConstituentInterest.objects.filter(constituent_id=constituent.pk). \
            filter(issue__name=name)
        if query_set.count() > 0:
            return query_set.get()
        else:
            return None
            
    def create_interest(constituent, name):
        query_set = Issue.objects.filter(name=name)
        if query_set.count() == 0:
            issue = Issue.objects.create(name=name)
        else:
            issue = query_set.get()
        return ConstituentInterest.objects.create(constituent=constituent, issue=issue)

    def delete_interest(constituent, name):
        query_set = ConstituentInterest.objects.filter(constituent_id=constituent.pk). \
            filter(issue__name=name)
        query_set.delete()
            
    def __str__(self):
        return str(self.constituent) + ': ' + str(self.issue)

class MCInterest(models.Model):
    mc = models.ForeignKey(MC, db_index=True, db_column='mc_id');
    issue = models.ForeignKey(Issue, db_index=True, db_column='issue_id');
    entryTime = models.DateTimeField(db_column='entry_time', db_index=True)

    def __str__(self):
        return str(self.mc) + ': ' + str(self.issue)

class EventIssue(models.Model):
    event = models.ForeignKey(Event, db_index=True, db_column='event_id');
    issue = models.ForeignKey(Issue, db_index=True, db_column='issue_id');

    def __str__(self):
        return str(self.event) + ': ' + str(self.issue)


