from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import render, redirect
from Dashboard.forms import *
from Dashboard.models import *
from django.contrib import messages


@login_required
def homepage(request):
    print(request.user.get_user_permissions())
    # get the set of all organizations and projects managed by this user.
    context = {
        'organizations': [],
        'user_permissions': request.user.get_user_permissions()
    }

    user_organizations = Organization.objects.filter(manager=request.user).all()
    # all projects where user is manager or second_manager
    user_projects = set(
        Project.objects.filter(manager=request.user).all()
    ).union(
        set(Project.objects.filter(second_manager__username=request.user.username))
    )

    for organization in user_organizations:
        # these proxies are used to structure data passed to template
        # because we can't access db in template
        proxy_organization = Org()
        proxy_organization.name = organization.name
        proxy_organization.proj_list = []
        for proj in user_projects:
            if proj.org == organization:
                proxy_project = Org()
                proxy_project.name = proj.name
                proxy_project.project_manager = proj.second_manager
                proxy_project.users = set(u for u in Project.objects.get(name=proxy_project.name).user_set.all())
                proxy_organization.proj_list.append(proxy_project)
        context['organizations'].append(proxy_organization)

        all_users = organization.user_set.all()
        assigned = [u for x in proxy_organization.proj_list for u in x.users]  # reference resolved at runtime
        unassigned = set(all_users) - set(assigned)
        if len(unassigned) != 0:
            unassigned_project = Org()
            unassigned_project.name = 'Unassigned'
            unassigned_project.users = list(unassigned)
            proxy_organization.proj_list.append(unassigned_project)

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
    # TODO: delete project / organization option, warn user on delete
    # TODO: refactor delete user (should have its own page and add warning)
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
            return redirect(to='change_user_permissions')

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


@login_required
def manage_permissions(request):
    if request.method == 'POST' and 'select' in request.POST:
        # we concat these with backtick in the template
        username, projectname = tuple(request.POST.get('select').split('`'))
        user = User.objects.get(username=username)
        project = Project.objects.get(name=projectname)
        messages.success(request, f'User {user} Assigned as Project Manager for {project}')
        user.groups.add(project)
        project.second_manager = user
        project.save()

    user_list = set()  # no dupes here!
    project_list = Project.objects.filter(manager=request.user).all()
    for project in project_list:
        for user in project.user_set.all():
            user_list.add(user)
    context = {
        'form': SelectManagerForm(),
        'users': user_list,
        'projects': [
            {'name': project, 'manager': project.second_manager}
            for project in project_list
        ]
    }
    return render(request, 'change_user_permissions.html', context)
