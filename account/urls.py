from django.urls import path
from .views import *

urlpatterns = [
    path('', accounts),
    path('login/', log_in, name='login'),
    path('signup/', signup, name='signup'),
    path('forget/', forget, name='forget'),


    path('settings/', setting, name='settings'),


    path('werifier-api/', werifier_api, name='werifier_api'),

    path('logout/', log_out, name='logout'),
]
