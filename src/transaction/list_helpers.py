from itertools import groupby
from typing import Union

from sqlalchemy import and_, desc
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import UnaryExpression

from src.cache.transaction import cache_categories
from src.models import ExpenseCategory, ExpenseSubCategory, IncomeCategory, Transaction


def add_filter_by_type(_filters: list, type_id: int) -> None:
    """
    Add filter by Transaction type.
    """
    _filters.append(Transaction.transaction_type_id == type_id)


def add_filter_by_category(
    _filters: list, type_id: int, transaction_column, ids: Union[tuple, int]
) -> None:
    """
    Add filter by Transaction category and subcategory.
    """
    if isinstance(ids, tuple):
        _filters.append(
            and_(
                Transaction.transaction_type_id == type_id,
                transaction_column.in_(ids),
            )
        )
    else:
        _filters.append(
            and_(
                Transaction.transaction_type_id == type_id,
                transaction_column == ids,
            )
        )


def get_category_id(model, model_column, search_term: str, db: Session) -> int:
    """
    Get category or subcategory ID based on search term.
    """
    return db.query(model.id).filter(model_column.ilike(f"%{search_term}%")).scalar()


def add_search(_filters: list, params: dict, db: Session) -> None:
    """
    Try finding the income category first, Then try finding
    the expense category and finally, check for expense subcategory
    If no category or subcategory matched, search in transaction description.
    """
    try:
        if "validated_query" in params:
            income_category_id = get_category_id(
                IncomeCategory, IncomeCategory.category, params["validated_query"], db
            )
            if income_category_id:
                add_filter_by_category(
                    _filters,
                    1,
                    Transaction.transaction_type_category_id,
                    income_category_id,
                )
                return

            expense_category_id = get_category_id(
                ExpenseCategory, ExpenseCategory.category, params["validated_query"], db
            )
            if expense_category_id:
                add_filter_by_category(
                    _filters,
                    2,
                    Transaction.transaction_type_category_id,
                    expense_category_id,
                )
                return

            expense_subcategory_id = get_category_id(
                ExpenseSubCategory,
                ExpenseSubCategory.sub_category,
                params["validated_query"],
                db,
            )
            if expense_subcategory_id:
                add_filter_by_category(
                    _filters,
                    2,
                    Transaction.transaction_type_subcategory_id,
                    expense_subcategory_id,
                )
                return

            _filters.append(
                Transaction.description.ilike(f"%{params['validated_query']}%")
            )
    except Exception as exe:
        print("Exe: ", exe)


def add_filters(_filters: list, params: dict) -> None:
    """
    Add all the filter parameters passed in request.
    """
    try:
        if "transaction_type_id" in params:
            add_filter_by_type(_filters, params["transaction_type_id"])

        if "income_category_ids" in params:
            add_filter_by_category(
                _filters,
                1,
                Transaction.transaction_type_category_id,
                tuple(params["income_category_ids"]),
            )
        if "expense_category_ids" in params:
            add_filter_by_category(
                _filters,
                2,
                Transaction.transaction_type_category_id,
                tuple(params["expense_category_ids"]),
            )
        if "expense_subcategory_ids" in params:
            ids = tuple(params["expense_subcategory_ids"])
            if "expense_category_ids" in params:
                _filters.append(Transaction.transaction_type_subcategory_id.in_(ids))
            else:
                add_filter_by_category(
                    _filters, 2, Transaction.transaction_type_subcategory_id, ids
                )

        if "min_amount" in params and "max_amount" in params:
            _filters.append(
                and_(
                    Transaction.amount >= params["min_amount"],
                    Transaction.amount <= params["max_amount"],
                )
            )

        if "start_date" in params and "end_date" in params:
            _filters.append(
                and_(
                    Transaction.transaction_date >= params["start_date"],
                    Transaction.transaction_date <= params["end_date"],
                )
            )
    except Exception as exe:
        print("Exception: ", exe)


def add_order_by(params: dict, order_by_field: UnaryExpression) -> UnaryExpression:
    if "order_by" in params:
        if params["order_by"] == "amount":
            order_by_field = desc(Transaction.amount)
        if params["order_by"] == "date":
            order_by_field = desc(Transaction.transaction_date)
    return order_by_field


def list_view(queryset: list, transactions: list) -> list[dict]:
    for obj in queryset:
        transaction = {}
        transaction["id"] = obj.id
        transaction["transaction_type_id"] = obj.transaction_type_id
        if obj.transaction_type_id == 1:
            transaction["transaction_type"] = "Income"
            transaction["transaction_type_category_id"] = (
                obj.transaction_type_category_id
            )
            transaction["transaction_type_category"] = (
                cache_categories.income_categories.get(obj.transaction_type_category_id)
            )
        elif obj.transaction_type_id == 2:
            transaction["transaction_type"] = "Expense"
            transaction["transaction_type_category_id"] = (
                obj.transaction_type_category_id
            )
            transaction["transaction_type_category"] = (
                cache_categories.expense_categories.get(
                    obj.transaction_type_category_id
                )
            )
            if obj.transaction_type_subcategory_id:
                transaction["transaction_type_subcategory_id"] = (
                    obj.transaction_type_subcategory_id
                )
                transaction["transaction_type_subcategory"] = (
                    cache_categories.expense_sub_categories.get(
                        obj.transaction_type_subcategory_id
                    )
                )
        transaction["amount"] = obj.amount
        transaction["description"] = obj.description
        transaction["transaction_date"] = obj.transaction_date
        transactions.append(transaction)


def grouped_view(
    params: dict, transactions: list[dict], grouped_transactions: list
) -> list[dict]:
    if params["group_by"] == "transaction_type":
        sorted_data = sorted(
            transactions,
            key=lambda transaction: transaction["transaction_type_id"],
        )
        grouped_data = groupby(
            sorted_data,
            key=lambda transaction: transaction["transaction_type_id"],
        )
    if params["group_by"] == "transaction_type_category":
        sorted_data = sorted(
            transactions,
            key=lambda transaction: transaction["transaction_type_category_id"],
        )
        grouped_data = groupby(
            sorted_data,
            key=lambda transaction: transaction["transaction_type_category_id"],
        )
    if params["group_by"] == "transaction_type_subcategory":
        """
        For Income category there is no subcategories and also
        for some Expense category there is no subcategories(as it is optional),
        in those cases treating missing keys value as float("inf")
        which places it at the end of the sorted list.
        """
        sorted_data = sorted(
            transactions,
            key=lambda transaction: transaction.get(
                "transaction_type_subcategory_id", float("inf")
            ),
        )
        grouped_data = groupby(
            sorted_data,
            key=lambda transaction: transaction.get(
                "transaction_type_subcategory_id", float("inf")
            ),
        )
    for _, group in grouped_data:
        grouped_transactions.extend(group)
    return grouped_transactions
