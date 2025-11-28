from django.contrib import admin
from .models import Client, ClientGroup


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'assigned_employee', 'created_at')
    list_filter = ('assigned_employee',)
    search_fields = ('name', 'address')
    date_hierarchy = 'created_at'


@admin.register(ClientGroup)
class ClientGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    filter_horizontal = ('clients',)
    search_fields = ('name',)