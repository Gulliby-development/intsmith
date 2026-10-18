import subprocess
import sys
from pathlib import Path

from intsmith.cli import USAGE, main


def test_invalid_utf8_on_real_stdin_reports_exact_bytes() -> None:
    repository_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "-m", "intsmith", "factor", "-"],
        cwd=repository_root,
        input=b"12\xff\n",
        capture_output=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 2
    assert result.stdout == b""
    assert result.stderr == b"intsmith: <stdin>: input is not valid UTF-8\n"


def test_readme_examples_match_cli() -> None:
    class FakeIo:
        def __init__(self) -> None:
            self.stdout: list[str] = []
            self.stderr: list[str] = []

        def read_stdin(self) -> bytes:
            return b""

        def out(self, text: str) -> None:
            self.stdout.append(text)

        def err(self, text: str) -> None:
            self.stderr.append(text)

    readme_path = Path(__file__).resolve().parents[1] / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    usage_section = readme.split("## Usage\n", 1)[1].split("\n## ", 1)[0]

    blocks: list[str] = []
    block_lines: list[str] = []
    in_block = False
    for line in usage_section.splitlines(keepends=True):
        marker = line.rstrip("\n")
        if marker == "```text" and not in_block:
            block_lines = []
            in_block = True
        elif marker == "```" and in_block:
            blocks.append("".join(block_lines))
            in_block = False
        elif in_block:
            block_lines.append(line)

    assert not in_block
    assert len(blocks) == 7
    assert blocks[0] == USAGE + "\n"

    expected_arguments = [
        ["gcd", "17", "3120"],
        ["crt", "2:3", "3:5", "2:7"],
        ["cfrac", "pell", "61"],
    ]
    for index, expected_argv in enumerate(expected_arguments):
        command_lines = blocks[1 + index * 2].splitlines()
        assert len(command_lines) == 1
        command_tokens = command_lines[0].split()
        assert command_tokens[:3] == ["python", "-m", "intsmith"]
        argv = command_tokens[3:]
        assert argv == expected_argv

        io = FakeIo()
        assert main(argv, io) == 0
        assert io.stdout == [blocks[2 + index * 2]]
        assert io.stderr == []

    help_io = FakeIo()
    assert main(["--help"], help_io) == 0
    assert help_io.stdout == [USAGE + "\n"]
    assert help_io.stderr == []
