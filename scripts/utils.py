import re

def extractUserId(s: str) -> str:
    """
    Extracts the numeric user ID from a string.

    Example:
        "73120473(r***@tutamail.com)" -> "73120473"
    """
    match = re.match(r"(\d+)", s)
    if match:
        return match.group(1)
    raise ValueError(f"No user ID found in string: {s}")