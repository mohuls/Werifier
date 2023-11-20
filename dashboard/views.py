from django.shortcuts import render, redirect
from django.db.models import Q
from wa.models import Lead, List

def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')

    leads = Lead.objects.filter(list__user=request.user)
    total = leads.count()
    valid = leads.filter(Q(status='sent') | Q(status='delivered') | Q(status='read')).count()
    low = leads.filter(status='sent').count()
    high = leads.filter(status='delivered').count()
    very_high = leads.filter(status='read').count()
    invalid = leads.filter(status='failed').count()


    context = {
        'total': total,
        'valid': valid,
        'low': low,
        'high': high,
        'very_high': very_high,
        'invalid': invalid,
    }
    return render(request, 'dashboard/dashboard.html', context)