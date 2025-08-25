from itertools import groupby
from typing import Union

from fastapi.encoders import jsonable_encoder
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from src.kafka.producer import KafkaProducerWrapper
from src.models import ExpenseCategory, ExpenseSubCategory, IncomeCategory, Transaction
from src.schemas import TransactionCreate, TransactionUpdate
from src.transaction.list_helpers import *


def list_categories(db: Session) -> list:
    """
    Retrieves a list of categories of a transaction type.

    Returns:
        list: A list of categories.
    """
    categories = {"income": [], "expense": []}
    for e in db.query(IncomeCategory.id, IncomeCategory.category).all():
        categories["income"].append({"value": e[0], "label": e[1]})
    for e in db.query(ExpenseCategory.id, ExpenseCategory.category).all():
        categories["expense"].append({"value": e[0], "label": e[1]})
    return categories


def list_subcategories(db: Session):
    subcategories = {"income": {}, "expense": {}}
    expense_queryset = db.query(
        ExpenseSubCategory.id,
        ExpenseSubCategory.expense_category_id,
        ExpenseSubCategory.sub_category,
    ).all()
    expense_sorted_queryset = sorted(expense_queryset, key=lambda item: item[1])
    expense_grouped_queryset = groupby(
        expense_sorted_queryset, key=lambda item: item[1]
    )
    expense_groups = {}
    for expense_category_id, group in expense_grouped_queryset:
        _list = []
        for obj in group:
            _list.append({"value": obj[0], "label": obj[2]})
        expense_groups[expense_category_id] = _list
    subcategories["expense"] = expense_groups
    return subcategories


def create_transaction(data: TransactionCreate, user_id: int, db: Session) -> int:
    """
    Creates a new transaction record in the database and send data to kafka topic
    to check budget status.

    Args:
        data (TransactionCreate): A `TransactionCreate` object containing the details
                                   of the transaction (amount, category,
                                   transaction_type_category, description and transaction_date).
        user_id (int): The ID of the user who is making the transaction.
        db (Session): The SQLAlchemy database session used to interact with the database.

    Returns:
        int: The ID of the newly created transaction.
    """
    db_transaction = Transaction(
        user_id=user_id,
        transaction_type_id=data.transaction_type_id,
        transaction_type_category_id=data.transaction_type_category_id,
        transaction_type_subcategory_id=data.transaction_type_subcategory_id,
        amount=data.amount,
        description=data.description,
        transaction_date=data.transaction_date,
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)

    # Initialize Kafka producer
    kafka_producer = KafkaProducerWrapper(bootstrap_servers="localhost:9093")
    # Send transaction data to Kafka
    kafka_producer.send_message(
        "create_transaction_topic", jsonable_encoder(db_transaction)
    )

    return db_transaction.id


def read_transaction_details(
    transaction_id: int, user_id: int, db: Session
) -> Union[Transaction, None]:
    """
    Retrieves the details of a specific transaction from the database.

    Args:
        transaction_id (int): The unique identifier of the transaction to be retrieved.
        user_id (int): The ID of the user who made the transaction.
        db (Session): The SQLAlchemy database session used to interact with the database.

    Returns:
        Union[Transaction, None]: The transaction object if found, otherwise None.
    """
    return (
        db.query(Transaction)
        .filter(Transaction.id == transaction_id, Transaction.user_id == user_id)
        .first()
    )


def update_transaction(
    data: TransactionUpdate, transaction_id: int, user_id: int, db: Session
) -> None:
    """
    Updates a transaction record in the database with the provided new data.

    Args:
        data (TransactionUpdate): The new data to update the transaction with.
                                  This is expected to be an instance of `TransactionUpdate` model,
                                  containing the fields to be updated.
        transaction_id (int): The ID of the transaction to be updated.
        user_id (int): The ID of the user who made the transaction.
        db (Session): The SQLAlchemy database session used to interact with the database.

    Returns:
        None: The function performs the update directly on the database and does not return any value.
    """
    update_data = data.model_dump(exclude_unset=True)
    db.query(Transaction).filter(
        Transaction.id == transaction_id, Transaction.user_id == user_id
    ).update(update_data)
    db.commit()

    db_transaction = (
        db.query(Transaction)
        .filter(Transaction.id == transaction_id, Transaction.user_id == user_id)
        .first()
    )
    kafka_producer = KafkaProducerWrapper(bootstrap_servers="localhost:9093")
    kafka_producer.send_message(
        "create_transaction_topic", jsonable_encoder(db_transaction)
    )  # change the name create to update (later)


def delete_transaction(transaction_id: int, user_id: int, db: Session) -> None:
    """
    Deletes a transaction record in the database.

    Args:
        transaction_id (int): The ID of the transaction to be deleted.
        user_id (int): The ID of the user who made the transaction.
        db (Session): The SQLAlchemy database session used to interact with the database.

    Returns:
        None: The function performs the update directly on the database and does not return any value.
    """
    db.query(Transaction).filter(
        Transaction.id == transaction_id, Transaction.user_id == user_id
    ).delete()
    db.commit()


def list_transactions(user_id: int, params: dict, db: Session) -> list[dict]:
    """
    Retrieves a list of transactions for a specific user from the database.

    Args:
        user_id (int): The ID of the user who made those transactions.
        params (dict): A dictionary of filters to apply.
        db (Session): The SQLAlchemy database session used to interact with the database.

    Returns:
        list: A list of transactions, each containing the transaction's ID,
            amount, transaction_type and transaction_type_category.
            The list is limited by the `skip` and `limit` parameters.
    """
    # Contional list to pass in sqlalachemy .filter()
    _filters = [Transaction.user_id == user_id]
    order_by_field = desc(Transaction.transaction_date)

    # If parameters passed then add Search, Filters and Order by conditions
    if params:
        add_search(_filters, params, db)
        add_filters(_filters, params)
        order_by_field = add_order_by(params, order_by_field)

    # Count the total number of filtered records (for pagination)
    count = db.query(func.count(Transaction.id)).filter(*_filters).scalar()

    # Apply Search, Filters and Order by
    query = db.query(Transaction).filter(*_filters).order_by(order_by_field)

    # Apply Pagination
    if "page_number" in params and "page_size" in params:
        query = query.limit(params["page_size"]).offset(
            (params["page_number"] - 1) * params["page_size"]
        )

    # Retrieve result
    queryset = query.all()

    # List View
    transactions = []
    list_view(queryset, transactions)

    # Grouped List View
    if "group_by" in params:
        grouped_transactions = []
        grouped_view(params, transactions, grouped_transactions)
        return grouped_transactions, count

    return transactions, count


def list_recent_transactions(user_id: int, db: Session) -> list[dict]:
    query = (
        db.query(Transaction)
        .filter(Transaction.user_id == user_id)
        .order_by(desc(Transaction.transaction_date))
    )
    queryset = query.limit(10).all()
    transactions = []
    list_view(queryset, transactions)
    return transactions
