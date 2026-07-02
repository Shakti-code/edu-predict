from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'has_face_data_display', 'face_registered_at', 'face_updated_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('face_registered_at', 'face_updated_at', 'face_encoding_preview')
    list_filter = ('face_registered_at',)

    fieldsets = (
        ('User Info', {
            'fields': ('user',)
        }),
        ('Face Biometric Data', {
            'fields': ('face_encoding', 'face_encoding_preview', 'face_registered_at', 'face_updated_at'),
            'description': 'Stores the 128-dimension face descriptor vector as a JSON array.'
        }),
    )

    def has_face_data_display(self, obj):
        return '✓ Yes' if obj.has_face_data else '✗ No'
    has_face_data_display.short_description = 'Face Registered'

    def face_encoding_preview(self, obj):
        if obj.face_encoding:
            import json
            try:
                data = json.loads(obj.face_encoding)
                return f"128-float vector (first 5 values: {data[:5]})"
            except Exception:
                return "Invalid JSON"
        return "No face data stored."
    face_encoding_preview.short_description = 'Face Data Preview'
