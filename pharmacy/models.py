from django.db import models
from django.contrib.auth.models import User


# =========================
# PHARMACY
# =========================
class Pharmacy(models.Model):
    name = models.CharField(max_length=150)
    location_name = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    phone = models.CharField(max_length=20)
    opening_hours = models.CharField(max_length=100)
    license_number = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# =========================
# PHARMACY STAFF
# =========================
class PharmacyStaff(models.Model):
    pharmacy = models.ForeignKey(
        Pharmacy,
        on_delete=models.CASCADE,
        related_name="staff"
    )
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.name


# =========================
# MEDICINE
# =========================
class Medicine(models.Model):
    name = models.CharField(max_length=150)
    brand = models.CharField(max_length=100)
    requires_prescription = models.BooleanField(default=False)

    def __str__(self):
        return self.name


# =========================
# STOCK (INVENTORY)
# =========================
class Stock(models.Model):
    pharmacy = models.ForeignKey(
        Pharmacy,
        on_delete=models.CASCADE,
        related_name="stocks"
    )
    medicine = models.ForeignKey(
        Medicine,
        on_delete=models.CASCADE,
        related_name="stocks"
    )
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('pharmacy', 'medicine')  # one record per medicine per pharmacy

    def __str__(self):
        return f"{self.pharmacy.name} - {self.medicine.name} ({self.quantity})"


# =========================
# RESERVATION (WORKFLOW SYSTEM)
# =========================
class Reservation(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reservations"
    )

    pharmacy = models.ForeignKey(
        Pharmacy,
        on_delete=models.CASCADE,
        related_name="reservations"
    )

    medicine = models.ForeignKey(
        Medicine,
        on_delete=models.CASCADE,
        related_name="reservations"
    )

    quantity = models.PositiveIntegerField(default=1)

    reservation_date = models.DateTimeField(auto_now_add=True)
    expiry_time = models.DateTimeField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    def __str__(self):
        return f"{self.user.username} - {self.medicine.name} ({self.status})"