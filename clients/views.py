from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Client


@login_required
def client_list(request):
    """Display list of clients"""
    clients = Client.objects.all()
    return render(request, 'clients/client_list.html', {'clients': clients})


@login_required
def client_detail(request, client_id):
    """Display client details and related tasks"""
    client = get_object_or_404(Client, id=client_id)
    # Add logic to get related tasks
    return render(request, 'clients/client_detail.html', {'client': client})


@login_required
def create_client(request):
    """Create a new client"""
    # Add logic for creating a client
    return render(request, 'clients/create_client.html')


@login_required
def import_clients_excel(request):
    """Import clients from Excel file"""
    # Add logic for importing clients from Excel
    return render(request, 'clients/import_clients.html')