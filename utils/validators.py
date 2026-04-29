import re


def validate_password_strength(password):
    """
    Returns (is_valid, error_message).
    Rules:
    - Not empty or only spaces
    - At least 8 characters
    - At least 1 uppercase letter
    - At least 1 lowercase letter
    - At least 1 number
    - At least 1 special character
    """
    password = password or ""

    if not password.strip():
        return False, "Password cannot be empty or contain only spaces."
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number."
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?`~]", password):
        return False, "Password must contain at least one special character (!@#$%^&* etc)."
    return True, ""


def validate_email(email):
    """
    Returns (is_valid, error_message).
    Rules:
    - Not empty
    - No spaces
    - Valid format using regex
    """
    email = email or ""

    if not email:
        return False, "Email address cannot be empty."
    if email != email.strip():
        return False, "Email address cannot start or end with spaces."
    if " " in email:
        return False, "Email address cannot contain spaces."

    pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email.strip()):
        return False, "Please enter a valid email address (e.g. name@example.com)."
    return True, ""
