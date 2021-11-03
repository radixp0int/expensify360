from django.db import models


class Request(models.Model):
    # General
    userID = models.CharField(max_length=151)
    expenseDate = models.DateField()
    submissionDate = models.DateField(auto_now_add=True)

    # Mileage Specific
    miles = models.DecimalField(max_digits=8, decimal_places=1)
    mileageRate = models.DecimalField(max_digits=5, decimal_places=2)
    mileageTotal = models.DecimalField(max_digits=8, decimal_places=2)

    # Expense Specific
    # TO-DO FIlE UPLOAD HERE
    expenseCost = models.DecimalField(max_digits=8, decimal_places=2)
    tax = models.DecimalField(max_digits=8, decimal_places=2)
    shipping = models.DecimalField(max_digits=8, decimal_places=2)
    expenseTotal = models.DecimalField(max_digits=8, decimal_places=2)

    # Hours Specific
    hours = models.DecimalField(max_digits=6, decimal_places=2)
    hourlyRate = models.DecimalField(max_digits=6, decimal_places=2)
    hourTotal = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return str(self.userID)
