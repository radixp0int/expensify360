import re

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
    orgs = Organization.objects.filter(manager=request.user)
    prjs = Project.objects.filter(manager=request.user)
    for g in orgs:
        org_user_dict[g.name] = list(Organization.objects.get(name=g.name).user_set.all())
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
                manager=request.user,
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
            org = Organization.objects.get(name=request.GET.get('org-name'))
            prj = Project.create(
                name=form.cleaned_data['Project_Name'],
                manager=request.user,
                org=org
            )
            prj.save()
            request.user.groups.add(prj)
        return redirect('proj_success')
    return render(request, 'create-proj.html', {'form': CreateProjForm()})


def org_success(request):
    return render(request, template_name='org_success.html')


def proj_success(request):
    return render(request, template_name='proj_success.html')


@login_required
def manage_users(request):
    if request.method == 'POST':

        if 'register' in request.POST:
            # then we're registering a user
            form = UserCreationForm(request.POST)
            if form.is_valid():
                user = form.save()
                messages.success(request, f'{user.username} Added Successfully')
                return redirect(to='user_success')
            else:
                messages.error(request, 'Could Not Add User')
                return render(request, 'add_user.html',
                              {'add': UserCreationForm(), 'done_or_cancel': SubmitOrCancel()})

        elif 'add-user' in request.POST:
            # we want the registration form
            return render(request, 'add_user.html', {'add': UserCreationForm(), 'done_or_cancel': SubmitOrCancel()})

        elif 'remove-user' in request.POST:
            name = request.POST.get('Username')
            try:
                user = User.objects.get(username=request.POST.get('Username'))
                user.delete()
                messages.success(request, f'{name} Deleted Successfully')
                return render(
                    request,
                    'user_management.html',
                    {'add': ManageUsers(), 'rem': RemoveUser(), 'add_to_group': AddToGroup()}
                )
            except User.DoesNotExist:
                messages.error(request, f'{name} Does Not Exist')

        elif 'add-group' in request.POST:
            # take me to group add form
            return render(
                request,
                'add_to_group.html',
                {
                    'orgs': list(Organization.objects.filter(manager=request.user)),
                    'user_name': UserNameForm(),
                    'done_or_cancel': SubmitOrCancel(),
                    'select': SelectGroupForm()
                }
            )

        else:
            form = SelectGroupForm(request.POST)
            if form.is_valid():
                u = User.objects.get(username=request.POST.get('username'))
                org = Organization.objects.get(name=request.POST.get('org-name'))
                u.groups.add(org)
                messages.success(request, f'{u.username} Added To {org}')
                return render(
                    request,
                    'add_to_group.html',
                    {
                        'orgs': list(Organization.objects.filter(manager=request.user)),
                        'user_name': UserNameForm(),
                        'done_or_cancel': SubmitOrCancel(),
                        'select': SelectGroupForm()
                    }
                )
    # otherwise just render the options
    return render(
        request,
        'user_management.html',
        {'add': ManageUsers(), 'rem': RemoveUser(), 'add_to_group': AddToGroup()}
    )


def user_success(request):
    return render(request, template_name='user_success.html')

