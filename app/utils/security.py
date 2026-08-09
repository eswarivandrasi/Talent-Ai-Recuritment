import re

EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+$')


def sanitize_input(text):
    """Normalize user input. Jinja auto-escaping handles HTML output safely."""
    if not text or not isinstance(text, str):
        return ""
    return text.strip()


def validate_email(email):
    if not email:
        return False
    return bool(EMAIL_PATTERN.fullmatch(email.strip()))


def validate_password_strength(password):
    if not password or len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if len(password) > 128:
        return False, "Password must be 128 characters or fewer."
    return True, ""
