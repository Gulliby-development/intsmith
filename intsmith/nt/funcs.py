"""Arithmetic functions and divisor utilities for prime factorizations.

Each calculation consumes the supplied sorted ``(prime, exponent)`` pairs
without modifying them. The scalar formulas are products of their
prime-power formulas; Carmichael's function combines the prime-power exponents
with an LCM, including its separate powers-of-two cases.
"""

from math import lcm

Factorization = list[tuple[int, int]]


def tau(fs: Factorization) -> int:
    """Return the number of positive divisors represented by fs."""
    result = 1
    for _, exponent in fs:
        result *= exponent + 1
    return result


def sigma(fs: Factorization) -> int:
    """Return the sum of positive divisors represented by fs."""
    result = 1
    for prime, exponent in fs:
        result *= (prime ** (exponent + 1) - 1) // (prime - 1)
    return result


def phi(fs: Factorization) -> int:
    """Return Euler's totient for the number represented by fs."""
    result = 1
    for prime, exponent in fs:
        result *= prime ** (exponent - 1) * (prime - 1)
    return result


def mobius(fs: Factorization) -> int:
    """Return the Moebius function of the number represented by fs."""
    if any(exponent > 1 for _, exponent in fs):
        return 0
    return -1 if len(fs) % 2 else 1


def carmichael(fs: Factorization) -> int:
    """Return the exponent of the group of units for the represented number."""
    result = 1
    for prime, exponent in fs:
        if prime == 2:
            if exponent == 1:
                prime_power_exponent = 1
            elif exponent == 2:
                prime_power_exponent = 2
            else:
                prime_power_exponent = 2 ** (exponent - 2)
        else:
            prime_power_exponent = prime ** (exponent - 1) * (prime - 1)
        result = lcm(result, prime_power_exponent)
    return result


def radical(fs: Factorization) -> int:
    """Return the product of the distinct prime factors represented by fs."""
    result = 1
    for prime, _ in fs:
        result *= prime
    return result


def divisors(fs: Factorization) -> list[int]:
    """Return all positive divisors in ascending order."""
    result = [1]
    for prime, exponent in fs:
        previous = result[:]
        prime_power = 1
        for _ in range(exponent):
            prime_power *= prime
            result.extend(divisor * prime_power for divisor in previous)
        result.sort()
    return result


def format_factors(fs: Factorization) -> str:
    """Format a sorted factorization, omitting exponent one."""
    if not fs:
        return "1"
    return " * ".join(
        str(prime) if exponent == 1 else f"{prime}^{exponent}" for prime, exponent in fs
    )
