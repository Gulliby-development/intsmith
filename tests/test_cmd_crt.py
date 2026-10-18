import pytest

from intsmith.commands.crt import run
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


def assert_success(argv: list[str], expected_output: str, expected_result: int = 0) -> None:
    io = FakeIo()

    assert run(argv, io) == expected_result
    assert io.out_calls == [expected_output]
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
    ("argv", "expected_output", "expected_result"),
    [
        (
            ["2:3", "3:5", "2:7"],
            "crt       3 congruences\nx         23 (mod 105)\n",
            0,
        ),
        (
            ["1:4", "2:6"],
            "crt       2 congruences\nstatus    no solution\n",
            1,
        ),
        (
            ["-1:7", "3:9", "0:5"],
            "crt       3 congruences\nx         300 (mod 315)\n",
            0,
        ),
        (
            ["5:7"],
            "crt       1 congruence\nx         5 (mod 7)\n",
            0,
        ),
        (
            ["7:1"],
            "crt       1 congruence\nx         0 (mod 1)\n",
            0,
        ),
        (
            ["2:4", "6:8"],
            "crt       2 congruences\nx         6 (mod 8)\n",
            0,
        ),
        (
            ["-99999999999999999999:99999999999999999999"],
            ("crt       1 congruence\nx         0 (mod 99999999999999999999)\n"),
            0,
        ),
        (
            [
                "0:1",
                "0:1",
                "0:1",
                "0:1",
                "0:1",
                "0:1",
                "0:1",
                "0:1",
                "0:1",
                "0:1",
                "0:1",
                "0:1",
            ],
            "crt       12 congruences\nx         0 (mod 1)\n",
            0,
        ),
    ],
)
def test_crt_prints_complete_exact_results_once(
    argv: list[str], expected_output: str, expected_result: int
) -> None:
    assert_success(argv, expected_output, expected_result)


def test_crt_requires_at_least_one_congruence() -> None:
    assert_failure([], "missing R:M")


def test_crt_rejects_a_thirteenth_congruence() -> None:
    assert_failure(
        [
            "0:1",
            "0:1",
            "0:1",
            "0:1",
            "0:1",
            "0:1",
            "0:1",
            "0:1",
            "0:1",
            "0:1",
            "0:1",
            "0:1",
            "0:1",
        ],
        "too many congruences (at most 12)",
    )


def test_crt_checks_options_before_the_congruence_count() -> None:
    assert_failure(
        [
            "0:1",
            "0:1",
            "0:1",
            "0:1",
            "0:1",
            "0:1",
            "0:1",
            "0:1",
            "0:1",
            "0:1",
            "0:1",
            "0:1",
            "0:1",
            "--help",
        ],
        'unknown option "--help"',
    )


@pytest.mark.parametrize(
    ("argv", "expected_message"),
    [
        (["bad"], 'invalid congruence "bad" (expected R:M)'),
        (["1:2:3"], 'invalid congruence "1:2:3" (expected R:M)'),
        ([""], 'invalid congruence "" (expected R:M)'),
        (["-"], 'invalid congruence "-" (expected R:M)'),
    ],
)
def test_crt_requires_exactly_one_colon(argv: list[str], expected_message: str) -> None:
    assert_failure(argv, expected_message)


@pytest.mark.parametrize(
    ("argv", "expected_message"),
    [
        (
            [":1"],
            'invalid R "" (expected an integer from -99999999999999999999 to 99999999999999999999)',
        ),
        (
            ["1:"],
            'invalid M "" (expected an integer from 1 to 99999999999999999999)',
        ),
        (
            ["1:0"],
            'invalid M "0" (expected an integer from 1 to 99999999999999999999)',
        ),
        (
            ["bad:0"],
            'invalid R "bad" (expected an integer from -99999999999999999999 to 99999999999999999999)',
        ),
    ],
)
def test_crt_checks_residue_then_modulus_with_exact_ranges(
    argv: list[str], expected_message: str
) -> None:
    assert_failure(argv, expected_message)


@pytest.mark.parametrize(
    ("argv", "expected_message"),
    [
        (
            ["-0:7"],
            'invalid R "-0" (expected an integer from -99999999999999999999 to 99999999999999999999)',
        ),
        (
            ["+3:7"],
            'invalid R "+3" (expected an integer from -99999999999999999999 to 99999999999999999999)',
        ),
        (
            ["007:7"],
            'invalid R "007" (expected an integer from -99999999999999999999 to 99999999999999999999)',
        ),
        (
            ["1.5:7"],
            'invalid R "1.5" (expected an integer from -99999999999999999999 to 99999999999999999999)',
        ),
        (
            ["1e3:7"],
            'invalid R "1e3" (expected an integer from -99999999999999999999 to 99999999999999999999)',
        ),
        (
            ["٣:7"],
            'invalid R "?" (expected an integer from -99999999999999999999 to 99999999999999999999)',
        ),
        (
            ["100000000000000000000:7"],
            'invalid R "100000000000000000000" (expected an integer from -99999999999999999999 to 99999999999999999999)',
        ),
    ],
)
def test_crt_rejects_noncanonical_or_out_of_range_residues(
    argv: list[str], expected_message: str
) -> None:
    assert_failure(argv, expected_message)


@pytest.mark.parametrize(
    ("argv", "expected_message"),
    [
        (
            ["1:-0"],
            'invalid M "-0" (expected an integer from 1 to 99999999999999999999)',
        ),
        (
            ["1:+3"],
            'invalid M "+3" (expected an integer from 1 to 99999999999999999999)',
        ),
        (
            ["1:01"],
            'invalid M "01" (expected an integer from 1 to 99999999999999999999)',
        ),
        (
            ["1:100000000000000000000"],
            'invalid M "100000000000000000000" (expected an integer from 1 to 99999999999999999999)',
        ),
    ],
)
def test_crt_rejects_noncanonical_or_out_of_range_moduli(
    argv: list[str], expected_message: str
) -> None:
    assert_failure(argv, expected_message)


def test_crt_checks_each_word_before_later_word_shape() -> None:
    assert_failure(
        ["1:0", "not-a-congruence"],
        'invalid M "0" (expected an integer from 1 to 99999999999999999999)',
    )


def test_crt_checks_word_shape_before_its_numeric_components() -> None:
    assert_failure(
        ["bad:2:3"],
        'invalid congruence "bad:2:3" (expected R:M)',
    )


def test_crt_rejects_unknown_options_even_when_they_follow_valid_words() -> None:
    assert_failure(["1:1", "--not-supported"], 'unknown option "--not-supported"')
