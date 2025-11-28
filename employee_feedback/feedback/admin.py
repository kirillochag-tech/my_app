from django.contrib import admin
from .models import TaskResponse, SurveyResponse, PhotoReportResponse


@admin.register(TaskResponse)
class TaskResponseAdmin(admin.ModelAdmin):
    list_display = ('task', 'employee', 'client', 'completed_at')
    list_filter = ('task', 'employee', 'client', 'completed_at')
    search_fields = ('task__title', 'employee__username', 'client__name')
    date_hierarchy = 'completed_at'


@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = ('task_response', 'question', 'text_answer_preview')
    list_filter = ('question', 'task_response__task', 'task_response__employee')
    search_fields = ('question__question_text', 'text_answer')
    
    def text_answer_preview(self, obj):
        return obj.text_answer[:50] + '...' if len(obj.text_answer) > 50 else obj.text_answer
    text_answer_preview.short_description = 'Text Answer Preview'


@admin.register(PhotoReportResponse)
class PhotoReportResponseAdmin(admin.ModelAdmin):
    list_display = ('task_response', 'client', 'address', 'equipment_count')
    list_filter = ('client', 'task_response__task', 'task_response__employee')
    search_fields = ('client__name', 'address', 'comment')