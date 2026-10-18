import pytest

from intsmith.commands.gcd import run
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


def assert_no_output(io: FakeIo) -> None:
    assert io.out_calls == []
    assert io.err_calls == []
    assert io.read_calls == 0


def assert_failure(argv: list[str], expected_message: str) -> None:
    io = FakeIo()
    with pytest.raises(Failure) as exc_info:
        run(argv, io)

    assert exc_info.value.message == expected_message
    assert_no_output(io)


@pytest.mark.parametrize(
    ("argv", "expected_output"),
    [
        (
            ["240", "46"],
            "gcd       2\nlcm       5520\nbezout    x=14 y=-73\ninverse   none\n",
        ),
        (
            ["17", "3120"],
            "gcd       1\nlcm       53040\nbezout    x=2753 y=-15\ninverse   2753\n",
        ),
        (
            ["-12", "0"],
            "gcd       12\nlcm       0\nbezout    x=-1 y=0\ninverse   none\n",
        ),
        (
            ["0", "0"],
            "gcd       0\nlcm       0\nbezout    x=0 y=0\ninverse   none\n",
        ),
        (
            ["0", "-7"],
            "gcd       7\nlcm       0\nbezout    x=0 y=-1\ninverse   none\n",
        ),
        (
            ["7", "-3"],
            "gcd       1\nlcm       21\nbezout    x=1 y=2\ninverse   1\n",
        ),
        (
            ["-7", "3"],
            "gcd       1\nlcm       21\nbezout    x=2 y=5\ninverse   2\n",
        ),
        (
            ["99999999999999999999", "0"],
            "gcd       99999999999999999999\nlcm       0\nbezout    x=1 y=0\ninverse   none\n",
        ),
        (
            ["-99999999999999999999", "99999999999999999999"],
            (
                "gcd       99999999999999999999\n"
                "lcm       99999999999999999999\n"
                "bezout    x=0 y=1\n"
                "inverse   none\n"
            ),
        ),
        (
            ["99999999999999999999", "99999999999999999999"],
            (
                "gcd       99999999999999999999\n"
                "lcm       99999999999999999999\n"
                "bezout    x=0 y=1\n"
                "inverse   none\n"
            ),
        ),
    ],
)
def test_gcd_prints_the_complete_exact_result_once(argv: list[str], expected_output: str) -> None:
    io = FakeIo()

    assert run(argv, io) == 0
    assert io.out_calls == [expected_output]
    assert io.err_calls == []
    assert io.read_calls == 0


def test_gcd_missing_first_argument_precedes_other_validation() -> None:
    assert_failure([], "missing A")


def test_gcd_reports_missing_second_argument_before_parsing_first() -> None:
    assert_failure(["01"], "missing B")


def test_gcd_reports_too_many_arguments_before_parsing_values() -> None:
    assert_failure(["01", "2", "bad"], "too many arguments")


def test_gcd_unknown_option_precedes_arity_validation() -> None:
    assert_failure(["--help"], 'unknown option "--help"')


def test_gcd_validates_first_number_before_second_number() -> None:
    assert_failure(
        ["01", "not-a-number"],
        'invalid A "01" (expected an integer from -99999999999999999999 to 99999999999999999999)',
    )


@pytest.mark.parametrize(
    ("argv", "expected_message"),
    [
        (
            ["+3", "2"],
            'invalid A "+3" (expected an integer from -99999999999999999999 to 99999999999999999999)',
        ),
        (
            ["-0", "2"],
            'invalid A "-0" (expected an integer from -99999999999999999999 to 99999999999999999999)',
        ),
        (
            ["007", "2"],
            'invalid A "007" (expected an integer from -99999999999999999999 to 99999999999999999999)',
        ),
        (
            ["3.5", "2"],
            'invalid A "3.5" (expected an integer from -99999999999999999999 to 99999999999999999999)',
        ),
        (
            ["1e3", "2"],
            'invalid A "1e3" (expected an integer from -99999999999999999999 to 99999999999999999999)',
        ),
        (
            ["٣", "2"],
            'invalid A "?" (expected an integer from -99999999999999999999 to 99999999999999999999)',
        ),
        (
            ["", "2"],
            'invalid A "" (expected an integer from -99999999999999999999 to 99999999999999999999)',
        ),
    ],
)
def test_gcd_rejects_noncanonical_integer_grammar(argv: list[str], expected_message: str) -> None:
    assert_failure(argv, expected_message)


def test_gcd_rejects_values_outside_the_signed_big_boundary() -> None:
    assert_failure(
        ["100000000000000000000", "2"],
        'invalid A "100000000000000000000" (expected an integer from -99999999999999999999 to 99999999999999999999)',
    )
