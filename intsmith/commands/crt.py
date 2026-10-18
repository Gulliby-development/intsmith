from intsmith.core.ints import parse_int
from intsmith.core.options import parse
from intsmith.core.text import BIG, Failure, line, plural, show
from intsmith.core.words import Io
from intsmith.nt.gcd import crt


def run(argv: list[str], io: Io) -> int:
    """Run the bounded CRT adapter (at most 12 congruences)."""
    parsed = parse(argv, [])
    words = parsed.args
    if not words:
        raise Failure("missing R:M")
    if len(words) > 12:
        raise Failure("too many congruences (at most 12)")

    items: list[tuple[int, int]] = []
    for word in words:
        if word.count(":") != 1:
            raise Failure(f"invalid congruence {show(word)} (expected R:M)")
        residue_text, modulus_text = word.split(":")
        residue = parse_int("R", residue_text, -BIG, BIG)
        modulus = parse_int("M", modulus_text, 1, BIG)
        items.append((residue, modulus))

    output = line("crt", plural(len(items), "congruence", "congruences"))
    solution = crt(items)
    if solution is None:
        output += line("status", "no solution")
        result = 1
    else:
        residue, modulus = solution
        output += line("x", f"{residue} (mod {modulus})")
        result = 0

    io.out(output)
    return result
