from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.shortcuts import render
from Dashboard.forms import *


@login_required
def homepage(request):
    context = {}
    groups = list(request.user.groups.values_list('name', flat=True))
    for g in groups:
        context[g] = list(Group.objects.get(id=g).user_set.all())
    return render(request=request, template_name='homepage.html', context=context)


def create_org(request):
    if request.method == 'POST':
        return render(request, 'homepage.html')
    return render(request, 'create_org.html', {'form': CreateOrgForm()})
