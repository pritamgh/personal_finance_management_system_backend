from fastapi import APIRouter, Body, Depends, status
from sqlalchemy.orm import Session

from src.dependencies import get_db
from src.models import (
    ExpenseCategory,
    ExpenseSubCategory,
    IncomeCategory,
    TransactionType,
)

router = APIRouter()


@router.post("/type/")
def type_create(data: dict = Body(...), db: Session = Depends(get_db)):
    try:
        obj = TransactionType(type=data.get("type"))
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return {"data": obj.id, "status": "success"}, status.HTTP_200_OK
    except Exception as exe:
        return {
            "message": str(exe),
            "status": "error",
        }, status.HTTP_500_INTERNAL_SERVER_ERROR


@router.post("/category/")
def category_create(data: dict = Body(...), db: Session = Depends(get_db)):
    try:
        # obj = IncomeCategory(
        #     transaction_type_id= data.get("transaction_type_id"),
        #     category=data.get("category")
        # )
        obj = ExpenseCategory(
            transaction_type_id=data.get("transaction_type_id"),
            category=data.get("category"),
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return {"data": obj.id, "status": "success"}, status.HTTP_200_OK
    except Exception as exe:
        return {
            "message": str(exe),
            "status": "error",
        }, status.HTTP_500_INTERNAL_SERVER_ERROR


@router.post("/subcategory/")
def category_create(data: dict = Body(...), db: Session = Depends(get_db)):
    try:
        # obj = IncomeCategory(
        #     transaction_type_id= data.get("transaction_type_id"),
        #     category=data.get("category")
        # )
        obj = ExpenseSubCategory(
            expense_category_id=data.get("expense_category_id"),
            sub_category=data.get("sub_category"),
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return {"data": obj.id, "status": "success"}, status.HTTP_200_OK
    except Exception as exe:
        return {
            "message": str(exe),
            "status": "error",
        }, status.HTTP_500_INTERNAL_SERVER_ERROR
