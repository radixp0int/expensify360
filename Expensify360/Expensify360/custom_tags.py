from django import template
from Expensify360.toolkit import project_manager_permissions


register = template.Library()


@register.simple_tag(takes_context=True)
def is_project_manager(context):
    """
    template tag for use with django template language.
    Takes no args in practice.

    :return: bool, True if user is a project manager or manager else False
    """
    user = context['user']
    return set(project_manager_permissions()).intersection([perm for perm in user.user_permissions.all()]) != set([])
