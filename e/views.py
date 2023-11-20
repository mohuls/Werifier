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
import pandas as pd

from bulkemailverifier import *


# Create your views here.
def e_validator(request):
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')
    if request.method == 'POST':
        # add new elist
        if request.POST.get('list_name') and request.FILES.get('email_list'):
            my_file = request.FILES.get('email_list')

            # create panda csv instance
            pd.options.display.max_rows = 9999
            df = pd.read_csv(request.FILES.get('email_list'))

            name_exists = EList.objects.filter(user=request.user, name=request.POST.get('list_name')).first()
            if name_exists:
                messages.add_message(request, messages.ERROR, 'Duplicate list name detected! Please define a unique list name for your further reference.')
                return redirect('/email/validator/')

            # create a new list using list name and user
            new_list=EList.objects.create(
                user=request.user,
                name=request.POST.get('list_name')
            )

            # iterating the rows
            for index, row in df.iterrows():
                try:
                    email=row['Emails']
                    ELead.objects.create(
                        elist=new_list,
                        email=email,
                        status=0
                    )
                except KeyError:
                    pass

            messages.add_message(request, messages.INFO, 'List successfully updated')
            return redirect('/email/validator/')
        
        # start email validation
        if request.POST.get('validate'):
            has_list = EList.objects.filter(id=request.POST.get('validate'), status=False, user=request.user).first()
            if has_list:
                leads = ELead.objects.filter(elist=has_list)
                leads_count = leads.count()
                
                eapi = EApi.objects.all()
                for i in eapi:
                    x = requests.get(f'https://user.whoisxmlapi.com/user-service/account-balance?apiKey={i.key}')
                    if leads_count < x.json()['data'][0]['credits']:
                        client = Client(i.key)
                        emails = [i.email for i in leads]
                        request_id = client.create_request(emails=emails)
                        RequestID.objects.create(
                            elist=has_list,
                            eapi=i,
                            requestid=request_id
                        )
                        
                        has_list.status = True
                        has_list.save()
                        break

            messages.add_message(request, messages.SUCCESS, "List successfully validated.")
            return redirect('/email/validator/')

        # delete list
        if request.POST.get('deletelist'):
            has_list = EList.objects.filter(id=request.POST.get('deletelist'), user=request.user).first()
            if has_list:
                has_list.delete()
                messages.add_message(request, messages.SUCCESS, "The selected list " + str(has_list.name) + " was deleted successfully!")
                return redirect('/email/validator/')

    lists = EList.objects.filter(user=request.user).order_by('-id')
    context = {
        'lists': lists
    }
    return render(request, 'e/validator.html', context)

@csrf_exempt
def e_exportlist(request):
    if not request.user.is_authenticated:
        raise Http404
    if request.POST.get('list_id'):
            # query db
            has_list = EList.objects.filter(user=request.user, id=request.POST.get('list_id')).first()
            if has_list:
                to_generate=ELead.objects.filter(elist=has_list)
                if to_generate:
                    report_name = (has_list.name) + '_email_report.csv'
                    header = ['Email']
                    response = HttpResponse(
                        content_type='text/csv',
                        headers={'Content-Disposition': f'attachment; filename="{report_name}"'},
                    )
                    writer = csv.writer(response)
                    writer.writerow(header)

                    for lead in to_generate:
                        # status = ''
                        # if lead.status == 'sent' or lead.status == 'delivered' or lead.status == 'read':
                        #     status = 'Valid'
                        # elif lead.status == 'failed':
                        #     status = 'Invalid'
                        # else:
                        #     status = 'Unknown'

                        # priority = ''
                        # if lead.status == 'sent':
                        #     priority = 'Low'
                        # elif lead.status == 'delivered':
                        #     priority = 'High'
                        # elif lead.status == 'read':
                        #     priority = 'Very High'
                        # else:
                        #     priority = 'No priority'

                        data = [str(lead.email)]
                        writer.writerow(data)
                    return response
                else:
                    messages.add_message(request, messages.ERROR, 'There is no enough data to export from this list. Try to delet this list & reupload the list.')
                    return redirect('/email/validator/')
            else:
                messages.add_message(request, messages.ERROR, 'The report of this list is not yet ready! Please validate the list first before downloading.')
                return redirect('/email/validator/')


def e_uploaded(request):
    # redirect no-authenticated user to login page
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')
        
    leads = ELead.objects.filter(elist__user=request.user).order_by('-id')

    context = {
        'leads': leads
    }
    return render(request, 'e/uploaded.html', context)

@csrf_exempt
def e_update(request):
    if request.method == 'POST':
        request_ids = RequestID.objects.filter(processed=False)
        if request_ids:
            for request_id in request_ids:
                client = Client(request_id.eapi.key)
                result = client.get_status(request_ids=[request_id.requestid])
                ready = result['data'][0]['ready']
                if ready:
                    request_id.processed = True
                    request_id.save()
                    completed = client.get_records(request_id=request_id.requestid)
                    if completed['data']:
                        for mail in completed['data']:
                            Result.objects.create(
                                elist=request_id.elist,
                                email=mail['email_address'],
                                format_check=mail['format_check'],
                                smtp_check=mail['smtp_check'],
                                dns_check=mail['dns_check'],
                                free_check=mail['free_check'],
                                disposable_check=mail['disposable_check'],
                                catch_all_check=mail['catch_all_check'],
                                result=mail['result'],
                                error=mail['error'],
                            )
                    return JsonResponse({'status': 200})
        return JsonResponse({'status': 404})
        # completed = client.get_records(request_id=46236)
        # result = client.get_status(request_ids=[46236])
        # id = result['data'][0]['id']
        # date_start = result['data'][0]['date_start']
        # total_emails = result['data'][0]['total_emails']
        # invalid_emails = result['data'][0]['invalid_emails']
        # processed_emails = result['data'][0]['processed_emails']
        # failed_emails = result['data'][0]['failed_emails']
        # ready = result['data'][0]['ready']
    else:
        raise Http404

def e_leads(request):
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')
    
    results = Result.objects.filter(elist__user=request.user).order_by('-id')
    context = {
        'results': results
    }
    return render(request, 'e/leads.html', context)
