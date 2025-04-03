from config import ALLOWED_USERS


def is_user_allowed(user_id: int) -> bool:
    return user_id in ALLOWED_USERS
