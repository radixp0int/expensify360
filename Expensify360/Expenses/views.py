from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponseRedirect
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

            print(userID, expenseDate)
    else:
        form = mileageEntryForm(initial={'userID': current_user,
                                     'expenseDate': today})

    context = {
        'form': form,
    }

    return render(request, 'expense.html', context)
