import uuid
from django.conf import settings
from django.db import models


# The system's memory of who did what and when. One generic table so any
# kind of action can be logged without new columns for each - this is
# what makes the audit trail complete.
class ActivityLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    action = models.CharField(max_length=64)
    entity_type = models.CharField(max_length=64)
    entity_id = models.CharField(max_length=64, null=True, blank=True)
    details = models.JSONField(null=True, blank=True)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='activity_log_entries'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'activity_log'
        indexes = [
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['actor']),
        ]
        ordering = ['-created_at']
