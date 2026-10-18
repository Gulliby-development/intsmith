"""Exact rational and quadratic continued fractions, including Pell solutions.

Rational terms use Euclid's algorithm and convergents use a linear recurrence.
For square roots, the standard integer state recurrence uses ``isqrt`` and a
constant number of integer operations per term; requesting at most 200 terms is
therefore linear in that count. The period states are reduced complete quotients
``(P + sqrt(d)) / Q`` with ``1 <= P <= isqrt(d)`` and conjugate in ``(-1, 0)``.
Consequently ``Q`` lies in the open interval
``(sqrt(d) - P, sqrt(d) + P)``, which contains at most ``2 * P`` integers.
Distinct states give the conservative finite bound
``L <= sum(2 * P for P in 1..isqrt(d)) = a0 * (a0 + 1)``. Thus the configured
``d <= 100_000_000`` period domain has at most 99,990,000 states (not 20,000);
this loose bound does not itself prove the five-second target for every input.
For Pell's smaller ``d <= 10_000`` domain, ``a0 <= 99``, so ``L <= 9,900`` and
the positive solution uses at most ``2 * L <= 19,800`` convergent terms, not 400.
A hard literal workload at ``d = 9,949`` has period 217 and exercises 434 terms.
Each recurrence step is constant-count exact integer arithmetic. Convergent bit
length grows with the answer, which can itself be large, but no search over
candidate solutions is performed. Host timings of the hard fixture are evidence
for that fixture only, not a universal timing guarantee.
"""

from math import isqrt


def frac_terms(p: int, q: int) -> list[int]:
    """Return the canonical floor-Euclidean continued fraction for ``p / q``."""
    if q < 0:
        p, q = -p, -q

    terms: list[int] = []
    while q:
        quotient, remainder = divmod(p, q)
        terms.append(quotient)
        p, q = q, remainder
    return terms


def convergents(terms: list[int]) -> list[tuple[int, int]]:
    """Return numerator/denominator pairs for every prefix of ``terms``."""
    result: list[tuple[int, int]] = []
    previous_numerator, numerator = 0, 1
    previous_denominator, denominator = 1, 0

    for term in terms:
        next_numerator = term * numerator + previous_numerator
        next_denominator = term * denominator + previous_denominator
        result.append((next_numerator, next_denominator))
        previous_numerator, numerator = numerator, next_numerator
        previous_denominator, denominator = denominator, next_denominator

    return result


def _sqrt_step(d: int, a0: int, m: int, denominator: int, a: int) -> tuple[int, int, int]:
    """Advance one exact continued-fraction state for ``sqrt(d)``."""
    next_m = denominator * a - m
    next_denominator = (d - next_m * next_m) // denominator
    next_a = (a0 + next_m) // next_denominator
    return next_m, next_denominator, next_a


def sqrt_terms(d: int, count: int) -> list[int]:
    """Return the first ``count`` terms of the continued fraction for ``sqrt(d)``.

    A square has the finite canonical expansion consisting of its integer root.
    """
    if count <= 0:
        return []

    a0 = isqrt(d)
    if a0 * a0 == d:
        return [a0]

    terms = [a0]
    m, denominator, a = 0, 1, a0
    while len(terms) < count:
        m, denominator, a = _sqrt_step(d, a0, m, denominator, a)
        terms.append(a)
    return terms


def sqrt_period(d: int) -> int:
    """Return the repeating period length for ``sqrt(d)``, or zero for squares."""
    a0 = isqrt(d)
    if a0 * a0 == d:
        return 0

    m, denominator, a = 0, 1, a0
    period = 0
    while True:
        m, denominator, a = _sqrt_step(d, a0, m, denominator, a)
        period += 1
        if a == 2 * a0:
            return period


def pell(d: int) -> tuple[int, int, tuple[int, int] | None]:
    """Return the minimal positive Pell +1 solution and optional -1 solution.

    For a nonsquare positive ``d``, the +1 solution is the convergent at index
    ``L - 1`` when the square-root period ``L`` is even, or ``2L - 1`` when it
    is odd. A -1 solution exists exactly for odd ``L`` and is the convergent at
    index ``L - 1``. This parity theorem avoids searching candidate ``x`` and
    ``y`` values.
    """
    period = sqrt_period(d)
    positive_term_count = period if period % 2 == 0 else 2 * period
    terms = sqrt_terms(d, positive_term_count)
    prefixes = convergents(terms)
    x, y = prefixes[-1]
    negative = prefixes[period - 1] if period % 2 == 1 else None
    return x, y, negative
