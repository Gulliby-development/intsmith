"""Factor command adapter.

The adapter accepts batches of at most 100 values. The upstream factorization
routine uses deterministic Pollard-rho restarts with expected fast costs for
hard semiprimes, but does not claim a uniform worst-case time bound.
"""

from intsmith.core.ints import parse_int
from intsmith.core.options import parse
from intsmith.core.text import BIG, Failure
from intsmith.core.words import Io, words_of
from intsmith.nt.funcs import format_factors
from intsmith.nt.primes import factor


def run(argv: list[str], io: Io) -> int:
    """Factor each validated argument or stdin word, preserving its order."""
    args = parse(argv, []).args
    words = words_of(io, args)
    if not words:
        raise Failure("missing N")
    if len(words) > 100:
        raise Failure("too many numbers (at most 100)")

    numbers = [parse_int("N", word, 1, BIG) for word in words]
    output = "".join(f"{number} = {format_factors(factor(number))}\n" for number in numbers)
    io.out(output)
    return 0
