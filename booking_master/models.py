from django.db import models
from rooms.models import RoomType
from reservation_source_master.models import ReservationSource

class Booking(models.Model):
    ID_PROOF_CHOICES = [
        ('AADHAR', 'Aadhar Card'),
        ('PAN', 'PAN Card'),
        ('DRIVING_LICENCE', 'Driving Licence'),
        ('OTHER', 'Other'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('UPI', 'UPI'),
        ('CARD', 'Card'),
        ('OTHER', 'Other'),
    ]

    booking_id = models.AutoField(primary_key=True)
    customer_first_name = models.CharField(max_length=100)
    customer_last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    id_proof_type = models.CharField(max_length=20, choices=ID_PROOF_CHOICES)
    id_number = models.CharField(max_length=50)
    id_photo = models.ImageField(upload_to='guest_id_proofs/')
    booking_date = models.DateField(auto_now_add=True)
    booking_time = models.TimeField(auto_now_add=True)
    room_type = models.ForeignKey(RoomType, on_delete=models.PROTECT)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
    reservation_source = models.ForeignKey(ReservationSource, on_delete=models.PROTECT)

    def __str__(self):
        return f"Booking {self.booking_id} - {self.customer_first_name} {self.customer_last_name}"
