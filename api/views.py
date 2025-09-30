from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import connection
from django.utils import timezone
from .models import Person, Address, CreditCard
from .serializers import (
    PersonSerializer,
    CreatePersonSerializer,
    UpdatePersonSerializer,
    AddressSerializer,
    UnmaskedAddressSerializer,
    CreateAddressSerializer,
    UpdateAddressSerializer,
    CreditCardSerializer,
    CreateCreditCardSerializer,
    UpdateCreditCardSerializer,
    HealthSerializer,
)


class PersonListCreateView(generics.ListCreateAPIView):
    """List all persons or create a new person."""

    queryset = Person.objects.prefetch_related(
        "addresses", "credit_cards"
    ).all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreatePersonSerializer
        return PersonSerializer


class PersonDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a person."""

    queryset = Person.objects.prefetch_related(
        "addresses", "credit_cards"
    ).all()

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return UpdatePersonSerializer
        return PersonSerializer


class AddressListCreateView(generics.ListCreateAPIView):
    """List addresses for a person or create a new address."""

    def get_queryset(self):
        person_id = self.kwargs["person_id"]
        return Address.objects.filter(person_id=person_id)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateAddressSerializer
        return AddressSerializer

    def perform_create(self, serializer):
        person_id = self.kwargs["person_id"]
        person = get_object_or_404(Person, id=person_id)
        serializer.save(person=person)


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an address."""

    queryset = Address.objects.all()

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return UpdateAddressSerializer
        return AddressSerializer


class UnmaskedAddressDetailView(generics.RetrieveAPIView):
    """Retrieve an unmasked address."""

    queryset = Address.objects.all()
    serializer_class = UnmaskedAddressSerializer


class CreditCardListCreateView(generics.ListCreateAPIView):
    """List credit cards for a person or create a new credit card."""

    def get_queryset(self):
        person_id = self.kwargs["person_id"]
        return CreditCard.objects.filter(person_id=person_id)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateCreditCardSerializer
        return CreditCardSerializer

    def perform_create(self, serializer):
        person_id = self.kwargs["person_id"]
        person = get_object_or_404(Person, id=person_id)
        serializer.save(person=person)


class CreditCardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a credit card."""

    queryset = CreditCard.objects.all()

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return UpdateCreditCardSerializer
        return CreditCardSerializer


@api_view(["GET"])
def health_check(request):
    """Health check endpoint."""
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

        # Get basic statistics
        person_count = Person.objects.count()
        address_count = Address.objects.count()
        credit_card_count = CreditCard.objects.count()

        health_data = {
            "status": "healthy",
            "timestamp": timezone.now(),
            "database": "connected",
            "statistics": {
                "persons": person_count,
                "addresses": address_count,
                "creditCards": credit_card_count,
            },
        }

        serializer = HealthSerializer(health_data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as ex:
        health_data = {
            "status": "unhealthy",
            "timestamp": timezone.now(),
            "error": str(ex),
        }

        serializer = HealthSerializer(health_data)
        return Response(
            serializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
def readiness_check(request):
    """Readiness check endpoint."""
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

        readiness_data = {
            "status": "ready", 
            "timestamp": timezone.now(),
            "database": "connected",
            "statistics": {
                "total_persons": Person.objects.count(),
                "total_addresses": Address.objects.count(),
                "total_credit_cards": CreditCard.objects.count(),
            }
        }

        serializer = HealthSerializer(readiness_data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as ex:
        readiness_data = {
            "status": "not ready",
            "timestamp": timezone.now(),
            "database": "disconnected",
            "statistics": {},
            "error": str(ex),
        }

        serializer = HealthSerializer(readiness_data)
        return Response(
            serializer.data, status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
