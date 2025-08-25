from functools import wraps


def subscription_type_list(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        current_user = kwargs.get("current_user")
        if current_user.users_subscriptions:
            user_subscription = current_user.users_subscriptions[0]
            if user_subscription.status == "active":
                print("User's subscription is active")
                # kwargs["page_size"] = 5
            elif user_subscription.status == "expired":
                print("User's subscription is expired")
            return func(*args, **kwargs)
        else:
            print("User currently don't have subscription!")

    return wrapper
