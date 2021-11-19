from Expenses.models import *
from Dashboard.models import Organization, Project
from contextlib import suppress
from numpy import datetime64
import numpy as np
import datetime
import pandas as pd

def get_expenses(user):
    # expense uses charfields so we need a list of names for groups this user manages
    organizations = Organization.objects.filter(manager=user).all()
    # TODO: arg for getting expenses by project, or for a project lead
    #projects = Project.objects.filter(manager=user).all()  # might want this?

    group_names = [organization.name for organization in organizations]
    # group_names += [project.name for project in projects]
    expenses = []
    for name in group_names:
        with suppress(Exception):
            # TODO: once approval logic is done, need an arg to select by status
            expenses += Expense.objects.filter(organization=name).all()
    return expenses

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


class Org(object):
    pass


def make_test_data(user):
    organizations = []
    # call me from a view. BUT FIRST
    # make sure there is a manager
    # and users who are members of
    # at least 1 project. Also there is
    # a tiny probability that this will
    # generate a dupe expense, in which
    # case there will be an IntegrityError
    user_organizations = [organization for organization in user.organization_set.all()]
    user_projects = [project for project in user.project_set.all()]
    for organization in user_organizations:
        # these proxies are used to structure data passed to template
        # because we can't access db in template
        proxy_organization = Org()
        proxy_organization.name = organization.name
        proxy_organization.proj_list = []
        for proj in user_projects:
            if proj.org == organization:
                proxy_project = Org()
                proxy_project.name = proj.name
                proxy_project.project_manager = proj.second_manager
                proxy_project.users = set(u for u in Project.objects.get(name=proxy_project.name).users.all())
                proxy_organization.proj_list.append(proxy_project)
        organizations.append(proxy_organization)
    base_date = np.datetime64('2001-09-11')
    days_since = 7374 # to nov 18 2021
    type_list = ['Mileage', 'Expense', 'Hours']
    for i in range(10000):
        rng = np.random.default_rng()
        proxy_organization = rng.choice(organizations)
        organization = Organization.objects.get(name=proxy_organization.name)
        proxy_project = rng.choice(proxy_organization.proj_list)
        project = Project.objects.get(name=proxy_project.name)
        u = rng.choice(list(proxy_project.users))
        # General
        userID = u.username
        expenseDate = str(base_date + rng.choice(days_since))
        organization = organization
        project = project
        isApproved = 'Approved'
        expenseType = rng.choice(type_list)
        if expenseType == type_list[0]:
            # Mileage Specific
            miles = rng.choice(3000) + 10.0 # must be nonzero!
            mileageRate = 0.53
            mileageTotal = miles * mileageRate
            expense = Expense.create(
                userID=userID,
                expenseDate=expenseDate,
                organization=organization,
                project=project,
                isApproved=isApproved,
                expenseType=expenseType,
                miles=miles,
                mileageRate=mileageRate,
                mileageTotal=mileageTotal
            )
        elif expenseType == type_list[1]:
            # Expense Specific
            expensePhoto = 'http://blog.everythingdinosaur.co.uk/wp-content/uploads/2017/12/chris_packham_rex2jpg.jpg'
            expenseCost = rng.choice(10000) + 10.0
            tax = .07
            shipping = rng.choice(1000)
            expenseTotal = (expenseCost + shipping) * tax
            expense = Expense.create(
                userID=userID,
                expenseDate=expenseDate,
                organization=organization,
                project=project,
                isApproved=isApproved,
                expenseType=expenseType,
                expenseCost=expenseCost,
                expensePhoto=expensePhoto,
                tax=tax,
                shipping=shipping,
                expenseTotal=expenseTotal
            )
        else:
            # Hours Specific
            hours = rng.choice(100) + 10.0
            hourlyRate = 40.0
            hourTotal = hours * hourlyRate
            expense = Expense.create(
                userID=userID,
                expenseDate=expenseDate,
                organization=organization,
                project=project,
                isApproved=isApproved,
                expenseType=expenseType,
                hours=hours,
                hourTotal=hourTotal,
                hourlyRate=hourlyRate
            )
        expense.save()


