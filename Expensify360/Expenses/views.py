from django.shortcuts import render
from .forms import *


def expense(request):
    mileageForm = MileageForm(request.POST or None)
    expenseForm = ExpenseForm(request.POST or None)
    hoursForm = HoursForm(request.POST or None)

    context = {
        'mileageForm': mileageForm,
        'expenseForm': expenseForm,
        'hoursForm': hoursForm,
    }
    return render(request, 'expense.html', context)
