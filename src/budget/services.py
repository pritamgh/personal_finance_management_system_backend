from typing import Union

from sqlalchemy.orm import Session

from src.models import (
    Budget,
    BudgetExpense,
    ExpenseCategory,
    ExpenseSubCategory,
    Transaction,
)
from src.schemas import (
    BudgetCreate,
    BudgetExpenseCreate,
    BudgetExpenseUpdate,
    BudgetUpdate,
)
from src.utils import get_month_range


def create_budget(data: BudgetCreate, user_id: int, db: Session) -> int:
    """
    Creates a new budget record in the database.

    Args:
        data (BudgetCreate): A `BudgetCreate` object containing the details
                                   of the budget (transaction_type_category, amount, start_date and end_date).
        user_id (int): The ID of the user who is making the budget.
        db (Session): The SQLAlchemy database session used to interact with the database.

    Returns:
        int: The ID of the newly created budget.
    """
    db_budget = Budget(
        user_id=user_id,
        transaction_type_category_id=data.transaction_type_category_id,
        transaction_type_subcategory_id=data.transaction_type_subcategory_id,
        amount=data.amount,
        start_date=data.start_date,
        end_date=data.end_date,
    )
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget.id


def update_budget(
    data: BudgetUpdate, budget_id: int, user_id: int, db: Session
) -> None:
    """
    Updates a budget record in the database with the provided new data.

    Args:
        data (BudgetUpdate): The new data to update the budget with.
                                  This is expected to be an instance of `BudgetUpdate` model,
                                  containing the fields to be updated.
        budget_id (int): The ID of the budget to be updated.
        user_id (int): The ID of the user who made the budget.
        db (Session): The SQLAlchemy database session used to interact with the database.

    Returns:
        None: The function performs the update directly on the database and does not return any value.
    """
    update_data = data.model_dump(exclude_unset=True)
    db.query(Budget).filter(Budget.id == budget_id, Budget.user_id == user_id).update(
        update_data
    )
    db.commit()


def delete_budget(budget_id: int, user_id: int, db: Session) -> None:
    """
    Deletes a budget record in the database.

    Args:
        budget_id (int): The ID of the budget to be deleted.
        user_id (int): The ID of the user who made the transaction.
        db (Session): The SQLAlchemy database session used to interact with the database.

    Returns:
        None: The function performs the delete directly on the database and does not return any value.
    """
    db.query(Budget).filter(Budget.id == budget_id, Budget.user_id == user_id).delete()
    db.commit()


def list_budgets(user_id: int, params: dict, db: Session) -> list[tuple]:
    """
    Retrieves a list of budgets for a specific user from the database.

    Args:
        user_id (int): The ID of the user who made those transactions.
        params (dict): A dictionary of filters to apply to the budgets, such as
        `transaction_type_category`.
        db (Session): The SQLAlchemy database session used to interact with the database.

    Returns:
        list: A list of budget tuples, each containing the budget's ID,
            transaction_type_category, amount, start_date and end_date.
    """
    _filters = [Budget.user_id == user_id]
    if params:
        if "transaction_type_category_id" in params:
            _filters.append(
                Budget.transaction_type_category_id
                == params["transaction_type_category_id"]
            )
        if "transaction_type_subcategory_id" in params:
            _filters.append(
                Budget.transaction_type_subcategory_id
                == params["transaction_type_subcategory_id"]
            )

    queryset = (
        db.query(
            Budget.id,
            Budget.transaction_type_category_id,
            Budget.transaction_type_subcategory_id,
            Budget.amount,
            Budget.start_date,
            Budget.end_date,
        )
        .filter(*_filters)
        .all()
    )

    budgets = []
    for obj in queryset:
        budget = {}
        budget["id"] = obj.id
        budget["transaction_type_category_id"] = obj.transaction_type_category_id
        budget["transaction_type_category"] = (
            db.query(ExpenseCategory.category)
            .filter(ExpenseCategory.id == obj.transaction_type_category_id)
            .scalar()
        )
        if obj.transaction_type_subcategory_id:
            budget["transaction_type_subcategory_id"] = (
                obj.transaction_type_subcategory_id
            )
            budget["transaction_type_subcategory"] = (
                db.query(ExpenseSubCategory.sub_category)
                .filter(ExpenseSubCategory.id == obj.transaction_type_subcategory_id)
                .scalar()
            )
        budget["amount"] = obj.amount
        budget["start_date"] = obj.start_date
        budget["end_date"] = obj.end_date
        budgets.append(budget)

    return budgets


def check_budget(trasaction: Transaction, db: Session) -> Union[Budget, None]:
    """
    Checks and retrieves if there is an existing budget for the user that matches the category of
    the given transaction and if the transaction date falls within the budget's start and end date range.

    Args:
        trasaction (Transaction): Object of Transaction.
        db (Session): The SQLAlchemy database session used to interact with the database.

    Returns:
        Union[Budget, None]: The budget object if found, otherwise None.
    """
    return (
        db.query(Budget)
        .filter(
            Budget.user_id == trasaction.user_id,
            Budget.transaction_type_category_id
            == trasaction.transaction_type_category_id,
            Budget.start_date <= trasaction.transaction_date,
            Budget.end_date >= trasaction.transaction_date,
        )
        .first()
    )


def create_budget_expense(data: BudgetExpenseCreate, db: Session) -> int:
    """
    Creates a new budget expense record in the database.

    Args:
        data (BudgetExpenseCreate): A `BudgetExpenseCreate` object containing the details
                                   of the budget expense (budget_id, transaction_type_category, amount_spent).
        db (Session): The SQLAlchemy database session used to interact with the database.

    Returns:
        int: The ID of the newly created budget expense.
    """
    db_budget_expense = BudgetExpense(
        budget_id=data["budget_id"],
        transaction_type_category_id=data["transaction_type_category_id"],
        transaction_type_subcategory_id=data["transaction_type_subcategory_id"],
        amount_spent=data["amount_spent"],
    )
    db.add(db_budget_expense)
    db.commit()
    db.refresh(db_budget_expense)
    return db_budget_expense.id


def update_budget_expense(data: BudgetExpenseUpdate, db: Session) -> None:
    """
    Updates a budget expense record in the database with the provided new data.

    Args:
        data (BudgetExpenseUpdate): The new data to update the budget expense with.
                                  This is expected to be an instance of `BudgetExpenseUpdate` model,
                                  containing the fields to be updated.
        db (Session): The SQLAlchemy database session used to interact with the database.

    Returns:
        None: The function performs the update directly on the database and does not return any value.
    """
    db.query(BudgetExpense).filter(BudgetExpense.budget_id == data["budget_id"]).update(
        {BudgetExpense.amount_spent: data["amount_spent"]}
    )
    db.commit()


def check_budget_expense(budget: Budget, db: Session) -> Union[BudgetExpense, None]:
    """
    Checks and retrieves if there is a budget expense for the given budget ID and transaction category.

    Args:
        budget (Budget): Object of Budget.
        db (Session): The SQLAlchemy database session used to interact with the database.

    Returns:
        Union[BudgetExpense, None]: The budget expense object if found, otherwise None.
    """
    _filters = [BudgetExpense.budget_id == budget.id]
    if budget.transaction_type_category_id:
        _filters.append(
            BudgetExpense.transaction_type_category_id
            == budget.transaction_type_category_id
        )
    if budget.transaction_type_subcategory_id:
        _filters.append(
            Budget.transaction_type_subcategory_id
            == budget.transaction_type_subcategory_id
        )
    return db.query(BudgetExpense).filter(*_filters).first()


def budget_tracker(trasaction: Transaction, db: Session) -> None:
    """
    Tracks and updates the budget expenses for a given user and transaction.

    Steps:
        1. Check if the user has a budget associated with the transaction's category.
        2. If budget exists, check if an expense record for the budget already exists:
            - If it exists, update the amount spent.
            - If it does not exist, create a new expense record.
        3. Calculate the amount remaining for the budget and the percentage of the budget used.
        4. Provides warnings if the user exceeds certain spending thresholds
            for the budgeted category (80%, 90%, or 100% of the allocated budget).

    Args:
        transaction (Transaction): Object of Transaction.
        db (Session): The SQLAlchemy database session used to interact with the database.

    Returns:
        None: The function does not return any value.
    """
    print("Checking Budget ....")
    budget = check_budget(trasaction, db)
    print("Budget: ", budget)
    if budget:
        budget_expense = check_budget_expense(budget, db)
        print("budget expense: ", budget_expense)
        if budget_expense:
            amount_spent_so_far = budget_expense.amount_spent + trasaction.amount
            data = {"budget_id": budget.id, "amount_spent": amount_spent_so_far}
            print("Updating budget expense amount...")
            update_budget_expense(data, db)
        else:
            amount_spent_so_far = trasaction.amount
            data = {
                "budget_id": budget.id,
                "transaction_type_category_id": budget.transaction_type_category_id,
                "transaction_type_subcategory_id": (
                    budget.transaction_type_subcategory_id
                    if budget.transaction_type_subcategory_id
                    else None
                ),
                "amount_spent": amount_spent_so_far,
            }
            print("Creating budget expense amount...")
            budget_expense_id = create_budget_expense(data, db)


def budget_status(budget_id: int, user_id: int, db: Session):
    budget = (
        db.query(Budget)
        .filter(Budget.id == budget_id, Budget.user_id == user_id)
        .first()
    )
    print("Budget: ", budget)
    if budget:
        budget_expense = check_budget_expense(budget, db)
        print("budget expense: ", budget_expense)
        if budget_expense:
            amount_spent_so_far = budget_expense.amount_spent
        else:
            print("Budget allocated but no expense so far.")
            amount_spent_so_far = 0

        # Amount remaining for this budget
        amount_remaining = budget.amount - amount_spent_so_far
        print("Amount remaining: ", amount_remaining)
        # Total spent amount till now (in %)
        percentage = (amount_spent_so_far / budget.amount) * 100
        print("Percentage: ", percentage)

        transaction_type_category = (
            db.query(ExpenseCategory.category)
            .filter(
                ExpenseCategory.id == budget.transaction_type_category_id,
            )
            .scalar()
        )
        if budget.transaction_type_subcategory_id:
            transaction_type_subcategory = (
                db.query(ExpenseSubCategory.sub_category)
                .filter(
                    ExpenseSubCategory.id == budget.transaction_type_subcategory_id,
                )
                .scalar()
            )
        else:
            transaction_type_subcategory = ""

        # Send warnings
        alert = f"You have spent {percentage}% of your budget for {transaction_type_category} {transaction_type_subcategory} this month!"
        if percentage > 80:
            alert = f"You have spent {percentage}% of your budget for {transaction_type_category} this month!"
        elif percentage > 90:
            alert = f"You have spent {percentage}% of your budget for {transaction_type_category} this month!"
        elif percentage > 100:
            alert = f"You have exceeded your budget limit for {transaction_type_category} this month!"

    return {
        "transaction_type_category": transaction_type_category,
        "transaction_type_subcategory": transaction_type_subcategory,
        "amount": budget.amount,
        "amount_spent": amount_spent_so_far,
        "amount_remaining": amount_remaining,
        "percentage": percentage,
        "alert": alert,
    }


def budget_usage(user_id: int, month: str, db: Session):
    """
    Budget usages of categories, sub categories.
    """
    year = 2025
    start_date, end_date = get_month_range(month, year)
    # all budgets setted for categories of current month
    budgets = (
        db.query(Budget)
        .filter(
            Budget.user_id == user_id,
            Budget.start_date >= start_date,
            Budget.end_date <= end_date,
        )
        .all()
    )
    # check the budgets status for those categories
    usage = []
    for budget in budgets:
        status = budget_status(budget.id, user_id, db)
        usage.append(status)
    return usage
