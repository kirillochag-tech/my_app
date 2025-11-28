from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Task, TaskAssignment, SurveyQuestion, SurveyChoice, PhotoReportTask
from .forms import TaskForm, SurveyQuestionForm, PhotoReportTaskForm
from accounts.models import User


@login_required
def task_list(request):
    # Filter tasks based on user role
    if request.user.role == 'employee':
        # Employees see only assigned tasks
        tasks = Task.objects.filter(
            Q(assigned_employees=request.user) | 
            Q(assigned_employee_groups__in=request.user.employeegroup_set.all())
        ).distinct()
    elif request.user.role in ['moderator', 'super_moderator']:
        # Moderators see all tasks or tasks they created
        tasks = Task.objects.all()
    else:
        tasks = Task.objects.none()
    
    # Apply additional filters
    status_filter = request.GET.get('status')
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    
    employee_filter = request.GET.get('employee')
    if employee_filter:
        tasks = tasks.filter(assigned_employees__id=employee_filter)
    
    context = {
        'tasks': tasks,
        'employees': User.objects.filter(role='employee'),
    }
    return render(request, 'tasks/task_list.html', context)


@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    return render(request, 'tasks/task_detail.html', {'task': task})


@login_required
def execute_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    if request.user.role != 'employee':
        messages.error(request, 'Только сотрудники могут выполнять задачи')
        return redirect('tasks:task_list')
    
    # Check if task is assigned to this employee
    if not (task.assigned_employees.filter(id=request.user.id).exists() or 
            task.assigned_employee_groups.filter(employeegroup__in=request.user.employeegroup_set.all()).exists()):
        messages.error(request, 'Эта задача не назначена вам')
        return redirect('tasks:task_list')
    
    # Handle form submission
    if request.method == 'POST':
        # Process the task execution based on task type
        if task.task_type == 'survey':
            # Process survey questions and answers
            for question in task.questions.all():
                if question.question_type == 'text':
                    answer = request.POST.get(f'question_{question.id}_text', '')
                elif question.question_type in ['single_choice', 'single_checkbox']:
                    answer = request.POST.get(f'question_{question.id}_choice', '')
                elif question.question_type in ['multiple_choice', 'multiple_checkbox']:
                    answer = request.POST.getlist(f'question_{question.id}_choice', [])
                elif question.question_type == 'photo':
                    answer = request.FILES.get(f'question_{question.id}_photo', '')
                
                # Save the answer (simplified - in real implementation, you'd save to TaskResponse model)
                messages.success(request, f'Задача "{task.title}" выполнена!')
        
        # Update task assignment status
        task_assignment, created = TaskAssignment.objects.get_or_create(
            task=task,
            employee=request.user,
            defaults={'status': 'completed'}
        )
        if not created:
            task_assignment.status = 'completed'
            task_assignment.save()
        
        return redirect('tasks:task_list')
    
    context = {
        'task': task,
        'questions': task.questions.all() if task.task_type == 'survey' else None,
    }
    return render(request, 'tasks/execute_task.html', context)


@login_required
def task_result(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    return render(request, 'tasks/task_result.html', {'task': task})


@login_required
def create_task(request):
    if request.user.role not in ['moderator', 'super_moderator']:
        messages.error(request, 'Только модераторы могут создавать задачи')
        return redirect('tasks:task_list')
    
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            
            # Handle many-to-many relationships
            form.save_m2m()
            
            # Create task assignments for assigned employees
            for employee in task.assigned_employees.all():
                TaskAssignment.objects.get_or_create(task=task, employee=employee)
            
            messages.success(request, 'Задача успешно создана')
            return redirect('tasks:task_list')
    else:
        form = TaskForm()
    
    return render(request, 'tasks/create_task.html', {'form': form})


@login_required
def create_photo_report_task(request):
    if request.user.role not in ['moderator', 'super_moderator']:
        messages.error(request, 'Только модераторы могут создавать задачи')
        return redirect('tasks:task_list')
    
    if request.method == 'POST':
        task_form = TaskForm(request.POST)
        photo_report_form = PhotoReportTaskForm(request.POST)
        
        if task_form.is_valid() and photo_report_form.is_valid():
            task = task_form.save(commit=False)
            task.created_by = request.user
            task.task_type = 'photo_report_simple'  # Default for this view
            task.save()
            task_form.save_m2m()
            
            # Create the photo report task
            photo_task = photo_report_form.save(commit=False)
            photo_task.task = task
            photo_task.save()
            
            # Create task assignments
            for employee in task.assigned_employees.all():
                TaskAssignment.objects.get_or_create(task=task, employee=employee)
            
            messages.success(request, 'Фотоотчет задача успешно создана')
            return redirect('tasks:task_list')
    else:
        task_form = TaskForm()
        photo_report_form = PhotoReportTaskForm()
    
    return render(request, 'tasks/create_photo_report_task.html', {
        'task_form': task_form,
        'photo_report_form': photo_report_form
    })