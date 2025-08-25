from collections import defaultdict
from datetime import datetime
from itertools import groupby

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.models import Budget, BudgetExpense, ExpenseCategory, Transaction
from src.utils import get_current_week_range, get_month_range


def fetch_expenses_within_daterange(user_id, start_date, end_date, db):
    """
    Retrieve expenses from the database for a user within a date range.
    """
    _filters = [
        Transaction.user_id == user_id,
        Transaction.transaction_type_id == 2,
        Transaction.transaction_date >= start_date,
        Transaction.transaction_date <= end_date,
    ]
    return (
        db.query(
            Transaction.id,
            Transaction.amount,
            Transaction.transaction_type_category_id,
            Transaction.transaction_date,
        )
        .filter(*_filters)
        .all()
    )


def get_periodical_expense_weekly(user_id, start_date, end_date, db) -> list[dict]:
    """
    Retrieve weekly periodical expense data for a user within the specified date range.
    """
    expenses = fetch_expenses_within_daterange(user_id, start_date, end_date, db)
    # Sort by Date, then Group by Date [Day wise]
    sorted_expenses = sorted(expenses, key=lambda expense: expense[3])
    grouped_expenses = groupby(sorted_expenses, key=lambda expense: expense[3].date())
    groups = []
    # For each group calculate the total amount
    for date, group in grouped_expenses:
        total = sum(expense[1] for expense in group)
        groups.append({"transaction_date": date, "total": total})
    return groups


def get_periodical_expense_monthly(user_id, start_date, end_date, db):
    """
    Retrieve monthly periodical expense data for a user within the specified date range.
    """
    expenses = fetch_expenses_within_daterange(user_id, start_date, end_date, db)
    sorted_expenses = sorted(expenses, key=lambda expense: expense[3])
    weekly_data = defaultdict(list)
    for expense in sorted_expenses:
        date = expense[3]
        week_number = (date.day - 1) // 8 + 1
        weekly_data[week_number].append(expense)
    groups = []
    monthly_total = 0
    for week, data in weekly_data.items():
        total = sum(expense[1] for expense in data)
        monthly_total += total
        groups.append({"transaction_date": f"Week {week}", "total": total})
    return groups


def periodical_expense(user_id: int, period: str, db: Session) -> list[dict]:
    """
    Calculates the total monthly expenses for each category.

    This function retrieves all expense transactions of a specified user within a given month and year,
    and then groups the expenses by category.

    Args:
        user_id (int): The ID of the user who made those transactions.
        period (str): The period for which the expense data is requested.
        db (Session): The SQLAlchemy database session used to interact with the database.

    Returns:
        list[dict]: A list of dictionaries.
    """
    groups = []
    if period == "Weekly":
        # Per day basis
        start_date, end_date = get_current_week_range()
        groups = get_periodical_expense_weekly(user_id, start_date, end_date, db)
    elif period == "Monthly":
        # Per week basis
        year = 2025
        today = datetime.today()
        start_date, end_date = get_month_range(today.strftime("%B"), year)
        groups = get_periodical_expense_monthly(user_id, start_date, end_date, db)
    return groups


def monthly_expense_of_category(user_id: int, month: str, db: Session) -> list[dict]:
    """
    Calculates the total monthly expenses for each category.

    This function retrieves all expense transactions of a specified user within a given month and year,
    and then groups the expenses by category. It returns a list of dictionaries, each containing a
    transaction category and the total expense amount for that category.

    Args:
        user_id (int): The ID of the user who made those transactions.
        month (str): The month for which to calculate the total expenses (e.g., "January", "February").
        db (Session): The SQLAlchemy database session used to interact with the database.

    Returns:
        list[dict]: A list of dictionaries, each containing
            'transaction_type_category', 'total' expense amount for the
            specified category in the given month.
    """
    year = 2025
    start_date, end_date = get_month_range(month, year)
    expenses = fetch_expenses_within_daterange(user_id, start_date, end_date, db)
    # Sort by Category
    sorted_expenses = sorted(expenses, key=lambda expense: expense[2])
    # Group by Category
    grouped_expenses = groupby(sorted_expenses, key=lambda expense: expense[2])
    groups = []
    # For each group calculate the total amount
    for transaction_type_category_id, group in grouped_expenses:
        total = sum(expense[1] for expense in group)
        groups.append(
            {
                "transaction_type_category": db.query(ExpenseCategory.category)
                .filter(ExpenseCategory.id == transaction_type_category_id)
                .scalar(),
                "total": total,
            }
        )
    return groups


def monthly_budget_vs_expense(user_id: int, params: dict, db: Session) -> list[dict]:
    """
    based on the date range check if any
    """

    year = 2025
    start_date, end_date = get_month_range(params["month"], year)
    budget_filter = [
        Budget.user_id == user_id,
        Budget.start_date >= start_date,
        Budget.end_date <= end_date,
    ]
    expense_filter = [
        Transaction.user_id == user_id,
        Transaction.transaction_type_id == 2,
        Transaction.transaction_date >= start_date,
        Transaction.transaction_date <= end_date,
    ]
    total_budget = db.query(func.sum(Budget.amount)).filter(*budget_filter).scalar()
    total_expense = (
        db.query(func.sum(Transaction.amount)).filter(*expense_filter).scalar()
    )
    income_vs_expense = [
        {"transaction_type": "Income", "total": total_budget},
        {"transaction_type": "Expense", "total": total_expense},
    ]
    return income_vs_expense
