from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from src.models import Transaction, ExpenseCategory
from src.utils import get_month_range
from src.budget.services import budget_usage


def get_summary_card(user_id: int, month: str, db: Session) -> list[dict]:
    """
    Total Income, Total Expense of current month
    """
    year = 2025
    start_date, end_date = get_month_range(month, year)
    income_filter = [
        Transaction.user_id == user_id,
        Transaction.transaction_type_id == 1,
        Transaction.transaction_date >= start_date,
        Transaction.transaction_date <= end_date,
    ]
    expense_filter = [
        Transaction.user_id == user_id,
        Transaction.transaction_type_id == 2,
        Transaction.transaction_date >= start_date,
        Transaction.transaction_date <= end_date,
    ]
    total_income = (
        db.query(func.sum(Transaction.amount)).filter(*income_filter).scalar()
    )
    highest_income = db.query(Transaction).filter(*income_filter).order_by(desc(Transaction.amount)).first()
    highest_income_category = (
        db.query(ExpenseCategory.category)
        .filter(
            ExpenseCategory.id == highest_income.transaction_type_category_id,
        )
        .scalar()
    )
    total_expense = (
        db.query(func.sum(Transaction.amount)).filter(*expense_filter).scalar()
    )
    most_expense = db.query(Transaction).filter(*expense_filter).order_by(desc(Transaction.amount)).first()
    most_expense_category = (
        db.query(ExpenseCategory.category)
        .filter(
            ExpenseCategory.id == most_expense.transaction_type_category_id,
        )
        .scalar()
    )

    usage = budget_usage(user_id, month, db)
    total_budget = sum(item.get("amount", 0.0) for item in usage)
    total_amount_spent = sum(item.get("amount_spent", 0.0) for item in usage)
    usage_percentage = (total_amount_spent / total_budget) * 100 if total_budget else 0.0
    max_budget_used = max(usage, key=lambda item: item.get("amount_spent", 0.0)) if usage else None

    summary = [
        {"label": "Total Balance", "amount": 100000, "icon": "💰", "transaction_type_category": ""},
        {"label": "Total Income", "amount": total_income, "icon": "💵", "transaction_type_category": highest_income_category},
        {"label": "Total Expense", "amount": total_expense, "icon": "📉", "transaction_type_category": most_expense_category},
        {"label": "Budget Used", "amount": round(usage_percentage, 2), "icon": "📊", "transaction_type_category": max_budget_used["transaction_type_category"]},
    ]
    return summary


def get_income_vs_expense(user_id: int, db: Session) -> list[dict]:
    income_filter = [
        Transaction.user_id == user_id,
        Transaction.transaction_type_id == 1,
    ]
    expense_filter = [
        Transaction.user_id == user_id,
        Transaction.transaction_type_id == 2,
    ]

    total_income = (
        db.query(
            func.to_char(Transaction.transaction_date, "Mon").label("Month"),
            func.sum(Transaction.amount).label("total_income"),
        )
        .filter(*income_filter)
        .group_by(func.to_char(Transaction.transaction_date, "Mon"))
        .order_by("Month")
        .all()
    )

    total_expense = (
        db.query(
            func.to_char(Transaction.transaction_date, "Mon").label("Month"),
            func.sum(Transaction.amount).label("total_expense"),
        )
        .filter(*expense_filter)
        .group_by(func.to_char(Transaction.transaction_date, "Mon"))
        .order_by("Month")
        .all()
    )

    # Convert income and expense results to dictionaries
    income_dict = {month.strip(): float(income) for month, income in total_income}
    expense_dict = {month.strip(): float(expense) for month, expense in total_expense}

    # Union of all months from both income and expense data
    all_months = sorted(
        set(income_dict) | set(expense_dict),
        key=lambda m: (
            [
                "Jan",
                "Feb",
                "Mar",
                "Apr",
                "May",
                "Jun",
                "Jul",
                "Aug",
                "Sep",
                "Oct",
                "Nov",
                "Dec",
            ].index(m)
        ),
    )

    result = [
        {
            "month": month,
            "income": income_dict.get(month, 0),
            "expense": expense_dict.get(month, 0),
        }
        for month in all_months
    ]
    return result
