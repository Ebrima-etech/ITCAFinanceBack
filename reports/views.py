from datetime import date, datetime
from django.http import HttpResponse
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from accounts.permissions import IsInternalUser
from ledger.models import Transaction, is_inflow
from events.models import Event


# Turns raw ledger data into an exportable CSV for annual budgeting,
# funding proposals, and committee reviews.
class TransactionsReportView(APIView):
    permission_classes = [IsInternalUser]

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


# Public financial summary for landing page transparency
class PublicFinancialReportView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        year = int(request.query_params.get('year', date.today().year))
        start = timezone.make_aware(datetime(year, 1, 1))
        end = timezone.make_aware(datetime(year + 1, 1, 1))

        transactions = Transaction.objects.filter(
            deleted_at__isnull=True, occurred_at__gte=start, occurred_at__lt=end
        )

        income = 0.0
        expenses = 0.0
        by_month = {}
        by_type = {}

        for t in transactions:
            amount = float(t.amount)
            month_key = t.occurred_at.strftime('%Y-%m')
            by_month.setdefault(month_key, {'income': 0.0, 'expenses': 0.0})
            by_type[t.type] = by_type.get(t.type, 0.0) + amount

            if is_inflow(t.type):
                income += amount
                by_month[month_key]['income'] += amount
            else:
                expenses += amount
                by_month[month_key]['expenses'] += amount

        events = Event.objects.filter(date__gte=start, date__lt=end).prefetch_related('transactions')
        event_results = []
        for event in events:
            revenue = 0.0
            cost = 0.0
            for t in event.transactions.filter(deleted_at__isnull=True):
                amount = float(t.amount)
                if is_inflow(t.type):
                    revenue += amount
                else:
                    cost += amount
            event_results.append({
                'id': event.id, 'name': event.name, 'date': event.date,
                'status': event.status,
                'revenue': revenue, 'cost': cost, 'result': revenue - cost,
            })

        return Response({
            'year': year,
            'income': income,
            'expenses': expenses,
            'net': income - expenses,
            'by_month': [{'month': k, **v} for k, v in sorted(by_month.items())],
            'by_type': by_type,
            'events': event_results,
        })
