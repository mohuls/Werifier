from django.urls import path
from .views import *
urlpatterns = [
    path('validator/', e_validator, name='e_validator'),
    path('exportlist/', e_exportlist, name='e_xportlist'),
    path('uploaded/', e_uploaded, name='e_uploaded'),
    path('leads/', e_leads, name='e_leads'),
    path('update/', e_update, name='e_update')
]
