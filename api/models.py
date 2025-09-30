import uuid
from django.db import models
from django.core.validators import (
    RegexValidator,
    MinValueValidator,
    MaxValueValidator,
)


class Person(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField()
    ssn = models.CharField(
        max_length=11,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r"^(\d{9}|\d{3}-\d{2}-\d{4})$",
                message="SSN must be 9 digits or in format XXX-XX-XXXX",
            )
        ],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "api_person"
        ordering = [
            "-created_at"
        ]  # Add default ordering to fix pagination warnings
        constraints = [
            models.CheckConstraint(
                check=models.Q(ssn__isnull=True)
                | models.Q(ssn__regex=r"^\d{9}$")
                | models.Q(ssn__regex=r"^\d{3}-\d{2}-\d{4}$"),
                name="chk_ssn_format",
            )
        ]

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Address(models.Model):
    ADDRESS_TYPE_CHOICES = [
        ("Home", "Home"),
        ("Work", "Work"),
        ("Mailing", "Mailing"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    person = models.ForeignKey(
        Person, on_delete=models.CASCADE, related_name="addresses"
    )
    address_type = models.CharField(
        max_length=20, choices=ADDRESS_TYPE_CHOICES
    )
    street_address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    zip_code = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex=r"^\d{5}(-\d{4})?$",
                message="Zip Code must be in format 12345 or 12345-6789",
            )
        ],
    )
    country = models.CharField(max_length=2, default="US")
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "api_address"
        ordering = [
            "-created_at"
        ]  # Add default ordering to fix pagination warnings

    def __str__(self) -> str:
        return (
            f"{self.street_address}, {self.city}, {self.state} {self.zip_code}"
        )


class CreditCard(models.Model):
    CARD_TYPE_CHOICES = [
        ("Visa", "Visa"),
        ("MasterCard", "MasterCard"),
        ("American Express", "American Express"),
        ("Discover", "Discover"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    person = models.ForeignKey(
        Person, on_delete=models.CASCADE, related_name="credit_cards"
    )
    card_type = models.CharField(max_length=20, choices=CARD_TYPE_CHOICES)
    last_four_digits = models.CharField(max_length=4)
    expiration_month = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    expiration_year = models.IntegerField(
        validators=[MinValueValidator(2024), MaxValueValidator(2030)]
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "api_creditcard"
        ordering = [
            "-created_at"
        ]  # Add default ordering to fix pagination warnings

    def __str__(self) -> str:
        return f"{self.card_type} ****{self.last_four_digits}"
