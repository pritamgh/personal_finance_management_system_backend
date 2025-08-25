from datetime import datetime
from unittest import mock

import pytest
from sqlalchemy.orm import Session

from src.models import Transaction, TransactionType
from src.schemas import TransactionCreate, TransactionUpdate
from src.transaction import services


@pytest.fixture
def mock_db():
    return mock.MagicMock(spec=Session)


# Test create_transaction() function
def test_create_transaction(mock_db):
    data = TransactionCreate(
        amount=100.0,
        transaction_type="expense",
        transaction_type_category="groceries",
        description="Transaction create test",
        transaction_date=datetime(2025, 1, 2, 0, 0),
    )
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.side_effect = lambda x: setattr(x, "id", 99999)

    user_id = -1
    transaction_id = services.create_transaction(data, user_id, mock_db)

    assert mock_db.add.called
    assert mock_db.commit.called
    assert mock_db.refresh.called
    assert isinstance(transaction_id, int)
    assert transaction_id == 99999


# Test read_transaction_details() function
def test_read_transaction_details(mock_db):
    db_transaction = Transaction(
        id=1,
        amount=100.0,
        transaction_type="expense",
        transaction_type_category="groceries",
        description="Transaction",
        transaction_date=datetime(2025, 1, 2, 0, 0),
    )
    mock_db.query.return_value.filter.return_value.first.return_value = db_transaction

    transaction_id = -100
    user_id = -1
    transaction = services.read_transaction_details(transaction_id, user_id, mock_db)

    assert transaction is not None
    assert transaction.amount == 100.0


# Test update_transaction() function
def test_update_transaction(mock_db):
    create_data = TransactionCreate(
        amount=100.0,
        transaction_type="expense",
        transaction_type_category="groceries",
        description="Transaction create test",
        transaction_date=datetime(2025, 1, 2, 0, 0),
    )
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.side_effect = lambda x: setattr(x, "id", 99999)

    user_id = -1
    transaction_id = services.create_transaction(create_data, user_id, mock_db)

    update_data = TransactionUpdate(amount=150.0)
    mock_db.commit.return_value = None
    services.update_transaction(update_data, transaction_id, user_id, mock_db)

    assert mock_db.commit.called


# Test delete_transaction() function
def test_delete_transaction(mock_db):
    create_data = TransactionCreate(
        amount=100.0,
        transaction_type="expense",
        transaction_type_category="groceries",
        description="Transaction create test",
        transaction_date=datetime(2025, 1, 2, 0, 0),
    )
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.side_effect = lambda x: setattr(x, "id", 99999)

    user_id = -1
    transaction_id = services.create_transaction(create_data, user_id, mock_db)

    mock_db.commit.return_value = None
    services.delete_transaction(transaction_id, user_id, mock_db)

    assert mock_db.commit.called


# Test list_transactions() function
def test_list(mock_db):
    transaction_result = [
        (1, 100, "income", "category1"),
        (2, 200, "income", "category2"),
    ]
    # Arrange: Mock the query result for db.query().filter().offset().limit().all()
    mock_db.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = (
        transaction_result
    )

    # Act: Call the function with params
    params = {
        "transaction_type": "income",
        "transaction_type_category": "category1",
        "validated_query": "test",
        "skip": 0,
        "limit": 10,
    }
    result = services.list_transactions(1, params, mock_db)

    # Assert: Check query filters
    mock_db.query.return_value.filter.assert_called_with(
        Transaction.user_id == 1,
        Transaction.transaction_type == TransactionType("income").name,
        Transaction.transaction_type_category == "category1",
        Transaction.description.ilike("%test%"),
    )

    # Assert: Check that the result matches the mock data
    assert result == transaction_result
