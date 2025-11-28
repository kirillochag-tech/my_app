from django.db import models
from accounts.models import User
from tasks.models import Task, SurveyQuestion, SurveyChoice
from clients.models import Client


class TaskResponse(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='responses')
    employee = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'employee'})
    client = models.ForeignKey(Client, on_delete=models.CASCADE, blank=True, null=True)
    completed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['task', 'employee', 'client']
    
    def __str__(self):
        return f"Response: {self.task.title} - {self.employee.username}"


class SurveyResponse(models.Model):
    task_response = models.ForeignKey(TaskResponse, on_delete=models.CASCADE, related_name='survey_responses')
    question = models.ForeignKey(SurveyQuestion, on_delete=models.CASCADE)
    text_answer = models.TextField(blank=True)
    selected_choices = models.ManyToManyField(SurveyChoice, blank=True)
    photo_answer = models.ImageField(upload_to='survey_photos/', blank=True, null=True)
    
    def __str__(self):
        return f"Survey Response: {self.question.question_text[:50]}..."


class PhotoReportResponse(models.Model):
    task_response = models.OneToOneField(TaskResponse, on_delete=models.CASCADE, related_name='photo_report_response')
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    address = models.TextField()
    equipment_count = models.IntegerField(null=True, blank=True)
    photos = models.ImageField(upload_to='photo_reports/', blank=True, null=True)
    comment = models.TextField(blank=True)
    
    def __str__(self):
        return f"Photo Report: {self.task_response.task.title}"