import re
from typing import Protocol

from intsmith.core.text import Failure


class Io(Protocol):
    def read_stdin(self) -> bytes: ...

    def out(self, text: str) -> None: ...

    def err(self, text: str) -> None: ...


def _decode_stdin(data: bytes) -> list[str]:
    try:
        text = data.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        raise Failure("<stdin>: input is not valid UTF-8") from None

    text = text.removeprefix("\ufeff")
    return [word for word in re.split(r"[ \t\r\n]+", text) if word]


def words_of(io: Io, args: list[str]) -> list[str]:
    if args != ["-"]:
        return args

    try:
        data = io.read_stdin()
    except OSError:
        raise Failure("<stdin>: cannot read the input") from None

    words = _decode_stdin(data)
    if not words:
        raise Failure("<stdin>: no input")
    return words
