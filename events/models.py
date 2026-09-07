import uuid
from django.db import models
from django.utils import timezone


# One row per event or project. Its money isn't stored here - it lives in
# transactions that point back to it, so profit/loss is always just
# "add up the transactions linked to this event."
class Event(models.Model):
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('happening', 'Happening'),
        ('passed', 'Passed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=1000, null=True, blank=True)
    date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'events'
        ordering = ['-date']

    def save(self, *args, **kwargs):
        now = timezone.now()
        if self.date > now:
            self.status = 'upcoming'
        elif self.date.replace(hour=23, minute=59, second=59) < now:
            self.status = 'passed'
        else:
            self.status = 'happening'
        super().save(*args, **kwargs)


# Event sponsorship/partnership applications - partners apply for specific events
class EventPartner(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='partners', null=True)
    organization_name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    website = models.URLField(null=True, blank=True)
    logo_url = models.URLField(null=True, blank=True)
    description = models.TextField(max_length=2000)
    sponsorship_level = models.CharField(
        max_length=50,
        choices=[('gold', 'Gold'), ('silver', 'Silver'), ('bronze', 'Bronze')],
        default='bronze'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'event_partners'
        ordering = ['-created_at']
        unique_together = ['event', 'email']
