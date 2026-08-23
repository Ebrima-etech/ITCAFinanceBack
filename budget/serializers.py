from rest_framework import serializers
from .models import BudgetItem


class BudgetItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetItem
        fields = ['id', 'year', 'category', 'label', 'planned_amount', 'notes', 'entered_by_id', 'created_at']


class CreateBudgetItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetItem
        fields = ['year', 'category', 'label', 'planned_amount', 'notes']

    def validate_planned_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('Planned amount must be positive')
        return value


class UpdateBudgetItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetItem
        fields = ['year', 'category', 'label', 'planned_amount', 'notes']
        extra_kwargs = {field: {'required': False} for field in fields}
