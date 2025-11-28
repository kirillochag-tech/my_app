from django.contrib import admin
from .models import Task, SurveyQuestion, SurveyChoice, TaskAssignment, PhotoReportTask


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'task_type', 'status', 'is_active', 'created_by', 'created_at')
    list_filter = ('task_type', 'status', 'is_active', 'created_at', 'created_by')
    search_fields = ('title', 'description')
    filter_horizontal = ('assigned_employees', 'assigned_employee_groups', 'assigned_clients', 'assigned_client_groups')
    date_hierarchy = 'created_at'


@admin.register(SurveyQuestion)
class SurveyQuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'task', 'question_type', 'required', 'order')
    list_filter = ('question_type', 'task')
    search_fields = ('question_text',)


@admin.register(SurveyChoice)
class SurveyChoiceAdmin(admin.ModelAdmin):
    list_display = ('choice_text', 'question', 'order')
    list_filter = ('question',)
    search_fields = ('choice_text', 'question__question_text')


@admin.register(TaskAssignment)
class TaskAssignmentAdmin(admin.ModelAdmin):
    list_display = ('task', 'employee', 'assigned_at', 'status')
    list_filter = ('status', 'assigned_at', 'employee')
    search_fields = ('task__title', 'employee__username')


@admin.register(PhotoReportTask)
class PhotoReportTaskAdmin(admin.ModelAdmin):
    list_display = ('task', 'client', 'address')
    list_filter = ('client',)
    search_fields = ('task__title', 'client__name', 'address')