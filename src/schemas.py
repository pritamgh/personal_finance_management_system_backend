from datetime import datetime
from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel

from src.models import ExpenseCategory, IncomeCategory, TransactionType


class SignUp(BaseModel):
    """
    SignUp model represents the data required for user registration.
    """

    email: str
    password: str


class User(BaseModel):
    """
    User model represents a user entity in the system.
    """

    email: str

    class Config:
        orm_mode = True


class TransactionBase(BaseModel):
    """
    TransactionBase model represents the basic information for a financial transaction.
    """

    transaction_type_id: int
    transaction_type_category_id: int
    transaction_type_subcategory_id: Optional[int] = None
    amount: float
    description: Optional[str] = None
    transaction_date: datetime


class TransactionCreate(TransactionBase):
    """
    TransactionCreate model is used to create a new transaction.
    Inherits from `TransactionBase` and is designed to validate the data needed
    to create a new transaction record. This model is typically used during
    transaction creation processes.
    """

    pass


class TransactionUpdate(TransactionBase):
    """
    TransactionUpdate model is used to update an existing transaction.
    Inherits from `TransactionBase` and allows partial updates to a transaction's data.
    Attributes in this model are optional or nullable, enabling flexible modification of
    existing transaction records.
    """

    transaction_type_id: Optional[int] = None
    transaction_type_category_id: int
    transaction_type_subcategory_id: Optional[int] = None
    amount: float | None = None
    description: Optional[str] = None
    transaction_date: datetime | None = None


class BudgetBase(BaseModel):
    transaction_type_category_id: int
    transaction_type_subcategory_id: Optional[int] = None
    amount: float
    start_date: datetime
    end_date: datetime


class BudgetCreate(BudgetBase):
    pass


class BudgetUpdate(BudgetBase):
    transaction_type_category_id: Optional[int] = None
    transaction_type_subcategory_id: Optional[int] = None
    amount: float | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None


class BudgetExpenseBase(BaseModel):
    budget_id: int
    transaction_type_category_id: int
    transaction_type_subcategory_id: Optional[int] = None
    amount_spent: float


class BudgetExpenseCreate(BudgetExpenseBase):
    pass


class BudgetExpenseUpdate(BudgetExpenseBase):
    transaction_type_category_id: Optional[int] = None
    transaction_type_subcategory_id: Optional[int] = None
    amount_spent: float | None = None


class SavingBase(BaseModel):
    amount: float
    saving_date: datetime


class SavingCreate(SavingBase):
    pass


class Saving(SavingBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True
