from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.dashboard.services import get_income_vs_expense, get_summary_card
from src.dependencies import get_db
from src.schemas import User
from src.user.services import get_current_user

router = APIRouter()


@router.get("/summary-card/")
def summary_card(
    month: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieves summary of the total balance, income, expenses and
    budget used amount of current month for the current authenticated user.

    Args:
        current_user (User, default Depends(get_current_user)): The currently authenticated user
                                   (retrieved from the `get_current_user` dependency).
        db (Session, default Depends(get_db)): The SQLAlchemy database session used to interact with
                                               the database (retrieved from the `get_db` dependency).

    Returns:
        dict: A dictionary containing the amount of balance, income expense and budget used.
    """
    try:
        summary = get_summary_card(current_user.id, month, db)
        if summary:
            return {"data": summary, "status": "success"}, status.HTTP_200_OK
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


@router.get("/income-vs-expense/")
def chart_income_vs_expense(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieves retrieve the total income and expenses amount of every month
    for the current authenticated user.

    Args:
        current_user (User, default Depends(get_current_user)): The currently authenticated user
                                   (retrieved from the `get_current_user` dependency).
        db (Session, default Depends(get_db)): The SQLAlchemy database session used to interact with
                                               the database (retrieved from the `get_db` dependency).

    Returns:
        dict: A dictionary containing the list of income and expenses.
    """
    try:
        income_expense = get_income_vs_expense(current_user.id, db)
        if income_expense:
            return {"data": income_expense, "status": "success"}, status.HTTP_200_OK
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
