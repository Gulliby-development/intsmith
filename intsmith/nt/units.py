"""Multiplicative orders and primitive roots modulo integers.

An order is obtained from the Carmichael exponent of the unit group. Removing
prime factors while the corresponding power remains one yields the exact
least order. This needs factorization of the modulus and exponent, followed by
at most the prime-factor multiplicity of the exponent in modular-power tests;
the deterministic upstream factorizer has no uniform worst-case time bound.

Primitive roots exist only for 2, 4, odd prime powers, and twice odd prime
powers. After this classification, candidates are tested in increasing order
using the distinct prime factors of phi(n), factored once and shared by all
candidates. The scan examines at most n - 1 candidates, with a gcd and at most
omega(phi(n)) modular powers per candidate; it therefore has no polylogarithmic
worst-case bound. A command that independently computes phi, an order, and a
primitive root can repeat factorization of n (and related exponents), so these
costs and the upstream factorizer's limitations preclude a universal timing
claim for every permitted input.
"""

from math import gcd

from intsmith.nt.funcs import carmichael, phi
from intsmith.nt.primes import factor


def multiplicative_order(a: int, n: int) -> int:
    """Return the least positive exponent giving a**k == 1 modulo n.

    The preconditions are n >= 2 and gcd(a, n) == 1.
    """
    residue = a % n
    exponent = carmichael(factor(n))
    order = exponent

    for prime, _ in factor(exponent):
        while order % prime == 0 and pow(residue, order // prime, n) == 1:
            order //= prime

    return order


def smallest_primitive_root(n: int) -> int | None:
    """Return the smallest primitive root modulo n, or None if none exists.

    The precondition is n >= 2. The unit group is cyclic exactly for 2, 4,
    odd prime powers, and twice odd prime powers.
    """
    factors = factor(n)
    if n == 2:
        return 1

    cyclic = False
    if len(factors) == 1:
        prime, exponent = factors[0]
        cyclic = (prime != 2) or (exponent == 2)
    elif len(factors) == 2:
        first, second = factors
        cyclic = first == (2, 1) and second[0] != 2

    if not cyclic:
        return None

    group_order = phi(factors)
    prime_divisors = factor(group_order)
    distinct_primes = [prime for prime, _ in prime_divisors]

    for candidate in range(1, n):
        if gcd(candidate, n) != 1:
            continue
        if all(pow(candidate, group_order // prime, n) != 1 for prime in distinct_primes):
            return candidate

    return None
