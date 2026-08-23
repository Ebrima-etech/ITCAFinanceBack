import uuid
from django.conf import settings
from django.db import models


class TransactionType(models.TextChoices):
    DUE = 'DUE'
    EVENT_REVENUE = 'EVENT_REVENUE'
    EVENT_COST = 'EVENT_COST'
    GIFT = 'GIFT'
    OTHER_INCOME = 'OTHER_INCOME'
    OTHER_EXPENSE = 'OTHER_EXPENSE'


# Whether a transaction type represents money coming in (True) or going
# out (False). Used anywhere a net figure (event profit/loss, dashboard
# totals) is calculated from raw transaction rows.
INFLOW_TYPES = {
    TransactionType.DUE,
    TransactionType.EVENT_REVENUE,
    TransactionType.GIFT,
    TransactionType.OTHER_INCOME,
}


def is_inflow(transaction_type: str) -> bool:
    return transaction_type in INFLOW_TYPES


# The heart of the system. Every bit of money in or out lives here as one
# row. Nothing else stores a money figure directly - it's always
# calculated by summing these rows.
class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=32, choices=TransactionType.choices)
    category = models.CharField(max_length=100)
    description = models.CharField(max_length=500, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    occurred_at = models.DateTimeField()

    event = models.ForeignKey(
        'events.Event', null=True, blank=True, on_delete=models.SET_NULL, related_name='transactions'
    )
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='transactions_recorded'
    )

    # Soft delete: money records are never truly erased, just flagged, so
    # the audit trail stays honest even after a mistake is undone.
    deleted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'transactions'
        indexes = [
            models.Index(fields=['type']),
            models.Index(fields=['event']),
            models.Index(fields=['occurred_at']),
        ]
        ordering = ['-occurred_at']
