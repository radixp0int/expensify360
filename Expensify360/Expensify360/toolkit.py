from django.contrib.auth.models import Permission
from Dashboard.models import Organization, Project
from Expenses.models import Expense
from contextlib import suppress


PROJECT_LEAD_PERMISSIONS = (
    'add_expense',
    'view_expense',
    'change_expense',
    'delete_expense'
)


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
        return expense.mileageTotal
    if str.upper(expense_type) == 'EXPENSE':
        return expense.expenseTotal
    if str.upper(expense_type) == 'HOURS':
        return expense.hourTotal
    return 0.0  # silent failure


def get_organization_structure(request, include_unassigned_users=True):
    """
    :param request: HttpRequest
    :param include_unassigned_users: default=True, so users not assigned a project
    will be returned in a project named 'Unassigned
    :return: a list of organization proxies. fields are attributes, access like
        ith_organization = get_organization_structure(request)[i] |
        ith_organization.name:str |
        ith_organization.proj_list: list of projects proxies in this organization with attributes |
        .proj_list.name:str |
        .proj_list.project_manager:User |
        .proj_list.users:set of User objects assigned to this project
    """
    organization_list = []
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
    :return: bool, True if user is a project manager else False
    """
    return set(project_manager_permissions()).intersection(user.user_permissions) != set([])


def get_expenses(user):
    """
    :param user: User object, a manager
    :return: list of Expense objects for which user is responsible
    """
    # expense uses charfields so we need a list of names for groups this user manages
    organizations = Organization.objects.filter(manager=user).all()

    group_names = [organization.name for organization in organizations]
    # group_names += [project.name for project in projects]
    expenses = []
    for name in group_names:
        with suppress(Exception):
            # TODO: once approval logic is done, need an arg to select by status
            expenses += Expense.objects.filter(organization=name).all()
    return expenses


def get_expense_records(user, filter_function=None):
    """
            :param user: manager user object
            :param filter_function: optional, function that takes
                an expense object and returns a bool. Used to filter
                expenses by a criteria i.e. approval status, requester, etc.

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
    """
    expenses = get_expenses(user)
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
        proxy.status = expense.isApproved
        proxy.type = expense.expenseType
        proxy.amount = expense_total(expense)
    return records
