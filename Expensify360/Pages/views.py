from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login


def sign_up(request):
    context = {}
    form = UserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return render(request, 'homepage.html')
    context['form'] = form
    return render(request=request, template_name='registration/sign_up.html', context=context)
