from intsmith.commands.cfrac import run as run_cfrac
from intsmith.commands.crt import run as run_crt
from intsmith.commands.dlog import run as run_dlog
from intsmith.commands.factor import run as run_factor
from intsmith.commands.funcs import run as run_funcs
from intsmith.commands.gcd import run as run_gcd
from intsmith.commands.order import run as run_order
from intsmith.commands.prime import run as run_prime
from intsmith.commands.sqrt import run as run_sqrt
from intsmith.core.text import Failure, show
from intsmith.core.words import Io

USAGE = """usage: intsmith gcd A B
       intsmith crt R:M...
       intsmith prime test|next|prev N
       intsmith prime list [--count] LO HI
       intsmith factor N...
       intsmith funcs [--divisors] N
       intsmith order A N
       intsmith sqrt A P
       intsmith dlog G H M
       intsmith cfrac frac P Q
       intsmith cfrac sqrt [--terms T] D
       intsmith cfrac pell D"""

_COMMANDS = {
    "gcd": run_gcd,
    "crt": run_crt,
    "prime": run_prime,
    "factor": run_factor,
    "funcs": run_funcs,
    "order": run_order,
    "sqrt": run_sqrt,
    "dlog": run_dlog,
    "cfrac": run_cfrac,
}


def main(argv: list[str], io: Io) -> int:
    try:
        if argv == ["--help"]:
            io.out(USAGE + "\n")
            return 0
        if not argv:
            raise Failure(
                "missing command (gcd, crt, prime, factor, funcs, order, sqrt, dlog or cfrac)"
            )

        command = argv[0]
        run = _COMMANDS.get(command)
        if run is None:
            raise Failure(f"unknown command {show(command)}")
        return run(argv[1:], io)
    except Failure as failure:
        io.err(f"intsmith: {failure.message}\n")
        return 2
