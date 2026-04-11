from django.db import transaction
from rest_framework import serializers
from .models import Event, Reservation


class EventSerializer(serializers.ModelSerializer):
    reservations_count = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = '__all__'

    def get_reservations_count(self, obj):
        return obj.reservations.filter(status='confirmed').count()

    def validate(self, data):
        available = data.get('available_seats')
        total = data.get('total_seats')

        # on update, fall back to existing values
        if available is None and self.instance:
            available = self.instance.available_seats
        if total is None and self.instance:
            total = self.instance.total_seats

        if available is not None and total is not None and available > total:
            raise serializers.ValidationError({
                'available_seats': ['available_seats cannot exceed total_seats.']
            })
        return data


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = '__all__'

    def validate_seats_reserved(self, value):
        if value < 1:
            raise serializers.ValidationError("Ensure this value is greater than or equal to 1.")
        return value

    def create(self, validated_data):
        event = validated_data['event']
        seats = validated_data['seats_reserved']

        # only allow booking for upcoming or ongoing events
        if event.status not in ('upcoming', 'ongoing'):
            raise serializers.ValidationError({
                'event': ['Reservations are only allowed for upcoming or ongoing events.']
            })

        # lock the event row so two people can't book the last seat at the same time
        with transaction.atomic():
            event = Event.objects.select_for_update().get(pk=event.pk)

            if seats > event.available_seats:
                raise serializers.ValidationError({
                    'seats_reserved': ['Not enough available seats.']
                })

            event.available_seats -= seats
            event.save()

        validated_data['event'] = event
        return super().create(validated_data)
