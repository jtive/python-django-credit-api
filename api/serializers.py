from rest_framework import serializers
from django.core.validators import RegexValidator
from .models import Person, Address, CreditCard
from .services import DataMaskingService


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "id",
            "person",
            "address_type",
            "street_address",
            "city",
            "state",
            "zip_code",
            "country",
            "is_primary",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Apply data masking
        masking_service = DataMaskingService()
        data["street_address"] = masking_service.mask_address(
            data["street_address"]
        )
        data["city"] = masking_service.mask_city(data["city"])
        data["state"] = masking_service.mask_state(data["state"])
        data["zip_code"] = masking_service.mask_zip_code(data["zip_code"])
        data["country"] = masking_service.mask_country(data["country"])
        return data


class UnmaskedAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "id",
            "person",
            "address_type",
            "street_address",
            "city",
            "state",
            "zip_code",
            "country",
            "is_primary",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class CreateAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "address_type",
            "street_address",
            "city",
            "state",
            "zip_code",
            "country",
            "is_primary",
        ]


class UpdateAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "address_type",
            "street_address",
            "city",
            "state",
            "zip_code",
            "country",
            "is_primary",
        ]


class CreditCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditCard
        fields = [
            "id",
            "person",
            "card_type",
            "last_four_digits",
            "expiration_month",
            "expiration_year",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Apply data masking
        masking_service = DataMaskingService()
        data["last_four_digits"] = masking_service.mask_credit_card(
            data["last_four_digits"]
        )
        return data


class CreateCreditCardSerializer(serializers.ModelSerializer):
    card_number = serializers.CharField(
        max_length=19,
        validators=[
            RegexValidator(
                regex=r"^\d{13,19}$",
                message="Card Number must be 13-19 digits",
            )
        ],
    )

    class Meta:
        model = CreditCard
        fields = [
            "card_type",
            "card_number",
            "expiration_month",
            "expiration_year",
            "is_active",
        ]

    def create(self, validated_data):
        card_number = validated_data.pop("card_number")
        # Extract last four digits
        validated_data["last_four_digits"] = card_number[-4:]
        return super().create(validated_data)


class UpdateCreditCardSerializer(serializers.ModelSerializer):
    card_number = serializers.CharField(
        max_length=19,
        required=False,
        validators=[
            RegexValidator(
                regex=r"^\d{13,19}$",
                message="Card Number must be 13-19 digits",
            )
        ],
    )

    class Meta:
        model = CreditCard
        fields = [
            "card_type",
            "card_number",
            "expiration_month",
            "expiration_year",
            "is_active",
        ]

    def update(self, instance, validated_data):
        card_number = validated_data.pop("card_number", None)
        if card_number:
            validated_data["last_four_digits"] = card_number[-4:]
        return super().update(instance, validated_data)


class PersonSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True, read_only=True)
    credit_cards = CreditCardSerializer(many=True, read_only=True)

    class Meta:
        model = Person
        fields = [
            "id",
            "first_name",
            "last_name",
            "birth_date",
            "ssn",
            "created_at",
            "updated_at",
            "addresses",
            "credit_cards",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Apply data masking
        masking_service = DataMaskingService()
        data["ssn"] = masking_service.mask_ssn(data["ssn"])
        return data


class CreatePersonSerializer(serializers.ModelSerializer):
    addresses = CreateAddressSerializer(many=True, required=False)
    credit_cards = CreateCreditCardSerializer(many=True, required=False)
    ssn = serializers.CharField(
        validators=[
            RegexValidator(
                regex=r"^\d{9}$", message="SSN must be exactly 9 digits"
            )
        ]
    )

    class Meta:
        model = Person
        fields = [
            "first_name",
            "last_name",
            "birth_date",
            "ssn",
            "addresses",
            "credit_cards",
        ]

    def create(self, validated_data):
        addresses_data = validated_data.pop("addresses", [])
        credit_cards_data = validated_data.pop("credit_cards", [])

        person = Person.objects.create(**validated_data)

        # Create addresses
        for address_data in addresses_data:
            Address.objects.create(person=person, **address_data)

        # Create credit cards
        for card_data in credit_cards_data:
            card_number = card_data.pop("card_number")
            card_data["last_four_digits"] = card_number[-4:]
            CreditCard.objects.create(person=person, **card_data)

        return person


class UpdatePersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ["first_name", "last_name", "birth_date"]


class HealthSerializer(serializers.Serializer):
    status = serializers.CharField()
    timestamp = serializers.DateTimeField()
    database = serializers.CharField()
    statistics = serializers.DictField()
