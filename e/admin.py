from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(EList)
admin.site.register(ELead)
admin.site.register(EApi)
admin.site.register(RequestID)
admin.site.register(Result)