from typing import Optional, Union

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from src.dependencies import get_db
from src.schemas import TransactionCreate, TransactionUpdate, User
from src.transaction.request_helpers import prepare_list_params
from src.transaction.services import (
    create_transaction,
    delete_transaction,
    list_categories,
    list_recent_transactions,
    list_subcategories,
    list_transactions,
    read_transaction_details,
    update_transaction,
)
from src.user.decorators import subscription_type_list
from src.user.services import get_current_user

router = APIRouter()


@router.get("/categories/")
def category_list(db: Session = Depends(get_db)):
    """
    Retrieves a list of categories of a transaction type.

    Args:
        current_user (User, default Depends(get_current_user)): The currently authenticated user
                                   (retrieved from the `get_current_user` dependency).

    Returns:
        dict: A dictionary containing the list of categories and the status.
    """
    try:
        categories = list_categories(db)
        return {"data": categories, "status": "success"}, status.HTTP_200_OK
    except Exception as exe:
        return {
            "message": str(exe),
            "status": "error",
        }, status.HTTP_500_INTERNAL_SERVER_ERROR


@router.get("/sub-categories/")
def subcategory_list(db: Session = Depends(get_db)):
    """
    Retrieves a list of sub categories under categories of Expense transaction type.

    Args:
        current_user (User, default Depends(get_current_user)): The currently authenticated user
                                   (retrieved from the `get_current_user` dependency).

    Returns:
        dict: A dictionary containing the list of categories and the status.
    """
    try:
        subcategories = list_subcategories(db)
        return {"data": subcategories, "status": "success"}, status.HTTP_200_OK
    except Exception as exe:
        return {
            "message": str(exe),
            "status": "error",
        }, status.HTTP_500_INTERNAL_SERVER_ERROR


@router.post("/create/")
def create(
    data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Creates a new transaction for the current user.

    Args:
        data (TransactionCreate): A `TransactionCreate` object containing the transaction details
                                   (amount, transaction_type, transaction_type_category, description and transaction_date).
        current_user (User, default Depends(get_current_user)): The currently authenticated user
                                   (retrieved from the `get_current_user` dependency).
        db (Session, default Depends(get_db)): The SQLAlchemy database session used to interact with
                                               the database (retrieved from the `get_db` dependency).

    Returns:
        dict: A dictionary containing a success message if the transaction
              is created successfully, or an error message if an exception occurs.
    """
    try:
        transaction_id = create_transaction(data, current_user.id, db)
        return {
            "id": transaction_id,
            "message": "Transaction created.",
            "status": "success",
        }, status.HTTP_201_CREATED
    except Exception as exe:
        return {
            "message": str(exe),
            "status": "error",
        }, status.HTTP_500_INTERNAL_SERVER_ERROR


@router.get("/read/{transaction_id}")
def read_details(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieves detailed information for a specific transaction by its ID.

    Args:
        transaction_id (int): The unique identifier of the transaction to retrieve.
        current_user (User, default Depends(get_current_user)): The currently authenticated user
                                   (retrieved from the `get_current_user` dependency).
        db (Session, default Depends(get_db)): The SQLAlchemy database session used to interact with
                                               the database (retrieved from the `get_db` dependency).

    Returns:
        dict: A dictionary containing the transaction data and status.
    """
    try:
        transaction = read_transaction_details(transaction_id, current_user.id, db)
        if transaction:
            data = {
                "id": transaction.id,
                "amount": transaction.amount,
                "transaction_type": transaction.transaction_type,
                "transaction_type_category": transaction.transaction_type_category,
                "description": transaction.description,
                "transaction_date": transaction.transaction_date,
            }
            return {"data": data, "status": "success"}, status.HTTP_200_OK
        else:
            return {
                "message": "Transaction not found.",
                "status": "error",
            }, status.HTTP_204_NO_CONTENT
    except Exception as exe:
        return {
            "message": str(exe),
            "status": "error",
        }, status.HTTP_500_INTERNAL_SERVER_ERROR


@router.patch("/update/{transaction_id}")
def update(
    data: TransactionUpdate,
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Updates an existing transaction.

    Args:
        data (TransactionCreate): A `TransactionCreate` object containing the transaction details
                                   (amount, category, description, transaction_type, and transaction_date).
        transaction_id (int): The unique identifier of the transaction to update.
        current_user (User, default Depends(get_current_user)): The currently authenticated user
                                   (retrieved from the `get_current_user` dependency).
        db (Session, default Depends(get_db)): The SQLAlchemy database session used to interact with
                                               the database (retrieved from the `get_db` dependency).

    Returns:
        dict: A dictionary containing a success message if the transaction
              is updated successfully, or an error message if an exception occurs.
    """
    try:
        update_transaction(data, transaction_id, current_user.id, db)
        return {
            "message": "Transaction updated.",
            "status": "success",
        }, status.HTTP_200_OK
    except Exception as exe:
        return {
            "message": str(exe),
            "status": "error",
        }, status.HTTP_500_INTERNAL_SERVER_ERROR


@router.delete("/delete/{transaction_id}")
def delete(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Deletes an existing transaction.

    Args:
        transaction_id (int): The unique identifier of the transaction to delete.
        current_user (User, default Depends(get_current_user)): The currently authenticated user
                                   (retrieved from the `get_current_user` dependency).
        db (Session, default Depends(get_db)): The SQLAlchemy database session used to interact with
                                               the database (retrieved from the `get_db` dependency).

    Returns:
        dict: A dictionary containing a success message if the transaction
              is updated successfully, or an error message if an exception occurs.
    """
    try:
        delete_transaction(transaction_id, current_user.id, db)
        return {
            "message": "Transaction deleted.",
            "status": "success",
        }, status.HTTP_200_OK
    except Exception as exe:
        return {
            "message": str(exe),
            "status": "error",
        }, status.HTTP_500_INTERNAL_SERVER_ERROR


@router.get("/list/")
def list(
    request: Request,
    q: Optional[str] = None,
    transaction_type_id: Optional[int] = None,
    min_amount: Optional[Union[int, float]] = None,
    max_amount: Optional[Union[int, float]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    order_by: Optional[str] = None,
    group_by: Optional[str] = None,
    page_number: Optional[int] = None,
    page_size: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieves a list of transactions for the current authenticated user.

    Args:
        q (Optional[str]): A search query to filter transactions by description or other attributes.
        transaction_type (Optional[str]): Filter transactions by their type (e.g., 'income', 'expense').
        transaction_type_category (Optional[str]): Filter transactions by category, only applicable if `transaction_type` is provided.
        min_amount (Optional[int or float]): Minimum transaction amount for filtering.
        max_amount (Optional[int or float]): Maximum transaction amount for filtering.
        start_date (Optional[str]): Start date for filtering transactions by date (in 'YYYY-MM-DD' format).
        end_date (Optional[str]): End date for filtering transactions by date (in 'YYYY-MM-DD' format).
        order_by (Optional[str]): Sort transactions by 'category', 'amount', or 'date'.
        page_number (Optional[int]): The page number to retrieve (for pagination).
        page_size (Optional[int]): The number of transactions per page (for pagination).
        current_user (User, default Depends(get_current_user)): The currently authenticated user
                                   (retrieved from the `get_current_user` dependency).
        db (Session, default Depends(get_db)): The SQLAlchemy database session used to interact with
                                               the database (retrieved from the `get_db` dependency).

    Returns:
        dict: A dictionary containing the list of transactions and the status.
    """
    try:
        params = {}
        # Prepare and format the request parameters
        prepare_list_params(
            request,
            params,
            q,
            transaction_type_id,
            min_amount,
            max_amount,
            start_date,
            end_date,
            order_by,
            group_by,
            page_number,
            page_size,
        )

        # Fetch Transactions list
        transactions, count = list_transactions(current_user.id, params, db)
        if transactions:
            return {
                "data": transactions,
                "count": count,
                "status": "success",
            }, status.HTTP_200_OK
        else:
            return {
                "message": "No transactions records found.",
                "status": "error",
            }, status.HTTP_204_NO_CONTENT
    except Exception as exe:
        return {
            "message": str(exe),
            "status": "error",
        }, status.HTTP_500_INTERNAL_SERVER_ERROR


@router.get("/recent-list/")
def recent_list(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieves a list of recent transactions for the current authenticated user.

    Args:
        current_user (User, default Depends(get_current_user)): The currently authenticated user
                                   (retrieved from the `get_current_user` dependency).
        db (Session, default Depends(get_db)): The SQLAlchemy database session used to interact with
                                               the database (retrieved from the `get_db` dependency).

    Returns:
        dict: A dictionary containing the list of recent transactions and the status.
    """
    try:
        # Fetch Transactions list
        transactions = list_recent_transactions(current_user.id, db)
        if transactions:
            return {
                "data": transactions,
                "status": "success",
            }, status.HTTP_200_OK
        else:
            return {
                "message": "No transactions records found.",
                "status": "error",
            }, status.HTTP_204_NO_CONTENT
    except Exception as exe:
        return {
            "message": str(exe),
            "status": "error",
        }, status.HTTP_500_INTERNAL_SERVER_ERROR
