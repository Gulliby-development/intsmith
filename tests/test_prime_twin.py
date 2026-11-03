import pytest

from intsmith.commands.prime import run
from intsmith.core.text import Failure


class FakeIo:
    def __init__(self) -> None:
        self.out_calls: list[str] = []

    def read_stdin(self) -> bytes:
        return b""

    def out(self, text: str) -> None:
        self.out_calls.append(text)

    def err(self, text: str) -> None:
        raise AssertionError(text)


@pytest.mark.parametrize(
    ("argv", "expected"),
    [
        (["list", "--twin", "1", "30"], "twin primes from 1 to 30: 4\n3 5\n5 7\n11 13\n17 19\n"),
        (["list", "1", "30", "--twin"], "twin primes from 1 to 30: 4\n3 5\n5 7\n11 13\n17 19\n"),
        (["list", "--twin", "--count", "1", "30"], "twin primes from 1 to 30: 4\n"),
        (["list", "--count", "--twin", "10", "30"], "twin primes from 10 to 30: 2\n"),
        (["list", "--twin", "10", "30"], "twin primes from 10 to 30: 2\n11 13\n17 19\n"),
        (["list", "--twin", "29", "31"], "twin primes from 29 to 31: 1\n29 31\n"),
        (["list", "--twin", "29", "30"], "twin primes from 29 to 30: 0\n"),
        (["list", "--twin", "0", "1"], "twin primes from 0 to 1: 0\n"),
        (["list", "--twin", "2", "2"], "twin primes from 2 to 2: 0\n"),
        (["list", "--twin", "7", "9"], "twin primes from 7 to 9: 0\n"),
        (
            ["list", "--twin", "1000", "1100"],
            "twin primes from 1000 to 1100: 5\n1019 1021\n1031 1033\n1049 1051\n1061 1063\n1091 1093\n",
        ),
        (["list", "--twin", "--count", "1000", "11000"], "twin primes from 1000 to 11000: 186\n"),
    ],
)
def test_twin_lists_pairs_inside_the_range(argv: list[str], expected: str) -> None:
    io = FakeIo()

    assert run(argv, io) == 0
    assert io.out_calls == [expected]


def test_list_without_twin_is_unchanged() -> None:
    io = FakeIo()

    assert run(["list", "10", "13"], io) == 0
    assert io.out_calls == ["primes from 10 to 13: 2\n11\n13\n"]


@pytest.mark.parametrize(
    ("argv", "message"),
    [
        (["test", "--twin", "7"], 'unknown option "--twin"'),
        (["next", "--twin", "7"], 'unknown option "--twin"'),
        (["list", "--twin=1", "1", "30"], "--twin takes no value"),
        (["list", "--twin", "30", "1"], "HI must not be below LO"),
        (["list", "--twin", "0", "10001"], "HI - LO must be at most 10000"),
        (["list", "--twin", "5"], "missing HI"),
    ],
)
def test_twin_keeps_the_prime_command_checks(argv: list[str], message: str) -> None:
    io = FakeIo()

    with pytest.raises(Failure) as failure:
        run(argv, io)

    assert failure.value.message == message
    assert io.out_calls == []
