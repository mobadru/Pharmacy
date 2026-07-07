from django.db import models
from django.contrib.auth.models import User


# =====================================
# USER PROFILE
# =====================================

class UserProfile(models.Model):

    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("staff", "Staff"),
        ("patient", "Patient"),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="patient"
    )

    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=200, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


# =====================================
# PHARMACY
# =====================================

class Pharmacy(models.Model):

    name = models.CharField(max_length=150)
    location_name = models.CharField(max_length=200)

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6
    )

    phone = models.CharField(max_length=20)

    opening_hours = models.CharField(max_length=100)

    license_number = models.CharField(
        max_length=100,
        unique=True
    )

    def __str__(self):
        return self.name


# =====================================
# PHARMACY STAFF
# =====================================

class PharmacyStaff(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="staff_profile"
    )

    pharmacy = models.ForeignKey(
        Pharmacy,
        on_delete=models.CASCADE,
        related_name="staff"
    )

    def __str__(self):
        return self.user.username


# =====================================
# PRODUCT
# =====================================

class Product(models.Model):

    CATEGORY_CHOICES = (
        ("medicine", "Medicine"),
        ("equipment", "Medical Equipment"),
        ("cosmetic", "Cosmetic"),
        ("vitamin", "Vitamin"),
        ("baby", "Baby Care"),
        ("supply", "Medical Supply"),
        ("other", "Other"),
    )

    UNIT_CHOICES = (
        ("tablet", "Tablet"),
        ("capsule", "Capsule"),
        ("bottle", "Bottle"),
        ("tube", "Tube"),
        ("box", "Box"),
        ("piece", "Piece"),
        ("pack", "Pack"),
        ("vial", "Vial"),
        ("sachet", "Sachet"),
    )

    name = models.CharField(max_length=150)

    # Manual entry
    brand = models.CharField(
        max_length=100,
        blank=True
    )

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="medicine"
    )

    unit = models.CharField(
        max_length=20,
        choices=UNIT_CHOICES,
        default="piece"
    )

    requires_prescription = models.BooleanField(
        default=False
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name


# =====================================
# STOCK
# =====================================

class Stock(models.Model):

    pharmacy = models.ForeignKey(
        Pharmacy,
        on_delete=models.CASCADE,
        related_name="stocks"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="stocks"
    )

    quantity = models.PositiveIntegerField(default=0)

    batch_number = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    expiry_date = models.DateField(
        blank=True,
        null=True
    )

    class Meta:
        unique_together = ("pharmacy", "product")

    def __str__(self):
        return f"{self.pharmacy.name} - {self.product.name}"


# =====================================
# RESERVATION
# =====================================

class Reservation(models.Model):

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("expired", "Expired"),
        ("completed", "Completed"),
    )

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

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reservations"
    )

    quantity = models.PositiveIntegerField(default=1)

    reservation_date = models.DateTimeField(
        auto_now_add=True
    )

    expiry_time = models.DateTimeField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processed_reservations"
    )

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"