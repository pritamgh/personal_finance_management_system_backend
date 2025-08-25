from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.dependencies import get_db
from src.user.services import get_current_user

auth_routes = [
    "/api/v1/user/auth/signup/",
    "/api/v1/user/auth/login/",
    "/api/v1/transaction/categories",
    "/api/v1/transaction/sub-categories",
]
free_routes = [
    "/api/v1/transaction/create/"
    "/api/v1/transaction/read/"
    "/api/v1/transaction/list/"
]
premium_routes = ["/api/v1/transaction/update/", "/api/v1/transaction/delete/"]


class SubscriptionMiddleware(BaseHTTPMiddleware):

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request, call_next):
        print("URL path: ", request.url.path)
        print("Headers: ", request.headers)
        if request.url.path not in auth_routes:
            authorization = request.headers.get("authorization")
            if not authorization:
                raise HTTPException(
                    status_code=401, detail="Authorization Header missing."
                )
            if not authorization.startswith("Bearer "):
                raise HTTPException(
                    status_code=401, detail="Invalid Authorization code."
                )

            # Extract the token (after 'Bearer ')
            token = authorization[7:]
            print("Access Token: ", token)

            # get Db session
            db = next(get_db())

            # get the current user
            current_user = get_current_user(token, db)
            print("User ID:", current_user.id)

            requested_api = request.url.path
            print("Requested path: ", requested_api)

            # Check if the user is trying to access a premium route and if they have a subscription
            if self.is_premium_route(request) and not current_user.users_subscriptions:
                print("Free tier user.")
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={
                        "detail": "You must be a premium user to access this feature."
                    },
                )

        # Continue processing the request
        response = await call_next(request)
        return response

    def is_premium_route(self, request):
        """
        Checks if the request is targeting an endpoint that requires premium access.
        Add your logic here to identify which endpoints require premium access.
        """
        return any(premium_api in request.url.path for premium_api in premium_routes)
