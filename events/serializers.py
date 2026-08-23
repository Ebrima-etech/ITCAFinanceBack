from rest_framework import serializers
from ledger.models import is_inflow
from ledger.serializers import TransactionSerializer
from .models import Event


def summarize(transactions):
    revenue = sum(float(t.amount) for t in transactions if is_inflow(t.type))
    cost = sum(float(t.amount) for t in transactions if not is_inflow(t.type))
    return {'revenue': revenue, 'cost': cost, 'result': revenue - cost}


class EventListSerializer(serializers.ModelSerializer):
    revenue = serializers.SerializerMethodField()
    cost = serializers.SerializerMethodField()
    result = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ['id', 'name', 'description', 'date', 'revenue', 'cost', 'result']

    def _summary(self, obj):
        if not hasattr(obj, '_summary_cache'):
            obj._summary_cache = summarize(obj.transactions.filter(deleted_at__isnull=True))
        return obj._summary_cache

    def get_revenue(self, obj):
        return self._summary(obj)['revenue']

    def get_cost(self, obj):
        return self._summary(obj)['cost']

    def get_result(self, obj):
        return self._summary(obj)['result']


class EventDetailSerializer(EventListSerializer):
    transactions = serializers.SerializerMethodField()

    class Meta(EventListSerializer.Meta):
        fields = EventListSerializer.Meta.fields + ['transactions']

    def get_transactions(self, obj):
        qs = obj.transactions.filter(deleted_at__isnull=True).select_related('recorded_by').order_by('-occurred_at')
        return TransactionSerializer(qs, many=True).data


class CreateEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['name', 'description', 'date']


class UpdateEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['name', 'description', 'date']
        extra_kwargs = {field: {'required': False} for field in fields}
