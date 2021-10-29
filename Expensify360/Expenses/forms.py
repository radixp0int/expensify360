from django import forms
from .models import Request


class MileageForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ('expenseDate', 'miles', 'mileageRate', 'mileageTotal')


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ('expenseDate', 'expenseCost', 'tax', 'shipping', 'expenseTotal')


class HoursForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ('expenseDate', 'hours', 'hourlyRate', 'hourTotal')