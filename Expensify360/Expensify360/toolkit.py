from django.contrib.auth.models import Permission

PROJECT_LEAD_PERMISSIONS = (
    'Expenses.add_expense',
    'Expenses.view_expense',
    'Expenses.change_expense',
    'Expenses.delete_expense')


def project_manager_permissions():
    return [perm for perm in Permission.objects.filter(PROJECT_LEAD_PERMISSIONS)]


def is_manager(user, organization=None, project=None):
    return Permission.objects.get(codename='Dashboard.add_organization') in user.user_permissions


def is_project_manager(user, project=None):
    return set(project_manager_permissions()).intersection(user.user_permissions) != set([])
