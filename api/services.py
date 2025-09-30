import re
from typing import Optional


class DataMaskingService:
    """Service for masking sensitive data in API responses."""

    def mask_ssn(self, ssn: Optional[str]) -> str:
        """Mask SSN, showing only last 4 digits."""
        if not ssn:
            return ""

        # Remove any formatting
        clean_ssn = re.sub(r"[^\d]", "", ssn)

        if len(clean_ssn) == 9:
            return f"***-**-{clean_ssn[-4:]}"
        elif len(clean_ssn) == 11:  # Already formatted
            return f"***-**-{clean_ssn[-4:]}"

        return "***-**-****"

    def mask_address(self, address: str) -> str:
        """Mask street address, showing only first few characters."""
        if not address:
            return ""

        if len(address) <= 5:
            return "*" * len(address)

        # Show first 2 characters and mask the rest
        return address[:2] + "*" * (len(address) - 2)

    def mask_city(self, city: str) -> str:
        """Mask city name, showing only first character."""
        if not city:
            return ""

        if len(city) <= 2:
            return "*" * len(city)

        return city[0] + "*" * (len(city) - 1)

    def mask_state(self, state: str) -> str:
        """Mask state abbreviation."""
        if not state:
            return ""

        return "*" * len(state)

    def mask_zip_code(self, zip_code: str) -> str:
        """Mask zip code, showing only last 2 digits."""
        if not zip_code:
            return ""

        # Remove any formatting
        clean_zip = re.sub(r"[^\d]", "", zip_code)

        if len(clean_zip) >= 2:
            return "*" * (len(clean_zip) - 2) + clean_zip[-2:]

        return "*" * len(clean_zip)

    def mask_country(self, country: str) -> str:
        """Mask country code."""
        if not country:
            return ""

        return "*" * len(country)

    def mask_credit_card(self, last_four: str) -> str:
        """Mask credit card last four digits."""
        if not last_four:
            return ""

        if len(last_four) >= 4:
            return "****" + last_four[-4:]

        return "*" * len(last_four)
