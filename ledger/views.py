from django.utils.dateparse import parse_date
from django.db.models import Sum
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from accounts.permissions import ReadOnlyOrAdminFinance
from activitylog.utils import record_activity
from .models import Transaction
from .serializers import TransactionSerializer, CreateTransactionSerializer, UpdateTransactionSerializer


# The engine room. Every due paid, event ticket sold, gift received, or
# cost paid is one row here. Everything else in the system - event
# profit/loss, dues totals, budget-vs-actual - is calculated by summing
# these rows, never stored twice.
class TransactionListCreateView(APIView):
    permission_classes = [ReadOnlyOrAdminFinance]

    def filtered_queryset(self, request):
        qs = Transaction.objects.filter(deleted_at__isnull=True).select_related('event', 'recorded_by')
        params = request.query_params
        if params.get('type'):
            qs = qs.filter(type=params['type'])
        if params.get('category'):
            qs = qs.filter(category=params['category'])
        if params.get('eventId'):
            qs = qs.filter(event_id=params['eventId'])
        if params.get('from'):
            qs = qs.filter(occurred_at__gte=parse_date(params['from']))
        if params.get('to'):
            qs = qs.filter(occurred_at__lte=parse_date(params['to']))
        return qs

    def get(self, request):
        qs = self.filtered_queryset(request)
        total = qs.aggregate(total=Sum('amount'))['total'] or 0
        return Response({
            'transactions': TransactionSerializer(qs, many=True).data,
            'total': total,
            'count': qs.count(),
        })

    def post(self, request):
        serializer = CreateTransactionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        transaction = serializer.save(recorded_by=request.user)

        record_activity(
            action='CREATE',
            entity_type='Transaction',
            entity_id=str(transaction.id),
            actor=request.user,
            details={'type': transaction.type, 'category': transaction.category, 'amount': str(transaction.amount)},
        )

        return Response(TransactionSerializer(transaction).data, status=201)


class TransactionDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [ReadOnlyOrAdminFinance]
    lookup_url_kwarg = 'pk'

    def get_queryset(self):
        return Transaction.objects.filter(deleted_at__isnull=True)

    def get_object(self):
        try:
            return self.get_queryset().get(pk=self.kwargs['pk'])
        except Transaction.DoesNotExist:
            raise NotFound('Transaction not found')

    def get_serializer_class(self):
        if self.request.method in ('PATCH', 'PUT'):
            return UpdateTransactionSerializer
        return TransactionSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        transaction = serializer.save()

        record_activity(
            action='UPDATE',
            entity_type='Transaction',
            entity_id=str(transaction.id),
            actor=request.user,
            details={'changed': list(request.data.keys())},
        )

        return Response(TransactionSerializer(transaction).data)

    # Soft delete only: money data is never truly erased, just flagged, so
    # the audit trail stays honest even after a mistake is undone.
    def destroy(self, request, *args, **kwargs):
        from django.utils import timezone
        transaction = self.get_object()
        transaction.deleted_at = timezone.now()
        transaction.save(update_fields=['deleted_at'])
        record_activity(action='DELETE', entity_type='Transaction', entity_id=str(transaction.id), actor=request.user)
        return Response(TransactionSerializer(transaction).data)
