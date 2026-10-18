from math import gcd, isqrt

from intsmith.core.ints import parse_int
from intsmith.core.options import integer, parse
from intsmith.core.text import BIG, Failure, join_or, line, show
from intsmith.core.words import Io
from intsmith.nt.cfrac import convergents, frac_terms, pell, sqrt_period, sqrt_terms


def run(argv: list[str], io: Io) -> int:
    if not argv:
        raise Failure("missing mode (frac, sqrt or pell)")

    mode = argv[0]
    if mode not in ("frac", "sqrt", "pell"):
        raise Failure(f"unknown mode {show(mode)} (expected {join_or(['frac', 'sqrt', 'pell'])})")

    if mode == "sqrt":
        parsed = parse(argv[1:], [integer("--terms", 1, 200, 12)])
        args = parsed.args
        if len(args) < 1:
            raise Failure("missing D")
        if len(args) > 1:
            raise Failure("too many arguments")

        d = parse_int("D", args[0], 1, 100000000)
        root = isqrt(d)
        if root * root == d:
            terms = [root]
            period = 0
        else:
            terms = sqrt_terms(d, parsed.values["--terms"])
            period = sqrt_period(d)

        output = (
            line("value", f"sqrt({d})")
            + line("terms", " ".join(str(term) for term in terms))
            + line("period", str(period))
        )
        io.out(output)
        return 0

    parsed = parse(argv[1:], [])
    args = parsed.args

    if mode == "frac":
        if len(args) < 2:
            missing = ("P", "Q")[len(args)]
            raise Failure(f"missing {missing}")
        if len(args) > 2:
            raise Failure("too many arguments")

        numerator = parse_int("P", args[0], -BIG, BIG)
        denominator = parse_int("Q", args[1], -BIG, BIG)
        if denominator == 0:
            raise Failure("Q must not be 0")

        common = gcd(numerator, denominator)
        numerator //= common
        denominator //= common
        if denominator < 0:
            numerator = -numerator
            denominator = -denominator

        terms = frac_terms(numerator, denominator)
        prefixes = convergents(terms)
        output = (
            line("fraction", f"{numerator}/{denominator}")
            + line("terms", " ".join(str(term) for term in terms))
            + line("conv", " ".join(f"{h}/{k}" for h, k in prefixes))
        )
        io.out(output)
        return 0

    if len(args) < 1:
        raise Failure("missing D")
    if len(args) > 1:
        raise Failure("too many arguments")

    d = parse_int("D", args[0], 1, 10000)
    output = line("equation", f"x^2 - {d}*y^2 = 1")
    root = isqrt(d)
    if root * root == d:
        output += line("status", "no solution (D is a perfect square)")
        io.out(output)
        return 1

    x, y, negative = pell(d)
    output += line("x", str(x)) + line("y", str(y))
    minus_one = "none" if negative is None else f"{negative[0]} {negative[1]}"
    output += line("minus1", minus_one)
    io.out(output)
    return 0
