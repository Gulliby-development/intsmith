from intsmith.core.ints import parse_int
from intsmith.core.options import parse
from intsmith.core.text import BIG, Failure, line
from intsmith.core.words import Io
from intsmith.nt.gcd import egcd, inverse, lcm


def run(argv: list[str], io: Io) -> int:
    parsed = parse(argv, [])
    if len(parsed.args) < 2:
        if not parsed.args:
            raise Failure("missing A")
        raise Failure("missing B")
    if len(parsed.args) > 2:
        raise Failure("too many arguments")

    a = parse_int("A", parsed.args[0], -BIG, BIG)
    b = parse_int("B", parsed.args[1], -BIG, BIG)
    gcd_value, x, y = egcd(a, b)
    inverse_value = inverse(a, b)
    output = "".join(
        (
            line("gcd", str(gcd_value)),
            line("lcm", str(lcm(a, b))),
            line("bezout", f"x={x} y={y}"),
            line("inverse", str(inverse_value) if inverse_value is not None else "none"),
        )
    )
    io.out(output)
    return 0
