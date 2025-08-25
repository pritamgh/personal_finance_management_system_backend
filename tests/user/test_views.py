from unittest import mock

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from main import app
from src.dependencies import get_db
from src.schemas import SignUp

client = TestClient(app)


@pytest.fixture
def mock_db():
    return mock.MagicMock(spec=Session)


def test_sign_up_success():
    user_data = {"email": "test@example.com", "password": "testpassword"}

    with mock.patch(
        "src.dependencies.get_db", return_value=mock.MagicMock(spec=Session)
    ):
        # Mock create_user to return a user ID
        with mock.patch("src.user.services.create_user", return_value=1):
            response = client.post("/api/v1/auth/sign-up/", json=user_data)

    response = response.json()
    assert response[0] == {"id": 1, "status": "success"}
