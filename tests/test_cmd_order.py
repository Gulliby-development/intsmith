import pytest

from intsmith.commands.order import run
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
            ["3", "7"],
            "residue   3\nphi       6\norder     6\nsmallest  3\n",
            0,
        ),
        (
            ["6", "9"],
            "residue   6\nphi       6\nstatus    not a unit (gcd 3)\n",
            1,
        ),
        (
            ["3", "100"],
            "residue   3\nphi       40\norder     20\nsmallest  none\n",
            0,
        ),
        (
            ["-3", "7"],
            "residue   4\nphi       6\norder     3\nsmallest  3\n",
            0,
        ),
        (
            ["0", "7"],
            "residue   0\nphi       6\nstatus    not a unit (gcd 7)\n",
            1,
        ),
        (
            ["1", "2"],
            "residue   1\nphi       1\norder     1\nsmallest  1\n",
            0,
        ),
        (
            ["99999999999999999999", "2"],
            "residue   1\nphi       1\norder     1\nsmallest  1\n",
            0,
        ),
        (
            ["-99999999999999999999", "2"],
            "residue   1\nphi       1\norder     1\nsmallest  1\n",
            0,
        ),
        (
            ["3", "8"],
            "residue   3\nphi       4\norder     2\nsmallest  none\n",
            0,
        ),
        (
            ["7", "99999999999999999989"],
            (
                "residue   7\nphi       99999999999999999988\n"
                "order     99999999999999999988\nsmallest  2\n"
            ),
            0,
        ),
        (
            ["0", "99999999999999999999"],
            (
                "residue   0\nphi       58301444908800000000\n"
                "status    not a unit (gcd 99999999999999999999)\n"
            ),
            1,
        ),
    ],
)
def test_order_answers_are_exact_and_truncate_negative_results(
    argv: list[str], expected: str, expected_status: int
) -> None:
    assert_answer(argv, expected, expected_status)


@pytest.mark.parametrize(
    ("argv", "expected_message"),
    [
        ([], "missing A"),
        (["3"], "missing N"),
        (["not-an-integer"], "missing N"),
        (["not-an-integer", "7", "extra"], "too many arguments"),
        (["1", "2", "3", "--help"], 'unknown option "--help"'),
        (["--", "1", "2"], 'unknown option "--"'),
        (["1", "2", "3"], "too many arguments"),
        (
            ["01", "7"],
            (
                'invalid A "01" (expected an integer from -99999999999999999999 to '
                "99999999999999999999)"
            ),
        ),
        (
            ["", "7"],
            (
                'invalid A "" (expected an integer from -99999999999999999999 to '
                "99999999999999999999)"
            ),
        ),
        (
            ["1", "01"],
            'invalid N "01" (expected an integer from 2 to 99999999999999999999)',
        ),
        (
            ["-0", "7"],
            (
                'invalid A "-0" (expected an integer from -99999999999999999999 to '
                "99999999999999999999)"
            ),
        ),
        (
            ["+3", "7"],
            (
                'invalid A "+3" (expected an integer from -99999999999999999999 to '
                "99999999999999999999)"
            ),
        ),
        (
            ["007", "7"],
            (
                'invalid A "007" (expected an integer from -99999999999999999999 to '
                "99999999999999999999)"
            ),
        ),
        (
            ["1.5", "7"],
            (
                'invalid A "1.5" (expected an integer from -99999999999999999999 to '
                "99999999999999999999)"
            ),
        ),
        (
            ["1e3", "7"],
            (
                'invalid A "1e3" (expected an integer from -99999999999999999999 to '
                "99999999999999999999)"
            ),
        ),
        (
            ["٣", "7"],
            (
                'invalid A "?" (expected an integer from -99999999999999999999 to '
                "99999999999999999999)"
            ),
        ),
        (
            ["100000000000000000000", "7"],
            (
                'invalid A "100000000000000000000" (expected an integer from '
                "-99999999999999999999 to 99999999999999999999)"
            ),
        ),
        (
            ["-100000000000000000000", "7"],
            (
                'invalid A "-100000000000000000000" (expected an integer from '
                "-99999999999999999999 to 99999999999999999999)"
            ),
        ),
        (
            ["1", "1"],
            'invalid N "1" (expected an integer from 2 to 99999999999999999999)',
        ),
        (
            ["1", "100000000000000000000"],
            (
                'invalid N "100000000000000000000" (expected an integer from 2 to '
                "99999999999999999999)"
            ),
        ),
    ],
)
def test_order_validation_preserves_exact_precedence_and_messages(
    argv: list[str], expected_message: str
) -> None:
    assert_failure(argv, expected_message)


@pytest.mark.parametrize(
    ("argv", "expected", "expected_status"),
    [
        (
            ["--roots", "3", "7"],
            "residue   3\nphi       6\norder     6\nsmallest  3\nroots     2\n",
            0,
        ),
        (
            ["3", "--roots", "8"],
            "residue   3\nphi       4\norder     2\nsmallest  none\nroots     0\n",
            0,
        ),
        (
            ["--roots", "4", "8"],
            "residue   4\nphi       4\nstatus    not a unit (gcd 4)\nroots     0\n",
            1,
        ),
        (
            ["--roots", "2", "9"],
            "residue   2\nphi       6\norder     6\nsmallest  2\nroots     2\n",
            0,
        ),
    ],
)
def test_order_roots_answers_are_exact(
    argv: list[str], expected: str, expected_status: int
) -> None:
    assert_answer(argv, expected, expected_status)


def test_order_roots_flag_rejects_value() -> None:
    assert_failure(["--roots=1", "3", "7"], "--roots takes no value")
