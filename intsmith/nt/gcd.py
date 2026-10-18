"""Exact gcd, inverse, and generalized Chinese remainder arithmetic.

The extended Euclidean recurrence computes a Bezout coefficient pair. For a
nonzero second argument, reducing the coefficient of ``a`` modulo ``|b|/g``
selects the unique canonical nonnegative coefficient; the other coefficient
then follows exactly from the Bezout identity. CRT systems are merged one
congruence at a time using that same gcd and a modular inverse, so compatible
non-coprime moduli are handled without search.
"""


def egcd(a: int, b: int) -> tuple[int, int, int]:
    """Return the canonical Bezout triple ``(g, x, y)`` for ``a`` and ``b``."""
    if a == 0 and b == 0:
        return 0, 0, 0
    if b == 0:
        return abs(a), 1 if a > 0 else -1, 0

    old_remainder, remainder = abs(a), abs(b)
    old_coefficient, coefficient = 1, 0
    while remainder:
        quotient = old_remainder // remainder
        old_remainder, remainder = remainder, old_remainder - quotient * remainder
        old_coefficient, coefficient = (
            coefficient,
            old_coefficient - quotient * coefficient,
        )

    gcd_value = old_remainder
    x = old_coefficient if a > 0 else -old_coefficient
    x %= abs(b) // gcd_value
    y = (gcd_value - a * x) // b
    return gcd_value, x, y


def lcm(a: int, b: int) -> int:
    """Return the nonnegative least common multiple of ``a`` and ``b``."""
    if a == 0 or b == 0:
        return 0
    return abs((a // egcd(a, b)[0]) * b)


def inverse(a: int, m: int) -> int | None:
    """Return the least positive inverse of ``a`` modulo ``abs(m)``, if any."""
    modulus = abs(m)
    if modulus < 2:
        return None
    gcd_value, x, _ = egcd(a, modulus)
    if gcd_value != 1:
        return None
    return x


def crt(items: list[tuple[int, int]]) -> tuple[int, int] | None:
    """Merge congruences into a normalized residue and their lcm modulus.

    Each new congruence is compatible precisely when its residue agrees with
    the current residue modulo the gcd of the two moduli. Dividing by that gcd
    leaves a coprime linear congruence for the merge multiplier.
    """
    residue, modulus = 0, 1
    for next_residue, next_modulus in items:
        gcd_value, inverse_coefficient, _ = egcd(modulus, next_modulus)
        difference = next_residue - residue
        if difference % gcd_value != 0:
            return None

        reduced_modulus = next_modulus // gcd_value
        if reduced_modulus == 1:
            multiplier = 0
        else:
            multiplier = ((difference // gcd_value) * inverse_coefficient) % reduced_modulus

        combined_modulus = modulus * reduced_modulus
        residue = (residue + modulus * multiplier) % combined_modulus
        modulus = combined_modulus
    return residue, modulus
