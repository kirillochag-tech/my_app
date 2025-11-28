from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('super_moderator', 'Супер модератор'),
        ('moderator', 'Модератор'),
        ('employee', 'Сотрудник'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class EmployeeGroup(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    moderators = models.ManyToManyField(User, related_name='managed_groups', limit_choices_to={'role': 'moderator'})
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name