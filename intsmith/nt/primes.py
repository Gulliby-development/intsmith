"""Exact primality, neighboring-prime, and integer-factorization routines.

Primality uses strong Miller--Rabin tests to the first twelve prime bases,
2 through 37. Sorenson and Webster's bound for the first common strong
pseudoprime to those bases is 318665857834031151167461, so this test is
deterministic throughout the required interval n < 3 * 10**23.

Factorization strips primes below 1000, detects exact perfect powers, and
recursively splits composites with Brent's batched Pollard-rho algorithm.
For a least prime factor p, rho has expected O(sqrt(p)) modular steps; a
balanced semiprime below 10**20 therefore takes about 10**5 expected steps.
One hundred distinct such inputs are about 10**7 expected rho steps, apart
from primality checks. Each deterministic restart is capped at 500000 steps
and the seed/constant schedule continues until a split succeeds. Rho's
restart schedule is not a proof of a uniform worst-case time bound, so these
expected costs do not establish the universal five-second target.

A prime interval of width at most 10000 has at most 5001 odd candidates.
Each candidate receives small-prime divisions followed, when needed, by
twelve logarithmic-time modular exponentiation tests. This bounds the number
of candidates, rather than searching through integers up to their square
roots.
"""

from math import gcd, isqrt

_MR_BASES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
_POWER_EXPONENTS = (3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61)
_RHO_STEP_LIMIT = 500_000
_RHO_BLOCK_SIZE = 128


def _primes_below(limit: int) -> tuple[int, ...]:
    """Return the primes below limit using a compact sieve."""
    sieve = bytearray(b"\x01") * limit
    if limit > 0:
        sieve[0] = 0
    if limit > 1:
        sieve[1] = 0

    for candidate in range(2, isqrt(limit - 1) + 1):
        if sieve[candidate]:
            start = candidate * candidate
            count = (limit - 1 - start) // candidate + 1
            sieve[start:limit:candidate] = b"\x00" * count

    return tuple(candidate for candidate in range(2, limit) if sieve[candidate])


_SMALL_PRIMES = _primes_below(1000)


def is_prime(n: int) -> bool:
    """Return whether n is prime, exactly for every n < 3 * 10**23."""
    if n < 2:
        return False

    for prime in _SMALL_PRIMES:
        if n == prime:
            return True
        if n % prime == 0:
            return False

    odd_part = n - 1
    powers_of_two = 0
    while odd_part % 2 == 0:
        odd_part //= 2
        powers_of_two += 1

    for base in _MR_BASES:
        residue = pow(base, odd_part, n)
        if residue == 1 or residue == n - 1:
            continue

        for _ in range(powers_of_two - 1):
            residue = residue * residue % n
            if residue == n - 1:
                break
        else:
            return False

    return True


def next_prime(n: int) -> int:
    """Return the smallest prime strictly greater than n."""
    candidate = n + 1
    if candidate < 2:
        candidate = 2
    elif candidate > 2 and candidate % 2 == 0:
        candidate += 1

    while not is_prime(candidate):
        candidate = 3 if candidate == 2 else candidate + 2
    return candidate


def prev_prime(n: int) -> int | None:
    """Return the largest prime strictly less than n, if one exists."""
    if n <= 2:
        return None

    candidate = n - 1
    if candidate > 2 and candidate % 2 == 0:
        candidate -= 1

    while candidate >= 2:
        if is_prime(candidate):
            return candidate
        candidate -= 2
    return None


def _integer_nth_root(n: int, exponent: int) -> int:
    """Return floor(n ** (1 / exponent)) without floating-point arithmetic."""
    low = 1
    high = 1 << ((n.bit_length() + exponent - 1) // exponent)

    while low < high:
        middle = (low + high + 1) // 2
        if middle**exponent <= n:
            low = middle
        else:
            high = middle - 1
    return low


def _perfect_power(n: int) -> tuple[int, int] | None:
    """Return root and exponent when n is an exact nontrivial power."""
    square_root = isqrt(n)
    if square_root * square_root == n:
        return square_root, 2

    for exponent in _POWER_EXPONENTS:
        if exponent >= n.bit_length():
            break
        root = _integer_nth_root(n, exponent)
        if root**exponent == n:
            return root, exponent
    return None


def _brent_split(n: int) -> int:
    """Find a nontrivial factor with deterministic Brent-rho restarts."""
    if n % 2 == 0:
        return 2

    attempt = 1
    while True:
        constant = attempt % (n - 1) + 1
        y = (attempt + 1) % (n - 1) + 1
        divisor = 1
        radius = 1
        steps = 0
        x = 0
        saved_y = 0

        while divisor == 1 and steps < _RHO_STEP_LIMIT:
            x = y
            advance = min(radius, _RHO_STEP_LIMIT - steps)
            for _ in range(advance):
                y = (y * y + constant) % n
            steps += advance

            offset = 0
            while offset < radius and divisor == 1 and steps < _RHO_STEP_LIMIT:
                saved_y = y
                batch_size = min(
                    _RHO_BLOCK_SIZE,
                    radius - offset,
                    _RHO_STEP_LIMIT - steps,
                )
                product = 1
                for _ in range(batch_size):
                    y = (y * y + constant) % n
                    product = product * abs(x - y) % n
                divisor = gcd(product, n)
                offset += batch_size
                steps += batch_size

            if divisor == 1 and steps < _RHO_STEP_LIMIT:
                radius *= 2

        if 1 < divisor < n:
            return divisor

        if divisor == n:
            divisor = 1
            recovery_steps = 0
            while divisor == 1 and recovery_steps < _RHO_BLOCK_SIZE and steps < _RHO_STEP_LIMIT:
                saved_y = (saved_y * saved_y + constant) % n
                divisor = gcd(abs(x - saved_y), n)
                recovery_steps += 1
                steps += 1
            if 1 < divisor < n:
                return divisor

        attempt += 1


def factor(n: int) -> list[tuple[int, int]]:
    """Return the sorted prime factorization of n for n >= 1."""
    if n == 1:
        return []

    factors: dict[int, int] = {}
    remainder = n

    for prime in _SMALL_PRIMES:
        if prime * prime > remainder:
            break
        while remainder % prime == 0:
            factors[prime] = factors.get(prime, 0) + 1
            remainder //= prime

    pending = [(remainder, 1)] if remainder > 1 else []
    while pending:
        value, multiplicity = pending.pop()
        if is_prime(value):
            factors[value] = factors.get(value, 0) + multiplicity
            continue

        power = _perfect_power(value)
        if power is not None:
            root, exponent = power
            pending.append((root, multiplicity * exponent))
            continue

        divisor = _brent_split(value)
        pending.append((divisor, multiplicity))
        pending.append((value // divisor, multiplicity))

    return sorted(factors.items())
