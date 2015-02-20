from django.contrib import admin
##from django.contrib.auth.admin import UserAdmin
##from django.contrib.auth.forms import UserCreationForm, UserChangeForm, ReadOnlyPasswordHashField
##from dico.models import AuthUser
##from django import forms

# Register your models here.
from dico.models import Issue, Constituent, MC, Event, ConstituentInterest, MCInterest, EventIssue

    
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

admin.site.register(Issue)
admin.site.register(Constituent, ConstituentAdmin)
admin.site.register(MC, MCAdmin)
admin.site.register(Event, EventAdmin)
