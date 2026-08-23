from datetime import date, datetime
from django.db.models import Sum
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from activitylog.utils import record_activity
from ledger.models import Transaction
from .models import BudgetItem
from .serializers import BudgetItemSerializer, CreateBudgetItemSerializer, UpdateBudgetItemSerializer


# Deliberately no "actual spent" column on budget_items - the actual
# figure is always calculated live here from transactions, so
# budget-vs-actual can never fall out of sync with the ledger.
def actual_by_category(year):
    start = timezone.make_aware(datetime(year, 1, 1))
    end = timezone.make_aware(datetime(year + 1, 1, 1))
    rows = (
        Transaction.objects.filter(deleted_at__isnull=True, occurred_at__gte=start, occurred_at__lt=end)
        .values('category')
        .annotate(total=Sum('amount'))
    )
    return {row['category']: float(row['total'] or 0) for row in rows}


# Budget planning is deliberately open to every logged-in role, not just
# finance officers - it's the committee's proposed spending.
class BudgetListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        year = int(request.query_params.get('year', date.today().year + 1))
        items = BudgetItem.objects.filter(year=year)
        actuals = actual_by_category(year)
        prior = actual_by_category(year - 1)

        result = []
        for item in items:
            planned = float(item.planned_amount)
            actual = actuals.get(item.category, 0)
            result.append({
                **BudgetItemSerializer(item).data,
                'actual': actual,
                'variance': planned - actual,
                'priorYearActual': prior.get(item.category, 0),
            })
        return Response(result)

    def post(self, request):
        serializer = CreateBudgetItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = serializer.save(entered_by=request.user)

        record_activity(
            action='CREATE', entity_type='BudgetItem', entity_id=str(item.id),
            actor=request.user, details={'year': item.year, 'category': item.category, 'label': item.label},
        )

        return Response(BudgetItemSerializer(item).data, status=201)


class BudgetDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return BudgetItem.objects.get(pk=pk)
        except BudgetItem.DoesNotExist:
            raise NotFound('Budget item not found')

    def patch(self, request, pk):
        item = self.get_object(pk)
        serializer = UpdateBudgetItemSerializer(item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        item = serializer.save()

        record_activity(
            action='UPDATE', entity_type='BudgetItem', entity_id=str(item.id),
            actor=request.user, details={'changed': list(request.data.keys())},
        )

        return Response(BudgetItemSerializer(item).data)

    def delete(self, request, pk):
        item = self.get_object(pk)
        item_id = str(item.id)
        item.delete()

        record_activity(action='DELETE', entity_type='BudgetItem', entity_id=item_id, actor=request.user)

        return Response({'id': item_id})
