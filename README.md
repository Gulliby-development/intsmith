<p align="center"><img src="docs/logo.svg" width="96" alt="" /></p>

# intsmith

intsmith is an exact, offline number-theory calculator for students, puzzle solvers, contest solvers, and anyone who wants reliable integer results without a computer algebra system. It provides nine commands for common number-theory calculations, using Python's exact integer arithmetic and no runtime dependencies.

[![CI](https://github.com/Gulliby-development/intsmith/actions/workflows/ci.yml/badge.svg)](https://github.com/Gulliby-development/intsmith/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Install

intsmith requires Python 3.11 or newer. Clone the repository and run commands from its root; there is nothing to install and no runtime dependencies. Run a command with:

```text
python -m intsmith COMMAND
```

Replace `COMMAND` with one of the command forms below.

## Usage

```text
usage: intsmith gcd A B
       intsmith crt R:M...
       intsmith prime test|next|prev N
       intsmith prime list LO HI
       intsmith factor N...
       intsmith funcs [--divisors] N
       intsmith order A N
       intsmith sqrt A P
       intsmith dlog G H M
       intsmith cfrac frac P Q
       intsmith cfrac sqrt [--terms T] D
       intsmith cfrac pell D
```

For example, run `python -m intsmith gcd 17 3120` from the repository root:

```text
python -m intsmith gcd 17 3120
```

```text
gcd       1
lcm       53040
bezout    x=2753 y=-15
inverse   2753
```

The Chinese remainder theorem example is `python -m intsmith crt 2:3 3:5 2:7`:

```text
python -m intsmith crt 2:3 3:5 2:7
```

```text
crt       3 congruences
x         23 (mod 105)
```

The Pell equation example is `python -m intsmith cfrac pell 61`:

```text
python -m intsmith cfrac pell 61
```

```text
equation  x^2 - 61*y^2 = 1
x         1766319049
y         226153980
minus1    29718 3805
```

## Commands

- `gcd A B` reports the greatest common divisor, least common multiple, a Bezout pair, and an inverse when one exists.
- `crt R:M...` solves a system of one or more congruences, or reports that the system has no solution.
- `prime test|next|prev N` tests primality or finds the next or previous prime; `prime list LO HI` lists primes in an inclusive range.
- `factor N...` prints prime factorizations for one or more positive integers. Use `-` as the only number argument to read whitespace-separated numbers from standard input.
- `funcs [--divisors] N` reports arithmetic functions and number classifications; `--divisors` also lists the divisors.
- `order A N` reports the multiplicative order of a unit modulo N, along with the smallest primitive root when one exists.
- `sqrt A P` reports the Legendre symbol and square roots of `A` modulo the prime P, or indicates that there is no root.
- `dlog G H M` finds the smallest discrete logarithm of `H` to base `G` modulo M, when one exists.
- `cfrac frac P Q`, `cfrac sqrt [--terms T] D`, and `cfrac pell D` compute a rational continued fraction and convergents, terms of a square-root continued fraction, or Pell equation solutions.

## Exit codes

- `0`: the command succeeded.
- `1`: the calculation has a negative answer, such as a composite primality test or a congruence system with no solution.
- `2`: invalid input or another command diagnostic. The message is written to standard error, and standard output is empty.

## Development

The tests and lint checks need `pytest` and `ruff` (`python -m pip install pytest ruff`). Run them from the repository root:

```text
pytest -q
ruff check .
ruff format --check .
```

## License

MIT, see [LICENSE](LICENSE).

---

Built with BAKED
