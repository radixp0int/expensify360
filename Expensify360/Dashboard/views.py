import re
from contextlib import suppress

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from django.db import IntegrityError
from django.shortcuts import render, redirect
from Dashboard.forms import *
from Dashboard.models import *
from django.contrib import messages
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, HTML
from crispy_forms.bootstrap import FormActions


@login_required
def homepage(request):
    context = {'organizations': []}

    orgs = Organization.objects.filter(manager=request.user).all()
    prjs = Project.objects.filter(manager=request.user).all()

    for g in orgs:
        if g.name == 'Unassigned':
            continue
        i = Org()
        i.name = g.name
        i.proj_list = []
        for proj in prjs:
            if proj.org == g:
                p = Org()
                p.name = proj.name
                p.users = [u for u in Project.objects.get(name=p.name).user_set.all()]
                i.proj_list.append(p)
        context['organizations'].append(i)

        all_users = g.user_set.all()
        assigned = [u for x in i.proj_list for u in x.users]
        unassigned = set(all_users) - set(assigned)
        if len(unassigned) != 0:
            g = Org()
            g.name = 'Unassigned'
            g.users = list(unassigned)
            i.proj_list.append(g)

    return render(request, 'homepage.html', context)


@login_required
def create_org(request):
    if request.method == 'POST':
        form = CreateOrgForm(request.POST)
        if form.is_valid():
            org = Organization.create(
                name=form.cleaned_data['Organization_Name'],
                manager=request.user,
            )
            try:
                org.save()
                request.user.groups.add(org)
                messages.success(request, f'{org} Created')
            except IntegrityError:
                messages.error(request, f'{org} already exists')
    # either way render an empty form
    return render(request, 'create_org.html', {'form': CreateOrgForm()})


@login_required
def create_proj(request):
    if request.method == 'POST':
        form = CreateProjForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['Project_Name']

            # check for reserved char
            if '`' in name:
                messages.error(request, "Backtick ' ` ' Not Allowed in Project Name!")
                return render(request, 'create-proj.html', {'form': form})

            org = Organization.objects.get(name=request.GET.get('org-name'))
            prj = Project.create(
                name=name,
                manager=request.user,
                org=org
            )
            try:
                prj.save()
                request.user.groups.add(prj)
                messages.success(request, f'{prj} Project Created in {org}')
            except IntegrityError:
                messages.error(request, f'{prj} already exists')
    # either way render an empty form
    return render(request, 'create-proj.html', {'form': CreateProjForm()})


@login_required
def manage_users(request):
    # TODO: add remove user from group option
    # TODO add user to project option
    if request.method == 'POST':
        print(request.POST)
        if 'register' in request.POST:
            # then we're registering a user
            form = UserCreationForm(request.POST)
            if form.is_valid():
                user = form.save()
                messages.success(request, f'{user.username} Added')
            else:
                messages.error(request, 'Could Not Add User')
            # either way render an empty form
            return render(request, 'add_user.html', {'add': UserCreationForm(), 'done_or_cancel': SubmitOrCancel()})

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

        elif 'org-name' in request.POST:
            # adding user to group
            form = SelectGroupForm(request.POST)
            if form.is_valid():
                try:
                    user = User.objects.get(username=request.POST.get('username'))
                    org = Organization.objects.get(name=request.POST.get('org-name'))
                    user.groups.add(org)
                    messages.success(request, f'{user.username} Added To {org}')
                except User.DoesNotExist:
                    bad_name = request.POST.get('username')
                    if len(bad_name) == 0:
                        messages.error(request, 'Please Enter a Username')
                    messages.error(request, f"User '{bad_name}' Does Not Exist")
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

        elif 'add-project' in request.POST:
            # take me to project add form
            return render(
                request,
                'add_to_project.html',
                {
                    'orgs': list(Project.objects.filter(manager=request.user)),
                    'user_name': UserNameForm(),
                    'done_or_cancel': SubmitOrCancel(),
                    'select': SelectGroupForm()
                }
            )

        elif 'project-name' in request.POST:
            # add user to project
            form = SelectGroupForm(request)
            if form.is_valid():
                try:
                    user = User.objects.get(username=request.POST.get('username'))
                    org = Project.objects.get(name=request.POST.get('project-name'))
                    user.groups.add(org)
                    messages.success(request, f'{user.username} Added To {org}')
                except User.DoesNotExist:
                    bad_name = request.POST.get('username')
                    if len(bad_name) == 0:
                        messages.error(request, 'Please Enter a Username')
                    messages.error(request, f"User '{bad_name}' Does Not Exist")
                return render(
                    request,
                    'add_to_project.html',
                    {
                        'orgs': list(Project.objects.filter(manager=request.user)),
                        'user_name': UserNameForm(),
                        'done_or_cancel': SubmitOrCancel(),
                        'select': SelectGroupForm()
                    }
                )

        elif 'select_user_permissions' in request.POST:
            return redirect(to='change_user_permissions') #manage_permissions(request)

    # otherwise just render the options
    return render(
        request,
        'user_management.html',
        context={
            'add': ManageUsers(),
            'rem': RemoveUser(),
            'add_to_group': AddToGroup(),
            'add_to_project': AddToProject(),
            'delegate_project': ChangePermissionsButton()
        }
    )


class Org(object):
    # magic class
    pass


def manage_permissions(request):
    #TODO: need prime and second managers now :(
    print('select' in request.POST)
    if request.method == 'POST' and 'select' in request.POST:
        # we concat these with backtick in the template
        username, projectname = tuple(request.POST.get('select').split('`'))
        print(username)
        print(projectname)
        user = User.objects.get(username=username)
        project = Project.objects.get(name=projectname)
        messages.success(request, f'{request.POST} user{user}, proj{project}')
        user.groups.add(project)
        project.manager = user
        project.save()

    user_list = set([])  # no dupes here!
    project_list = Project.objects.filter(manager=request.user).all()
    for project in project_list:
        for user in project.user_set.all():
            user_list.add(user)
    context = {
        'form' : SelectManagerForm(),
        'users': user_list,
        'projects': [
            {'name' : project, 'manager' : project.manager}
            for project in project_list
        ]
    }
    return render(request, 'change_user_permissions.html', context)
