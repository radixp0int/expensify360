from django.db import models


class Expense(models.Model):
    # General
    userID = models.CharField(max_length=151)
    expenseDate = models.DateField()
    submissionDate = models.DateField(auto_now_add=True)
    organization = models.CharField(max_length=151)
    project = models.CharField(max_length=151)
    isApproved = models.CharField(max_length=50, default="Pending")

    # Mileage Specific
    miles = models.DecimalField(max_digits=8, decimal_places=1, null=True, default=None)
    mileageRate = models.DecimalField(max_digits=5, decimal_places=2, null=True, default=None)
    mileageTotal = models.DecimalField(max_digits=8, decimal_places=2, null=True, default=None)

    # Expense Specific
    expensePhoto = models.FileField(upload_to='ExpenseFiles', null=True, default=None)
    expenseCost = models.DecimalField(max_digits=8, decimal_places=2, null=True, default=None)
    tax = models.DecimalField(max_digits=8, decimal_places=2, null=True, default=None)
    shipping = models.DecimalField(max_digits=8, decimal_places=2, null=True, default=None)
    expenseTotal = models.DecimalField(max_digits=8, decimal_places=2, null=True, default=None)

    # Hours Specific
    hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, default=None)
    hourlyRate = models.DecimalField(max_digits=6, decimal_places=2, null=True, default=None)
    hourTotal = models.DecimalField(max_digits=6, decimal_places=2, null=True, default=None)

    def __str__(self):
        return str(self.userID)
