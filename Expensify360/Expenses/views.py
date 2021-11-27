from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponseRedirect
from Dashboard.data_visualization import VisualizationManager

from .models import *
from .forms import *

import datetime


# @login_required
def expense(request):
    context = {}
    return render(request, 'expense.html', context)


def mileageEntry(request):
    # Grab the current user ID to pre-populate the form
    current_user = request.user

    # Get current date and time and convert it to USA format
    today = datetime.date.today()
    today = today.strftime("%m/%d/%Y")

    if request.method == 'POST':
        form = mileageEntryForm(request.POST)
        if form.is_valid():
            userID = form.cleaned_data['userID']
            expenseDate = form.cleaned_data['expenseDate']
            organization = form.cleaned_data['organization']
            project = form.cleaned_data['project']
            miles = form.cleaned_data['miles']
            mileageRate = form.cleaned_data['mileageRate']
            mileageTotal = form.cleaned_data['mileageTotal']
            expenseType = "Mileage"

            mileageInfo = Expense(userID=userID,
                                  expenseDate=expenseDate,
                                  organization=organization,
                                  project=project,
                                  miles=miles,
                                  mileageRate=mileageRate,
                                  mileageTotal=mileageTotal,
                                  expenseType=expenseType,)
            mileageInfo.save()
            print(userID, expenseDate)
            return HttpResponseRedirect('/expense')
    else:
        # Load a clean copy of the mileage entry form
        form = mileageEntryForm(initial={'userID': current_user,
                                         'expenseDate': today})

        context = {
            'form': form,
        }

        return render(request, 'mileageEntry.html', context)


def expenseEntry(request):
    # Grab the current user ID to pre-populate the form
    current_user = request.user

    # Get current date and time and convert it to USA format
    today = datetime.date.today()
    today = today.strftime("%m/%d/%Y")

    if request.method == 'POST':
        form = expenseEntryForm(request.POST, request.FILES)

        print(form.errors)
        if form.is_valid():
            userID = form.cleaned_data['userID']
            expenseDate = form.cleaned_data['expenseDate']
            organization = form.cleaned_data['organization']
            project = form.cleaned_data['project']
            file = request.FILES['file']
            expenseCost = form.cleaned_data['expenseCost']
            tax = form.cleaned_data['tax']
            shipping = form.cleaned_data['shipping']
            expenseTotal = form.cleaned_data['expenseTotal']
            expenseType = "Expense"

            expenseInfo = Expense(userID=userID,
                                  expenseDate=expenseDate,
                                  organization=organization,
                                  project=project,
                                  expensePhoto=file,
                                  expenseCost=expenseCost,
                                  tax=tax,
                                  shipping=shipping,
                                  expenseTotal=expenseTotal,
                                  expenseType=expenseType,)
            expenseInfo.save()
            return HttpResponseRedirect('/expense')
            # TODO FINISH FILE UPLOAD
    else:
        # Load a clean copy of the expense entry form
        form = expenseEntryForm(initial={'userID': current_user,
                                         'expenseDate': today})

        context = {
            'form': form,
        }

        return render(request, 'expenseEntry.html', context)


def timeEntry(request):
    # Grab the current user ID to pre-populate the form
    current_user = request.user

    # Get current date and time and convert it to USA format
    today = datetime.date.today()
    today = today.strftime("%m/%d/%Y")

    if request.method == 'POST':
        form = timeEntryForm(request.POST)
        if form.is_valid():
            userID = form.cleaned_data['userID']
            expenseDate = form.cleaned_data['expenseDate']
            organization = form.cleaned_data['organization']
            project = form.cleaned_data['project']
            hours = form.cleaned_data['hours']
            hourlyRate = form.cleaned_data['hourlyRate']
            hourTotal = form.cleaned_data['hourTotal']
            expenseType = "Time"

            hourInfo = Expense(userID=userID,
                                  expenseDate=expenseDate,
                                  organization=organization,
                                  project=project,
                                  hours=hours,
                                  hourlyRate=hourlyRate,
                                  hourTotal=hourTotal,
                               expenseType=expenseType,)
            hourInfo.save()
            return HttpResponseRedirect('/expense')
    else:
        # Load a clean copy of the time entry form
        form = timeEntryForm(initial={'userID': current_user,
                                      'expenseDate': today})

    context = {
        'form': form,
    }

    return render(request, 'timeEntry.html', context)


# @login_required
def expense_approval(request):
    context = {}

    VisualizationManager.update_all(request.user)  # update viz datasets AFTER an expense is approved
    return render(request, 'expense_approval.html', context)
