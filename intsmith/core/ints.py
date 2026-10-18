from intsmith.core.text import Failure, show


def parse_int(name: str, text: str, lo: int, hi: int) -> int:
    """Parse a canonical ASCII decimal integer within inclusive bounds."""
    digits = text.removeprefix("-")
    valid = digits == "0" or (
        1 <= len(digits) <= 20
        and "1" <= digits[0] <= "9"
        and all("0" <= digit <= "9" for digit in digits[1:])
    )
    if text.startswith("-") and digits == "0":
        valid = False
    if not valid:
        raise Failure(f"invalid {name} {show(text)} (expected an integer from {lo} to {hi})")

    value = int(text)
    if not lo <= value <= hi:
        raise Failure(f"invalid {name} {show(text)} (expected an integer from {lo} to {hi})")
    return value
