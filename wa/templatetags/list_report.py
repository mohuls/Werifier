from django import template
register = template.Library()

from wa.models import *

@register.filter
def total(list):
    tl = Lead.objects.filter(list=list).count()
    return tl

@register.filter
def uninitialized(list):
    un = Lead.objects.filter(list=list, status='uninitialized').count()
    return un

@register.filter
def read(list):
    rd = Lead.objects.filter(list=list, status='read').count()
    return rd

@register.filter
def delivered(list):
    dv = Lead.objects.filter(list=list, status='delivered').count()
    return dv

@register.filter
def failed(list):
    fl = Lead.objects.filter(list=list, status='failed').count()
    return fl
    
@register.filter
def valid(list):
    d = Lead.objects.filter(list=list, status='delivered').count()
    r = Lead.objects.filter(list=list, status='read').count()
    return d+r