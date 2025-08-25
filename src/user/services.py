from datetime import datetime, timedelta, timezone
from typing import Union

import jwt
from fastapi import Depends, HTTPException, status
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.config import Config
from src.dependencies import get_db, oauth2_scheme
from src.models import Subscription, User, UsersSubscription
from src.schemas import SignUp


def get_pwd_context():
    """
    Create and return a CryptContext for hashing and verifying passwords.

    Returns:
        CryptContext: The password context object.
    """
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context


def create_user(user: SignUp, db: Session) -> int:
    """
    Create a new user in the database.

    Args:
        user (SignUp): The user data to be created.
        db (Session): The database session for interaction with the database.

    Returns:
        int: The ID of the newly created user.
    """
    pwd_context = get_pwd_context()
    hashed_password = pwd_context.hash(user.password)
    user.password = hashed_password
    db_user = User(
        email=user.email,
        password=user.password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user.id


def get_user(email: str, db: Session) -> Union[User, None]:
    """
    Retrieve a user from the database by email.

    Args:
        email (str): The email of the user to be fetched.
        db (Session): The database session to query the user.

    Returns:
        Union[User, None]: The user object if found, otherwise None.
    """
    return db.query(User).filter(User.email == email).one_or_none()


def verify_password(requested_password: str, password: str) -> bool:
    """
    Verify if the requested password matches the stored password hash.

    Args:
        requested_password (str): The password provided by the user.
        password (str): The hashed password stored in the database.

    Returns:
        bool: True if passwords match, False otherwise.
    """
    pwd_context = get_pwd_context()
    return pwd_context.verify(requested_password, password)


def authenticate_user(
    email: str, requested_password: str, db: Session
) -> Union[tuple[User, str], tuple[bool, str]]:
    """
    Authenticate a user by checking the email and password.

    Args:
        email (str): The email of the user to be authenticated.
        requested_password (str): The password provided by the user.
        db (Session): The database session to retrieve user information.

    Returns:
        Union[tuple[User, str], tuple[bool, str]]: The user object with message if authentication is successful,
                            otherwise False along with an error message.
    """
    user = get_user(email, db)
    if not user:
        return False, "Email not found or incorrect."
    if not verify_password(requested_password, user.password):
        return False, "Incorrect password."
    return user, "User authenticated."


def create_access_token(data: dict) -> str:
    """
    Generate an access token (JWT) for authentication.

    Args:
        data (dict): The data (payload) to be included in the token. Typically contains user information.

    Returns:
        str: The generated JWT access token.
    """
    to_encode = data.copy()
    access_token_expires = timedelta(
        minutes=Config.settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    if access_token_expires:
        expire = datetime.now(tz=timezone.utc) + access_token_expires
    else:
        expire = datetime.now(tz=timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, Config.settings.SECRET_KEY, algorithm=Config.settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> str:
    """
    Verify the JWT token and extract the user data.

    Args:
        token (str): The JWT token to be verified.

    Returns:
        email: The extracted user email if the token is valid.
    """
    try:
        payload = jwt.decode(
            token, Config.settings.SECRET_KEY, algorithms=[Config.settings.ALGORITHM]
        )
        email = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials.",
            )
        return email
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired.",
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
        )


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """
    Retrieves the current authenticated user based on the provided OAuth2 token.

    Args:
        token (str): The OAuth2 token representing the user's authentication. Defaults to
            Depends(oauth2_scheme) which extracts the token from the request.
        db (Session): The database session to retrieve user information.

    Returns:
        user (User): The authenticated user object.
    """
    email = verify_token(token)
    user = get_user(email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found."
        )
    return user


def create_subscription(subscription_id: int, user_id: int, db: Session) -> int:
    subscription = (
        db.query(Subscription).filter(Subscription.id == subscription_id).first()
    )
    subscription_date = datetime.now(tz=timezone.utc)
    if subscription.plan_type == "30 days":
        subscription_end_date = subscription_date + timedelta(days=30)
    elif subscription.plan_type == "6 months":
        subscription_end_date = subscription_date + timedelta(days=180)
    elif subscription.plan_type == "1 year":
        subscription_end_date = subscription_date + timedelta(days=365)

    db_user_subscription = UsersSubscription(
        user_id=user_id,
        subscription_id=subscription_id,
        subscription_date=subscription_date,
        subscription_end_date=subscription_end_date,
        status="active",
    )
    db.add(db_user_subscription)
    db.commit()
    db.refresh(db_user_subscription)
    return db_user_subscription.id
