from django.contrib.auth.models import Group
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def homepage(request):
    context = {}
    groups = list(request.user.groups.values_list('name', flat=True))
    for g in groups:
        context[g] = list(Group.objects.get(id=g).user_set.all())
    return render(request=request, template_name='homepage.html', context=context)
