"""Order-bounded discrete logarithms for unit groups.

Baby-step giant-step searches only exponents below the base's actual order.
For order r it takes O(sqrt(r)) modular multiplications and stores O(sqrt(r))
residues, then returns the first matching exponent in ascending giant-block
order. With the CLI modulus cap of 10**10, r is below 10**10 and the table
contains at most 100000 entries. The preceding order computation factors the
modulus and a Carmichael exponent; the upstream deterministic factorizer has
no uniform worst-case time bound, and a command may repeat this work when it
also displays the order.
"""

from math import gcd, isqrt

from intsmith.nt.units import multiplicative_order


def discrete_log(g: int, h: int, m: int) -> int | None:
    """Return the least nonnegative x such that g**x == h modulo m, if any.

    The preconditions are m >= 2 and gcd(g, m) == 1. A nonunit target cannot
    lie in the base's unit subgroup. For a unit target, exhausting one full
    base-order interval proves that it is outside the subgroup.
    """
    base = g % m
    target = h % m

    if target == 1:
        return 0
    if gcd(target, m) != 1:
        return None

    order = multiplicative_order(base, m)
    width = isqrt(order)
    if width * width < order:
        width += 1

    baby_steps: dict[int, int] = {}
    residue = 1
    for exponent in range(width):
        baby_steps.setdefault(residue, exponent)
        residue = residue * base % m

    # Since base is a unit, modular inversion is defined. Multiplying by this
    # inverse advances target * base**(-block * width) through giant blocks.
    giant_factor = pow(base, -width, m)
    giant_value = target
    block_count = (order + width - 1) // width

    for block in range(block_count):
        baby_exponent = baby_steps.get(giant_value)
        if baby_exponent is not None:
            candidate = block * width + baby_exponent
            if candidate < order:
                return candidate
        giant_value = giant_value * giant_factor % m

    return None
