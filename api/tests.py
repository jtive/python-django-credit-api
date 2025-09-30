from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Person, Address, CreditCard


class PersonAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # This runs once per test class
        cls.person_data = {
            "first_name": "John",
            "last_name": "Doe",
            "birth_date": "1990-01-01",
            "ssn": "123456789",
        }

    def setUp(self):
        # Clear all data before each test method -
        #  use raw SQL to ensure complete cleanup
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM api_creditcard")
            cursor.execute("DELETE FROM api_address")
            cursor.execute("DELETE FROM api_person")

    def test_create_person(self):
        """Test creating a new person."""
        url = reverse("api:person-list-create")
        response = self.client.post(url, self.person_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Person.objects.count(), 1)
        self.assertEqual(Person.objects.get().first_name, "John")

    def test_list_persons(self):
        """Test listing all persons."""
        Person.objects.create(**self.person_data)
        url = reverse("api:person-list-create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_get_person(self):
        """Test retrieving a specific person."""
        person = Person.objects.create(**self.person_data)
        url = reverse("api:person-detail", kwargs={"pk": person.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "John")
        # Check that SSN is masked
        self.assertTrue(response.data["ssn"].startswith("***-**-"))

    def test_update_person(self):
        """Test updating a person."""
        person = Person.objects.create(**self.person_data)
        url = reverse("api:person-detail", kwargs={"pk": person.id})
        update_data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "birth_date": "1990-01-01",
        }
        response = self.client.put(url, update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        person.refresh_from_db()
        self.assertEqual(person.first_name, "Jane")

    def test_delete_person(self):
        """Test deleting a person."""
        person = Person.objects.create(**self.person_data)
        url = reverse("api:person-detail", kwargs={"pk": person.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Person.objects.count(), 0)


class AddressAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # This runs once per test class
        cls.person_data = {
            "first_name": "John",
            "last_name": "Doe",
            "birth_date": "1990-01-01",
            "ssn": "123456789",
        }

    def setUp(self):
        # Clear all data before each test method -
        #  use raw SQL to ensure complete cleanup
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM api_creditcard")
            cursor.execute("DELETE FROM api_address")
            cursor.execute("DELETE FROM api_person")

        # Create fresh person for each test
        self.person = Person.objects.create(**self.person_data)
        self.address_data = {
            "address_type": "Home",
            "street_address": "123 Main St",
            "city": "Anytown",
            "state": "NY",
            "zip_code": "12345",
            "country": "US",
            "is_primary": True,
        }

    def test_create_address(self):
        """Test creating a new address."""
        url = reverse(
            "api:address-list-create", kwargs={"person_id": self.person.id}
        )
        response = self.client.post(url, self.address_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Address.objects.count(), 1)
        self.assertEqual(Address.objects.get().street_address, "123 Main St")

    def test_get_addresses_for_person(self):
        """Test listing addresses for a person."""
        Address.objects.create(person=self.person, **self.address_data)
        url = reverse(
            "api:address-list-create", kwargs={"person_id": self.person.id}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        # Check that address is masked
        self.assertTrue(
            response.data["results"][0]["street_address"].startswith("12")
        )
        self.assertTrue("*" in response.data["results"][0]["street_address"])

    def test_get_unmasked_address(self):
        """Test getting unmasked address."""
        address = Address.objects.create(
            person=self.person, **self.address_data
        )
        url = reverse("api:address-unmasked", kwargs={"pk": address.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that address is not masked
        self.assertEqual(response.data["street_address"], "123 Main St")


class CreditCardAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # This runs once per test class
        cls.person_data = {
            "first_name": "John",
            "last_name": "Doe",
            "birth_date": "1990-01-01",
            "ssn": "123456789",
        }

    def setUp(self):
        # Clear all data before each test method - use
        #  raw SQL to ensure complete cleanup
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM api_creditcard")
            cursor.execute("DELETE FROM api_address")
            cursor.execute("DELETE FROM api_person")

        # Create fresh person for each test
        self.person = Person.objects.create(**self.person_data)
        self.credit_card_data = {
            "card_type": "Visa",
            "card_number": "4111111111111111",
            "expiration_month": 12,
            "expiration_year": 2025,
            "is_active": True,
        }

    def test_create_credit_card(self):
        """Test creating a new credit card."""
        url = reverse(
            "api:creditcard-list-create", kwargs={"person_id": self.person.id}
        )
        response = self.client.post(url, self.credit_card_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CreditCard.objects.count(), 1)
        credit_card = CreditCard.objects.get()
        self.assertEqual(credit_card.card_type, "Visa")
        self.assertEqual(credit_card.last_four_digits, "1111")

    def test_get_credit_cards_for_person(self):
        """Test listing credit cards for a person."""
        CreditCard.objects.create(
            person=self.person,
            card_type="Visa",
            last_four_digits="1111",
            expiration_month=12,
            expiration_year=2025,
        )
        url = reverse(
            "api:creditcard-list-create", kwargs={"person_id": self.person.id}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        # Check that credit card is masked
        self.assertTrue(
            response.data["results"][0]["last_four_digits"].startswith("****")
        )


class HealthCheckTestCase(APITestCase):
    def setUp(self):
        # Clear all data before each test - use
        #  raw SQL to ensure complete cleanup
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM api_creditcard")
            cursor.execute("DELETE FROM api_address")
            cursor.execute("DELETE FROM api_person")

    def test_health_check(self):
        """Test health check endpoint."""
        url = reverse("api:health-check")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "healthy")
        self.assertEqual(response.data["database"], "connected")
        self.assertIn("statistics", response.data)

    def test_readiness_check(self):
        """Test readiness check endpoint."""
        url = reverse("api:readiness-check")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "ready")
