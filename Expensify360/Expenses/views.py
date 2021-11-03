from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .forms import *


# @login_required
def expense(request):
    generalForm = GeneralForm(request.POST or None)
    mileageForm = MileageForm(request.POST or None)
    expenseForm = ExpenseForm(request.POST or None)
    hoursForm = HoursForm(request.POST or None)

    context = {
        'generalForm': generalForm,
        'mileageForm': mileageForm,
        'expenseForm': expenseForm,
        'hoursForm': hoursForm,
    }
    return render(request, 'expense.html', context)
