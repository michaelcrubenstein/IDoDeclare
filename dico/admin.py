from django.contrib import admin
##from django.contrib.auth.admin import UserAdmin
##from django.contrib.auth.forms import UserCreationForm, UserChangeForm, ReadOnlyPasswordHashField
##from dico.models import AuthUser
##from django import forms

# Register your models here.
from dico.models import Issue, Constituent, ConstituentInterest, ContactMethod, \
    Petition, PetitionIssue, PetitionVote, Argument, ArgumentRating, Note, Story, \
    Frequency, Via, Message, Envelope, \
    MC, Event, MCInterest, EventIssue
    
class ArgumentRatingInline(admin.TabularInline):
    model = ArgumentRating
    extra = 1

class ArgumentAdmin(admin.ModelAdmin):
    inlines = [ArgumentRatingInline]

class ArgumentInline(admin.StackedInline):
    model = Argument
    extra = 1
    
class NoteInline(admin.StackedInline):
    model = Note
    extra = 1
    
class StoryInline(admin.StackedInline):
    model = Story
    extra = 1
    
class PetitionAdmin(admin.ModelAdmin):
    inlines = [ArgumentInline, NoteInline, StoryInline]
    
class PetitionIssueInline(admin.StackedInline):
    model = PetitionIssue
    extra = 1

class IssueAdmin(admin.ModelAdmin):
    inlines = [PetitionIssueInline]
    ordering = ('name',)

class ConstituentInterestInline(admin.StackedInline):
    model = ConstituentInterest
    extra = 1

class ConstituentVoteInline(admin.StackedInline):
    model = PetitionVote
    extra = 1

class EnvelopeInline(admin.StackedInline):
    model = Envelope
    extra = 1

class ConstituentAdmin(admin.ModelAdmin):
##    fieldsets = [
##        (None, {'fields': ['firstName', 'lastName', 'email']}),
##        ('Address', {'fields': ['streetAddress', 'zipCode', 'state', 'district']}),
##    ]
##    list_display = ('firstName', 'lastName', 'email', 'streetAddress', 'zipCodeStr', 'state', 'district',)
    inlines = [ConstituentInterestInline, ConstituentVoteInline]

class MCInterestInline(admin.StackedInline):
    model = MCInterest
    extra = 3


class MCAdmin(admin.ModelAdmin):
##    fieldsets = [
##        (None,               {'fields': ['question_text']}),
##        ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
##    ]
    inlines = [MCInterestInline]

class EventIssueInline(admin.StackedInline):
    model = EventIssue
    extra = 3


class EventAdmin(admin.ModelAdmin):
##    fieldsets = [
##        (None,               {'fields': ['question_text']}),
##        ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
##    ]
    inlines = [EventIssueInline]

class MessageAdmin(admin.ModelAdmin):
    inlines = [EnvelopeInline]

admin.site.register(Issue, IssueAdmin)
admin.site.register(Constituent, ConstituentAdmin)
admin.site.register(ContactMethod)
admin.site.register(Petition, PetitionAdmin)
admin.site.register(Argument, ArgumentAdmin)
admin.site.register(MC, MCAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Note)
admin.site.register(Story)
admin.site.register(Frequency)
admin.site.register(Via)
admin.site.register(Message, MessageAdmin)
