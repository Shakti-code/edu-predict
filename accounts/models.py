from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    face_encoding = models.TextField(null=True, blank=True)  # JSON array of 128-float face descriptor
    face_registered_at = models.DateTimeField(null=True, blank=True)  # When face was captured
    face_updated_at = models.DateTimeField(null=True, blank=True)     # Last update timestamp

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return f"{self.user.username} — Face: {'✓ Registered' if self.face_encoding else '✗ Not Registered'}"

    @property
    def has_face_data(self):
        return bool(self.face_encoding)

    def set_face_encoding(self, encoding_json: str):
        """Store face encoding JSON and update timestamps."""
        self.face_encoding = encoding_json
        now = timezone.now()
        if not self.face_registered_at:
            self.face_registered_at = now
        self.face_updated_at = now
        self.save()
