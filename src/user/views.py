from fastapi import APIRouter, Body, Depends, status
from sqlalchemy.orm import Session

from src.dependencies import get_db
from src.schemas import SignUp, User
from src.user.services import (
    authenticate_user,
    create_access_token,
    create_subscription,
    create_user,
    get_current_user,
)

router = APIRouter()


@router.post("/auth/sign-up/")
def sign_up(user: SignUp, db: Session = Depends(get_db)):
    """
    Register / SignUp a new user.

    Args:
        user (SignUp): The user data (such as username, email, password)
                       submitted for registration. The data should be
                       validated according to the schema defined in SignUp.
        db (Session): The database session dependency used to interact with the
                      database.

    Returns:
        dict: If user is registered successfully, it returns a success
                message along with an access token. If any error occured,
                it returns an error message and an unauthorized response.
    """
    try:
        user_id = create_user(user=user, db=db)
        if user_id:
            access_token = create_access_token(data={"sub": user.email})
            return {
                "message": "Signed Up successfully.",
                "access_token": access_token,
                "token_type": "bearer",
                "status": "success",
            }, status.HTTP_201_CREATED
        else:
            return {
                "message": "Something went wrong while registering user.",
                "status": "error",
            }, status.HTTP_401_UNAUTHORIZED
    except Exception as exe:
        return {
            "message": str(exe),
            "status": "error",
        }, status.HTTP_500_INTERNAL_SERVER_ERROR


@router.post("/auth/login/")
def login(user: SignUp, db: Session = Depends(get_db)):
    """
    User login and generate access token.

    Args:
        user (SignUp): The user data containing the email and password
                       to be authenticated.
        db (Session): The database session dependency used to interact with the
                        database.

    Returns:
        dict: If the user is authenticated successfully, it returns a success
                message along with an access token. If the credentials are invalid,
                it returns an error message and an unauthorized response.
    """
    try:
        user, msg = authenticate_user(
            email=user.email, requested_password=user.password, db=db
        )
        if user:
            access_token = create_access_token(data={"sub": user.email})
            return {
                "message": "Logged In successfully.",
                "access_token": access_token,
                "token_type": "bearer",
                "status": "success",
            }, status.HTTP_200_OK
        else:
            return {"message": msg, "status": "error"}, status.HTTP_401_UNAUTHORIZED
    except Exception as exe:
        return {
            "message": str(exe),
            "status": "error",
        }, status.HTTP_500_INTERNAL_SERVER_ERROR


@router.get("/auth/me/")
def get_auth_user(current_user: User = Depends(get_current_user)):
    return {
        "message": f"Hello {current_user.email}, you have access to this route!",
        "status": "success",
    }, status.HTTP_200_OK


@router.post("/subscription/create/")
def subscription_add(
    data: dict = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Creates a new subscription plan for the current user.

    Args:
        subscription_id (int): The unique identifier of the subscription to create.
        current_user (User, default Depends(get_current_user)): The currently authenticated user
                                   (retrieved from the `get_current_user` dependency).
        db (Session, default Depends(get_db)): The SQLAlchemy database session used to interact with
                                               the database (retrieved from the `get_db` dependency).

    Returns:
        dict: A dictionary containing a success message if the transaction
              is created successfully, or an error message if an exception occurs.
    """
    try:
        user_subscription_id = create_subscription(
            data.get("subscription_id"), current_user.id, db
        )
        return {
            "id": user_subscription_id,
            "message": "Subscription created.",
            "status": "success",
        }, status.HTTP_201_CREATED
    except Exception as exe:
        return {
            "message": str(exe),
            "status": "error",
        }, status.HTTP_500_INTERNAL_SERVER_ERROR
