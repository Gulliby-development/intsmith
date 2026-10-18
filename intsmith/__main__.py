import sys

from intsmith.cli import main


class _RealIo:
    def read_stdin(self) -> bytes:
        return sys.stdin.buffer.read()

    def out(self, text: str) -> None:
        sys.stdout.buffer.write(text.encode("utf-8"))
        sys.stdout.buffer.flush()

    def err(self, text: str) -> None:
        sys.stderr.buffer.write(text.encode("utf-8"))
        sys.stderr.buffer.flush()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:], _RealIo()))
