from django.db import models
from accounts.models import User, EmployeeGroup
from clients.models import Client, ClientGroup


class Task(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('sent', 'Отправлено'),
        ('in_progress', 'На доработке'),
        ('completed', 'Выполнено'),
    ]
    
    TASK_TYPE_CHOICES = [
        ('survey', 'Анкета'),
        ('photo_report_stand', 'Фотоотчет по стендам'),
        ('photo_report_simple', 'Фотоотчет простой'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    task_type = models.CharField(max_length=20, choices=TASK_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_active = models.BooleanField(default=True)
    
    # Target recipients
    assigned_employees = models.ManyToManyField(User, blank=True, limit_choices_to={'role': 'employee'}, related_name='assigned_tasks')
    assigned_employee_groups = models.ManyToManyField(EmployeeGroup, blank=True, related_name='assigned_tasks')
    assigned_clients = models.ManyToManyField(Client, blank=True, related_name='assigned_tasks')
    assigned_client_groups = models.ManyToManyField(ClientGroup, blank=True, related_name='assigned_tasks')
    
    # For moderators
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks', limit_choices_to={'role__in': ['moderator', 'super_moderator']})
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Plan for survey tasks
    plan_count = models.IntegerField(null=True, blank=True, help_text="План по количеству анкет (для задач типа 'Анкета')")
    
    def __str__(self):
        return f"{self.title} ({self.get_task_type_display()})"


class SurveyQuestion(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('text', 'Текстовое поле'),
        ('single_choice', 'Список с единичным выбором'),
        ('multiple_choice', 'Список с множественным выбором'),
        ('single_checkbox', 'Чекбокс с единичным выбором'),
        ('multiple_checkbox', 'Чекбокс с множественным выбором'),
        ('photo', 'Фото'),
    ]
    
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='questions', limit_choices_to={'task_type': 'survey'})
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES)
    required = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.question_text[:50]}..."


class SurveyChoice(models.Model):
    question = models.ForeignKey(SurveyQuestion, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.choice_text


class TaskAssignment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    employee = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'employee'})
    assigned_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Task.STATUS_CHOICES, default='sent')
    
    class Meta:
        unique_together = ['task', 'employee']
    
    def __str__(self):
        return f"{self.task.title} - {self.employee.username}"


class PhotoReportTask(models.Model):
    task = models.OneToOneField(Task, on_delete=models.CASCADE, limit_choices_to={'task_type__in': ['photo_report_stand', 'photo_report_simple']})
    client = models.ForeignKey(Client, on_delete=models.CASCADE, blank=True, null=True)
    address = models.TextField(blank=True)
    comment = models.TextField(blank=True)
    
    def __str__(self):
        return f"Photo Report: {self.task.title}"