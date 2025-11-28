from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def group_list(request):
    """Display list of groups"""
    return render(request, 'groups/group_list.html')


@login_required
def create_group(request):
    """Create a new group"""
    return render(request, 'groups/create_group.html')