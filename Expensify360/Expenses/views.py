from django.shortcuts import render

def mileage(request):
    return render(request, 'mileage.html')
