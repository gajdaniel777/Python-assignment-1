from django.db import models

class Event(models.Model):
    title = models.CharField(max_length=200)
    venue = models.CharField(max_length=200)
    date = models.DateField()
    total_seats = models.PositiveIntegerField()
    available_seats = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=[
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default='upcoming')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return self.title


class Reservation(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='reservations')
    attendee_name = models.CharField(max_length=200)
    attendee_email = models.EmailField()
    seats_reserved = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=[
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ], default='confirmed')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.attendee_name} - {self.event.title}"
