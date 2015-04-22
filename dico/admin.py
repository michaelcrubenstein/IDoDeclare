from django.contrib import admin
##from django.contrib.auth.admin import UserAdmin
##from django.contrib.auth.forms import UserCreationForm, UserChangeForm, ReadOnlyPasswordHashField
##from dico.models import AuthUser
##from django import forms

# Register your models here.
from dico.models import Issue, Constituent, ConstituentInterest, ContactMethod, \
    Petition, PetitionIssue, Argument, ArgumentRating, \
    MC, Event, MCInterest, EventIssue
    
class ArgumentRatingInline(admin.TabularInline):
    model = ArgumentRating
    extra = 1

class ArgumentAdmin(admin.ModelAdmin):
    inlines = [ArgumentRatingInline]

class ArgumentInline(admin.StackedInline):
    model = Argument
    extra = 1
    
class PetitionAdmin(admin.ModelAdmin):
    inlines = [ArgumentInline]
    
class PetitionIssueInline(admin.StackedInline):
    model = PetitionIssue
    extra = 1

class IssueAdmin(admin.ModelAdmin):
    inlines = [PetitionIssueInline]
    ordering = ('name',)

class ConstituentInterestInline(admin.StackedInline):
    model = ConstituentInterest
    extra = 3

class ConstituentAdmin(admin.ModelAdmin):
##    fieldsets = [
##        (None, {'fields': ['firstName', 'lastName', 'email']}),
##        ('Address', {'fields': ['streetAddress', 'zipCode', 'state', 'district']}),
##    ]
##    list_display = ('firstName', 'lastName', 'email', 'streetAddress', 'zipCodeStr', 'state', 'district',)
    inlines = [ConstituentInterestInline]

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

admin.site.register(Issue, IssueAdmin)
admin.site.register(Constituent, ConstituentAdmin)
admin.site.register(ContactMethod)
admin.site.register(Petition, PetitionAdmin)
admin.site.register(Argument, ArgumentAdmin)
admin.site.register(MC, MCAdmin)
admin.site.register(Event, EventAdmin)
