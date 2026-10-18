import pytest

from intsmith.cli import USAGE, main


class FakeIo:
    def __init__(self, data: bytes = b"", error: OSError | None = None) -> None:
        self.data = data
        self.error = error
        self.read_calls = 0
        self.out_calls: list[str] = []
        self.err_calls: list[str] = []

    def read_stdin(self) -> bytes:
        self.read_calls += 1
        if self.error is not None:
            raise self.error
        return self.data

    def out(self, text: str) -> None:
        self.out_calls.append(text)

    def err(self, text: str) -> None:
        self.err_calls.append(text)


def assert_main_result(
    argv: list[str],
    expected_stdout: str,
    expected_stderr: str,
    expected_status: int,
    data: bytes = b"",
    error: OSError | None = None,
    expected_reads: int = 0,
) -> None:
    io = FakeIo(data, error)

    assert main(argv, io) == expected_status
    assert io.out_calls == ([expected_stdout] if expected_stdout else [])
    assert io.err_calls == ([expected_stderr] if expected_stderr else [])
    assert io.read_calls == expected_reads


EXPECTED_USAGE = """usage: intsmith gcd A B
       intsmith crt R:M...
       intsmith prime test|next|prev N
       intsmith prime list LO HI
       intsmith factor N...
       intsmith funcs [--divisors] N
       intsmith order A N
       intsmith sqrt A P
       intsmith dlog G H M
       intsmith cfrac frac P Q
       intsmith cfrac sqrt [--terms T] D
       intsmith cfrac pell D"""


def test_usage_and_standalone_help_are_exact() -> None:
    assert USAGE == EXPECTED_USAGE
    assert_main_result(["--help"], EXPECTED_USAGE + "\n", "", 0)


@pytest.mark.parametrize(
    (
        "argv",
        "expected_stdout",
        "expected_stderr",
        "expected_status",
        "data",
        "error",
        "expected_reads",
    ),
    [
        (
            [],
            "",
            "intsmith: missing command (gcd, crt, prime, factor, funcs, order, sqrt, dlog or cfrac)\n",
            2,
            b"",
            None,
            0,
        ),
        (
            ["--help", "gcd"],
            "",
            'intsmith: unknown command "--help"\n',
            2,
            b"",
            None,
            0,
        ),
        (
            ["GCD"],
            "",
            'intsmith: unknown command "GCD"\n',
            2,
            b"",
            None,
            0,
        ),
        (
            ["é\n"],
            "",
            'intsmith: unknown command "??"\n',
            2,
            b"",
            None,
            0,
        ),
        (
            ["gcd", "--help"],
            "",
            'intsmith: unknown option "--help"\n',
            2,
            b"",
            None,
            0,
        ),
        (
            ["gcd", "17", "3120"],
            "gcd       1\nlcm       53040\nbezout    x=2753 y=-15\ninverse   2753\n",
            "",
            0,
            b"",
            None,
            0,
        ),
        (
            ["crt", "2:3", "3:5", "2:7"],
            "crt       3 congruences\nx         23 (mod 105)\n",
            "",
            0,
            b"",
            None,
            0,
        ),
        (
            ["crt", "1:4", "2:6"],
            "crt       2 congruences\nstatus    no solution\n",
            "",
            1,
            b"",
            None,
            0,
        ),
        (
            ["prime", "test", "97"],
            "97 is prime\n",
            "",
            0,
            b"",
            None,
            0,
        ),
        (
            ["prime", "test", "91"],
            "91 is not prime\n",
            "",
            1,
            b"",
            None,
            0,
        ),
        (
            ["factor", "360", "97", "1"],
            "360 = 2^3 * 3^2 * 5\n97 = 97\n1 = 1\n",
            "",
            0,
            b"",
            None,
            0,
        ),
        (
            ["funcs", "--divisors", "28"],
            "n         28\nfactors   2^2 * 7\nomega     2\nbigomega  3\ntau       6\nsigma     56\nphi       12\nmu        0\nlambda    6\nradical   14\nclass     perfect\ndivisors  1 2 4 7 14 28\n",
            "",
            0,
            b"",
            None,
            0,
        ),
        (
            ["order", "3", "7"],
            "residue   3\nphi       6\norder     6\nsmallest  3\n",
            "",
            0,
            b"",
            None,
            0,
        ),
        (
            ["order", "6", "9"],
            "residue   6\nphi       6\nstatus    not a unit (gcd 3)\n",
            "",
            1,
            b"",
            None,
            0,
        ),
        (
            ["sqrt", "10", "13"],
            "residue   10\nsymbol    1\nroots     6 7\n",
            "",
            0,
            b"",
            None,
            0,
        ),
        (
            ["sqrt", "5", "13"],
            "residue   5\nsymbol    -1\nstatus    no square root\n",
            "",
            1,
            b"",
            None,
            0,
        ),
        (
            ["dlog", "3", "13", "17"],
            "base      3\ntarget    13\norder     16\nx         4\n",
            "",
            0,
            b"",
            None,
            0,
        ),
        (
            ["dlog", "2", "3", "7"],
            "base      2\ntarget    3\norder     3\nstatus    no solution\n",
            "",
            1,
            b"",
            None,
            0,
        ),
        (
            ["cfrac", "frac", "7", "-3"],
            "fraction  -7/3\nterms     -3 1 2\nconv      -3/1 -2/1 -7/3\n",
            "",
            0,
            b"",
            None,
            0,
        ),
        (
            ["cfrac", "pell", "16"],
            "equation  x^2 - 16*y^2 = 1\nstatus    no solution (D is a perfect square)\n",
            "",
            1,
            b"",
            None,
            0,
        ),
        (
            ["prime", "bogus", "--bad"],
            "",
            'intsmith: unknown mode "bogus" (expected test, next, prev or list)\n',
            2,
            b"",
            None,
            0,
        ),
        (
            ["cfrac"],
            "",
            "intsmith: missing mode (frac, sqrt or pell)\n",
            2,
            b"",
            None,
            0,
        ),
        (
            ["gcd", "01", "2", "--bad"],
            "",
            'intsmith: unknown option "--bad"\n',
            2,
            b"",
            None,
            0,
        ),
        (
            ["gcd", "01"],
            "",
            "intsmith: missing B\n",
            2,
            b"",
            None,
            0,
        ),
        (
            ["gcd", "01", "2", "3"],
            "",
            "intsmith: too many arguments\n",
            2,
            b"",
            None,
            0,
        ),
        (
            ["gcd", "01", "bad"],
            "",
            'intsmith: invalid A "01" (expected an integer from -99999999999999999999 to 99999999999999999999)\n',
            2,
            b"",
            None,
            0,
        ),
        (
            ["cfrac", "sqrt", "--terms", "0", "--bad"],
            "",
            'intsmith: unknown option "--bad"\n',
            2,
            b"",
            None,
            0,
        ),
        (
            ["cfrac", "sqrt", "--terms", "0"],
            "",
            'intsmith: invalid --terms "0" (expected an integer from 1 to 200)\n',
            2,
            b"",
            None,
            0,
        ),
        (
            ["cfrac", "sqrt", "--terms"],
            "",
            "intsmith: --terms needs a value\n",
            2,
            b"",
            None,
            0,
        ),
        (
            ["funcs", "--divisors=1", "28"],
            "",
            "intsmith: --divisors takes no value\n",
            2,
            b"",
            None,
            0,
        ),
        (
            ["crt", "1:0", "bad"],
            "",
            'intsmith: invalid M "0" (expected an integer from 1 to 99999999999999999999)\n',
            2,
            b"",
            None,
            0,
        ),
        (
            ["sqrt", "2", "91"],
            "",
            "intsmith: modulus 91 is not prime\n",
            2,
            b"",
            None,
            0,
        ),
        (
            ["cfrac", "frac", "1", "0"],
            "",
            "intsmith: Q must not be 0\n",
            2,
            b"",
            None,
            0,
        ),
        (
            ["prime", "list", "0", "10001"],
            "",
            "intsmith: HI - LO must be at most 10000\n",
            2,
            b"",
            None,
            0,
        ),
        (
            ["cfrac", "sqrt", "--terms", "0", "--terms", "1", "2"],
            "value     sqrt(2)\nterms     1\nperiod    1\n",
            "",
            0,
            b"",
            None,
            0,
        ),
        (
            ["factor", "-"],
            "12 = 2^2 * 3\n15 = 3 * 5\n7 = 7\n",
            "",
            0,
            b"\xef\xbb\xbf12\r\n 15\t7\n",
            None,
            1,
        ),
        (
            ["factor", "-"],
            "",
            "intsmith: <stdin>: input is not valid UTF-8\n",
            2,
            b"12\xff\n",
            None,
            1,
        ),
        (
            ["factor", "-"],
            "",
            "intsmith: <stdin>: no input\n",
            2,
            b" \r\n\t",
            None,
            1,
        ),
        (
            ["factor", "-"],
            "",
            "intsmith: <stdin>: cannot read the input\n",
            2,
            b"",
            OSError("read failed"),
            1,
        ),
        (
            ["factor", "12", "-"],
            "",
            'intsmith: invalid N "-" (expected an integer from 1 to 99999999999999999999)\n',
            2,
            b"",
            None,
            0,
        ),
    ],
)
def test_main_literal_cli_cases(
    argv: list[str],
    expected_stdout: str,
    expected_stderr: str,
    expected_status: int,
    data: bytes,
    error: OSError | None,
    expected_reads: int,
) -> None:
    assert_main_result(
        argv,
        expected_stdout,
        expected_stderr,
        expected_status,
        data,
        error,
        expected_reads,
    )
