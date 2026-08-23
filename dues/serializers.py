from decimal import Decimal
from rest_framework import serializers
from .models import MembershipDue


class MembershipDueSerializer(serializers.ModelSerializer):
    recorded_by = serializers.SerializerMethodField()

    class Meta:
        model = MembershipDue
        fields = ['id', 'member_name', 'member_email', 'amount', 'method', 'paid_at', 'recorded_by', 'created_at']

    def get_recorded_by(self, obj):
        return {'id': obj.recorded_by.id, 'name': obj.recorded_by.name}


class CreateDueSerializer(serializers.Serializer):
    member_name = serializers.CharField()
    member_email = serializers.EmailField(required=False, allow_null=True)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal('0.01'))
    method = serializers.ChoiceField(choices=['CASH', 'ONLINE'])
    paid_at = serializers.DateTimeField()
