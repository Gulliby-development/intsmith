from intsmith.core.ints import parse_int
from intsmith.core.options import parse
from intsmith.core.text import BIG, Failure, line
from intsmith.core.words import Io
from intsmith.nt.primes import is_prime
from intsmith.nt.residues import legendre, sqrt_mod_prime


def run(argv: list[str], io: Io) -> int:
    parsed = parse(argv, [])
    args = parsed.args

    if len(args) < 2:
        raise Failure(f"missing {'A' if len(args) == 0 else 'P'}")
    if len(args) > 2:
        raise Failure("too many arguments")

    operand = parse_int("A", args[0], -BIG, BIG)
    modulus = parse_int("P", args[1], 2, BIG)
    if not is_prime(modulus):
        raise Failure(f"modulus {modulus} is not prime")

    residue = operand % modulus
    symbol = legendre(residue, modulus)
    roots = sqrt_mod_prime(residue, modulus)

    output = line("residue", str(residue)) + line("symbol", str(symbol))
    if roots:
        output += line("roots", " ".join(str(root) for root in roots))
        io.out(output)
        return 0

    output += line("status", "no square root")
    io.out(output)
    return 1
