from rest_framework import serializers
from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    event = serializers.SerializerMethodField()
    recorded_by = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            'id', 'type', 'category', 'description', 'amount', 'occurred_at',
            'event_id', 'event', 'recorded_by', 'created_at', 'updated_at',
        ]

    def get_event(self, obj):
        if not obj.event_id:
            return None
        return {'id': obj.event.id, 'name': obj.event.name}

    def get_recorded_by(self, obj):
        return {'id': obj.recorded_by.id, 'name': obj.recorded_by.name}


class CreateTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['type', 'category', 'description', 'amount', 'occurred_at', 'event_id']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('Amount must be positive')
        return value


class UpdateTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['type', 'category', 'description', 'amount', 'occurred_at', 'event_id']
        extra_kwargs = {field: {'required': False} for field in fields}
