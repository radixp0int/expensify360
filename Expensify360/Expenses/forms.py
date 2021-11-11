from django import forms


class mileageEntryForm(forms.Form):
    userID = forms.CharField(label='User ID')
    expenseDate = forms.DateField(label='Expense Date')
    submissionDate = forms.DateField(label='Submission Date')
    organization = forms.CharField(label='Organization')
    project = forms.CharField(label='Project')
    miles = forms.DecimalField(label='Miles Driven')
    mileageRate = forms.DecimalField(label='Rate Per Mile')
    mileageTotal = forms.DecimalField(label='Total Cost')
