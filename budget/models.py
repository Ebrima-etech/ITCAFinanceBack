import uuid
from django.conf import settings
from django.db import models


# Next year's plan, entered by hand, line by line. There is deliberately
# no "actual spent" column - that figure is always calculated live from
# transactions, so budget-vs-actual can never fall out of sync.
class BudgetItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    year = models.IntegerField()
    category = models.CharField(max_length=100)
    label = models.CharField(max_length=255)
    planned_amount = models.DecimalField(max_digits=12, decimal_places=2)
    notes = models.CharField(max_length=1000, null=True, blank=True)

    entered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='budget_items_entered')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'budget_items'
        indexes = [models.Index(fields=['year'])]
        ordering = ['category', 'label']
