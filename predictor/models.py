from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import json


class Prediction(models.Model):
    """Store prediction history for users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='predictions')

    # Input parameters
    study_hours = models.FloatField(validators=[MinValueValidator(1.0), MaxValueValidator(10.0)])
    attendance = models.FloatField(validators=[MinValueValidator(50.0), MaxValueValidator(100.0)])
    sleep_hours = models.FloatField(validators=[MinValueValidator(4.0), MaxValueValidator(10.0)])
    parental_support = models.CharField(max_length=20, choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')])
    extracurricular = models.CharField(max_length=10, choices=[('Yes', 'Yes'), ('No', 'No')])
    internet_access = models.CharField(max_length=10, choices=[('Yes', 'Yes'), ('No', 'No')])
    previous_grade = models.FloatField(validators=[MinValueValidator(30.0), MaxValueValidator(100.0)])

    # Prediction results
    predicted_score = models.FloatField()
    grade_class = models.CharField(max_length=20, choices=[('Excellent', 'Excellent'), ('Good', 'Good'), ('Pass', 'Pass'), ('Fail', 'Fail')])

    # Store recommendations as JSON
    recommendations = models.JSONField(default=list, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Prediction'
        verbose_name_plural = 'Predictions'

    def __str__(self):
        return f"Prediction {self.id} - {self.predicted_score}% ({self.grade_class})"


class SavedScenario(models.Model):
    """Allow users to save specific scenarios for comparison"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_scenarios')
    name = models.CharField(max_length=100)

    # Input parameters
    study_hours = models.FloatField(validators=[MinValueValidator(1.0), MaxValueValidator(10.0)])
    attendance = models.FloatField(validators=[MinValueValidator(50.0), MaxValueValidator(100.0)])
    sleep_hours = models.FloatField(validators=[MinValueValidator(4.0), MaxValueValidator(10.0)])
    parental_support = models.CharField(max_length=20, choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')])
    extracurricular = models.CharField(max_length=10, choices=[('Yes', 'Yes'), ('No', 'No')])
    internet_access = models.CharField(max_length=10, choices=[('Yes', 'Yes'), ('No', 'No')])
    previous_grade = models.FloatField(validators=[MinValueValidator(30.0), MaxValueValidator(100.0)])

    # Optional notes
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Saved Scenario'
        verbose_name_plural = 'Saved Scenarios'

    def __str__(self):
        return f"{self.user.username}'s scenario: {self.name}"
