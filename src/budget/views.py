from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.budget.services import (
    budget_status,
    budget_usage,
    create_budget,
    delete_budget,
    list_budgets,
    update_budget,
)
from src.dependencies import get_db
from src.schemas import BudgetCreate, BudgetUpdate, User
from src.user.services import get_current_user

router = APIRouter()


@router.post("/create/")
def create(
    data: BudgetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Creates a new budget for the current user.

    Args:
        data (BudgetCreate): A `BudgetCreate` object containing the budget details
                                   (transaction_type_category, amount, start_date and end_date).
        current_user (User, default Depends(get_current_user)): The currently authenticated user
                                   (retrieved from the `get_current_user` dependency).
        db (Session, default Depends(get_db)): The SQLAlchemy database session used to interact with
                                               the database (retrieved from the `get_db` dependency).

    Returns:
        dict: A dictionary containing a success message if the budget
              is created successfully, or an error message if an exception occurs.
    """
    try:
        budget_id = create_budget(data, current_user.id, db)
        return {
            "message": "Budget created.",
            "status": "success",
        }, status.HTTP_201_CREATED
    except Exception as exe:
        return {
            "message": str(exe),
            "status": "error",
        }, status.HTTP_500_INTERNAL_SERVER_ERROR


@router.patch("/update/{budget_id}")
def update(
    data: BudgetUpdate,
    budget_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Updates an existing budget.

    Args:
        data (BudgetUpdate): A `BudgetUpdate` object containing the budget details
                                   (amount, start_date and end_date).
        budget_id (int): The unique identifier of the budget to update.
        current_user (User, default Depends(get_current_user)): The currently authenticated user
                                   (retrieved from the `get_current_user` dependency).
        db (Session, default Depends(get_db)): The SQLAlchemy database session used to interact with
                                               the database (retrieved from the `get_db` dependency).

    Returns:
        dict: A dictionary containing a success message if the budget
              is updated successfully, or an error message if an exception occurs.
    """
    try:
        update_budget(data, budget_id, current_user.id, db)
        return {
            "message": "Budget updated.",
            "status": "success",
        }, status.HTTP_200_OK
    except Exception as exe:
        return {
            "message": str(exe),
            "status": "error",
        }, status.HTTP_500_INTERNAL_SERVER_ERROR


@router.delete("/delete/{budget_id}")
def delete(
    budget_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Deletes an existing budget.

    Args:
        budget_id (int): The unique identifier of the budget to delete.
        current_user (User, default Depends(get_current_user)): The currently authenticated user
                                   (retrieved from the `get_current_user` dependency).
        db (Session, default Depends(get_db)): The SQLAlchemy database session used to interact with
                                               the database (retrieved from the `get_db` dependency).

    Returns:
        dict: A dictionary containing a success message if the transaction
              is updated successfully, or an error message if an exception occurs.
    """
    try:
        delete_budget(budget_id, current_user.id, db)
        return {
            "message": "Budget deleted.",
            "status": "success",
        }, status.HTTP_200_OK
    except Exception as exe:
        return {
            "message": str(exe),
            "status": "error",
        }, status.HTTP_500_INTERNAL_SERVER_ERROR


@router.get("/list/")
def list(
    transaction_type_category: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieves a list of budgets for the current authenticated user.

    Args:
        transaction_type_category (Optional[str], default None): Filter budgets by category.
        current_user (User, default Depends(get_current_user)): The currently authenticated user
                                   (retrieved from the `get_current_user` dependency).
        db (Session, default Depends(get_db)): The SQLAlchemy database session used to interact with
                                               the database (retrieved from the `get_db` dependency).

    Returns:
        dict: A dictionary containing the list of budgets and the status.
    """
    try:
        params = {}
        if transaction_type_category:
            params["transaction_type_category"] = transaction_type_category

        budgets = list_budgets(current_user.id, params, db)
        if budgets:
            return {"data": budgets, "status": "success"}, status.HTTP_200_OK
        else:
            return {
                "message": "No budgets records found.",
                "status": "error",
            }, status.HTTP_204_NO_CONTENT
    except Exception as exe:
        return {
            "message": str(exe),
            "status": "error",
        }, status.HTTP_500_INTERNAL_SERVER_ERROR


@router.get("/status/{budget_id}")
def status_of_budget(
    budget_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Budget status check.

    Args:
        budget_id (int): The unique identifier of the budget to update.
        current_user (User, default Depends(get_current_user)): The currently authenticated user
                                   (retrieved from the `get_current_user` dependency).
        db (Session, default Depends(get_db)): The SQLAlchemy database session used to interact with
                                               the database (retrieved from the `get_db` dependency).

    Returns:
        dict: A dictionary containing a budget status, or an error message if an exception occurs.
    """
    try:
        data = budget_status(budget_id, current_user.id, db)
        return {
            "data": data,
            "status": "success",
        }, status.HTTP_200_OK
    except Exception as exe:
        return {
            "message": str(exe),
            "status": "error",
        }, status.HTTP_500_INTERNAL_SERVER_ERROR


@router.get("/usage/")
def usage_of_budget(
    month: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Budget usage of current month.

    Args:
        current_user (User, default Depends(get_current_user)): The currently authenticated user
                                   (retrieved from the `get_current_user` dependency).
        db (Session, default Depends(get_db)): The SQLAlchemy database session used to interact with
                                               the database (retrieved from the `get_db` dependency).

    Returns:
        dict: A dictionary containing a budget usage, or an error message if an exception occurs.
    """
    try:
        data = budget_usage(current_user.id, month, db)
        return {
            "data": data,
            "status": "success",
        }, status.HTTP_200_OK
    except Exception as exe:
        return {
            "message": str(exe),
            "status": "error",
        }, status.HTTP_500_INTERNAL_SERVER_ERROR
