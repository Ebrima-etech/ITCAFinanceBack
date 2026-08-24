from datetime import date, datetime
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response

from accounts.permissions import IsInternalUser
from ledger.models import Transaction, is_inflow
from events.models import Event


# Stores nothing of its own. Reads the ledger and events, then serves up
# the summaries, charts, and profit/loss figures the dashboard screen shows.
class DashboardView(APIView):
    permission_classes = [IsInternalUser]

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
