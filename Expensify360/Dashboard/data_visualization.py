from Expenses.models import *
from Dashboard.models import Organization, Project
from contextlib import suppress
from numpy import datetime64
import numpy as np
import datetime
import pandas as pd


def preprocess(user, resolution='M', lookback=100):
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
            # TODO: once approval logic is done, only get approved expenses here
            expenses += Expense.objects.filter(organization=name).all()
    if len(expenses) == 0:
        # short-circuit and return empty arrs
        print('no expenses for user')  # debug
        return np.array([]), np.array([])

    t = pd.date_range(end=datetime.datetime.now(), periods=lookback, freq=resolution)
    t = np.unique(np.array(t).astype(f'datetime64[{resolution}]'))
    binned = np.zeros(lookback)
    # aggregate according to resolution
    sorted_by_date = sorted(expenses, key=lambda x: datetime64(x.expenseDate))
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
