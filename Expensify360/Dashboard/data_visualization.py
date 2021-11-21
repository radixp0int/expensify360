import pickle

from numpy import datetime64
import datetime
import pandas as pd
from Expensify360.toolkit import *
import pandas as pd
import plotly.express as px
from sklearn.svm import SVR


class VisualizationManager:

    def __init__(self, user, resolution='M', lookback=100):
        self.resolution = resolution
        self.user = user
        self.lookback = lookback
        self.name = f'{self.lookback}_{self.resolution}_{self.user}'

    def preprocess(self):
        """
            resolution:char
            'Y'|'M'|'W'|'D'
            default:'M'

            returns: tuple of x:datetime64, y:float
        """
        expenses = get_expenses(self.user)
        if len(expenses) == 0: return np.array([]), np.array([])

        t = pd.date_range(end=datetime.datetime.now(), periods=self.lookback, freq=self.resolution)
        t = np.unique(np.array(t).astype(f'datetime64[{self.resolution}]'))
        binned = np.zeros(self.lookback)
        # aggregate according to resolution
        for i, ele in enumerate(t):
            for expense in expenses:
                if (  # all this just to compare dates TODO: try just casting like in assignment to t
                        np.datetime_as_string(datetime64(expense.expenseDate), unit=self.resolution) ==
                        np.datetime_as_string(datetime64(ele), unit=self.resolution)
                ):
                    # have to check this, 2 will be null
                    if expense.expenseTotal:
                        binned[i] += float(expense.expenseTotal)
                    elif expense.mileageTotal:
                        binned[i] += float(expense.mileageTotal)
                    elif expense.hourTotal:
                        binned[i] += float(expense.hourTotal)
        return t, binned

    def create_plot(self):
        # TODO: check if db table has changed and update if true.
        try:
            data = pd.read_pickle(f'{self.name}_data')
        except FileNotFoundError:
            x, y = self.preprocess()
            svr_rbf = SVR(kernel='rbf', C=100, gamma=0.1, epsilon=0.1)
            X = np.arange(x.shape[0]).reshape(-1, 1)
            data = pd.DataFrame({'Time': x, 'Expenses': y, 'Trend': svr_rbf.fit(X, y).predict(X)})
            data.to_pickle(f'{self.name}_data')
        fig = px.line(data, x='Time', y=['Expenses', 'Trend']).to_html()

        return fig

    @classmethod
    def save(cls, instance):
        # create a pickle file
        f = open(instance.name, 'wb')
        # pickle the dictionary and write it to file
        pickle.dump(instance, f)
        # close the file
        f.close()

    @classmethod
    def load(cls, instance_name):
        # read the pickle file
        f = open(instance_name, 'rb')
        # unpickle the dataframe
        instance = pickle.load(f)
        # close file
        f.close()
        return instance
