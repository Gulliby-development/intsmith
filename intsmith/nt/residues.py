"""Legendre symbols and square roots modulo prime numbers.

The Tonelli-Shanks recurrence uses O(log p) iterations and O(log^2 p)
modular multiplications after a quadratic nonresidue is known; modular
exponentiation uses O(log p) multiplications. Roots are obtained directly
from the recurrence, never by scanning residues.

To find the needed nonresidue deterministically, candidates are tested in
increasing order with Euler's criterion. For prime p, this terminates no later
than p - 1, but its worst-case search is O(p log p) modular multiplications.
There is no unconditional polylogarithmic bound for this simple deterministic
search, so the modular-power recurrence alone does not prove a universal
five-second bound for every permitted modulus.
"""


def legendre(a: int, p: int) -> int:
    """Return the Legendre symbol, with the specified parity convention for p=2."""
    if p == 2:
        return a % 2

    residue = a % p
    if residue == 0:
        return 0
    return 1 if pow(residue, (p - 1) // 2, p) == 1 else -1


def sqrt_mod_prime(a: int, p: int) -> list[int]:
    """Return all square roots of a modulo the prime p in ascending order."""
    residue = a % p
    if p == 2:
        return [residue]
    if residue == 0:
        return [0]
    if pow(residue, (p - 1) // 2, p) != 1:
        return []

    if p % 4 == 3:
        root = pow(residue, (p + 1) // 4, p)
    else:
        odd_part = p - 1
        power_of_two = 0
        while odd_part % 2 == 0:
            odd_part //= 2
            power_of_two += 1

        nonresidue = 2
        while pow(nonresidue, (p - 1) // 2, p) != p - 1:
            nonresidue += 1

        exponent = odd_part
        coefficient = pow(nonresidue, exponent, p)
        remainder = pow(residue, exponent, p)
        root = pow(residue, (exponent + 1) // 2, p)
        remaining_power = power_of_two

        while remainder != 1:
            index = 1
            squared = remainder * remainder % p
            while squared != 1:
                squared = squared * squared % p
                index += 1

            adjustment = pow(coefficient, 1 << (remaining_power - index - 1), p)
            remaining_power = index
            coefficient = adjustment * adjustment % p
            remainder = remainder * coefficient % p
            root = root * adjustment % p

    other_root = (-root) % p
    return [root] if root == other_root else sorted([root, other_root])
