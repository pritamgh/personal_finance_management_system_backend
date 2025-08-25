import re
from datetime import datetime
from typing import Optional, Union

from fastapi import HTTPException, Request, status


def validate_search_query(q: Optional[str]) -> Optional[str]:
    """
    Validates, sanitizes, and normalizes the search query string.

    This function performs the following steps:
    - **Trims whitespace**: Any leading or trailing spaces from the
        search query are removed using the `strip()` method.
    - **Length validation**: Ensures the query is not excessively long.
        If the length exceeds 255 characters, an error is raised with a `400 Bad Request` status.
    - **Allowed character check**: The query is checked against a
        regular expression to ensure it only contains alphanumeric characters (a-zA-Z0-9),
        whitespace, and common punctuation (`-_,.`).
        If invalid characters are found, an error is raised with a `400 Bad Request` status.
    - **Case normalization**: The query is converted to lowercase to ensure case-insensitive searching.
    """
    if q:
        q = q.strip()  # Trim whitespace
        if len(q) > 255:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query is too long. Maximum length is 255 characters.",
            )
        if not re.match(r"^[a-zA-Z0-9\s\-_,.]*$", q):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid search query. Special characters are not allowed.",
            )
        q = q.lower()  # Normalize to lowercase
    return q


def prepare_list_params(
    request: Request,
    params: dict,
    q: Optional[str] = None,
    transaction_type_id: Optional[int] = None,
    min_amount: Optional[Union[int, float]] = None,
    max_amount: Optional[Union[int, float]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    order_by: Optional[str] = None,
    group_by: Optional[str] = None,
    page_number: Optional[int] = None,
    page_size: Optional[int] = None,
):
    if q:
        validated_query = validate_search_query(q)
        params["validated_query"] = validated_query
    if transaction_type_id:
        params["transaction_type_id"] = transaction_type_id
    if request.query_params.getlist("income_category_ids[]"):
        params["income_category_ids"] = [
            int(id) for id in request.query_params.getlist("income_category_ids[]")
        ]
    if request.query_params.getlist("expense_category_ids[]"):
        params["expense_category_ids"] = [
            int(id) for id in request.query_params.getlist("expense_category_ids[]")
        ]
    if request.query_params.getlist("expense_subcategory_ids[]"):
        params["expense_subcategory_ids"] = [
            int(id) for id in request.query_params.getlist("expense_subcategory_ids[]")
        ]
    if min_amount and max_amount:
        if min_amount > max_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Minimum amount should be less than Maximum amount.",
            )
        params["min_amount"] = min_amount
        params["max_amount"] = max_amount
    if start_date and end_date:
        start_date = start_date.split("T")[0] if "T" in start_date else start_date
        end_date = end_date.split("T")[0] if "T" in end_date else end_date
        if datetime.strptime(start_date, "%Y-%m-%d") > datetime.strptime(
            end_date, "%Y-%m-%d"
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start date should be less than End date.",
            )
        params["start_date"] = start_date
        params["end_date"] = end_date
    if order_by:
        params["order_by"] = order_by
    if group_by:
        params["group_by"] = group_by
    if page_number:
        params["page_number"] = page_number
    if page_size:
        params["page_size"] = page_size
