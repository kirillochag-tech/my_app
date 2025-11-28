from django.db import models


class Client(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True, null=True)
    assigned_employee = models.ForeignKey(
        'accounts.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_clients',
        limit_choices_to={'role': 'employee'}
    )
    contact_info = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


class ClientGroup(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    clients = models.ManyToManyField(Client, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name