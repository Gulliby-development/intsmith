import pytest

from intsmith.nt.gcd import crt, egcd, inverse, lcm


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        (0, 0, (0, 0, 0)),
        (-12, 0, (12, -1, 0)),
        (0, -7, (7, 0, -1)),
        (240, 46, (2, 14, -73)),
        (17, 3120, (1, 2753, -15)),
        (7, -3, (1, 1, 2)),
        (-7, 3, (1, 2, 5)),
        (-18, -30, (6, 3, -2)),
        (1, 99999999999999999999, (1, 1, 0)),
        (99999999999999999999, 0, (99999999999999999999, 1, 0)),
        (99999999999999999999, 99999999999999999999, (99999999999999999999, 0, 1)),
    ],
)
def test_egcd_returns_canonical_bezout_pair(a: int, b: int, expected: tuple[int, int, int]) -> None:
    assert egcd(a, b) == expected


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        (0, 0, 0),
        (0, -12, 0),
        (-12, 18, 36),
        (-4, -6, 12),
        (240, 46, 5520),
        (1, 99999999999999999999, 99999999999999999999),
        (99999999999999999999, 2, 199999999999999999998),
    ],
)
def test_lcm_is_nonnegative_and_exact(a: int, b: int, expected: int) -> None:
    assert lcm(a, b) == expected


@pytest.mark.parametrize(
    ("a", "modulus", "expected"),
    [
        (17, 3120, 2753),
        (17, -3120, 2753),
        (3, 11, 4),
        (-3, 11, 7),
        (1, 2, 1),
        (-1, 2, 1),
        (240, 46, None),
        (6, 9, None),
        (0, 7, None),
        (7, -1, None),
        (7, 0, None),
        (7, 1, None),
    ],
)
def test_inverse_returns_least_positive_inverse_or_none(
    a: int, modulus: int, expected: int | None
) -> None:
    assert inverse(a, modulus) == expected


@pytest.mark.parametrize(
    ("items", "expected"),
    [
        ([], (0, 1)),
        ([(2, 3), (3, 5), (2, 7)], (23, 105)),
        ([(1, 4), (2, 6)], None),
        ([(-1, 7), (3, 9), (0, 5)], (300, 315)),
        ([(2, 4), (6, 8)], (6, 8)),
        ([(7, 1)], (0, 1)),
        ([(2, 5), (7, 5)], (2, 5)),
        ([(2, 5), (3, 5)], None),
        ([(-1, 4)], (3, 4)),
        ([(7, 1), (-2, 3)], (1, 3)),
        ([(0, 2), (0, 99999999999999999999)], (0, 199999999999999999998)),
    ],
)
def test_crt_merges_generalized_congruences(
    items: list[tuple[int, int]], expected: tuple[int, int] | None
) -> None:
    assert crt(items) == expected
