import uuid
from django.db import models


# One row per event or project. Its money isn't stored here - it lives in
# transactions that point back to it, so profit/loss is always just
# "add up the transactions linked to this event."
class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=1000, null=True, blank=True)
    date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'events'
        ordering = ['-date']
