from django.db import models
from django.contrib.auth.models import User

class StudentPrediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='predictions')
    study_hours = models.FloatField()
    attendance = models.FloatField()
    sleep_hours = models.FloatField()
    parental_support = models.CharField(max_length=20)
    extracurricular = models.CharField(max_length=20)
    internet_access = models.CharField(max_length=20)
    previous_grade = models.FloatField()
    
    predicted_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.predicted_score}% ({self.created_at.strftime('%Y-%m-%d')})"

    class Meta:
        ordering = ['-created_at']
