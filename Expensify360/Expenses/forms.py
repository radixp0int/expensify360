from django import forms
from .models import Request


class GeneralForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ('expenseDate',)


class MileageForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ('miles', 'mileageRate', 'mileageTotal')


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ('expenseCost', 'tax', 'shipping', 'expenseTotal')


class HoursForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ('hours', 'hourlyRate', 'hourTotal')