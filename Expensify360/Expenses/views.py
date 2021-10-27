from django.shortcuts import render


def expense(request):
    return render(request, 'expense.html')
