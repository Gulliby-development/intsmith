"""Prime command adapter with bounded inclusive list enumeration."""

from intsmith.core.ints import parse_int
from intsmith.core.options import parse
from intsmith.core.text import BIG, Failure, show
from intsmith.core.words import Io
from intsmith.nt.primes import is_prime, next_prime, prev_prime


def run(argv: list[str], io: Io) -> int:
    """Run a prime mode after validating its mode, arity, values, and bounds."""
    if not argv:
        raise Failure("missing mode (test, next, prev or list)")

    mode = argv[0]
    if mode not in ("test", "next", "prev", "list"):
        raise Failure(f"unknown mode {show(mode)} (expected test, next, prev or list)")

    args = parse(argv[1:], []).args
    names = ["LO", "HI"] if mode == "list" else ["N"]
    if len(args) < len(names):
        raise Failure(f"missing {names[len(args)]}")
    if len(args) > len(names):
        raise Failure("too many arguments")

    values = [parse_int(name, text, 0, BIG) for name, text in zip(names, args)]
    if mode == "list":
        low, high = values
        if high < low:
            raise Failure("HI must not be below LO")
        if high - low > 10000:
            raise Failure("HI - LO must be at most 10000")

        primes = [candidate for candidate in range(low, high + 1) if is_prime(candidate)]
        output = f"primes from {low} to {high}: {len(primes)}\n"
        output += "".join(f"{prime}\n" for prime in primes)
        io.out(output)
        return 0

    number = values[0]
    if mode == "test":
        if is_prime(number):
            io.out(f"{number} is prime\n")
            return 0
        io.out(f"{number} is not prime\n")
        return 1

    if mode == "next":
        io.out(f"next prime after {number}: {next_prime(number)}\n")
        return 0

    previous = prev_prime(number)
    if previous is None:
        io.out(f"previous prime before {number}: none\n")
        return 1
    io.out(f"previous prime before {number}: {previous}\n")
    return 0
