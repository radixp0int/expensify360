from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from Expensify360.toolkit import make_demo


def demo_creation_hack(request):
    try:
        make_demo()
        print('success.')
    except Exception as e:
        print(e)
    return render(request, 'registration/sign_up.html')


def sign_up(request):
    context = {}
    form = UserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return render(request, 'homepage.html')
    context['form'] = form
    return render(request=request, template_name='registration/sign_up.html', context=context)