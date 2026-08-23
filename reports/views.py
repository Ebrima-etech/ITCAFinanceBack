from django.http import HttpResponse
from django.utils.dateparse import parse_date
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from ledger.models import Transaction


# Turns raw ledger data into an exportable CSV for annual budgeting,
# funding proposals, and committee reviews.
class TransactionsReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from_date = parse_date(request.query_params.get('from', ''))
        to_date = parse_date(request.query_params.get('to', ''))

        transactions = Transaction.objects.filter(
            deleted_at__isnull=True, occurred_at__gte=from_date, occurred_at__lte=to_date
        ).select_related('event', 'recorded_by').order_by('occurred_at')

        header = ['Date', 'Type', 'Category', 'Description', 'Amount', 'Event', 'Recorded By']
        rows = [header]
        total = 0.0
        for t in transactions:
            total += float(t.amount)
            rows.append([
                t.occurred_at.strftime('%Y-%m-%d'),
                t.type,
                t.category,
                (t.description or '').replace(',', ';'),
                str(t.amount),
                t.event.name if t.event else '',
                t.recorded_by.name,
            ])

        csv_text = '\n'.join(','.join(str(cell) for cell in row) for row in rows)

        if request.query_params.get('format') == 'csv':
            response = HttpResponse(csv_text, content_type='text/csv')
            response['Content-Disposition'] = (
                f'attachment; filename="itca-transactions-{request.query_params.get("from")}'
                f'_to_{request.query_params.get("to")}.csv"'
            )
            return response

        return Response({'csv': csv_text, 'count': transactions.count(), 'total': total})
