from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponseRedirect
from Dashboard.data_visualization import VisualizationManager

from Dashboard.models import *
from .models import *
from .forms import *

import datetime


@login_required
def expense(request):
    context = {}
    return render(request, 'expense.html', context)

@login_required
def mileageEntry(request):
    # Grab the current user ID to pre-populate the form
    current_user = request.user
    user_projects = [project for project in current_user.project_set.all()]

    # Get current date and time and convert it to USA format
    today = datetime.date.today()
    today = today.strftime("%m/%d/%Y")

    if request.method == 'POST':
        form = mileageEntryForm(request.POST)
        if form.is_valid():
            userID = current_user
            expenseDate = form.cleaned_data['expenseDate']

            project = request.POST.get('project')
            projectObject = Project.objects.get(name__exact=project)
            organization = projectObject.org

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
        form = mileageEntryForm(initial={'expenseDate': today})

        context = {
            'form': form,
            'projects': user_projects,
        }

        return render(request, 'mileageEntry.html', context)

@login_required
def expenseEntry(request):
    # Grab the current user ID to pre-populate the form
    current_user = request.user
    user_projects = [project for project in current_user.project_set.all()]

    # Get current date and time and convert it to USA format
    today = datetime.date.today()
    today = today.strftime("%m/%d/%Y")

    if request.method == 'POST':
        form = expenseEntryForm(request.POST, request.FILES)

        print(form.errors)
        if form.is_valid():
            userID = current_user
            expenseDate = form.cleaned_data['expenseDate']

            project = request.POST.get('project')
            projectObject = Project.objects.get(name__exact=project)
            organization = projectObject.org

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

    else:
        # Load a clean copy of the expense entry form
        form = expenseEntryForm(initial={'expenseDate': today},)

        context = {
            'form': form,
            'projects': user_projects,
        }

        return render(request, 'expenseEntry.html', context)

@login_required
def timeEntry(request):
    # Grab the current user ID to pre-populate the form
    current_user = request.user
    user_projects = [project for project in current_user.project_set.all()]

    # Get current date and time and convert it to USA format
    today = datetime.date.today()
    today = today.strftime("%m/%d/%Y")

    if request.method == 'POST':
        form = timeEntryForm(request.POST)
        if form.is_valid():
            userID = current_user
            expenseDate = form.cleaned_data['expenseDate']

            project = request.POST.get('project')
            projectObject = Project.objects.get(name__exact=project)
            organization = projectObject.org

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
            print(userID, expenseDate)
            return HttpResponseRedirect('/expense')
    else:
        # Load a clean copy of the time entry form
        form = timeEntryForm(initial={'expenseDate': today})

    context = {
        'form': form,
        'projects': user_projects,
    }

    return render(request, 'timeEntry.html', context)


@login_required
def editExpense(request):
    id = request.session.get('ExpenseID')
    expense = Expense.objects.get(id=id)

    if request.method == 'POST':
        form = expenseEditForm(request.POST, request.FILES)

        print(form.errors)
        if form.is_valid():
            # expense.expensePhoto = request.FILES['file']
            expense.tax = form.cleaned_data['tax']
            expense.shipping = form.cleaned_data['shipping']
            expense.expenseTotal = form.cleaned_data['expenseTotal']
            expense.isApproved = "Approved"
            expense.save()
            return HttpResponseRedirect('/expense_manager')

    else:
        form = expenseEditForm(initial={'expenseDate': expense.expenseDate,
                                         'file': expense.expensePhoto,
                                         'expenseCost': expense.expenseCost,
                                         'tax' : expense.tax,
                                         'shipping': expense.shipping,
                                         'expenseTotal': expense.expenseTotal},
                                        )
        context = {
            'form': form,
        }
        return render(request, 'expense_editing.html', context)


@login_required
def expense_approval(request):
    context = {}
    return render(request, 'expense_approval.html', context)