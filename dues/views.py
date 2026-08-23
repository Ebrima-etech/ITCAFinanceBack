from django.db import transaction as db_transaction
from rest_framework.views import APIView
from rest_framework.response import Response

from accounts.permissions import ReadOnlyOrAdminFinance
from activitylog.utils import record_activity
from ledger.models import Transaction, TransactionType
from .models import MembershipDue
from .serializers import MembershipDueSerializer, CreateDueSerializer


# Dues arrive two ways - online payment, or cash handed over and typed in
# by an officer. Both end up as one membership_dues row wrapping one
# transaction of type DUE, so ledger totals and membership income never
# disagree.
class MembershipDueListCreateView(APIView):
    permission_classes = [ReadOnlyOrAdminFinance]

    def get(self, request):
        dues = MembershipDue.objects.select_related('recorded_by').all()
        total = sum(float(d.amount) for d in dues)
        return Response({
            'dues': MembershipDueSerializer(dues, many=True).data,
            'total': total,
            'count': dues.count(),
        })

    def post(self, request):
        serializer = CreateDueSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        with db_transaction.atomic():
            txn = Transaction.objects.create(
                type=TransactionType.DUE,
                category='Membership Dues',
                description=f"Dues - {data['member_name']}",
                amount=data['amount'],
                occurred_at=data['paid_at'],
                recorded_by=request.user,
            )
            due = MembershipDue.objects.create(
                member_name=data['member_name'],
                member_email=data.get('member_email'),
                amount=data['amount'],
                method=data['method'],
                paid_at=data['paid_at'],
                transaction=txn,
                recorded_by=request.user,
            )

        record_activity(
            action='CREATE', entity_type='MembershipDue', entity_id=str(due.id),
            actor=request.user,
            details={'memberName': due.member_name, 'amount': str(due.amount), 'method': due.method},
        )

        return Response(MembershipDueSerializer(due).data, status=201)
