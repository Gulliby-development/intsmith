import pytest

from intsmith.nt.units import multiplicative_order, smallest_primitive_root


@pytest.mark.parametrize(
    ("a", "n", "expected"),
    [
        (1, 2, 1),
        (-1, 7, 2),
        (3, 7, 6),
        (3, 100, 20),
        (5, 16, 4),
        (10, 9, 1),
        (2, 9, 6),
        (7, 99999999999999999989, 99999999999999999988),
        (8, 7, 1),
        (-7, 16, 2),
    ],
)
def test_multiplicative_order(a: int, n: int, expected: int) -> None:
    assert multiplicative_order(a, n) == expected


@pytest.mark.parametrize(
    ("n", "expected"),
    [
        (2, 1),
        (3, 2),
        (4, 3),
        (7, 3),
        (9, 2),
        (18, 5),
        (25, 2),
        (8, None),
        (12, None),
        (15, None),
        (100, None),
        (99999999999999999989, 2),
        (16, None),
        (27, 2),
        (50, 3),
    ],
)
def test_smallest_primitive_root(n: int, expected: int | None) -> None:
    assert smallest_primitive_root(n) == expected


def test_large_order_and_primitive_root_workload() -> None:
    modulus = 99999999999999999989
    assert multiplicative_order(7, modulus) == 99999999999999999988
    assert smallest_primitive_root(modulus) == 2
