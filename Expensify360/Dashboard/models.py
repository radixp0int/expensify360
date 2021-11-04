from django.contrib.auth import models
from django.db import models as m


class Organization(models.Group):

    manager = m.ForeignKey(models.User, on_delete=m.CASCADE)

    @classmethod
    def create(cls, name=None, manager=None):
        org = cls(name=name, manager=manager)
        org.name = name
        org.manager = manager
        return org


class Project(models.Group):

    manager = m.ForeignKey(models.User, on_delete=m.CASCADE)
    org = m.ForeignKey(Organization, on_delete=m.CASCADE)
    group_ptr_id = m.OneToOneField(
        auto_created=True,
        on_delete=m.deletion.CASCADE,
        parent_link=True,
        primary_key=True,
        serialize=False,
        to='auth.Group'
    )

    @classmethod
    def create(cls, name=None, manager=None, org=None):
        prj = cls(name=name, manager=manager, org=org)
        prj.org = org
        prj.name = name
        prj.manager = manager   # this is expected to be the manager object itself
        return prj
