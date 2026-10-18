import pytest

from intsmith.commands.sqrt import run
from intsmith.core.text import Failure


class FakeIo:
    def __init__(self) -> None:
        self.read_calls = 0
        self.out_calls: list[str] = []
        self.err_calls: list[str] = []

    def read_stdin(self) -> bytes:
        self.read_calls += 1
        return b""

    def out(self, text: str) -> None:
        self.out_calls.append(text)

    def err(self, text: str) -> None:
        self.err_calls.append(text)


def assert_answer(argv: list[str], expected: str, expected_status: int) -> None:
    io = FakeIo()

    assert run(argv, io) == expected_status
    assert io.out_calls == [expected]
    assert io.err_calls == []
    assert io.read_calls == 0


def assert_failure(argv: list[str], expected_message: str) -> None:
    io = FakeIo()

    with pytest.raises(Failure) as exc_info:
        run(argv, io)

    assert exc_info.value.message == expected_message
    assert io.out_calls == []
    assert io.err_calls == []
    assert io.read_calls == 0


@pytest.mark.parametrize(
    ("argv", "expected", "expected_status"),
    [
        (
            ["10", "13"],
            "residue   10\nsymbol    1\nroots     6 7\n",
            0,
        ),
        (
            ["5", "13"],
            "residue   5\nsymbol    -1\nstatus    no square root\n",
            1,
        ),
        (
            ["0", "13"],
            "residue   0\nsymbol    0\nroots     0\n",
            0,
        ),
        (
            ["2", "2"],
            "residue   0\nsymbol    0\nroots     0\n",
            0,
        ),
        (
            ["1", "2"],
            "residue   1\nsymbol    1\nroots     1\n",
            0,
        ),
        (
            ["-1", "7"],
            "residue   6\nsymbol    -1\nstatus    no square root\n",
            1,
        ),
        (
            ["-3", "7"],
            "residue   4\nsymbol    1\nroots     2 5\n",
            0,
        ),
        (
            ["99999999999999999999", "2"],
            "residue   1\nsymbol    1\nroots     1\n",
            0,
        ),
        (
            ["-99999999999999999999", "2"],
            "residue   1\nsymbol    1\nroots     1\n",
            0,
        ),
        (
            ["1", "99999999999999999989"],
            "residue   1\nsymbol    1\nroots     1 99999999999999999988\n",
            0,
        ),
        (
            ["15241578750190521", "99999999999999999989"],
            (
                "residue   15241578750190521\nsymbol    1\n"
                "roots     123456789 99999999999876543200\n"
            ),
            0,
        ),
    ],
)
def test_sqrt_answers_are_exact_sorted_and_truncate_no_root_results(
    argv: list[str], expected: str, expected_status: int
) -> None:
    assert_answer(argv, expected, expected_status)


@pytest.mark.parametrize(
    ("argv", "expected_message"),
    [
        ([], "missing A"),
        (["1"], "missing P"),
        (["not-an-integer"], "missing P"),
        (["1", "13", "extra"], "too many arguments"),
        (["bad", "13", "extra"], "too many arguments"),
        (["--help"], 'unknown option "--help"'),
        (["--", "1", "13"], 'unknown option "--"'),
        (
            ["--help", "bad", "13"],
            'unknown option "--help"',
        ),
        (
            ["01", "13"],
            (
                'invalid A "01" (expected an integer from -99999999999999999999 to '
                "99999999999999999999)"
            ),
        ),
        (
            ["-0", "13"],
            (
                'invalid A "-0" (expected an integer from -99999999999999999999 to '
                "99999999999999999999)"
            ),
        ),
        (
            ["+3", "13"],
            (
                'invalid A "+3" (expected an integer from -99999999999999999999 to '
                "99999999999999999999)"
            ),
        ),
        (
            ["٣", "13"],
            (
                'invalid A "?" (expected an integer from -99999999999999999999 to '
                "99999999999999999999)"
            ),
        ),
        (
            ["100000000000000000000", "13"],
            (
                'invalid A "100000000000000000000" (expected an integer from '
                "-99999999999999999999 to 99999999999999999999)"
            ),
        ),
        (
            ["1", "1"],
            'invalid P "1" (expected an integer from 2 to 99999999999999999999)',
        ),
        (
            ["1", "100000000000000000000"],
            (
                'invalid P "100000000000000000000" (expected an integer from 2 to '
                "99999999999999999999)"
            ),
        ),
        (
            ["not-a-number", "91"],
            (
                'invalid A "not-a-number" (expected an integer from -99999999999999999999 '
                "to 99999999999999999999)"
            ),
        ),
        (["2", "91"], "modulus 91 is not prime"),
        (["1", "99999999999999999999"], "modulus 99999999999999999999 is not prime"),
    ],
)
def test_sqrt_validation_preserves_exact_precedence_and_messages(
    argv: list[str], expected_message: str
) -> None:
    assert_failure(argv, expected_message)
