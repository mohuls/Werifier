import csv
import requests
from importlib.metadata import requires
from django.shortcuts import render, redirect
from django.http import JsonResponse, Http404, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .models import *
from account import models as AccountModel
import datetime
import phonenumbers
from phonenumbers import geocoder, carrier

import pandas as pd


from twilio.rest import Client

# twilio api callback view
@csrf_exempt
def validation_status(request, id):
    if request.method == 'POST':
        number = request.POST.get('To')[9:]
        lead = Lead.objects.filter(list__user__id=id, number=number).first()
        
        status = request.POST.get('MessageStatus')
        if lead:
            lead.status = status
            lead.updated_at = datetime.datetime.now()
            lead.save()
            print("Here")
            if status == 'sent' or status == 'delivered' or status == 'read':
                has_api = AccountModel.WerifierApi.objects.filter(id=id).first()
                if has_api.key and has_api.webhook:
                    url = has_api.webhook
                    data = {
                        'api_key': has_api.key,
                        'list': lead.list.name,
                        'name': lead.name,
                        'number': number,
                        'country': lead.country,
                        'priority': status,
                    }
                    print("There")
                    x = requests.post(url, data=data)
                    return HttpResponse(status=200)
            else:
                return HttpResponse(status=200)
    else:
        raise Http404

def listing(request):
    # redirect no-authenticated user to logi page
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')
    
    # context initializer
    list_uploaded = False

    if request.method == 'POST':
        # add new list
        # upload csv file
        if request.POST.get('list_name') and request.FILES.get('number_list'):
            my_file = request.FILES.get('number_list')
            
            # if my_file.content_type == 'text/csv':
            #     pass
            # else:
            #     messages.add_message(request, messages.ERROR, "You are trying to upload an invalid file format.")
            #     return redirect('/whatsapp/validator/')
            
            # create panda csv instance
            pd.options.display.max_rows = 9999
            df = pd.read_csv(request.FILES.get('number_list'))
            
            name_exists = List.objects.filter(user=request.user, name=request.POST.get('list_name')).first()
            if name_exists:
                messages.add_message(request, messages.ERROR, 'Duplicate list name detected! Please define a unique list name for your further reference.')
                return redirect('/whatsapp/validator/')

            # create a new list using list name and user
            new_list=List.objects.create(
                user=request.user,
                name=request.POST.get('list_name')
            )

            # fail & success flag
            number_exists = 0
            fail_flag = 0
            success_flag = 0
            invalid_phone = 0

            # iterating the rows
            for index, row in df.iterrows():
                try:
                    name=row['Name']
                    number=row['Contacts']
                    if str(number)[0] == '+':
                        number = str(number)
                    else:
                        number = '+' + str(number)
                    try:
                        phoneNumber = phonenumbers.parse(number)
                        is_valid = phonenumbers.is_valid_number(phoneNumber)
                        if is_valid:
                            country = geocoder.description_for_number(phoneNumber, 'en')
                            
                            exists = Lead.objects.filter(number=number).first()
                            if exists:
                                number_exists = number_exists + 1
                            else:
                                Lead.objects.create(
                                    list=new_list,
                                    number=number,
                                    name=name,
                                    country=country,
                                    status='uninitialized'
                                )
                                success_flag=success_flag+1
                        else:
                            invalid_phone = invalid_phone+1
                    except phonenumbers.NumberParseException:
                        invalid_phone = invalid_phone+1
                except KeyError:
                    fail_flag=fail_flag+1

            messages.add_message(request, messages.INFO, 'List successfully updated.' + str(success_flag) + ' numbers was uploaded, ' + str(number_exists) + ' numbers skipped, ' + str(invalid_phone) + ' numbers are Invalid and ' +  str(fail_flag) + ' numbers are failed to upload.')
            return redirect('/whatsapp/validator/')
        
        # delete list
        if request.POST.get('deletelist'):
            has_list = List.objects.filter(id=request.POST.get('deletelist'), user=request.user).first()
            if has_list:
                has_list.delete()
                messages.add_message(request, messages.SUCCESS, "The selected list " + str(has_list.name) + " was deleted successfully!")
                return redirect('/whatsapp/validator/')

        # start number validation
        if request.POST.get('validate'):
            has_list = List.objects.filter(id=request.POST.get('validate'), user=request.user).first()
            if has_list:
                leads = Lead.objects.filter(list=has_list, status='uninitialized')
                client = Client('ACed6a47fd8358b72d497646378e243b26', '334cecd1d8bdf7693e9f2fed64fd943f')
                if leads:
                    body = "Expand your business with MultiBank Group and build your client network while benefitting from our IB and affiliate program!"
                    for lead in leads:
                        reply=client.messages.create(
                            from_='whatsapp:+447476552263',
                            body=body,
                            status_callback='https://werifier.com/whatsapp/validation-status/'+str(request.user.id)+'/',
                            to='whatsapp:'+(lead.number),
                            media_url=['https://hirecraft.ae/clients/multibank/mb-ib.mp4'],
                        )
                has_list.status = True
                has_list.save()
            messages.add_message(request, messages.SUCCESS, "Successfully validated.")
            return redirect('/whatsapp/validator/')
        
    lists = List.objects.filter(user=request.user).order_by('-id')
    context = {
        'lists': lists
    }
    return render(request, 'wa/list.html', context)

@csrf_exempt
def exportlist(request):
    if not request.user.is_authenticated:
        raise Http404
    if request.POST.get('list_id'):
            # query db
            has_list = List.objects.filter(user=request.user, id=request.POST.get('list_id'), status=True).first()
            if has_list:
                to_generate=Lead.objects.filter(list=has_list)
                if to_generate:
                    report_name = (has_list.name) + '_report.csv'
                    header = ['Country', 'Number', 'Status', 'Priority']
                    response = HttpResponse(
                        content_type='text/csv',
                        headers={'Content-Disposition': f'attachment; filename="{report_name}"'},
                    )
                    writer = csv.writer(response)
                    writer.writerow(header)

                    for lead in to_generate:
                        status = ''
                        if lead.status == 'sent' or lead.status == 'delivered' or lead.status == 'read':
                            status = 'Valid'
                        elif lead.status == 'failed':
                            status = 'Invalid'
                        else:
                            status = 'Unknown'

                        priority = ''
                        if lead.status == 'sent':
                            priority = 'Low'
                        elif lead.status == 'delivered':
                            priority = 'High'
                        elif lead.status == 'read':
                            priority = 'Very High'
                        else:
                            priority = 'No priority'

                        data = [str(lead.country), str(lead.number), status, priority]
                        writer.writerow(data)
                    return response
                else:
                    messages.add_message(request, messages.ERROR, 'There is no enough data to export from this list. Try to delet this list & reupload the list.')
                    return redirect('/whatsapp/validator/')
            else:
                messages.add_message(request, messages.ERROR, 'The report of this list is not yet ready! Please validate the list first before downloading.')
                return redirect('/whatsapp/validator/')

def leads(request):
    # redirect no-authenticated user to logi page
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')
        
    leads = Lead.objects.filter(list__user=request.user).order_by('-id')

    context = {
        'leads': leads
    }
    return render(request, 'wa/leads.html', context)

