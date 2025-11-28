from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def feedback_list(request):
    """Display list of feedback"""
    return render(request, 'feedback/feedback_list.html')


@login_required
def results_view(request):
    """Display results page"""
    return render(request, 'feedback/results.html')


@login_required
def results_detail(request, task_id):
    """Display detailed results for a specific task"""
    return render(request, 'feedback/results_detail.html', {'task_id': task_id})


@login_required
def statistics_view(request):
    """Display statistics"""
    return render(request, 'feedback/statistics.html')