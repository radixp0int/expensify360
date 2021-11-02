from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from Dashboard.forms import *
from Dashboard.models import *
from django.contrib import messages


@login_required
def homepage(request):
    org_user_dict = {}
    prj_org_dict = {}
    orgs = Organization.objects.filter(_manager=request.user.username)
    prjs = Project.objects.filter(_manager=request.user.username)
    for g in orgs:
        org_user_dict[g.name] = list(Organization.objects.get(id=g.id).user_set.all())
        org_user_dict[g.name].remove(request.user)
    for g in prjs:
        if g.org not in prj_org_dict.keys():
            prj_org_dict[g.org] = [g.name]
        else:
            prj_org_dict[g.org] += [g.name]

    return render(request, 'homepage.html', {'organizations': org_user_dict, 'projects': prj_org_dict})


@login_required
def create_org(request):
    if request.method == 'POST':
        form = CreateOrgForm(request.POST)
        if form.is_valid():
            org = Organization.create(
                name=form.cleaned_data['Organization_Name'],
                manager=request.user.username,
            )
            org.save()
            request.user.groups.add(org)
        return redirect('org_success')
    return render(request, 'create_org.html', {'form': CreateOrgForm()})


@login_required
def create_proj(request):
    if request.method == 'POST':
        form = CreateProjForm(request.POST)
        if form.is_valid():
            org_name = request.GET.get('org-name')
            prj = Project.create(
                name=form.cleaned_data['Project_Name'],
                manager=request.user.username,
                org_name=org_name
            )
            prj.save()
            request.user.groups.add(prj)
        return redirect('proj_success')
    return render(request, 'create-proj.html', {'form': CreateProjForm()})


def org_success(request):
    return render(request, template_name='org_success.html')


def proj_success(request):
    return render(request, template_name='proj_success.html')


def manage_users(request):
    if request.method == 'POST':
        if 'submit' in request.POST:
            form = UserCreationForm(request.POST or None)
            if form.is_valid():
                user = form.save()
                messages.success(request, f'{user.username} Added Successfully')
                return render(request, 'user_management.html', {'add': ManageUsers(), 'rem': RemoveUser()})
        elif 'add-user' in request.POST:
            return render(request, 'add_user.html', {'add': UserCreationForm(), 'submit_or_cancel': MakeUser()})
        elif 'remove-user' in request.POST:
            name = request.POST.get('Username')
            try:
                user = User.objects.get(username=request.POST.get('Username'))
                user.delete()
                messages.success(request, f'{name} Deleted Successfully')
            except User.DoesNotExist:
                messages.error(request, f'{name} Does Not Exist')
                rem = RemoveUser()
                return render(request, 'user_management.html', {'add': ManageUsers(), 'rem': rem})
    rem = RemoveUser()
    return render(request, 'user_management.html', {'add': ManageUsers(), 'rem': rem})
