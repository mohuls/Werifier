from django.urls import path
from .views import *

urlpatterns = [
    path('validator/', listing, name='list'), # list is now validator vusially
    path('exportlist/', exportlist, name='exportlist'),
    path('leads/', leads, name='leads'),
    path('validation-status/<int:id>/', validation_status, name='validation_status')
]
