import pytest

import intsmith.commands.funcs as funcs_command
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


def assert_success(argv: list[str], expected_output: str) -> None:
    io = FakeIo()

    assert funcs_command.run(argv, io) == 0
    assert io.out_calls == [expected_output]
    assert io.err_calls == []
    assert io.read_calls == 0


def assert_failure(argv: list[str], expected_message: str) -> None:
    io = FakeIo()

    with pytest.raises(Failure) as exc_info:
        funcs_command.run(argv, io)

    assert exc_info.value.message == expected_message
    assert io.out_calls == []
    assert io.err_calls == []
    assert io.read_calls == 0


@pytest.mark.parametrize(
    ("argv", "expected_output"),
    [
        (
            ["1"],
            (
                "n         1\nfactors   1\nomega     0\nbigomega  0\ntau       1\n"
                "sigma     1\nphi       1\nmu        1\nlambda    1\nradical   1\n"
                "class     deficient\n"
            ),
        ),
        (
            ["360"],
            (
                "n         360\nfactors   2^3 * 3^2 * 5\nomega     3\nbigomega  6\n"
                "tau       24\nsigma     1170\nphi       96\nmu        0\n"
                "lambda    12\nradical   30\nclass     abundant\n"
            ),
        ),
        (
            ["--divisors", "28"],
            (
                "n         28\nfactors   2^2 * 7\nomega     2\nbigomega  3\ntau       6\n"
                "sigma     56\nphi       12\nmu        0\nlambda    6\nradical   14\n"
                "class     perfect\ndivisors  1 2 4 7 14 28\n"
            ),
        ),
        (
            ["--divisors", "1"],
            (
                "n         1\nfactors   1\nomega     0\nbigomega  0\ntau       1\n"
                "sigma     1\nphi       1\nmu        1\nlambda    1\nradical   1\n"
                "class     deficient\ndivisors  1\n"
            ),
        ),
        (
            ["6"],
            (
                "n         6\nfactors   2 * 3\nomega     2\nbigomega  2\ntau       4\n"
                "sigma     12\nphi       2\nmu        1\nlambda    2\nradical   6\n"
                "class     perfect\n"
            ),
        ),
        (
            ["12"],
            (
                "n         12\nfactors   2^2 * 3\nomega     2\nbigomega  3\ntau       6\n"
                "sigma     28\nphi       4\nmu        0\nlambda    2\nradical   6\n"
                "class     abundant\n"
            ),
        ),
        (
            ["--divisors", "--divisors", "28"],
            (
                "n         28\nfactors   2^2 * 7\nomega     2\nbigomega  3\ntau       6\n"
                "sigma     56\nphi       12\nmu        0\nlambda    6\nradical   14\n"
                "class     perfect\ndivisors  1 2 4 7 14 28\n"
            ),
        ),
        (
            ["19683000000000"],
            (
                "n         19683000000000\nfactors   2^9 * 3^9 * 5^9\nomega     3\n"
                "bigomega  27\ntau       1000\nsigma     73737912371112\n"
                "phi       5248800000000\nmu        0\nlambda    328050000000\n"
                "radical   30\nclass     abundant\n"
            ),
        ),
        (
            ["963761198400"],
            (
                "n         963761198400\nfactors   2^6 * 3^4 * 5^2 * 7 * 11 * 13 * 17 * 19 * 23\n"
                "omega     9\nbigomega  18\ntau       6720\nsigma     5531765944320\n"
                "phi       157659955200\nmu        0\nlambda    23760\n"
                "radical   223092870\nclass     abundant\n"
            ),
        ),
        (
            ["99999999999999999999"],
            (
                "n         99999999999999999999\n"
                "factors   3^2 * 11 * 41 * 101 * 271 * 3541 * 9091 * 27961\n"
                "omega     8\nbigomega  9\ntau       384\n"
                "sigma     163688881007046979584\nphi       58301444908800000000\n"
                "mu        0\nlambda    7497613800\n"
                "radical   33333333333333333333\nclass     deficient\n"
            ),
        ),
    ],
)
def test_funcs_prints_complete_results_in_order(argv: list[str], expected_output: str) -> None:
    assert_success(argv, expected_output)


def test_divisors_are_not_called_when_the_flag_is_absent(monkeypatch: pytest.MonkeyPatch) -> None:
    divisor_calls: list[list[tuple[int, int]]] = []

    def unexpected_divisors(fs: list[tuple[int, int]]) -> list[int]:
        divisor_calls.append(fs)
        return [1]

    monkeypatch.setattr(funcs_command, "divisors", unexpected_divisors)

    assert_success(
        ["28"],
        "n         28\nfactors   2^2 * 7\nomega     2\nbigomega  3\ntau       6\n"
        "sigma     56\nphi       12\nmu        0\nlambda    6\nradical   14\n"
        "class     perfect\n",
    )
    assert divisor_calls == []


def test_tau_at_1000_is_allowed_and_divisors_are_materialized(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    divisor_calls: list[list[tuple[int, int]]] = []

    def record_divisors(fs: list[tuple[int, int]]) -> list[int]:
        divisor_calls.append(fs)
        return [1, 2]

    monkeypatch.setattr(funcs_command, "divisors", record_divisors)

    assert_success(
        ["--divisors", "19683000000000"],
        "n         19683000000000\nfactors   2^9 * 3^9 * 5^9\nomega     3\n"
        "bigomega  27\ntau       1000\nsigma     73737912371112\n"
        "phi       5248800000000\nmu        0\nlambda    328050000000\n"
        "radical   30\nclass     abundant\ndivisors  1 2\n",
    )
    assert divisor_calls == [[(2, 9), (3, 9), (5, 9)]]


def test_divisors_are_not_called_when_tau_exceeds_1000(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    divisor_calls: list[list[tuple[int, int]]] = []

    def unexpected_divisors(fs: list[tuple[int, int]]) -> list[int]:
        divisor_calls.append(fs)
        return []

    monkeypatch.setattr(funcs_command, "divisors", unexpected_divisors)

    assert_failure(
        ["--divisors", "963761198400"],
        "too many divisors to list (6720, at most 1000)",
    )
    assert divisor_calls == []


@pytest.mark.parametrize(
    ("argv", "expected_message"),
    [
        ([], "missing N"),
        (["0", "1"], "too many arguments"),
        (["--help"], 'unknown option "--help"'),
        (["--divisors=1"], "--divisors takes no value"),
        (["--divisors=1", "0", "1"], "--divisors takes no value"),
        (["0"], 'invalid N "0" (expected an integer from 1 to 99999999999999999999)'),
        (["-1"], 'invalid N "-1" (expected an integer from 1 to 99999999999999999999)'),
        (["-0"], 'invalid N "-0" (expected an integer from 1 to 99999999999999999999)'),
        (["+3"], 'invalid N "+3" (expected an integer from 1 to 99999999999999999999)'),
        (["007"], 'invalid N "007" (expected an integer from 1 to 99999999999999999999)'),
        (["1.5"], 'invalid N "1.5" (expected an integer from 1 to 99999999999999999999)'),
        (["1e3"], 'invalid N "1e3" (expected an integer from 1 to 99999999999999999999)'),
        (["٣"], 'invalid N "?" (expected an integer from 1 to 99999999999999999999)'),
        (
            ["100000000000000000000"],
            'invalid N "100000000000000000000" (expected an integer from 1 to 99999999999999999999)',
        ),
        (
            [""],
            'invalid N "" (expected an integer from 1 to 99999999999999999999)',
        ),
    ],
)
def test_funcs_reports_exact_validation_failures(argv: list[str], expected_message: str) -> None:
    assert_failure(argv, expected_message)


def test_option_and_arity_errors_precede_integer_validation() -> None:
    assert_failure(
        ["--divisors=1", "0", "1"],
        "--divisors takes no value",
    )
    assert_failure(["0", "1"], "too many arguments")
    assert_failure(["0"], 'invalid N "0" (expected an integer from 1 to 99999999999999999999)')
