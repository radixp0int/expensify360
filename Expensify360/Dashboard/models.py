from django.contrib.auth import models
from django.db import models as m
from django.contrib.contenttypes.models import ContentType


class Organization(models.Group):

    manager = m.ForeignKey(models.User, on_delete=m.CASCADE)

    class Meta:
        permissions = [
            ("can_create", "Can Create Organizations"),
        ]

    @classmethod
    def create(cls, name=None, manager=None):
        org = cls(name=name, manager=manager)
        org.name = name
        org.manager = manager
        return org


class Project(models.Group):

    manager = m.ForeignKey(models.User, on_delete=m.CASCADE)
    second_manager = m.ForeignKey(models.User, related_name='projects_led', on_delete=m.CASCADE)
    org = m.ForeignKey(Organization, on_delete=m.CASCADE)
    group_ptr_id = m.OneToOneField(
        auto_created=True,
        on_delete=m.deletion.CASCADE,
        parent_link=True,
        primary_key=True,
        serialize=False,
        to='auth.Group'
    )

    class Meta:
        permissions = [
            ("can_create", "Can Create Projects"),
            ("can_manage", "Can Manage Users"),
        ]

    @classmethod
    def create(cls, name=None, manager=None, second_manager=None, org=None):
        prj = cls(name=name, manager=manager, second_manager=second_manager, org=org)
        prj.org = org
        prj.name = name
        # if no second_manager arg is given, default to manager
        prj.second_manager = second_manager if second_manager else manager
        prj.manager = manager   # this is expected to be the manager object itself
        return prj
