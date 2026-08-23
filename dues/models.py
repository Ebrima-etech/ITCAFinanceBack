import uuid
from django.conf import settings
from django.db import models


class DuesMethod(models.TextChoices):
    CASH = 'CASH'
    ONLINE = 'ONLINE'


# Dues paid by members, whether paid online or handed over as cash and
# typed in by an officer. Each row wraps one transaction of type DUE.
class MembershipDue(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    member_name = models.CharField(max_length=255)
    member_email = models.EmailField(null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=16, choices=DuesMethod.choices)
    paid_at = models.DateTimeField()

    transaction = models.OneToOneField('ledger.Transaction', on_delete=models.CASCADE, related_name='membership_due')
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='dues_recorded')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'membership_dues'
        ordering = ['-paid_at']
