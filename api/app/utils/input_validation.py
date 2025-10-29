""" Input validation parameter functions """
import re


VALID_NAME_PATTERN = r"^[\w\s\-\.,&()áéíóúÁÉÍÓÚñÑ']+$"
MAX_CHAR_LENGTH = 100


def validate_name(
        name: str,
        length: int = MAX_CHAR_LENGTH,
        string_pattern: str = VALID_NAME_PATTERN
) -> None:
    """
    Validates that the institution name is not empty, under 50 characters,
    and only contains allowed characters.

    Args:
        name (str): Institution name to validate.
        length (int, optional): Length of institution name to validate.
        string_pattern (str, optional): String pattern to validate against.

    Raises:
        ValueError: If the name is empty or contains invalid characters.
    """
    regex_pattern = re.compile(string_pattern)
    if not name or not name.strip():
        raise ValueError("Name cannot be empty.")

    if len(name.strip()) >= length:
        raise ValueError(F"Name must be less than {length} characters.")

    if not regex_pattern.fullmatch(name):
        raise ValueError("Name contains invalid characters.")
