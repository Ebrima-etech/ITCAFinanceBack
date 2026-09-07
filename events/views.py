from django.utils.dateparse import parse_date
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated

from accounts.permissions import ReadOnlyOrAdminFinance
from activitylog.utils import record_activity
from ledger.models import Transaction, TransactionType
from .models import Event, EventPartner
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

    def delete(self, request, pk):
        event = self.get_object(pk)
        event_id = str(event.id)
        event.delete()

        record_activity(action='DELETE', entity_type='Event', entity_id=event_id, actor=request.user)

        return Response({'id': event_id})


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


# Event Partners (Sponsorship applications)
class EventPartnerListCreateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # Public list - show only approved partners
        partners = EventPartner.objects.filter(status='approved')
        data = [
            {
                'id': str(p.id),
                'organizationName': p.organization_name,
                'logoUrl': p.logo_url,
                'sponsorshipLevel': p.sponsorship_level,
            }
            for p in partners
        ]
        return Response(data)

    def post(self, request):
        # Public application submission
        data = {
            'organization_name': request.data.get('organizationName'),
            'contact_person': request.data.get('contactPerson'),
            'email': request.data.get('email'),
            'phone': request.data.get('phone'),
            'website': request.data.get('website'),
            'logo_url': request.data.get('logoUrl'),
            'description': request.data.get('description'),
            'sponsorship_level': request.data.get('sponsorshipLevel', 'bronze'),
        }

        if not all([data['organization_name'], data['contact_person'], data['email'], data['phone']]):
            raise ValidationError('Missing required fields')

        partner = EventPartner.objects.create(**data)

        record_activity(
            action='CREATE', entity_type='EventPartner', entity_id=str(partner.id),
            actor=None, details={'organization': partner.organization_name},
        )

        return Response({
            'id': str(partner.id),
            'status': partner.status,
            'message': 'Application submitted successfully. We will review your application shortly.'
        }, status=201)


class EventPartnerDetailView(APIView):
    permission_classes = [ReadOnlyOrAdminFinance]

    def get_object(self, pk):
        try:
            return EventPartner.objects.get(pk=pk)
        except EventPartner.DoesNotExist:
            raise NotFound('Partner not found')

    def get(self, request, pk):
        partner = self.get_object(pk)
        return Response({
            'id': str(partner.id),
            'organizationName': partner.organization_name,
            'contactPerson': partner.contact_person,
            'email': partner.email,
            'phone': partner.phone,
            'website': partner.website,
            'logoUrl': partner.logo_url,
            'description': partner.description,
            'sponsorshipLevel': partner.sponsorship_level,
            'status': partner.status,
            'createdAt': partner.created_at,
        })

    def patch(self, request, pk):
        partner = self.get_object(pk)
        if 'status' in request.data:
            partner.status = request.data['status']
            partner.save()

            record_activity(
                action='UPDATE', entity_type='EventPartner', entity_id=str(partner.id),
                actor=request.user, details={'status': partner.status},
            )

        return Response({
            'id': str(partner.id),
            'status': partner.status,
            'organizationName': partner.organization_name,
        })
