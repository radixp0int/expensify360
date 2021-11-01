from django.contrib.auth import models


class Organization(models.Group):

    # no overriding init in django
    @classmethod
    def create(cls, name=None, manager=None, is_project=False):
        org = cls(manager=manager, is_project=is_project)
        org.name = name
        return org

    @property
    def manager(self):
        return self._manager

    @manager.setter
    def manager(self, username):
        self._manager = username


