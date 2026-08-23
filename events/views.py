from django.utils.dateparse import parse_date
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError

from accounts.permissions import ReadOnlyOrAdminFinance
from activitylog.utils import record_activity
from ledger.models import Transaction, TransactionType
from .models import Event
from .serializers import (
    EventListSerializer,
    EventDetailSerializer,
    CreateEventSerializer,
    UpdateEventSerializer,
)


class EventListCreateView(APIView):
    permission_classes = [ReadOnlyOrAdminFinance]

    def get(self, request):
        events = Event.objects.all()
        return Response(EventListSerializer(events, many=True).data)

    def post(self, request):
        serializer = CreateEventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = serializer.save()

        record_activity(
            action='CREATE', entity_type='Event', entity_id=str(event.id),
            actor=request.user, details={'name': event.name},
        )

        return Response(EventListSerializer(event).data, status=201)


class EventDetailView(APIView):
    permission_classes = [ReadOnlyOrAdminFinance]

    def get_object(self, pk):
        try:
            return Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            raise NotFound('Event not found')

    def get(self, request, pk):
        return Response(EventDetailSerializer(self.get_object(pk)).data)

    def patch(self, request, pk):
        event = self.get_object(pk)
        serializer = UpdateEventSerializer(event, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        event = serializer.save()

        record_activity(
            action='UPDATE', entity_type='Event', entity_id=str(event.id),
            actor=request.user, details={'changed': list(request.data.keys())},
        )

        return Response(EventListSerializer(event).data)


# Ticketing data lands here as a CSV of `description,amount,occurredAt`
# rows, each becoming one EVENT_REVENUE transaction linked to the event.
# An automatic sync can replace this once the ticketing system opens an API.
class EventImportRevenueView(APIView):
    permission_classes = [ReadOnlyOrAdminFinance]

    def post(self, request, pk):
        try:
            event = Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            raise NotFound('Event not found')

        csv_text = request.data.get('csv', '')
        lines = [line.strip() for line in csv_text.splitlines() if line.strip()]
        if lines and lines[0].lower().startswith('description'):
            lines = lines[1:]

        rows = []
        for line in lines:
            cells = [c.strip() for c in line.split(',')]
            if len(cells) < 3:
                raise ValidationError(f'Malformed CSV row: "{line}"')
            description, amount_raw, occurred_at_raw = cells[0], cells[1], cells[2]
            occurred_at = parse_date(occurred_at_raw)
            if not description or not occurred_at:
                raise ValidationError(f'Malformed CSV row: "{line}"')
            try:
                amount = float(amount_raw)
            except ValueError:
                raise ValidationError(f'Malformed CSV row: "{line}"')

            rows.append(Transaction(
                type=TransactionType.EVENT_REVENUE,
                category='Ticketing',
                description=description,
                amount=amount,
                occurred_at=occurred_at,
                event=event,
                recorded_by=request.user,
            ))

        Transaction.objects.bulk_create(rows)

        record_activity(
            action='IMPORT_CSV', entity_type='Event', entity_id=str(event.id),
            actor=request.user, details={'rowsImported': len(rows)},
        )

        return Response({'rowsImported': len(rows)})
