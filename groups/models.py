from django.db import models
from accounts.models import User


class EmployeeGroup(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    employees = models.ManyToManyField(User, related_name='employee_groups')

    def __str__(self):
        return self.name
