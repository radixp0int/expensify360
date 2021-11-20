from numpy import datetime64
import numpy as np
import datetime
import pandas as pd
from Expensify360.toolkit import *


def preprocess(user, resolution='M', lookback=100):
    """
        resolution:char
        'Y'|'M'|'W'|'D'
        default:'M'

        returns: tuple of x:datetime64, y:float
    """
    expenses = get_expenses(user)
    if len(expenses) == 0: return np.array([]), np.array([])

    t = pd.date_range(end=datetime.datetime.now(), periods=lookback, freq=resolution)
    t = np.unique(np.array(t).astype(f'datetime64[{resolution}]'))
    binned = np.zeros(lookback)
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
