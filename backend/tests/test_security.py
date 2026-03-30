import pytest

from app.utils.security import (
    validate_password_strength,
    create_access_token,
    verify_access_token,
    create_email_token,
    verify_email_token,
    hash_refresh_token,
    get_password_hash,
    verify_password,
)


class TestPasswordValidation:
    def test_password_too_short(self):
        with pytest.raises(ValueError):
            validate_password_strength("short")

    def test_password_no_uppercase(self):
        with pytest.raises(ValueError):
            validate_password_strength("alllowercase123!")

    def test_password_no_digit(self):
        with pytest.raises(ValueError):
            validate_password_strength("NoDigitsHere!!")

    def test_password_no_special(self):
        with pytest.raises(ValueError):
            validate_password_strength("NoSpecial12345")

    def test_password_ok(self):
        validate_password_strength("GoodPass123!")


class TestPasswordHashing:
    def test_hash_and_verify(self):
        h = get_password_hash("GoodPass123!")
        assert verify_password("GoodPass123!", h)
        assert not verify_password("WrongPass123!", h)


class TestAccessToken:
    def test_create_and_verify(self):
        token = create_access_token(email="test@test.com", user_id=1, role="student")
        data = verify_access_token(token)
        assert data is not None
        assert data.email == "test@test.com"
        assert data.user_id == 1
        assert data.role == "student"

    def test_invalid_token(self):
        result = verify_access_token("invalid.token.here")
        assert result is None


class TestEmailToken:
    def test_create_and_verify(self):
        token = create_email_token(email="test@test.com", purpose="email_verify", expires_hours=24)
        email = verify_email_token(token, "email_verify")
        assert email == "test@test.com"

    def test_wrong_purpose(self):
        token = create_email_token(email="test@test.com", purpose="email_verify", expires_hours=24)
        email = verify_email_token(token, "password_reset")
        assert email is None


class TestRefreshTokenHash:
    def test_deterministic(self):
        h1 = hash_refresh_token("test-token")
        h2 = hash_refresh_token("test-token")
        assert h1 == h2

    def test_different_inputs(self):
        h1 = hash_refresh_token("token-1")
        h2 = hash_refresh_token("token-2")
        assert h1 != h2
