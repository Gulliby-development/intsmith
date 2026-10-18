"""Command adapter for arithmetic functions.

Divisors are materialized only when requested, after tau has confirmed that
there are at most 1000 of them.
"""

from intsmith.core.ints import parse_int
from intsmith.core.options import flag, parse
from intsmith.core.text import BIG, Failure, line
from intsmith.core.words import Io
from intsmith.nt.funcs import (
    carmichael,
    divisors,
    format_factors,
    mobius,
    phi,
    radical,
    sigma,
    tau,
)
from intsmith.nt.primes import factor


def run(argv: list[str], io: Io) -> int:
    """Print arithmetic functions for one validated positive integer."""
    parsed = parse(argv, [flag("--divisors")])
    if not parsed.args:
        raise Failure("missing N")
    if len(parsed.args) > 1:
        raise Failure("too many arguments")

    number = parse_int("N", parsed.args[0], 1, BIG)
    factors = factor(number)
    divisor_count = tau(factors)
    if parsed.values["--divisors"] and divisor_count > 1000:
        raise Failure(f"too many divisors to list ({divisor_count}, at most 1000)")

    divisor_sum = sigma(factors)
    classification = "deficient" if divisor_sum < 2 * number else "perfect"
    if divisor_sum > 2 * number:
        classification = "abundant"

    output = "".join(
        (
            line("n", str(number)),
            line("factors", format_factors(factors)),
            line("omega", str(len(factors))),
            line("bigomega", str(sum(exponent for _, exponent in factors))),
            line("tau", str(divisor_count)),
            line("sigma", str(divisor_sum)),
            line("phi", str(phi(factors))),
            line("mu", str(mobius(factors))),
            line("lambda", str(carmichael(factors))),
            line("radical", str(radical(factors))),
            line("class", classification),
        )
    )
    if parsed.values["--divisors"]:
        output += line("divisors", " ".join(str(value) for value in divisors(factors)))

    io.out(output)
    return 0
