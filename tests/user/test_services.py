from datetime import datetime, timedelta, timezone
from unittest import mock

import jwt
import pytest
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.config import Config
from src.models import User
from src.schemas import SignUp
from src.user import services


@pytest.fixture
def mock_db():
    return mock.MagicMock(spec=Session)


# Test get_pwd_context() function
def test_get_pwd_context():
    pwd_context = services.get_pwd_context()
    password = "secret_password"
    hashed_password = pwd_context.hash(password)

    assert pwd_context.verify(password, hashed_password)


# Test create_user() function
@pytest.fixture
def mock_user():
    return SignUp(email="test@example.com", password="testpassword")


def test_create_user(mock_user, mock_db):
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.side_effect = lambda x: setattr(x, "id", 1)

    user_id = services.create_user(mock_user, mock_db)

    assert mock_db.add.called
    assert mock_db.commit.called
    assert mock_db.refresh.called
    assert isinstance(user_id, int)
    assert user_id == 1


# Test get_user() function
def test_get_user_found(mock_db):
    email = "test@example.com"
    db_user = User(id=1, email=email, password="testpassword")
    mock_db.query.return_value.filter.return_value.one_or_none.return_value = db_user

    user = services.get_user(email, mock_db)

    assert user is not None
    assert user.email == email


def test_get_user_not_found(mock_db):
    email = "test@example.com"
    mock_db.query.return_value.filter.return_value.one_or_none.return_value = None

    user = services.get_user(email, mock_db)

    assert user is None


# Test verify_password() function
def test_verify_password():
    pwd_context = services.get_pwd_context()
    password = "testpassword"
    hashed_password = pwd_context.hash(password)

    is_valid = services.verify_password(password, hashed_password)

    assert is_valid is True


def test_verify_password_invalid():
    pwd_context = services.get_pwd_context()
    password = "testpassword"
    wrong_password = "wrongpassword"
    hashed_password = pwd_context.hash(password)

    is_valid = services.verify_password(wrong_password, hashed_password)

    assert is_valid is False


# Test authenticate_user() function
def test_authenticate_user(mock_db):
    email = "test@example.com"
    requested_password = "testpassword"
    pwd_context = services.get_pwd_context()
    hashed_password = pwd_context.hash(requested_password)
    db_user = User(id=1, email=email, password=hashed_password)
    mock_db.query.return_value.filter.return_value.one_or_none.return_value = db_user

    user, msg = services.authenticate_user(email, requested_password, mock_db)

    assert user is not None
    assert user.email == email
    assert msg == "User authenticated."


def test_authenticate_user_invalid_password(mock_db):
    email = "test@example.com"
    requested_password = "wrongpassword"
    pwd_context = services.get_pwd_context()
    hashed_password = pwd_context.hash("testpassword")
    db_user = User(id=1, email=email, password=hashed_password)
    mock_db.query.return_value.filter.return_value.one_or_none.return_value = db_user

    user, msg = services.authenticate_user(email, requested_password, mock_db)

    assert user is False
    assert msg == "Incorrect password."


def test_authenticate_user_not_found(mock_db):
    email = "test@example.com"
    requested_password = "testpassword"
    mock_db.query.return_value.filter.return_value.one_or_none.return_value = None

    user, msg = services.authenticate_user(email, requested_password, mock_db)

    assert user is False
    assert msg == "Email not found or incorrect."


# Test create_access_token() function
def test_create_access_token():
    data = {"sub": "test@example.com"}
    Config.settings.SECRET_KEY = "testsecretkey"
    Config.settings.ALGORITHM = "HS256"
    Config.settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30

    token = services.create_access_token(data)

    decoded_token = jwt.decode(
        token, Config.settings.SECRET_KEY, algorithms=[Config.settings.ALGORITHM]
    )

    assert decoded_token["sub"] == data["sub"]
    assert "exp" in decoded_token
    assert datetime.fromtimestamp(decoded_token["exp"], tz=timezone.utc) > datetime.now(
        tz=timezone.utc
    )


# Test verify_token() function
def test_verify_token_valid():
    data = {"sub": "test@example.com"}
    Config.settings.SECRET_KEY = "testsecretkey"
    Config.settings.ALGORITHM = "HS256"
    Config.settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30
    token = jwt.encode(
        data, Config.settings.SECRET_KEY, algorithm=Config.settings.ALGORITHM
    )

    email = services.verify_token(token)

    assert email == data["sub"]


def test_verify_token_expired():
    data = {
        "sub": "test@example.com",
        "exp": datetime.now(tz=timezone.utc) - timedelta(minutes=1),
    }
    Config.settings.SECRET_KEY = "testsecretkey"
    Config.settings.ALGORITHM = "HS256"
    token = jwt.encode(
        data, Config.settings.SECRET_KEY, algorithm=Config.settings.ALGORITHM
    )

    with pytest.raises(HTTPException) as excinfo:
        services.verify_token(token)

    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert excinfo.value.detail == "Token has expired."


def test_verify_token_invalid():
    token = "invalidtoken"
    Config.settings.SECRET_KEY = "testsecretkey"
    Config.settings.ALGORITHM = "HS256"

    with pytest.raises(HTTPException) as excinfo:
        services.verify_token(token)

    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert excinfo.value.detail == "Invalid token."


# Test get_current_user() function
def test_get_current_user_valid_token(mock_db):
    email = "test@example.com"
    token_data = {"sub": email}
    Config.settings.SECRET_KEY = "testsecretkey"
    Config.settings.ALGORITHM = "HS256"
    token = jwt.encode(
        token_data, Config.settings.SECRET_KEY, algorithm=Config.settings.ALGORITHM
    )
    db_user = User(id=1, email=email, password="hashedpassword")
    mock_db.query.return_value.filter.return_value.one_or_none.return_value = db_user

    # Mock verify_token to return the email
    with mock.patch("src.user.services.verify_token", return_value=email):
        user = services.get_current_user(token, mock_db)

    assert user is not None
    assert user.email == email


def test_get_current_user_invalid_token(mock_db):
    token = "invalidtoken"
    Config.settings.SECRET_KEY = "testsecretkey"
    Config.settings.ALGORITHM = "HS256"

    # Mock verify_token to raise an HTTPException
    with mock.patch(
        "src.user.services.verify_token",
        side_effect=HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        ),
    ):
        with pytest.raises(HTTPException) as excinfo:
            services.get_current_user(token, mock_db)

        assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert excinfo.value.detail == "Invalid token"


def test_get_current_user_user_not_found(mock_db):
    email = "test@example.com"
    token_data = {"sub": email}
    Config.settings.SECRET_KEY = "testsecretkey"
    Config.settings.ALGORITHM = "HS256"
    token = jwt.encode(
        token_data, Config.settings.SECRET_KEY, algorithm=Config.settings.ALGORITHM
    )

    # Mock verify_token to return the email
    with mock.patch("src.user.services.verify_token", return_value=email):
        # Mock get_user to return None
        mock_db.query.return_value.filter.return_value.one_or_none.return_value = None

        with pytest.raises(HTTPException) as excinfo:
            services.get_current_user(token, mock_db)

        assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert excinfo.value.detail == "User not found."
