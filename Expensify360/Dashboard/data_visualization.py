import datetime
import glob
import pickle

import plotly.graph_objs as go
import statsmodels.tsa.api as tsa
from numpy import datetime64
from pandas import date_range, read_pickle, DataFrame, concat, Series
from scipy.signal import savgol_filter

from Expensify360.toolkit import *


class VisualizationManager:

    def __init__(self, user, resolution='M', lookback=100000):
        self.resolution = resolution
        self.user = user  # this is a string!
        self.lookback = int(lookback)
        self.name = f'{self.lookback}_{self.resolution}_{self.user}'
        self.fig = None
        self.lag = 12
        self.fSteps = 6
        self._up_to_date = True

    def preprocess(self):
        expenses = list(get_expense_records(User.objects.get(username=self.user),
                                            filter_function=lambda x: x.isApproved == 'Approved').values())
        if len(expenses) == 0: return None
        now = np.datetime64(datetime.datetime.now(), self.resolution)
        earliest_expense = sorted(expenses, key=lambda e: np.datetime64(e.expense_date, self.resolution))[0]
        earliest_date = np.datetime64(earliest_expense.expense_date, self.resolution)
        delta = int((now - earliest_date).astype(f'timedelta64[{self.resolution}]'))
        n_periods = np.min((self.lookback, delta))
        t = date_range(
            end=now + np.timedelta64(1, self.resolution),
            periods=n_periods + 1,
            freq=self.resolution
        )

        t = np.unique(np.array(t).astype(f'datetime64[{self.resolution}]'))
        binned = np.zeros(n_periods + 1)
        # aggregate according to resolution
        for i, ele in enumerate(t):
            for expense in expenses:
                if (  # all this just to compare dates
                        np.datetime_as_string(datetime64(expense.expense_date), unit=self.resolution) ==
                        np.datetime_as_string(datetime64(ele), unit=self.resolution)
                ):
                    binned[i] += expense.amount
        x, y = t, binned
        if x.shape[0] < 1: return None  # caller must check for this!
        try:
            trend = savgol_filter(y, window_length=33, polyorder=5)
            trend[trend < 0] = 0.0
        except ValueError:
            trend = None
        data = DataFrame({'Time': x, 'Expenses': y, 'Trend': trend})
        try:
            if x.shape[0] > 2:
                pred = DataFrame(forecast(data, self.lag, self.fSteps))
                pred.to_pickle(f'{self.name}_forecast')
            else:
                pred = None
        except ValueError:  # this will be thrown for insufficient data
            pred = None
        data.to_pickle(f'{self.name}_data')
        return data, pred

    def create_plot(self):
        data, pred = self.load_data()
        future = Series(pd.date_range(
            start=datetime64(data['Time'].iloc[-1], 'M'),
            end=(datetime64(data['Time'].iloc[-1], 'M') + np.timedelta64(6, 'M')),
            freq='M'
        ))
        if data is None:
            # indicates not enough data, silent fail
            return ''
        self.fig = go.Figure()  # lol go figure
        self.fig.add_trace(go.Bar(x=data['Time'], y=data['Expenses'], name='Expenses'))
        if data['Trend'] is not None:
            self.fig.add_trace(go.Scatter(x=data['Time'], y=data['Trend'], name='Trend'))
        if pred is not None:
            self.fig.add_trace(go.Bar(x=future, y=pred['predicted_mean'], name="Forecast"))
            self.fig.add_trace(go.Scatter(x=future, y=pred['upper Expenses'],
                                          fill=None,
                                          mode='lines',
                                          line_color='indigo',
                                          name='Upper Bound'))
            self.fig.add_trace(go.Scatter(x=future, y=pred['lower Expenses'],
                                          fill='tonexty',
                                          mode='lines', line_color='indigo',
                                          name="Lower Bound"))

            self.fig.update_layout(legend_title_text='Expense History')
            self.fig.update_xaxes(title_text='Time')
            self.fig.update_yaxes(title_text='Dollars')

        return self.fig.to_html()

    def load_data(self):
        try:
            if self.up_to_date:
                data, pred = read_pickle(f'{self.name}_data'), read_pickle(f'{self.name}_forecast')
            else:
                print('processing data...')
                t0 = datetime.datetime.now()
                data, pred = self.preprocess()
                t1 = datetime.datetime.now()
                print(f'done in {np.datetime64(t1) - np.datetime64(t0)}')
                self.up_to_date = True
        except FileNotFoundError:
            data, pred = self.preprocess()
        return data, pred

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


def forecast(data, lag=12, fSteps=6):
    model = tsa.SARIMAX(data['Expenses'], order=(lag, 0, 1), trend='t')

    results = model.fit()

    forecast = results.get_forecast(steps=fSteps)
    confidence_intervals = forecast.conf_int()
    mean_forecast = forecast.predicted_mean
    forecast = concat(
        {
            'forecast': mean_forecast,
            'ci': confidence_intervals},
        axis=1
    )
    pred = forecast['forecast']['predicted_mean'].iloc[-6:].clip(lower=0)
    upper = forecast['ci']['upper Expenses'].iloc[-6:].clip(lower=0)
    lower = forecast['ci']['lower Expenses'].iloc[-6:].clip(lower=0)

    return concat([pred, upper, lower], axis=1)
