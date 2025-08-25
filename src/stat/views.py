from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.dependencies import get_db
from src.schemas import User
from src.stat.services import (
    monthly_budget_vs_expense,
    monthly_expense_of_category,
    periodical_expense,
)
from src.user.services import get_current_user

router = APIRouter()


@router.get("/periodical-expense/")
def chart_periodical_expense(
    period: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve the periodical expense data for the current authenticated user.

    This endpoint fetches periodical(Weekly, Monthly, Quarterly, Yearly) expense based on the specified period.
    It queries the database for relevant groups of expenses and returns the result in a structured format.

    Args:
        period (str): The period for which the expense data is requested. It can be one of 'weekly', 'monthly', 'quarterly', or 'yearly'.
        current_user (User, default Depends(get_current_user)): The currently authenticated user
                                   (retrieved from the `get_current_user` dependency).
        db (Session, default Depends(get_db)): The SQLAlchemy database session used to interact with
                                               the database (retrieved from the `get_db` dependency).

    Returns:
        A dictionary containing the list of total amount, period intervals and the status.
    """
    try:
        groups = periodical_expense(current_user.id, period, db)
        if groups:
            return {"data": groups, "status": "success"}, status.HTTP_200_OK
        else:
            return {
                "message": "No records found.",
                "status": "error",
            }, status.HTTP_204_NO_CONTENT
    except Exception as exe:
        return {
            "message": str(exe),
            "status": "error",
        }, status.HTTP_500_INTERNAL_SERVER_ERROR


@router.get("/monthly-expense-of-category/")
def chart_monthly_expense_of_category(
    month: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieves retrieve the total expense amount for each category
    for a given month for the current authenticated user.

    Args:
        month (str): The month for which to calculate the total expenses (e.g., "January", "February").
        current_user (User, default Depends(get_current_user)): The currently authenticated user
                                   (retrieved from the `get_current_user` dependency).
        db (Session, default Depends(get_db)): The SQLAlchemy database session used to interact with
                                               the database (retrieved from the `get_db` dependency).

    Returns:
        dict: A dictionary containing the list of expenses and the status.
    """
    try:
        groups = monthly_expense_of_category(current_user.id, month, db)
        if groups:
            return {"data": groups, "status": "success"}, status.HTTP_200_OK
        else:
            return {
                "message": "No records found.",
                "status": "error",
            }, status.HTTP_204_NO_CONTENT
    except Exception as exe:
        return {
            "message": str(exe),
            "status": "error",
        }, status.HTTP_500_INTERNAL_SERVER_ERROR


@router.get("/monthly-budget-vs-expense/")
def chart_monthly_budget_vs_expense(
    month: str,
    transaction_type_category_id: Optional[int] = None,
    transaction_type_subcategory_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieves retrieve the total expense amount for each category
    for a given month for the current authenticated user.

    Args:
        month (str): The month for which to calculate the total expenses (e.g., "January", "February").
        current_user (User, default Depends(get_current_user)): The currently authenticated user
                                   (retrieved from the `get_current_user` dependency).
        db (Session, default Depends(get_db)): The SQLAlchemy database session used to interact with
                                               the database (retrieved from the `get_db` dependency).

    Returns:
        dict: A dictionary containing the list of expenses and the status.
    """
    params = {"month": month}
    if transaction_type_category_id:
        params["transaction_type_category_id"] = transaction_type_category_id
    if transaction_type_subcategory_id:
        params["transaction_type_subcategory_id"] = transaction_type_subcategory_id
    try:
        budget_expense = monthly_budget_vs_expense(
            current_user.id,
            params,
            db,
        )
        if budget_expense:
            return {"data": budget_expense, "status": "success"}, status.HTTP_200_OK
        else:
            return {
                "message": "No records found.",
                "status": "error",
            }, status.HTTP_204_NO_CONTENT
    except Exception as exe:
        return {
            "message": str(exe),
            "status": "error",
        }, status.HTTP_500_INTERNAL_SERVER_ERROR
