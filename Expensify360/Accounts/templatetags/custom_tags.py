from django import template
from django.utils.safestring import mark_safe

from Expensify360.toolkit import project_manager_permissions


register = template.Library()


@register.filter
def is_project_manager(user):
    """
    template tag for use with django template language.
    Takes no args in practice.

    :return: bool, True if user is a project manager or manager else False
    """
    return set(project_manager_permissions()).intersection([perm for perm in user.user_permissions.all()]) != set([])
