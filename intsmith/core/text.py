class Failure(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


def show(text: str) -> str:
    """Render user text safely in an ASCII-quoted diagnostic."""
    return '"' + "".join(char if "!" <= char <= "~" else "?" for char in text) + '"'


def join_or(items: list[str]) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} or {items[1]}"
    return f"{', '.join(items[:-1])} or {items[-1]}"


def plural(n: int, one: str, many: str) -> str:
    return f"{n} {one if n == 1 else many}"


def line(key: str, value: str) -> str:
    return f"{key:<8}  {value}\n"


BIG = 99999999999999999999
