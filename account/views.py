import json
import random
import string
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from .serializers import UserSeriaizer
from django.contrib import messages
from .models import *

def log_in(request):
    if request.user.is_authenticated:
        return redirect('/')

    logout = False
    if request.method == 'GET':
        if request.GET.get('log_out_by_user') == '1':
            logout = True

    if request.method == 'POST':
        body = json.loads(request.body)
        username = body['username']
        password = body['password']
        user=User.objects.filter(username=username).first()
        if user:
            auth_user = authenticate(request, username=username, password=password)
            if auth_user is not None:
                login(request, auth_user)
                return JsonResponse({'status': 200}, status=200)
            else:
                return JsonResponse({'status': 404}, status=404)
        else:
            return JsonResponse({'status': 404}, status=404)
    
    context = {
        'logout': logout
    }

    return render(request, 'account/login.html', context)


def signup(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            first_name = body['first_name']
            last_name = body['last_name']
            username = body['username']
            email = body['email']
            password = body['password']
        except ValueError:
            pass
        
        has_already = User.objects.filter(username=str(username)).first()
        if has_already:
            return JsonResponse({'status': 409}, status=409)
        else:
            new_user = User.objects.create_user(username, email, password)
            new_user.first_name = first_name
            new_user.last_name = last_name
            new_user.save()
            login(request, new_user)
            return JsonResponse({'status': 201}, status=201)

    return render(request, 'account/signup.html')

def forget(request):
    return render(request, 'account/forget.html')

def accounts(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        pass
    return render(request, 'account/accounts.html')


def setting(request):
    if not request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        address = request.POST.get('address')
        city = request.POST.get('city')
        country = request.POST.get('country')
        postal_code = request.POST.get('postal_code')
        state = request.POST.get('state')
        bio = request.POST.get('bio')
        profile_picture = request.FILES.get('profile_picture')

        if email and first_name and last_name and address and city and country and postal_code and state and bio:
            email_exists=User.objects.filter(email=email).exclude(username=request.user.username).first()
            if not email_exists:
                request.user.email = email
                request.user.first_name = first_name
                request.user.last_name = last_name
                request.user.profile.address = address
                request.user.profile.city = city
                request.user.profile.country = country
                request.user.profile.postal_code = postal_code
                request.user.profile.state = state
                request.user.profile.bio = bio
                request.user.profile.dp = profile_picture if profile_picture else request.user.profile.dp
                request.user.save()
                messages.add_message(request, messages.SUCCESS, 'Profile successfully updated.')
                return redirect('/accounts/settings/')
            else:
                messages.add_message(request, messages.ERROR, 'The email you are trying to set is already exists.')
                return redirect('/accounts/settings/')
        else:
            messages.add_message(request, messages.ERROR, 'All the fields are required.')
            return redirect('/accounts/settings/')

    context = {
        
    }
    return render(request, 'account/setting.html', context)

# Werifier API
def werifier_api(request):
    # redirect no-authenticated user to logi page
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')

    if request.method == 'POST':
        # set api key
        if request.POST.get('regenarate'):
            def random_string_generator(str_size, allowed_chars):
                return ''.join(random.choice(allowed_chars) for x in range(str_size))
            chars = string.ascii_letters
            size = 20
            randomstr=str(request.user.id)+(random_string_generator(size, chars))

            has_already = WerifierApi.objects.filter(user=request.user).first()
            if has_already:
                has_already.key = randomstr
                has_already.save()
                messages.add_message(request, messages.SUCCESS, "API key has been set successfully!")
                return redirect('/accounts/werifier-api/')
            else:
                WerifierApi.objects.create(
                    user=request.user,
                    api = randomstr
                )
                messages.add_message(request, messages.SUCCESS, "API key has been set successfully!")
                return redirect('/accounts/werifier-api/')

        # set webhook url
        if request.POST.get('webhook_url'):
            has_already = WerifierApi.objects.filter(user=request.user).first()
            if has_already:
                has_already.webhook = request.POST.get('webhook_url')
                has_already.save()
                messages.add_message(request, messages.SUCCESS, "Wehook url has been set successfully!")
                return redirect('/accounts/werifier-api/')
            else:
                WerifierApi.objects.create(
                    user=request.user,
                    webhook = request.POST.get('webhook_url')
                )
                messages.add_message(request, messages.SUCCESS, "Wehook url has been set successfully!")
                return redirect('/accounts/werifier-api/')
    
    api=WerifierApi.objects.filter(user=request.user).first()
    context = {
        'api': api
    }
    return render(request, 'account/werifier-api.html', context)


def log_out(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('/accounts/login/?log_out_by_user=1')
    else:
        return redirect('/accounts/login/')