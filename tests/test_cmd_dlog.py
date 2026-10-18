import pytest

from intsmith.commands.dlog import run
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
            ["3", "13", "17"],
            "base      3\ntarget    13\norder     16\nx         4\n",
            0,
        ),
        (
            ["2", "3", "7"],
            "base      2\ntarget    3\norder     3\nstatus    no solution\n",
            1,
        ),
        (
            ["2", "1", "8"],
            "base      2\ntarget    1\nstatus    base is not a unit (gcd 2)\n",
            1,
        ),
        (
            ["5", "123456789", "1000000007"],
            ("base      5\ntarget    123456789\norder     1000000006\nx         981640996\n"),
            0,
        ),
        (
            ["99999999999999999999", "99999999999999999", "10"],
            "base      9\ntarget    9\norder     2\nx         1\n",
            0,
        ),
        (
            ["99999999999999999993", "99999999999999999997", "10"],
            "base      3\ntarget    7\norder     4\nx         3\n",
            0,
        ),
        (
            ["-3", "-4", "17"],
            "base      14\ntarget    13\norder     16\nx         4\n",
            0,
        ),
        (
            ["1", "1", "2"],
            "base      1\ntarget    1\norder     1\nx         0\n",
            0,
        ),
        (
            ["3", "1", "17"],
            "base      3\ntarget    1\norder     16\nx         0\n",
            0,
        ),
        (
            ["3", "2", "8"],
            "base      3\ntarget    2\norder     2\nstatus    no solution\n",
            1,
        ),
        (
            ["10", "1", "10"],
            "base      0\ntarget    1\nstatus    base is not a unit (gcd 10)\n",
            1,
        ),
        (
            ["-99999999999999999999", "99999999999999999999", "2"],
            "base      1\ntarget    1\norder     1\nx         0\n",
            0,
        ),
        (
            ["1", "1", "10000000000"],
            "base      1\ntarget    1\norder     1\nx         0\n",
            0,
        ),
        (
            ["3", "6666666667", "10000000000"],
            ("base      3\ntarget    6666666667\norder     500000000\nx         499999999\n"),
            0,
        ),
    ],
)
def test_dlog_answers_are_exact_and_negative_answers_stop_at_status(
    argv: list[str], expected: str, expected_status: int
) -> None:
    assert_answer(argv, expected, expected_status)


@pytest.mark.parametrize(
    ("argv", "expected_message"),
    [
        ([], "missing G"),
        (["3"], "missing H"),
        (["3", "13"], "missing M"),
        (["bad"], "missing H"),
        (["--help"], 'unknown option "--help"'),
        (["--"], 'unknown option "--"'),
        (["3", "--help"], 'unknown option "--help"'),
        (["bad", "2", "7", "extra"], "too many arguments"),
        (
            ["bad", "bad", "bad"],
            (
                'invalid G "bad" (expected an integer from '
                "-99999999999999999999 to 99999999999999999999)"
            ),
        ),
        (
            ["3", "bad", "bad"],
            (
                'invalid H "bad" (expected an integer from '
                "-99999999999999999999 to 99999999999999999999)"
            ),
        ),
        (
            ["3", "13", "bad"],
            'invalid M "bad" (expected an integer from 2 to 10000000000)',
        ),
        (
            ["1", "1", "1"],
            'invalid M "1" (expected an integer from 2 to 10000000000)',
        ),
        (
            ["1", "1", "10000000001"],
            'invalid M "10000000001" (expected an integer from 2 to 10000000000)',
        ),
        (
            ["100000000000000000000", "1", "2"],
            (
                'invalid G "100000000000000000000" (expected an integer from '
                "-99999999999999999999 to 99999999999999999999)"
            ),
        ),
        (
            ["-100000000000000000000", "1", "2"],
            (
                'invalid G "-100000000000000000000" (expected an integer from '
                "-99999999999999999999 to 99999999999999999999)"
            ),
        ),
        (
            ["1", "100000000000000000000", "2"],
            (
                'invalid H "100000000000000000000" (expected an integer from '
                "-99999999999999999999 to 99999999999999999999)"
            ),
        ),
    ],
)
def test_dlog_validation_precedence_and_bounds(argv: list[str], expected_message: str) -> None:
    assert_failure(argv, expected_message)


@pytest.mark.parametrize(
    ("text", "expected_message"),
    [
        (
            "-0",
            (
                'invalid G "-0" (expected an integer from -99999999999999999999 to '
                "99999999999999999999)"
            ),
        ),
        (
            "+3",
            (
                'invalid G "+3" (expected an integer from -99999999999999999999 to '
                "99999999999999999999)"
            ),
        ),
        (
            "007",
            (
                'invalid G "007" (expected an integer from -99999999999999999999 to '
                "99999999999999999999)"
            ),
        ),
        (
            "1.5",
            (
                'invalid G "1.5" (expected an integer from -99999999999999999999 to '
                "99999999999999999999)"
            ),
        ),
        (
            "1e3",
            (
                'invalid G "1e3" (expected an integer from -99999999999999999999 to '
                "99999999999999999999)"
            ),
        ),
        (
            "",
            'invalid G "" (expected an integer from -99999999999999999999 to 99999999999999999999)',
        ),
        (
            "٣",
            (
                'invalid G "?" (expected an integer from -99999999999999999999 to '
                "99999999999999999999)"
            ),
        ),
    ],
)
def test_dlog_rejects_noncanonical_integer_text(text: str, expected_message: str) -> None:
    assert_failure([text, "1", "2"], expected_message)
