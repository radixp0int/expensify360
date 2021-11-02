from django.contrib.auth import models
from django.db import models as m


class Organization(models.Group):

    _manager = m.CharField(max_length=30, null=True)

    @classmethod
    def create(cls, name=None, manager=None):
        org = cls(name=name, manager=manager)
        org.name = name
        org.manager = manager
        return org

    @property
    def manager(self):
        return self._manager

    @manager.setter
    def manager(self, username):
        self._manager = username


class Project(models.Group):

    _manager = m.CharField(max_length=30, null=True)
    _org = m.CharField(max_length=30, null=True)
    group_ptr_id = m.OneToOneField(
        auto_created=True,
        on_delete=m.deletion.CASCADE,
        parent_link=True,
        primary_key=True,
        serialize=False,
        to='auth.Group'
    )

    @classmethod
    def create(cls, name=None, manager=None, org_name=None):
        prj = cls(name=name, manager=manager, _org=org_name)
        prj.org = org_name
        prj.name = name
        prj.manager = manager
        return prj

    @property
    def manager(self):
        return self._manager

    @manager.setter
    def manager(self, username):
        self._manager = username

    @property
    def org(self):
        return self._org

    @org.setter
    def org(self, name):
        self._org = name
