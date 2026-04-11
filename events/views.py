from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Event, Reservation
from .serializers import EventSerializer, ReservationSerializer


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_queryset(self):
        qs = super().get_queryset()

        # filter by exact status if provided
        s = self.request.query_params.get('status')
        if s:
            qs = qs.filter(status=s)

        # filter by venue name (case-insensitive)
        v = self.request.query_params.get('venue')
        if v:
            qs = qs.filter(venue__icontains=v)

        return qs


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

    def get_queryset(self):
        qs = super().get_queryset()

        # filter by event id if provided
        event_id = self.request.query_params.get('event_id')
        if event_id:
            qs = qs.filter(event_id=event_id)

        return qs

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        reservation = self.get_object()

        if reservation.status == 'cancelled':
            return Response(
                {'detail': 'This reservation is already cancelled.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # cancel and give seats back
        with transaction.atomic():
            reservation.status = 'cancelled'
            reservation.save()

            event = Event.objects.select_for_update().get(pk=reservation.event_id)
            event.available_seats += reservation.seats_reserved
            event.save()

        return Response(ReservationSerializer(reservation).data)
