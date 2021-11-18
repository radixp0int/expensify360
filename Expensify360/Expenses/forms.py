from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, HTML
from crispy_forms.bootstrap import FormActions



class mileageEntryForm(forms.Form):
    userID = forms.CharField(label='User ID')
    expenseDate = forms.DateField(label='Expense Date')
    organization = forms.CharField(label='Organization')
    project = forms.CharField(label='Project')
    miles = forms.DecimalField(label='Miles Driven',
                               widget=forms.NumberInput(attrs={'onchange': "UpdateExpenseTotal();"}))
    mileageRate = forms.DecimalField(label='Rate Per Mile',
                                     widget=forms.NumberInput(attrs={'onchange': "UpdateExpenseTotal();"}))
    mileageTotal = forms.DecimalField(label='Total Cost',
                                      widget=forms.NumberInput(attrs={'readonly': True}))


class expenseEntryForm(forms.Form):
    userID = forms.CharField(label='User ID')
    expenseDate = forms.DateField(label='Expense Date')
    organization = forms.CharField(label='Organization')
    project = forms.CharField(label='Project')
    file = forms.FileField(label='Receipt Upload')
    expenseCost = forms.DecimalField(label='Item Cost',
                                     widget=forms.NumberInput(attrs={'onchange': "UpdateExpenseTotal();"}))
    tax = forms.DecimalField(label='Tax',
                             widget=forms.NumberInput(attrs={'onchange': "UpdateExpenseTotal();"}))
    shipping = forms.DecimalField(label='Shipping Cost',
                                  widget=forms.NumberInput(attrs={'onchange': "UpdateExpenseTotal();"}))
    expenseTotal = forms.DecimalField(label='Total Cost',
                                      widget=forms.NumberInput(attrs={'readonly': True}))


class timeEntryForm(forms.Form):
    userID = forms.CharField(label='User ID')
    expenseDate = forms.DateField(label='Expense Date')
    organization = forms.CharField(label='Organization')
    project = forms.CharField(label='Project')
    hours = forms.DecimalField(label='Hours Worked',
                               widget=forms.NumberInput(attrs={'onchange': "UpdateExpenseTotal();"}))
    hourlyRate = forms.DecimalField(label='Hourly Rate',
                                    widget=forms.NumberInput(attrs={'onchange': "UpdateExpenseTotal();"}))
    hourTotal = forms.DecimalField(label='Total Cost',
                                   widget=forms.NumberInput(attrs={'readonly': True}))
