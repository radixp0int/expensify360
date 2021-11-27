import pickle
from numpy import datetime64
import datetime
from Expensify360.toolkit import *
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from sklearn.svm import SVR
import glob


class VisualizationManager:

    def __init__(self, user, resolution='M', lookback=100):
        self.resolution = resolution
        self.user = user    # this is a string!
        self.lookback = int(lookback)
        self.name = f'{self.lookback}_{self.resolution}_{self.user}'
        self.fig = None
        self._up_to_date = True

    # TODO add a summary method
    def summary(self):
        # expenses [up/down] x% since last [period] and [increasing/decreasing] x1%/[period]
        pass

    def preprocess(self):
        """
            resolution:char
            'Y'|'M'|'W'|'D'
            default:'M'

            returns: tuple of x:datetime64, y:float
        """
        expenses = get_expenses(User.objects.get(username=self.user))
        if len(expenses) == 0: return np.array([]), np.array([])

        t = pd.date_range(
            end=np.datetime64(datetime.datetime.now(), self.resolution) + np.timedelta64(1, self.resolution),
            periods=self.lookback,
            freq=self.resolution
        )
        t = np.unique(np.array(t).astype(f'datetime64[{self.resolution}]'))
        binned = np.zeros(self.lookback)
        # aggregate according to resolution
        for i, ele in enumerate(t):
            for expense in expenses:
                if (  # all this just to compare dates TODO: try just casting like in assignment to t
                        np.datetime_as_string(datetime64(expense.expenseDate), unit=self.resolution) ==
                        np.datetime_as_string(datetime64(ele), unit=self.resolution)
                ):
                    binned[i] += expense_total(expense)
        x, y = t, binned
        if x.shape[0] < 1: return ''
        svr_rbf = SVR(kernel='rbf', degree=7, C=np.mean(y), gamma=0.1, epsilon=0.1)
        X = np.arange(x.shape[0]).reshape(-1, 1)
        data = pd.DataFrame({'Time': x, 'Expenses': y, 'Trend': svr_rbf.fit(X, y).predict(X)})
        data.to_pickle(f'{self.name}_data')
        return data

    def create_plot(self):
        data = self.load_data()
        # TODO change this chart
        # TODO check for at least x timesteps
        # TODO include forecast plot
        self.fig = px.line(data, x='Time', y=['Expenses', 'Trend']).to_html()
        return self.fig

    def load_data(self):
        try:
            if self.up_to_date:
                data = pd.read_pickle(f'{self.name}_data')
            else:
                print('processing data...')
                t0 = datetime.datetime.now()
                data = self.preprocess()
                t1 = datetime.datetime.now()
                print(f'done in {np.datetime64(t1) - np.datetime64(t0)}')
                self.up_to_date = True
        except FileNotFoundError:
            data = self.preprocess()
        return data

    @property
    def up_to_date(self):
        return self._up_to_date

    @up_to_date.setter
    def up_to_date(self, new_value):
        if type(new_value) == bool:
            self._up_to_date = new_value
            VisualizationManager.save(self)
        else:
            raise ValueError('up_to_date cannot be assigned to non-bool.')

    @classmethod
    def save(cls, instance):
        f = open(instance.name, 'wb')
        pickle.dump(instance, f)
        f.close()

    @classmethod
    def load(cls, instance_name):
        try:
            f = open(instance_name, 'rb')
            instance = pickle.load(f)
            f.close()
        except FileNotFoundError:
            # instantiate a new model if it doesn't exist
            print(f'{instance_name} not found, creating...')
            lookback, resolution, user = instance_name.split('_', 2)
            instance = cls(user, resolution=resolution, lookback=lookback)  # up to user to save instance!
        return instance

    @classmethod
    def load_all(cls, user):
        instances = []
        instance_files = glob.glob(f'*_{user.username}')
        for i in instance_files:
            instances.append(cls.load(i))
        return instances

    @classmethod
    def update_all(cls, user):
        instances = cls.load_all(user)
        for instance in instances:
            instance.up_to_date = False
