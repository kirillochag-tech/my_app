from django import forms
from .models import Task, SurveyQuestion, SurveyChoice, PhotoReportTask


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('title', 'description', 'task_type', 'status', 'is_active', 'assigned_employees', 
                  'assigned_employee_groups', 'assigned_clients', 'assigned_client_groups', 'plan_count')
        widgets = {
            'assigned_employees': forms.CheckboxSelectMultiple,
            'assigned_employee_groups': forms.CheckboxSelectMultiple,
            'assigned_clients': forms.CheckboxSelectMultiple,
            'assigned_client_groups': forms.CheckboxSelectMultiple,
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class SurveyQuestionForm(forms.ModelForm):
    class Meta:
        model = SurveyQuestion
        fields = ('question_text', 'question_type', 'required', 'order')
        widgets = {
            'question_text': forms.Textarea(attrs={'rows': 2}),
        }


class SurveyChoiceForm(forms.ModelForm):
    class Meta:
        model = SurveyChoice
        fields = ('choice_text', 'order')


class PhotoReportTaskForm(forms.ModelForm):
    class Meta:
        model = PhotoReportTask
        fields = ('client', 'address', 'comment')
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
        }