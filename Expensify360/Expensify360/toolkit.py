from django.contrib.auth.models import Permission
from models import Organization
from Expenses.models import Expense
from contextlib import suppress


PROJECT_LEAD_PERMISSIONS = (
    'Expenses.add_expense',
    'Expenses.view_expense',
    'Expenses.change_expense',
    'Expenses.delete_expense'
)


class Org(object):
    pass


def expense_total(expense):
    expense_type = expense.expenseType
    if str.upper(expense_type) == 'MILEAGE':
        return expense.mileageTotal
    if str.upper(expense_type) == 'EXPENSE':
        return expense.expenseTotal
    if str.upper(expense_type) == 'HOURS':
        return expense.hourTotal
    return 0.0  # silent failure


def project_manager_permissions():
    return [perm for perm in Permission.objects.filter(PROJECT_LEAD_PERMISSIONS)]


def is_manager(user):
    return Permission.objects.get(codename='Dashboard.add_organization') in user.user_permissions


def is_project_manager(user):
    return set(project_manager_permissions()).intersection(user.user_permissions) != set([])


def get_expenses(user):
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
        args:
            user: manager user object
            filter_function: optional, function that takes
                an expense object and returns a bool. Used to filter
                expenses by a criteria i.e. approval status, requester, etc.

        returns:
            a dict[expense object: data].
            fields are attributes of data objects:
                data.requester:str, username of requester
                data.expense_date:datetime
                data.submission:datetime
                data.project:str, name of project for this expense
                data.status:str, approval status
                data.type:str, in ['Mileage', 'Expense', 'Hours']
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
