import pytest

from intsmith.nt.dlog import discrete_log
from intsmith.nt.units import multiplicative_order


@pytest.mark.parametrize(
    ("g", "h", "m", "expected"),
    [
        (1, 1, 2, 0),
        (1, 2, 7, None),
        (3, 1, 17, 0),
        (3, 13, 17, 4),
        (2, 3, 7, None),
        (3, 0, 7, None),
        (3, 2, 8, None),
        (3, 5, 8, None),
        (3, 3, 8, 1),
        (2, 8, 9, 3),
        (-3, -4, 17, 4),
        (5, 123456789, 1000000007, 981640996),
        (99999999999999999993, 99999999999999999997, 10, 3),
        (-99999999999999999999, 1, 10, 0),
        (9999999999, 9999999999, 10000000000, 1),
        (3, 10, 17, 3),
        (3, 6, 17, 15),
        (2, 7, 101, 9),
        (2, 14, 101, 10),
        (2, 51, 101, 99),
    ],
)
def test_discrete_log_returns_the_least_exponent(
    g: int, h: int, m: int, expected: int | None
) -> None:
    assert discrete_log(g, h, m) == expected


def test_near_cap_large_order_workload() -> None:
    modulus = 10000000000
    target = 6666666667

    assert multiplicative_order(3, modulus) == 500000000
    assert discrete_log(3, target, modulus) == 499999999
