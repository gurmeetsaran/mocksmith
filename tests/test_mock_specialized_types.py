"""Tests for mock data generation in specialized types."""

from db_types.specialized import URL, City, CountryCode, Email, PhoneNumber, State, ZipCode


class TestCountryCodeMock:
    """Test mock generation for CountryCode type."""

    def test_country_code_mock_format(self):
        """CountryCode should generate 2-letter ISO codes."""
        country = CountryCode()
        mock_value = country.mock()

        assert isinstance(mock_value, str)
        assert len(mock_value) == 2
        assert mock_value.isupper()

    def test_country_code_mock_validates(self):
        """Generated country codes should pass validation."""
        country = CountryCode()
        mock_value = country.mock()

        # Should not raise
        country.validate(mock_value)

    def test_country_code_generates_variety(self):
        """Should generate different country codes."""
        country = CountryCode()
        values = [country.mock() for _ in range(20)]

        unique_values = set(values)
        assert len(unique_values) > 5  # Should have variety


class TestStateMock:
    """Test mock generation for State type."""

    def test_state_mock_respects_length(self):
        """State mock should respect length constraint."""
        state = State()  # Default 50 chars
        mock_value = state.mock()

        assert isinstance(mock_value, str)
        assert len(mock_value) <= 50

    def test_state_custom_length(self):
        """State with custom length should work."""
        state = State(length=30)
        mock_value = state.mock()

        assert len(mock_value) <= 30

    def test_state_mock_validates(self):
        """Generated state should pass validation."""
        state = State()
        mock_value = state.mock()

        # Should not raise
        state.validate(mock_value)


class TestCityMock:
    """Test mock generation for City type."""

    def test_city_mock_format(self):
        """City should generate reasonable city names."""
        city = City()
        mock_value = city.mock()

        assert isinstance(mock_value, str)
        assert len(mock_value) > 0
        assert len(mock_value) <= 100  # Default length

    def test_city_custom_length(self):
        """City with custom length should work."""
        city = City(length=50)
        mock_value = city.mock()

        assert len(mock_value) <= 50

    def test_city_mock_validates(self):
        """Generated city should pass validation."""
        city = City()
        mock_value = city.mock()

        # Should not raise
        city.validate(mock_value)


class TestZipCodeMock:
    """Test mock generation for ZipCode type."""

    def test_zipcode_mock_format(self):
        """ZipCode should generate postal codes."""
        zipcode = ZipCode()
        mock_value = zipcode.mock()

        assert isinstance(mock_value, str)
        assert len(mock_value) <= 10  # Default length
        # Should contain numbers or alphanumeric
        assert any(c.isdigit() for c in mock_value)

    def test_zipcode_mock_validates(self):
        """Generated zip code should pass validation."""
        zipcode = ZipCode()
        mock_value = zipcode.mock()

        # Should not raise
        zipcode.validate(mock_value)


class TestEmailMock:
    """Test mock generation for Email type."""

    def test_email_mock_format(self):
        """Email should generate valid email addresses."""
        email = Email()
        mock_value = email.mock()

        assert isinstance(mock_value, str)
        assert "@" in mock_value
        assert "." in mock_value.split("@")[1]

    def test_email_mock_validates(self):
        """Generated email should pass validation."""
        email = Email()
        mock_value = email.mock()

        # Should not raise - validates both length and format
        email.validate(mock_value)

    def test_email_respects_length(self):
        """Email should respect length constraint."""
        email = Email(length=50)
        mock_value = email.mock()

        assert len(mock_value) <= 50

    def test_email_generates_variety(self):
        """Should generate different email addresses."""
        email = Email()
        values = [email.mock() for _ in range(10)]

        unique_values = set(values)
        assert len(unique_values) == 10  # All should be unique


class TestPhoneNumberMock:
    """Test mock generation for PhoneNumber type."""

    def test_phone_mock_format(self):
        """PhoneNumber should generate phone numbers."""
        phone = PhoneNumber()
        mock_value = phone.mock()

        assert isinstance(mock_value, str)
        assert len(mock_value) <= 20  # Default length

    def test_phone_mock_validates(self):
        """Generated phone number should pass validation."""
        phone = PhoneNumber()
        mock_value = phone.mock()

        # Should not raise
        phone.validate(mock_value)


class TestURLMock:
    """Test mock generation for URL type."""

    def test_url_mock_format(self):
        """URL should generate valid URLs."""
        url = URL()
        mock_value = url.mock()

        assert isinstance(mock_value, str)
        assert mock_value.startswith("http://") or mock_value.startswith("https://")
        assert "." in mock_value

    def test_url_mock_validates(self):
        """Generated URL should pass validation."""
        url = URL()
        mock_value = url.mock()

        # Should not raise - validates both length and format
        url.validate(mock_value)

    def test_url_respects_length(self):
        """URL should respect length constraint."""
        url = URL(length=100)
        mock_value = url.mock()

        assert len(mock_value) <= 100
