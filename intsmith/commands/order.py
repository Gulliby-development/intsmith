"""The order command adapter.

Order and primitive-root computations inherit the upstream factorizer's
unbounded deterministic restart cost. Primitive-root search can scan candidates,
and this adapter's phi, order, and primitive-root calls may factor the modulus
repeatedly; these costs do not establish a universal timing bound.
"""

from math import gcd

from intsmith.core.ints import parse_int
from intsmith.core.options import parse
from intsmith.core.text import BIG, Failure, line
from intsmith.core.words import Io
from intsmith.nt.funcs import phi
from intsmith.nt.primes import factor
from intsmith.nt.units import multiplicative_order, smallest_primitive_root


def run(argv: list[str], io: Io) -> int:
    parsed = parse(argv, [])
    args = parsed.args

    if len(args) < 2:
        raise Failure(f"missing {'A' if len(args) == 0 else 'N'}")
    if len(args) > 2:
        raise Failure("too many arguments")

    operand = parse_int("A", args[0], -BIG, BIG)
    modulus = parse_int("N", args[1], 2, BIG)
    residue = operand % modulus
    totient = phi(factor(modulus))

    output = line("residue", str(residue)) + line("phi", str(totient))
    common_divisor = gcd(residue, modulus)
    if common_divisor != 1:
        output += line("status", f"not a unit (gcd {common_divisor})")
        io.out(output)
        return 1

    order = multiplicative_order(residue, modulus)
    primitive_root = smallest_primitive_root(modulus)
    output += line("order", str(order))
    output += line("smallest", str(primitive_root) if primitive_root is not None else "none")
    io.out(output)
    return 0
