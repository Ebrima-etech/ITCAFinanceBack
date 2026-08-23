import uuid
from django.db import models


# FUTURE. Digital receipts issued off an existing transaction. Thin layer,
# nothing else depends on it. Not wired into any view yet - schema only,
# so it can be bolted on later without disturbing the core.
class Receipt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction = models.OneToOneField('ledger.Transaction', on_delete=models.CASCADE, related_name='receipt')
    issued_to = models.CharField(max_length=255)
    issued_at = models.DateTimeField(auto_now_add=True)
    number = models.CharField(max_length=64, unique=True)

    class Meta:
        db_table = 'receipts'
