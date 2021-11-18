from Expenses.models import *
from Dashboard.models import Organization, Project
from contextlib import suppress
from numpy import datetime64
import numpy as np


def preprocess(user, resolution='M'): # TODO: add a lookback arg
    """
        resolution:char
        'Y'|'M'|'W'|'D'
        default:'M'

        returns: tuple of x:datetime64, y:float
    """
    res = np.timedelta64(1, resolution)
    # expense uses charfields so we need a list of names for groups this user manages
    organizations = Organization.objects.filter(manager=user).all()
    projects = Project.objects.filter(manager=user).all() # might want this?

    group_names = [organization.name for organization in organizations]
    # group_names += [project.name for project in projects]
    expenses = []
    for name in group_names:
        with suppress(Exception):
            expenses += Expense.objects.filter(organization=name).all()
    if len(expenses) == 0:
        # short-circuit and return empty arrs
        print('no expenses for user')  # debug
        return np.array([]), np.array([])
    sorted_by_date = sorted(expenses, key=lambda x: datetime64(x.expenseDate))
    # t = np.arange(
    #   datetime64(sorted_by_date[0].expenseDate), datetime64(sorted_by_date[-1].expenseDate)).astype(f'datetime64[{resolution}]')
    t = np.arange(
        datetime64('1988-07-09'), datetime64(sorted_by_date[-1].expenseDate)).astype(f'datetime64[{resolution}]') # only for debug!!!
    t = np.array(set(t))
    binned = np.zeros(len(t))

    # aggregate according to resolution
    for i, ele in enumerate(t):
        for expense in expenses:
            if (    # all this just to compare dates TODO: try just casting like in assignment to t
                    np.datetime_as_string(datetime64(expense.expenseDate), unit=resolution) ==
                    np.datetime_as_string(datetime64(ele), unit=resolution)
            ):
                # have to check this, 2 will be null
                if expense.expenseTotal:
                    binned[i] += float(expense.expenseTotal)
                elif expense.mileageTotal:
                    binned[i] += float(expense.mileageTotal)
                elif expense.hourTotal:
                    binned[i] += float(expense.hourTotal)
    return t, binned
