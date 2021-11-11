from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponseRedirect

from .models import *
from .forms import *

import datetime


# @login_required
def expense(request):
    current_user = request.user
    today = datetime.date.today()

    if request.method == 'POST':
        form = mileageEntryForm(request.POST)
        if form.is_valid():
            userID = form.cleaned_data['userID']
            expenseDate = form.cleaned_data['expenseDate']
            submissionDate = form.cleaned_data['submissionDate']
            organization = form.cleaned_data['organization']
            project = form.cleaned_data['project']
            miles = form.cleaned_data['miles']
            mileageRate = form.cleaned_data['mileageRate']
            mileageTotal = form.cleaned_data['mileageTotal']

            mileageInfo = Expense(userID=userID,
                                  expenseDate=expenseDate,
                                  submissionDate=submissionDate,
                                  organization=organization,
                                  project=project,
                                  miles=miles,
                                  mileageRate=mileageRate,
                                  mileageTotal=mileageTotal,)
            mileageInfo.save()
            print(userID, expenseDate)

    form = mileageEntryForm(initial={'userID': current_user,
                                     'expenseDate': today})

    context = {
        'form': form,
    }

    return render(request, 'expense.html', context)
