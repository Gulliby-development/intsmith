from dataclasses import dataclass

from intsmith.core.ints import parse_int
from intsmith.core.text import Failure, show


@dataclass(frozen=True)
class Spec:
    name: str
    flag: bool
    lo: int
    hi: int
    fallback: int


def flag(name: str) -> Spec:
    return Spec(name=name, flag=True, lo=0, hi=0, fallback=0)


def integer(name: str, lo: int, hi: int, fallback: int) -> Spec:
    return Spec(name=name, flag=False, lo=lo, hi=hi, fallback=fallback)


@dataclass
class Parsed:
    values: dict[str, int]
    args: list[str]


def parse(argv: list[str], specs: list[Spec]) -> Parsed:
    specs_by_name = {spec.name: spec for spec in specs}
    flag_values: set[str] = set()
    integer_texts: dict[str, str] = {}
    args: list[str] = []

    index = 0
    while index < len(argv):
        argument = argv[index]
        if not argument.startswith("--"):
            args.append(argument)
            index += 1
            continue

        if "=" in argument:
            name, value = argument.split("=", 1)
            has_value = True
        else:
            name = argument
            value = ""
            has_value = False

        spec = specs_by_name.get(name)
        if spec is None:
            raise Failure(f"unknown option {show(argument)}")

        if spec.flag:
            if has_value:
                raise Failure(f"{name} takes no value")
            flag_values.add(name)
        elif has_value:
            integer_texts[name] = value
        else:
            if index + 1 >= len(argv):
                raise Failure(f"{name} needs a value")
            index += 1
            integer_texts[name] = argv[index]

        index += 1

    values: dict[str, int] = {}
    for spec in specs:
        if spec.flag:
            values[spec.name] = int(spec.name in flag_values)
        elif spec.name in integer_texts:
            values[spec.name] = parse_int(spec.name, integer_texts[spec.name], spec.lo, spec.hi)
        else:
            values[spec.name] = spec.fallback

    return Parsed(values=values, args=args)
