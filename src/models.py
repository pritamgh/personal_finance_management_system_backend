import enum
from itertools import chain

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship, validates

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    transactions = relationship("Transaction", back_populates="owner")
    budgets = relationship("Budget", back_populates="user")
    users_subscriptions = relationship("UsersSubscription", back_populates="owner")


class TransactionType(Base):
    __tablename__ = "transaction_types"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)


class IncomeCategory(Base):
    __tablename__ = "income_categories"

    id = Column(Integer, primary_key=True, index=True)
    transaction_type_id = Column(Integer, ForeignKey("transaction_types.id"))
    category = Column(String)
    description = Column(String)
    icon = Column(String)


class ExpenseCategory(Base):
    __tablename__ = "expense_categories"

    id = Column(Integer, primary_key=True, index=True)
    transaction_type_id = Column(Integer, ForeignKey("transaction_types.id"))
    category = Column(String)
    description = Column(String)
    icon = Column(String)


class ExpenseSubCategory(Base):
    __tablename__ = "expense_subcategories"

    id = Column(Integer, primary_key=True, index=True)
    expense_category_id = Column(Integer, ForeignKey("expense_categories.id"))
    sub_category = Column(String)
    description = Column(String)
    icon = Column(String)


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    transaction_type_id = Column(Integer)
    transaction_type_category_id = Column(
        Integer
    )  # store both IncomeCategory and ExpenseCategory IDs
    transaction_type_subcategory_id = Column(Integer)
    amount = Column(Float)
    description = Column(String)
    transaction_date = Column(DateTime)

    owner = relationship("User", back_populates="transactions")


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    transaction_type_category_id = Column(Integer)
    transaction_type_subcategory_id = Column(Integer)
    amount = Column(Float)
    start_date = Column(DateTime)
    end_date = Column(DateTime)

    user = relationship("User", back_populates="budgets")
    budget_expenses = relationship("BudgetExpense", back_populates="budgets")


class BudgetExpense(Base):
    """
    When a new transaction created of a specific category, that time
    check the if that category is budgeted then look up the relevant BudgetExpense
    for that category and update the amount spent. If no such record exists,
    then create a new one.
    """

    __tablename__ = "budget_expenses"

    id = Column(Integer, primary_key=True, index=True)
    budget_id = Column(Integer, ForeignKey("budgets.id"))
    transaction_type_category_id = Column(Integer)
    transaction_type_subcategory_id = Column(Integer)
    amount_spent = Column(Float)

    budgets = relationship("Budget", back_populates="budget_expenses")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    plan_type = Column(String)
    description = Column(String)
    price = Column(Float)
    duration = Column(Integer)

    users_subscriptions = relationship(
        "UsersSubscription", back_populates="subscription"
    )


class UsersSubscription(Base):
    __tablename__ = "users_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"))
    subscription_date = Column(DateTime)
    subscription_end_date = Column(DateTime)
    status = Column(String)  # active, expired

    owner = relationship("User", back_populates="users_subscriptions")
    subscription = relationship("Subscription", back_populates="users_subscriptions")
