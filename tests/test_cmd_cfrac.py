import pytest

from intsmith.commands import cfrac as cfrac_command
from intsmith.commands.cfrac import run
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


def assert_answer(argv: list[str], expected: str, expected_status: int = 0) -> None:
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


PELL_9949_OUTPUT = (
    "equation  x^2 - 9949*y^2 = 1\n"
    "x         "
    "23551"
    "019"
    "614"
    "858"
    "223"
    "475"
    "933"
    "893"
    "515"
    "741"
    "198"
    "183"
    "163"
    "217"
    "312"
    "913"
    "587"
    "552"
    "899"
    "320"
    "396"
    "564"
    "478"
    "041"
    "197"
    "360"
    "918"
    "469"
    "501"
    "097"
    "146"
    "448"
    "985"
    "821"
    "854"
    "465"
    "768"
    "234"
    "479"
    "384"
    "482"
    "435"
    "117"
    "587"
    "576"
    "296"
    "319"
    "428"
    "592"
    "757"
    "548"
    "743"
    "265"
    "811"
    "454"
    "938"
    "493"
    "105"
    "633"
    "433"
    "315"
    "887"
    "574"
    "461"
    "850"
    "060"
    "798"
    "834"
    "186"
    "249"
    "\ny         "
    "236"
    "113"
    "054"
    "062"
    "810"
    "988"
    "826"
    "514"
    "929"
    "828"
    "649"
    "213"
    "339"
    "688"
    "520"
    "849"
    "720"
    "684"
    "015"
    "415"
    "366"
    "388"
    "626"
    "019"
    "230"
    "322"
    "623"
    "673"
    "232"
    "286"
    "474"
    "879"
    "711"
    "003"
    "505"
    "448"
    "178"
    "417"
    "385"
    "617"
    "250"
    "641"
    "629"
    "212"
    "134"
    "427"
    "833"
    "135"
    "509"
    "077"
    "013"
    "929"
    "303"
    "770"
    "208"
    "680"
    "820"
    "795"
    "381"
    "507"
    "114"
    "806"
    "491"
    "325"
    "360"
    "400"
    "076"
    "633"
    "910"
    "900"
    "\nminus1    "
    "3"
    "431"
    "546"
    "270"
    "623"
    "363"
    "128"
    "596"
    "014"
    "118"
    "116"
    "144"
    "221"
    "075"
    "051"
    "039"
    "537"
    "067"
    "641"
    "511"
    "872"
    "618"
    "579"
    "455"
    "226"
    "741"
    "550"
    "509"
    "978"
    "502"
    "410"
    "879"
    "762"
    "136"
    "834"
    "818"
    " "
    "34"
    "403"
    "303"
    "269"
    "449"
    "939"
    "153"
    "283"
    "126"
    "077"
    "708"
    "664"
    "857"
    "428"
    "452"
    "182"
    "230"
    "098"
    "434"
    "142"
    "453"
    "222"
    "430"
    "571"
    "308"
    "633"
    "791"
    "476"
    "247"
    "185"
    "645"
    "245"
    "170"
    "282"
    "525"
    "\n"
)


SQRT_2_TERMS_200_OUTPUT = (
    "value     sqrt(2)\n"
    "terms     "
    "1 2 2 2 2 2 2 2 2 2 "
    "2 2 2 2 2 2 2 2 2 2 "
    "2 2 2 2 2 2 2 2 2 2 "
    "2 2 2 2 2 2 2 2 2 2 "
    "2 2 2 2 2 2 2 2 2 2 "
    "2 2 2 2 2 2 2 2 2 2 "
    "2 2 2 2 2 2 2 2 2 2 "
    "2 2 2 2 2 2 2 2 2 2 "
    "2 2 2 2 2 2 2 2 2 2 "
    "2 2 2 2 2 2 2 2 2 2 "
    "2 2 2 2 2 2 2 2 2 2 "
    "2 2 2 2 2 2 2 2 2 2 "
    "2 2 2 2 2 2 2 2 2 2 "
    "2 2 2 2 2 2 2 2 2 2 "
    "2 2 2 2 2 2 2 2 2 2 "
    "2 2 2 2 2 2 2 2 2 2 "
    "2 2 2 2 2 2 2 2 2 2 "
    "2 2 2 2 2 2 2 2 2 2 "
    "2 2 2 2 2 2 2 2 2 2 "
    "2 2 2 2 2 2 2 2 2 2"
    "\nperiod    1\n"
)


@pytest.mark.parametrize(
    ("argv", "expected"),
    [
        (
            ["frac", "649", "200"],
            "fraction  649/200\nterms     3 4 12 4\nconv      3/1 13/4 159/49 649/200\n",
        ),
        (
            ["frac", "7", "-3"],
            "fraction  -7/3\nterms     -3 1 2\nconv      -3/1 -2/1 -7/3\n",
        ),
        (
            ["frac", "-7", "3"],
            "fraction  -7/3\nterms     -3 1 2\nconv      -3/1 -2/1 -7/3\n",
        ),
        (
            ["frac", "0", "-7"],
            "fraction  0/1\nterms     0\nconv      0/1\n",
        ),
        (
            ["frac", "14", "21"],
            "fraction  2/3\nterms     0 1 2\nconv      0/1 1/1 2/3\n",
        ),
        (
            ["frac", "-14", "-21"],
            "fraction  2/3\nterms     0 1 2\nconv      0/1 1/1 2/3\n",
        ),
        (
            ["frac", "6", "3"],
            "fraction  2/1\nterms     2\nconv      2/1\n",
        ),
        (
            ["frac", "-6", "3"],
            "fraction  -2/1\nterms     -2\nconv      -2/1\n",
        ),
        (
            ["frac", "99999999999999999999", "99999999999999999999"],
            "fraction  1/1\nterms     1\nconv      1/1\n",
        ),
        (
            ["frac", "99999999999999999999", "-99999999999999999999"],
            "fraction  -1/1\nterms     -1\nconv      -1/1\n",
        ),
        (
            ["frac", "-99999999999999999999", "1"],
            (
                "fraction  -99999999999999999999/1\n"
                "terms     -99999999999999999999\n"
                "conv      -99999999999999999999/1\n"
            ),
        ),
        (
            ["frac", "1", "99999999999999999999"],
            (
                "fraction  1/99999999999999999999\n"
                "terms     0 99999999999999999999\n"
                "conv      0/1 1/99999999999999999999\n"
            ),
        ),
    ],
)
def test_fraction_mode_reduces_signs_and_prints_every_convergent(
    argv: list[str], expected: str
) -> None:
    assert_answer(argv, expected)


@pytest.mark.parametrize(
    ("argv", "expected"),
    [
        (
            ["sqrt", "23"],
            "value     sqrt(23)\nterms     4 1 3 1 8 1 3 1 8 1 3 1\nperiod    4\n",
        ),
        (
            ["sqrt", "--terms", "5", "2"],
            "value     sqrt(2)\nterms     1 2 2 2 2\nperiod    1\n",
        ),
        (
            ["sqrt", "--terms=5", "2"],
            "value     sqrt(2)\nterms     1 2 2 2 2\nperiod    1\n",
        ),
        (
            ["sqrt", "2", "--terms", "5"],
            "value     sqrt(2)\nterms     1 2 2 2 2\nperiod    1\n",
        ),
        (
            ["sqrt", "2", "--terms=1"],
            "value     sqrt(2)\nterms     1\nperiod    1\n",
        ),
        (
            ["sqrt", "49"],
            "value     sqrt(49)\nterms     7\nperiod    0\n",
        ),
        (
            ["sqrt", "--terms=200", "100000000"],
            "value     sqrt(100000000)\nterms     10000\nperiod    0\n",
        ),
        (
            ["sqrt", "1", "--terms=1"],
            "value     sqrt(1)\nterms     1\nperiod    0\n",
        ),
        (
            ["sqrt", "--terms=bad", "--terms=1", "2"],
            "value     sqrt(2)\nterms     1\nperiod    1\n",
        ),
        (
            ["sqrt", "--terms=12", "2", "--terms=1"],
            "value     sqrt(2)\nterms     1\nperiod    1\n",
        ),
        (["sqrt", "--terms=200", "2"], SQRT_2_TERMS_200_OUTPUT),
    ],
)
def test_sqrt_mode_options_defaults_squares_and_periods(argv: list[str], expected: str) -> None:
    assert_answer(argv, expected)


@pytest.mark.parametrize(
    ("argv", "expected", "expected_status"),
    [
        (
            ["pell", "61"],
            (
                "equation  x^2 - 61*y^2 = 1\n"
                "x         1766319049\n"
                "y         226153980\n"
                "minus1    29718 3805\n"
            ),
            0,
        ),
        (
            ["pell", "3"],
            "equation  x^2 - 3*y^2 = 1\nx         2\ny         1\nminus1    none\n",
            0,
        ),
        (
            ["pell", "16"],
            "equation  x^2 - 16*y^2 = 1\nstatus    no solution (D is a perfect square)\n",
            1,
        ),
        (
            ["pell", "1"],
            "equation  x^2 - 1*y^2 = 1\nstatus    no solution (D is a perfect square)\n",
            1,
        ),
        (
            ["pell", "10000"],
            "equation  x^2 - 10000*y^2 = 1\nstatus    no solution (D is a perfect square)\n",
            1,
        ),
        (["pell", "9949"], PELL_9949_OUTPUT, 0),
    ],
)
def test_pell_mode_prints_minimal_solutions_and_square_status(
    argv: list[str], expected: str, expected_status: int
) -> None:
    assert_answer(argv, expected, expected_status)


def test_square_modes_do_not_call_nonsquare_only_engines(monkeypatch: pytest.MonkeyPatch) -> None:
    def unexpected_call(*args: object) -> None:
        raise AssertionError(f"nonsquare-only engine called for a square: {args}")

    monkeypatch.setattr(cfrac_command, "sqrt_terms", unexpected_call)
    monkeypatch.setattr(cfrac_command, "pell", unexpected_call)

    assert_answer(["sqrt", "49"], "value     sqrt(49)\nterms     7\nperiod    0\n")
    assert_answer(
        ["pell", "16"],
        "equation  x^2 - 16*y^2 = 1\nstatus    no solution (D is a perfect square)\n",
        1,
    )


@pytest.mark.parametrize(
    ("argv", "expected_message"),
    [
        ([], "missing mode (frac, sqrt or pell)"),
        (["bad"], 'unknown mode "bad" (expected frac, sqrt or pell)'),
        (["sqrt\u2603"], 'unknown mode "sqrt?" (expected frac, sqrt or pell)'),
        (["bad", "--terms=bad"], 'unknown mode "bad" (expected frac, sqrt or pell)'),
        (["frac"], "missing P"),
        (["frac", "1"], "missing Q"),
        (["sqrt"], "missing D"),
        (["pell"], "missing D"),
        (["frac", "--terms=3"], 'unknown option "--terms=3"'),
        (["pell", "--terms", "3", "5"], 'unknown option "--terms"'),
        (["sqrt", "--help"], 'unknown option "--help"'),
        (["sqrt", "--"], 'unknown option "--"'),
        (["sqrt", "--terms"], "--terms needs a value"),
        (
            ["sqrt", "--terms=bad"],
            'invalid --terms "bad" (expected an integer from 1 to 200)',
        ),
        (
            ["sqrt", "--terms=bad", "--terms=201", "2"],
            'invalid --terms "201" (expected an integer from 1 to 200)',
        ),
        (
            ["sqrt", "--terms=5", "--terms=bad", "2"],
            'invalid --terms "bad" (expected an integer from 1 to 200)',
        ),
        (
            ["sqrt", "--terms=0", "2"],
            'invalid --terms "0" (expected an integer from 1 to 200)',
        ),
        (
            ["sqrt", "--terms=201", "2"],
            'invalid --terms "201" (expected an integer from 1 to 200)',
        ),
        (
            ["sqrt", "--terms=", "2"],
            'invalid --terms "" (expected an integer from 1 to 200)',
        ),
        (
            ["sqrt", "--terms=5=6", "2"],
            'invalid --terms "5=6" (expected an integer from 1 to 200)',
        ),
        (
            ["sqrt", "--terms=bad", "--unknown"],
            'unknown option "--unknown"',
        ),
        (
            ["frac", "bad", "0", "extra"],
            "too many arguments",
        ),
        (
            ["sqrt", "bad", "extra"],
            "too many arguments",
        ),
        (
            ["pell", "bad", "extra"],
            "too many arguments",
        ),
        (
            ["frac", "bad", "1"],
            (
                'invalid P "bad" (expected an integer from '
                "-99999999999999999999 to 99999999999999999999)"
            ),
        ),
        (
            ["frac", "1", "bad"],
            (
                'invalid Q "bad" (expected an integer from '
                "-99999999999999999999 to 99999999999999999999)"
            ),
        ),
        (
            ["frac", "-0", "1"],
            (
                'invalid P "-0" (expected an integer from '
                "-99999999999999999999 to 99999999999999999999)"
            ),
        ),
        (
            ["frac", "+3", "1"],
            (
                'invalid P "+3" (expected an integer from '
                "-99999999999999999999 to 99999999999999999999)"
            ),
        ),
        (
            ["frac", "007", "1"],
            (
                'invalid P "007" (expected an integer from '
                "-99999999999999999999 to 99999999999999999999)"
            ),
        ),
        (
            ["frac", "1.5", "1"],
            (
                'invalid P "1.5" (expected an integer from '
                "-99999999999999999999 to 99999999999999999999)"
            ),
        ),
        (
            ["frac", "٣", "1"],
            (
                'invalid P "?" (expected an integer from '
                "-99999999999999999999 to 99999999999999999999)"
            ),
        ),
        (
            ["frac", "100000000000000000000", "1"],
            (
                'invalid P "100000000000000000000" (expected an integer from '
                "-99999999999999999999 to 99999999999999999999)"
            ),
        ),
        (
            ["frac", "1", "0"],
            "Q must not be 0",
        ),
        (
            ["frac", "bad", "0"],
            (
                'invalid P "bad" (expected an integer from '
                "-99999999999999999999 to 99999999999999999999)"
            ),
        ),
        (
            ["sqrt", "0"],
            'invalid D "0" (expected an integer from 1 to 100000000)',
        ),
        (
            ["sqrt", "100000001"],
            'invalid D "100000001" (expected an integer from 1 to 100000000)',
        ),
        (
            ["pell", "0"],
            'invalid D "0" (expected an integer from 1 to 10000)',
        ),
        (
            ["pell", "10001"],
            'invalid D "10001" (expected an integer from 1 to 10000)',
        ),
    ],
)
def test_modes_report_exact_errors_and_validation_precedence(
    argv: list[str], expected_message: str
) -> None:
    assert_failure(argv, expected_message)
