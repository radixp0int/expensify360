import pandas as pd
from django.contrib.auth.models import Permission, User
from Dashboard.models import Organization, Project
from Expenses.models import Expense
from contextlib import suppress
import numpy as np
from django.db import IntegrityError
import datetime

PROJECT_LEAD_PERMISSIONS = (
    'add_expense',
    'view_expense',
    'change_expense',
    'delete_expense'
)


def summarize_expense_records(expenses):
    total, pending, count = 0.0, 0.0, 0
    for expense in expenses.values():
        if expense.status == 'Approved':
            total += expense.amount
        elif expense.status == 'Pending':
            pending += expense.amount
            count += 1
    fmt = "${:,.2f}"
    data = {
        'total_expenses': fmt.format(total),
        'total_pending': fmt.format(pending),
        'pending_count': str(count)
    }
    return data


def summary(user):
    all_dict = summarize_expense_records(get_expense_records(user))
    return all_dict


class Org(object):
    """
    magic class. used as dynamic struct
    """
    pass


def expense_total(expense):
    """
    :param: expense: expense object
    :return: expense total for expense passed as arg
    """
    expense_type = expense.expenseType
    if str.upper(expense_type) == 'MILEAGE':
        return float(expense.mileageTotal)
    if str.upper(expense_type) == 'EXPENSE':
        return float(expense.expenseTotal)
    if str.upper(expense_type) == 'TIME' or str.upper(expense_type) == 'HOURS':
        return float(expense.hourTotal)
    return 0.0  # silent failure


def set_expense_total(expense, new_value):
    """
    :param: expense: expense object
    :param: new_value: new expense total for this expense
    :return: None
    """
    expense_type = expense.expenseType
    if str.upper(expense_type) == 'MILEAGE':
        expense.mileageTotal = new_value
    elif str.upper(expense_type) == 'EXPENSE':
        expense.expenseTotal = new_value
    elif str.upper(expense_type) == 'TIME' or str.upper(expense_type) == 'HOURS':
        expense.hourTotal = new_value
    expense.save()


def get_organization_structure(user=None, request=None, include_unassigned_users=True):
    """
    :param user: User, required if request not passed
    :param request: HttpRequest, required if user not passed
    :param include_unassigned_users: default=True, so users not assigned a project
    will be returned in a project named 'Unassigned
    :return: a list of organization proxies. fields are attributes, access like
        ith_organization = get_organization_structure(request=request)[i] |
        ith_organization.name:str |
        ith_organization.proj_list: list of projects proxies in this organization with attributes |
        .proj_list.name:str |
        .proj_list.project_manager:User |
        .proj_list.users:set of User objects assigned to this project.
    :raises ValueError: if neither request nor user is passed
    """
    if not user and not request:
        raise ValueError('user and request may not both be None')
    if request: user = request.user
    organization_list = []
    user_organizations = [organization for organization in user.organization_set.all()]
    user_projects = [project for project in user.project_set.all()]
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
        organization_list.append(proxy_organization)
        if include_unassigned_users:
            all_users = organization.users.all()
            assigned = [u for x in proxy_organization.proj_list for u in x.users]  # reference resolved at runtime
            unassigned = set(all_users) - set(assigned)
            if len(unassigned) != 0:
                unassigned_project = Org()
                unassigned_project.name = 'Unassigned'
                unassigned_project.users = list(unassigned)
                proxy_organization.proj_list.append(unassigned_project)
    return organization_list


def project_manager_permissions():
    """
    :return: list of Permission objects a project manager must have
    """
    perms = []
    for perm in PROJECT_LEAD_PERMISSIONS:
        perms.append(list(Permission.objects.filter(codename=perm))[0])
    return perms


def is_manager(user):
    """
    :param user: User object
    :return: bool, True if user is manager else False
    """
    return Permission.objects.get(codename='add_organization') in user.user_permissions.all()


def is_project_manager(user):
    """
    :param user: User object
    :return: bool, True if user is a project manager or manager else False
    """
    return set(project_manager_permissions()).intersection([perm for perm in user.user_permissions.all()]) != set([])


def get_expenses(user, manager=True):
    """
    :param user: User object
    :param manager: bool, if the user is a manager
    :return: list of Expense objects for which user is responsible
    """

    # expense uses charfields so we need a list of names for projects this user manages
    if manager:
        projects = set(
            list(Project.objects.filter(manager=user).all()) + list(Project.objects.filter(second_manager=user)))
    else:
        projects = list(user.project_set.all())
    project_names = [project.name for project in projects]
    expenses = []
    for name in project_names:
        with suppress(Exception):
            if not manager:
                expenses += Expense.objects.filter(project=name).filter(userID=user.username).all()
            else:
                expenses += Expense.objects.filter(project=name).all()
    return expenses


def get_expense_records(user, filter_function=None, manager=True):
    """
        :param user: User object
        :param filter_function: optional, function that takes
                an expense object and returns a bool. Used to filter
                expenses by a criteria i.e. approval status, requester, etc.
        :param manager: bool, if this user is a manager or project manager

        :return:
            a dict[expense object: data].
            fields are attributes of data objects:
                data.requester:str, username of requester |
                data.expense_date:datetime |
                data.submission:datetime |
                data.project:str, name of project for this expense |
                data.status:str, approval status |
                data.type:str, in ['Mileage', 'Expense', 'Hours'] |
                data.amount:float, expense total
                data.edited: bool
    """
    expenses = get_expenses(user, manager=manager)

    if filter_function: expenses = [e for e in expenses if filter_function(e)]
    records = {
        expense: Org()
        for expense in expenses
    }
    for expense, proxy in records.items():
        proxy.requester = expense.userID  # username
        proxy.expense_date = expense.expenseDate
        proxy.submission_date = expense.submissionDate
        proxy.project = expense.project
        status = expense.isApproved.split('/')
        proxy.status = status[0]
        if len(status) == 2:
            proxy.edited = True
        else:
            proxy.edited = False
        proxy.type = expense.expenseType
        proxy.amount = expense_total(expense)
        proxy.id = expense.id
    return records


def make_test_data(user, num_to_generate=500):
    """
    :param user: User, a manager
    :param num_to_generate:int, optional, default=500
    :return None:
    call me from a view. BUT FIRST
    make sure there is a manager
    and users who are members of
    at least 1 project.
    Also this will no longer
    dump ~num_to_generate / 3 dino
    pics on your device :) but instead
    write a url to an image to expensePhoto
    where applicable.
    all distributions are uniform
    in their respective ranges.
    """
    organizations = get_organization_structure(user)
    base_date = np.datetime64('2001-09-11')
    days_since = 7374  # to nov 18 2021
    type_list = ['Mileage', 'Expense', 'Hours']
    status_choices = ['Approved', 'Pending', 'Denied']
    for i in range(num_to_generate):
        rng = np.random.default_rng()
        proxy_organization = rng.choice(organizations)
        organization = Organization.objects.get(name=proxy_organization.name)
        proxy_project = rng.choice(proxy_organization.proj_list)
        project = Project.objects.get(name=proxy_project.name)
        u = rng.choice(list(proxy_project.users))
        # General
        userID = u.username
        expenseDate = str(base_date + rng.choice(days_since))
        organization = organization
        project = project
        isApproved = rng.choice(status_choices)
        expenseType = rng.choice(type_list)
        if expenseType == type_list[0]:
            # Mileage Specific
            miles = rng.choice(3000) + 10.0  # must be nonzero!
            mileageRate = 0.53
            mileageTotal = miles * mileageRate
            expense = Expense.create(
                userID=userID,
                expenseDate=expenseDate,
                organization=organization,
                project=project,
                isApproved=isApproved,
                expenseType=expenseType,
                miles=miles,
                mileageRate=mileageRate,
                mileageTotal=mileageTotal
            )
        elif expenseType == type_list[1]:
            # Expense Specific
            expensePhoto = 'http://blog.everythingdinosaur.co.uk/wp-content/uploads/2017/12/chris_packham_rex2jpg.jpg'
            expenseCost = rng.choice(10000) + 10.0
            tax = .07
            shipping = rng.choice(1000)
            expenseTotal = (expenseCost + shipping) * tax
            expense = Expense.create(
                userID=userID,
                expenseDate=expenseDate,
                organization=organization,
                project=project,
                isApproved=isApproved,
                expenseType=expenseType,
                expenseCost=expenseCost,
                expensePhoto=expensePhoto,
                tax=tax,
                shipping=shipping,
                expenseTotal=expenseTotal
            )
        else:
            # Hours Specific
            hours = rng.choice(100) + 10.0
            hourlyRate = 40.0
            hourTotal = hours * hourlyRate
            expense = Expense.create(
                userID=userID,
                expenseDate=expenseDate,
                organization=organization,
                project=project,
                isApproved=isApproved,
                expenseType=expenseType,
                hours=hours,
                hourTotal=hourTotal,
                hourlyRate=hourlyRate
            )
        with suppress(IntegrityError):
            # super tiny probability this
            # will generate a dupe expense
            # in that case it just won't
            # be saved
            expense.save()


def embed_seasonality_and_trend():
    expenses = sorted(list(Expense.objects.filter(isApproved='Approved').all()),
                      key=lambda x: np.datetime64(x.expenseDate), reverse=False)
    t = pd.date_range(start=np.datetime64(expenses[0].expenseDate), end=np.datetime64(expenses[-1].expenseDate))
    for i, ele in enumerate(t):
        for expense in expenses:
            if (
                    np.datetime_as_string(np.datetime64(expense.expenseDate), unit='M') ==
                    np.datetime_as_string(np.datetime64(ele), unit='M')
            ):
                set_expense_total(
                    expense, np.sin((i + np.pi / 2) * 1 / np.pi) + 100 * np.sin(
                        i * 6 / np.pi) + i / 5 + 100)


def make_demo():
    """
        runserver and go to /magic to run. Not safe to run
        if any users/projects/organizations already in db.
    """
    accounts = {
        'Thorstein_Veblen': 'tvpassword',
        'John_Kenneth_Galbraith': 'jkgpassword',
        'Joan_Robinson': 'jrpassword',
    }

    organization_name = 'NOFX'
    projects = ['Punk in Drublic', 'So Long and Thanks for All the Shoes']

    for name, pword in accounts.items():
        try:
            User.objects.create_user(username=name, password=pword)
            print(f'user: {name}, password: {pword} created')
        except IntegrityError:
            print(f'user {name} already exists, skipping...')

    boss = User.objects.get(username=list(accounts.keys())[0])
    boss.is_staff = True
    boss.is_admin = True
    boss.is_superuser = True
    boss.user_permissions.set([perm for perm in Permission.objects.all()])
    boss.save()

    organization = Organization.create(
        name=organization_name,
        manager=boss,
    )
    try:
        organization.save()
        print(f'organization {organization_name} created')
    except IntegrityError:
        print(f'Warning: organization {organization_name} already exists.')
    for user in list(accounts.keys()):
        Organization.objects.get(name=organization_name).users.add(User.objects.get(username=user))

    for name in projects:
        project_lead = list(accounts.keys())[1]
        project = Project.create(
            name=name,
            manager=boss,
            second_manager=User.objects.get(username=project_lead),
            org=Organization.objects.get(name=organization_name)
        )
        project.save()
        print(f'project {name} created. Project lead: {project_lead}')
        User.objects.get(username=project_lead).user_permissions.set(project_manager_permissions())
        for user in list(accounts.keys()):
            Project.objects.get(name=name).users.add(User.objects.get(username=user))
            print(f'user {user} added to {name}')
    print('generating expense data...')

    make_test_data(user=boss)
    embed_seasonality_and_trend()
    return
