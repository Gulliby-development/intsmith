import pytest

from intsmith.nt.funcs import carmichael, divisors, format_factors, mobius, phi, radical, sigma, tau


@pytest.mark.parametrize(
    ("fs", "expected"),
    [
        ([], (1, 1, 1, 1, 1, 1)),
        ([(2, 1)], (2, 3, 1, -1, 1, 2)),
        ([(2, 2)], (3, 7, 2, 0, 2, 2)),
        ([(2, 3)], (4, 15, 4, 0, 2, 2)),
        ([(2, 4)], (5, 31, 8, 0, 4, 2)),
        ([(2, 5)], (6, 63, 16, 0, 8, 2)),
        ([(3, 1)], (2, 4, 2, -1, 2, 3)),
        ([(3, 2)], (3, 13, 6, 0, 6, 3)),
        ([(5, 3)], (4, 156, 100, 0, 100, 5)),
        ([(2, 1), (3, 1)], (4, 12, 2, 1, 2, 6)),
        ([(2, 2), (3, 1)], (6, 28, 4, 0, 2, 6)),
        ([(2, 1), (3, 1), (5, 1)], (8, 72, 8, -1, 4, 30)),
        ([(2, 3), (3, 2), (5, 1)], (24, 1170, 96, 0, 12, 30)),
    ],
)
def test_factorization_functions(fs: list[tuple[int, int]], expected: tuple[int, ...]) -> None:
    (
        expected_tau,
        expected_sigma,
        expected_phi,
        expected_mobius,
        expected_carmichael,
        expected_radical,
    ) = expected
    assert tau(fs) == expected_tau
    assert sigma(fs) == expected_sigma
    assert phi(fs) == expected_phi
    assert mobius(fs) == expected_mobius
    assert carmichael(fs) == expected_carmichael
    assert radical(fs) == expected_radical


@pytest.mark.parametrize(
    ("fs", "expected"),
    [
        ([], [1]),
        ([(2, 1)], [1, 2]),
        ([(2, 3)], [1, 2, 4, 8]),
        ([(2, 2), (7, 1)], [1, 2, 4, 7, 14, 28]),
        ([(3, 1), (5, 1)], [1, 3, 5, 15]),
    ],
)
def test_divisors_are_complete_and_sorted(fs: list[tuple[int, int]], expected: list[int]) -> None:
    assert divisors(fs) == expected


@pytest.mark.parametrize(
    ("fs", "expected"),
    [
        ([], "1"),
        ([(2, 1)], "2"),
        ([(2, 1), (3, 1), (5, 1)], "2 * 3 * 5"),
        ([(2, 3), (3, 2), (5, 1)], "2^3 * 3^2 * 5"),
    ],
)
def test_format_factors_omits_unit_exponents(fs: list[tuple[int, int]], expected: str) -> None:
    assert format_factors(fs) == expected
