from dataclasses import FrozenInstanceError

import pytest

from intsmith.core.options import Parsed, Spec, flag, integer, parse
from intsmith.core.text import Failure


def assert_parse_error(argv: list[str], specs: list[Spec], expected_message: str) -> None:
    with pytest.raises(Failure) as exc_info:
        parse(argv, specs)
    assert exc_info.value.message == expected_message


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("--divisors", Spec("--divisors", True, 0, 0, 0)),
        ("--verbose", Spec("--verbose", True, 0, 0, 0)),
        ("--flag", Spec("--flag", True, 0, 0, 0)),
    ],
)
def test_flag_constructor_sets_name_and_zero_numeric_fields(name: str, expected: Spec) -> None:
    actual = flag(name)
    assert actual == expected
    assert actual.name == name
    assert actual.flag is True
    assert actual.lo == 0
    assert actual.hi == 0
    assert actual.fallback == 0


@pytest.mark.parametrize(
    ("name", "lo", "hi", "fallback"),
    [
        ("--terms", 1, 200, 12),
        ("--count", 0, 9, 0),
        ("--offset", -5, 5, -2),
    ],
)
def test_integer_constructor_preserves_fields(name: str, lo: int, hi: int, fallback: int) -> None:
    actual = integer(name, lo, hi, fallback)
    assert actual == Spec(name, False, lo, hi, fallback)
    assert actual.name == name
    assert actual.flag is False
    assert actual.lo == lo
    assert actual.hi == hi
    assert actual.fallback == fallback


def test_spec_is_frozen_and_parsed_is_mutable() -> None:
    spec = integer("--terms", 1, 200, 12)
    with pytest.raises(FrozenInstanceError):
        spec.name = "--count"

    parsed = Parsed(values={"--terms": 12}, args=["input"])
    parsed.values["--terms"] = 5
    parsed.values["--other"] = 1
    parsed.args.append("next")
    assert parsed.values == {"--terms": 5, "--other": 1}
    assert parsed.args == ["input", "next"]


def test_parse_with_no_arguments_returns_all_defaults() -> None:
    parsed = parse([], [flag("--divisors"), integer("--terms", 1, 200, 12)])
    assert parsed.values == {"--divisors": 0, "--terms": 12}
    assert parsed.args == []


def test_parse_with_empty_specs_returns_empty_values() -> None:
    parsed = parse([], [])
    assert parsed.values == {}
    assert parsed.args == []


@pytest.mark.parametrize(
    ("argv", "expected_args"),
    [
        (["-"], ["-"]),
        (["-5"], ["-5"]),
        (["word", "-", "-5"], ["word", "-", "-5"]),
        (["first", "second"], ["first", "second"]),
    ],
)
def test_parse_preserves_ordinary_arguments_in_order(
    argv: list[str], expected_args: list[str]
) -> None:
    parsed = parse(argv, [])
    assert parsed.values == {}
    assert parsed.args == expected_args


@pytest.mark.parametrize(
    ("argv", "expected_values"),
    [
        (["--terms=1"], {"--terms": 1}),
        (["--terms=5"], {"--terms": 5}),
        (["--terms=200"], {"--terms": 200}),
        (["--terms", "5"], {"--terms": 5}),
        (["--terms", "1"], {"--terms": 1}),
        (["--terms", "200"], {"--terms": 200}),
    ],
)
def test_parse_accepts_both_integer_value_syntaxes_and_inclusive_limits(
    argv: list[str], expected_values: dict[str, int]
) -> None:
    parsed = parse(argv, [integer("--terms", 1, 200, 12)])
    assert parsed.values == expected_values
    assert parsed.args == []


@pytest.mark.parametrize(
    ("argv", "expected_values", "expected_args"),
    [
        (["--terms=2", "word"], {"--terms": 2}, ["word"]),
        (["first", "--terms", "3", "last"], {"--terms": 3}, ["first", "last"]),
        (["--terms=4", "-", "-5"], {"--terms": 4}, ["-", "-5"]),
    ],
)
def test_parse_keeps_ordinary_arguments_around_options(
    argv: list[str], expected_values: dict[str, int], expected_args: list[str]
) -> None:
    parsed = parse(argv, [integer("--terms", 1, 200, 12)])
    assert parsed.values == expected_values
    assert parsed.args == expected_args


def test_parse_marks_repeated_flags_as_one() -> None:
    parsed = parse(["--divisors", "--divisors"], [flag("--divisors")])
    assert parsed.values == {"--divisors": 1}
    assert parsed.args == []


@pytest.mark.parametrize(
    ("argv", "expected"),
    [
        (["--terms=2", "--terms=3"], 3),
        (["--terms=3", "--terms=2"], 2),
        (["--terms", "2", "--terms", "3"], 3),
    ],
)
def test_parse_uses_the_last_integer_option(argv: list[str], expected: int) -> None:
    parsed = parse(argv, [integer("--terms", 1, 200, 12)])
    assert parsed.values == {"--terms": expected}


def test_parse_ignores_an_invalid_integer_value_that_is_overwritten() -> None:
    parsed = parse(
        ["--terms=bad", "--terms=5"],
        [integer("--terms", 1, 200, 12)],
    )
    assert parsed.values == {"--terms": 5}


@pytest.mark.parametrize(
    ("argv", "expected_message"),
    [
        (["--terms=bad"], 'invalid --terms "bad" (expected an integer from 1 to 200)'),
        (["--terms=201"], 'invalid --terms "201" (expected an integer from 1 to 200)'),
        (["--terms=0"], 'invalid --terms "0" (expected an integer from 1 to 200)'),
        (["--terms="], 'invalid --terms "" (expected an integer from 1 to 200)'),
        (["--terms=5=6"], 'invalid --terms "5=6" (expected an integer from 1 to 200)'),
        (["--terms=="], 'invalid --terms "=" (expected an integer from 1 to 200)'),
        (["--terms", "-5"], 'invalid --terms "-5" (expected an integer from 1 to 200)'),
        (["--terms", "--help"], 'invalid --terms "--help" (expected an integer from 1 to 200)'),
    ],
)
def test_parse_validates_the_retained_value_exactly(argv: list[str], expected_message: str) -> None:
    assert_parse_error(argv, [integer("--terms", 1, 200, 12)], expected_message)


@pytest.mark.parametrize(
    ("argv", "expected_message"),
    [
        (["--unknown"], 'unknown option "--unknown"'),
        (["--bad=x"], 'unknown option "--bad=x"'),
        (["--unknown=value"], 'unknown option "--unknown=value"'),
        (["--"], 'unknown option "--"'),
        (["--help"], 'unknown option "--help"'),
        (["--terms=5"], 'unknown option "--terms=5"'),
    ],
)
def test_parse_rejects_unknown_options_including_without_specs(
    argv: list[str], expected_message: str
) -> None:
    assert_parse_error(argv, [], expected_message)


@pytest.mark.parametrize(
    ("argv", "expected_message"),
    [
        (["--divisors=value"], "--divisors takes no value"),
        (["--divisors="], "--divisors takes no value"),
        (["--divisors=1=2"], "--divisors takes no value"),
    ],
)
def test_parse_rejects_any_equals_value_for_a_flag(argv: list[str], expected_message: str) -> None:
    assert_parse_error(argv, [flag("--divisors")], expected_message)


def test_parse_reports_missing_integer_option_value() -> None:
    assert_parse_error(
        ["--terms"],
        [integer("--terms", 1, 200, 12)],
        "--terms needs a value",
    )


def test_parse_structural_errors_beat_earlier_invalid_integer_values() -> None:
    assert_parse_error(
        ["--terms=bad", "--unknown"],
        [integer("--terms", 1, 200, 12)],
        'unknown option "--unknown"',
    )


def test_parse_reports_first_structural_error_from_left_to_right() -> None:
    assert_parse_error(
        ["--unknown", "--terms"],
        [integer("--terms", 1, 200, 12)],
        'unknown option "--unknown"',
    )


def test_parse_later_flag_structure_error_beats_invalid_integer_text() -> None:
    assert_parse_error(
        ["--terms=bad", "--divisors=value"],
        [integer("--terms", 1, 200, 12), flag("--divisors")],
        "--divisors takes no value",
    )


def test_parse_missing_value_error_beats_invalid_earlier_integer_text() -> None:
    assert_parse_error(
        ["--terms=bad", "--count"],
        [integer("--terms", 1, 200, 12), integer("--count", 0, 9, 0)],
        "--count needs a value",
    )


def test_parse_checks_invalid_retained_values_in_specs_order() -> None:
    assert_parse_error(
        ["--second=bad", "--first=bad"],
        [integer("--first", 0, 9, 0), integer("--second", 0, 9, 0)],
        'invalid --first "bad" (expected an integer from 0 to 9)',
    )


def test_parse_checks_only_the_final_repeated_value() -> None:
    parsed = parse(
        ["--terms=bad", "--terms=7"],
        [integer("--terms", 1, 200, 12)],
    )
    assert parsed.values == {"--terms": 7}


def test_parse_validates_an_invalid_final_repeated_value() -> None:
    assert_parse_error(
        ["--terms=5", "--terms=bad"],
        [integer("--terms", 1, 200, 12)],
        'invalid --terms "bad" (expected an integer from 1 to 200)',
    )
