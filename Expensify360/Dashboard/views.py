from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from Dashboard.forms import *
from django.contrib import messages
from Dashboard.data_visualization import *
from Expensify360.toolkit import *
from Expenses.models import *


@login_required
def homepage(request):
    context = {'organizations': get_organization_structure(request=request),
               'user_permissions': request.user.get_user_permissions(),
               }
    if is_manager(request.user):
        context['chart'] = get_chart(request)
    return render(request, 'homepage.html', context)


# not a view
def get_chart(request):
    lookback = 300
    resolution = 'M'
    # TODO add buttons to change resolution in template ['Y', 'M', 'W'] and lookback
    vm = VisualizationManager.load(f'{lookback}_{resolution}_{request.user}')
    VisualizationManager.save(vm)
    chart = vm.create_plot()
    return chart


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
    # TODO: delete project / organization option, warn user on delete
    if request.method == 'POST':
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
        
        elif 'remove-user' in request.POST:
            print('yes')
            return redirect(to='remove-user')

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
def remove_user(request):
    if request.method == 'POST' and 'username' in request.POST:
        username = request.POST.get('username')
        group_type, group_name = request.POST.get('selected-action').split('`')
        user = User.objects.get(username=username)
        if group_type == 'organization':
            group = Organization.objects.get(name=group_name)
            user.organization_set.remove(group)
        else:
            group = Project.objects.get(name=group_name)
            if group.second_manager.username == username:
                group.second_manager.user_permissions.set([])
                group.second_manager = request.user
                group.save()
            user.project_set.remove(group)

        group.user_set.remove()
        group.save()
        messages.success(request, f'{username} removed from {group_name} {group_type}.')

    users = []
    organizations = []
    projects = []

    org_struct = get_organization_structure(request.user, include_unassigned_users=False)
    for org in org_struct:
        organizations.append(org.name)
        for project in org.proj_list:
            projects.append(project.name)
            for user in project.users:
                if user != request.user:
                    users.append(user.username)
    context = {
        'users': list(set(users)),
        'orgs': organizations,
        'projects': projects
    }
    return render(request, 'remove_user.html', context)



@login_required
@permission_required('Can add user')
def manage_permissions(request):
    if request.method == 'POST' and 'select' in request.POST:
        # we concat these with backtick in the template
        username, projectname = tuple(request.POST.get('select').split('`'))
        user = User.objects.get(username=username)
        project = Project.objects.get(name=projectname)
        # remove permission from current lead iff they are not a manager
        if project.second_manager != project.manager:
            project.second_manager.user_permissions.set([])
        if not is_manager(user):
            user.user_permissions.set(project_manager_permissions())
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


@login_required
def expense_manager(request):
    if request.method == 'POST' and 'change' in request.POST:
        id, new_status = request.POST.get('change').split('_')
        expense = Expense.objects.get(id=id)
        expense.isApproved = new_status
        expense.save()

    expenses = list(
        get_expense_records(
            request.user,
            filter_function=lambda x: x.isApproved == 'Pending').values()
    )
    context = {
        'expenses': sorted(expenses, key=lambda x: x.expense_date, reverse=True)
    }
    VisualizationManager.update_all(request.user)  # only need to call after an approval has occurred
    return render(request, 'expense_manager.html', context)


def expense_history(request):
    expenses = list(
        get_expense_records(
            request.user,
            filter_function=lambda x: x.isApproved != 'Pending').values()
    )
    context = {
        'expenses': sorted(expenses, key=lambda x: x.expense_date, reverse=True)
    }
    return render(request, 'expense_history.html', context)
