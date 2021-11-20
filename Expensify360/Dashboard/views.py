from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import render, redirect
from Dashboard.forms import *
from Dashboard.models import *
from django.contrib import messages
from Dashboard.data_visualization import preprocess, make_test_data
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from Expensify360.toolkit import *


@login_required
def homepage(request):
    context = {
        'organizations': [],
        'user_permissions': request.user.get_user_permissions()
    }
    user_organizations = [organization for organization in request.user.organization_set.all()]
    user_projects = [project for project in request.user.project_set.all()]
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
                proxy_project.users = set(u for u in Project.objects.get(name=proxy_project.name).users.all())
                proxy_organization.proj_list.append(proxy_project)
        context['organizations'].append(proxy_organization)

        all_users = organization.users.all()
        assigned = [u for x in proxy_organization.proj_list for u in x.users]  # reference resolved at runtime
        unassigned = set(all_users) - set(assigned)
        if len(unassigned) != 0:
            unassigned_project = Org()
            unassigned_project.name = 'Unassigned'
            unassigned_project.users = list(unassigned)
            proxy_organization.proj_list.append(unassigned_project)

    # plots #
    # TODO: check if db table has changed and update if true.
    try:
        data = pd.read_pickle('expense_data')
    except FileNotFoundError:
        x, y = preprocess(request.user)
        data = pd.DataFrame({'Time': x, 'Expenses': y})
        data.to_pickle('expense_data')

    fig = px.scatter(data, x='Time', y='Expenses')
    context['chart'] = fig.to_html()

    # table #
    headerColor = 'grey'
    rowEvenColor = 'lightgrey'
    rowOddColor = 'white'

    table = go.Figure(data=[go.Table(
        header=dict(
            values=['<b>EXPENSES</b>', '<b>Q1</b>', '<b>Q2</b>', '<b>Q3</b>', '<b>Q4</b>'],
            line_color='darkslategray',
            fill_color=headerColor,
            align=['left', 'center'],
            font=dict(color='white', size=12)
        ),
        cells=dict(
            values=[
                ['Salaries', 'Office', 'Merchandise', 'Legal', '<b>TOTAL</b>'],
                [1200000, 20000, 80000, 2000, 12120000],
                [1300000, 20000, 70000, 2000, 130902000],
                [1300000, 20000, 120000, 2000, 131222000],
                [1400000, 20000, 90000, 2000, 14102000]],
            line_color='darkslategray',
            # 2-D list of colors for alternating rows
            fill_color=[[rowOddColor, rowEvenColor, rowOddColor, rowEvenColor, rowOddColor] * 5],
            align=['left', 'center'],
            font=dict(color='darkslategray', size=11)
        ))
    ])
    context['table'] = table.to_html()

    return render(request, 'homepage.html', context)


@login_required
@permission_required('Dashboard.add_organization')
def create_org(request):
    if request.method == 'POST':
        form = CreateOrgForm(request.POST)
        if form.is_valid():
            organization = Organization.create(
                name=form.cleaned_data['Organization_Name'],
                manager=request.user,
            )
            try:
                organization.save()
                organization.users.add(request.user)
                messages.success(request, f'{organization} Created')
            except IntegrityError:
                messages.error(request, f'{organization} already exists')
    # either way render an empty form
    return render(request, 'create_org.html', {'form': CreateOrgForm()})


@login_required
@permission_required('Dashboard.add_project')
def create_proj(request):
    make_test_data(request.user)
    if request.method == 'POST':
        form = CreateProjForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['Project_Name']

            # check for reserved char
            if '`' in name:
                messages.error(request, "Backtick ' ` ' Not Allowed in Project Name!")
                return render(request, 'create-proj.html', {'form': form})

            organization = Organization.objects.get(name=request.GET.get('org-name'))
            project = Project.create(
                name=name,
                manager=request.user,
                second_manager=request.user,
                org=organization,
            )
            try:
                project.save()
                project.users.add(request.user)
                messages.success(request, f'{project} Project Created in {organization}')
            except IntegrityError:
                messages.error(request, f'{project} already exists')
    # either way render an empty form
    return render(request, 'create-proj.html', {'form': CreateProjForm()})


@login_required
@permission_required('auth.add_user')
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
            # take me to organization add form
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
            # adding user to organization
            form = SelectGroupForm(request.POST)
            if form.is_valid():
                try:
                    user = User.objects.get(username=request.POST.get('username'))
                    organization = Organization.objects.get(name=request.POST.get('org-name'))
                    user.organization_set.add(organization)
                    organization.users.add(user)

                    messages.success(request, f'{user.username} Added To {organization}')
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
                    project = Project.objects.get(name=request.POST.get('project-name'))
                    project.users.add(user)
                    messages.success(request, f'{user.username} Added To {project}')
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


@login_required
@permission_required('Can add user')
def manage_permissions(request):
    # TODO: permissions need to revert when non-manager project leads are removed
    # TODO: project leads need expense permissions
    if request.method == 'POST' and 'select' in request.POST:
        # we concat these with backtick in the template
        username, projectname = tuple(request.POST.get('select').split('`'))
        user = User.objects.get(username=username)
        project = Project.objects.get(name=projectname)
        # remove permission from current lead iff they are not a manager
        if project.second_manager != project.manager:
            project.second_manager.user_permissions = []
        user.user_permissions.add(project_manager_permissions())
        project.second_manager = user
        project.users.add(user)
        project.save()
        messages.success(request, f'User {user} Assigned as Project Manager for {project}')

    user_list = set()  # no dupes here!
    project_list = set(
        list(request.user.projects_led.all()) + list(request.user.projects_managed.all())
    )
    for project in project_list:
        for user in project.users.all():
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


class Org(object):
    # magic class
    pass
