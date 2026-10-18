from math import gcd

from intsmith.core.ints import parse_int
from intsmith.core.options import parse
from intsmith.core.text import BIG, Failure, line
from intsmith.core.words import Io
from intsmith.nt.dlog import discrete_log
from intsmith.nt.units import multiplicative_order


def run(argv: list[str], io: Io) -> int:
    parsed = parse(argv, [])
    args = parsed.args

    if len(args) < 3:
        missing = ("G", "H", "M")[len(args)]
        raise Failure(f"missing {missing}")
    if len(args) > 3:
        raise Failure("too many arguments")

    base_arg = parse_int("G", args[0], -BIG, BIG)
    target_arg = parse_int("H", args[1], -BIG, BIG)
    modulus = parse_int("M", args[2], 2, 10000000000)

    base = base_arg % modulus
    target = target_arg % modulus
    output = line("base", str(base)) + line("target", str(target))
    base_gcd = gcd(base, modulus)
    if base_gcd != 1:
        output += line("status", f"base is not a unit (gcd {base_gcd})")
        io.out(output)
        return 1

    order = multiplicative_order(base, modulus)
    output += line("order", str(order))
    solution = discrete_log(base, target, modulus)
    if solution is None:
        output += line("status", "no solution")
        io.out(output)
        return 1

    output += line("x", str(solution))
    io.out(output)
    return 0
