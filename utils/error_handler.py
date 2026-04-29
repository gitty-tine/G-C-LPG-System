import re


def clean_db_error(error):
    """
    Converts raw MySQL/DB errors into user-friendly messages.
    Strips error codes like '1644 (45000):' from SIGNAL messages.
    """
    msg = str(error or "").strip()

    match = re.search(r"\d+\s*\(\d+\)\s*:\s*(.+)", msg)
    if match:
        return match.group(1).strip()

    msg = re.sub(r"^\d+\s*\(\w+\)\s*:\s*", "", msg).strip()

    if "Duplicate entry" in msg and "username" in msg.lower():
        return "Username is already taken."
    if "Duplicate entry" in msg and "email" in msg.lower():
        return "Email is already in use by another account."
    if "Cannot delete or update a parent row" in msg:
        return "This record cannot be deleted because it is linked to other records."
    if "Connection refused" in msg or "Can't connect" in msg:
        return "Could not connect to the database. Please try again."
    if "Access denied" in msg:
        return "Database access denied. Please contact your administrator."

    return "An unexpected error occurred. Please try again."
