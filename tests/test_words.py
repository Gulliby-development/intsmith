import pytest

from intsmith.core.text import Failure
from intsmith.core.words import Io, _decode_stdin, words_of


class FakeIo:
    def __init__(self, data: bytes = b"", error: OSError | None = None) -> None:
        self.data = data
        self.error = error
        self.read_calls = 0
        self.out_calls: list[str] = []
        self.err_calls: list[str] = []

    def read_stdin(self) -> bytes:
        self.read_calls += 1
        if self.error is not None:
            raise self.error
        return self.data

    def out(self, text: str) -> None:
        self.out_calls.append(text)

    def err(self, text: str) -> None:
        self.err_calls.append(text)


def assert_no_output(io: FakeIo) -> None:
    assert io.out_calls == []
    assert io.err_calls == []


def assert_words_failure(io: FakeIo, expected_message: str) -> None:
    with pytest.raises(Failure) as exc_info:
        words_of(io, ["-"])
    assert exc_info.value.message == expected_message
    assert io.read_calls == 1
    assert_no_output(io)


def assert_decoder_failure(data: bytes, expected_message: str) -> None:
    with pytest.raises(Failure) as exc_info:
        _decode_stdin(data)
    assert exc_info.value.message == expected_message


@pytest.mark.parametrize(
    ("args", "expected"),
    [
        ([], []),
        (["12"], ["12"]),
        (["-", "12"], ["-", "12"]),
        (["12", "-"], ["12", "-"]),
    ],
)
def test_non_stdin_args_are_returned_unchanged_without_io(
    args: list[str], expected: list[str]
) -> None:
    io = FakeIo(b"ignored")

    assert words_of(io, args) == expected
    assert io.read_calls == 0
    assert_no_output(io)


def test_stdin_words_skip_one_leading_bom_and_split_all_allowed_separators() -> None:
    io = FakeIo(b"\xef\xbb\xbf12\r\n 15\t7\n")

    assert words_of(io, ["-"]) == ["12", "15", "7"]
    assert io.read_calls == 1
    assert_no_output(io)


def test_stdin_words_drop_empty_parts_from_repeated_separators() -> None:
    io = FakeIo(b" \t\r\n12\t\t\r 15 \n")

    assert words_of(io, ["-"]) == ["12", "15"]
    assert io.read_calls == 1
    assert_no_output(io)


def test_stdin_words_remove_only_the_first_of_two_leading_boms() -> None:
    io = FakeIo(b"\xef\xbb\xbf\xef\xbb\xbf12")

    assert words_of(io, ["-"]) == ["\ufeff12"]
    assert io.read_calls == 1
    assert_no_output(io)


def test_stdin_words_preserve_a_bom_that_is_not_leading() -> None:
    io = FakeIo(b"12 \xef\xbb\xbf15")

    assert words_of(io, ["-"]) == ["12", "\ufeff15"]
    assert io.read_calls == 1
    assert_no_output(io)


def test_stdin_words_preserve_non_ascii_whitespace_nul_and_vertical_tab() -> None:
    io = FakeIo(b"12\xc2\xa015\x0016\v17")

    assert words_of(io, ["-"]) == ["12\u00a015\x0016\v17"]
    assert io.read_calls == 1
    assert_no_output(io)


@pytest.mark.parametrize(
    "data",
    [
        b"",
        b" \t\r\n",
        b"\xef\xbb\xbf",
    ],
)
def test_empty_stdin_words_raise_the_exact_no_input_failure(data: bytes) -> None:
    assert_words_failure(FakeIo(data), "<stdin>: no input")


def test_stdin_read_oserror_raises_the_exact_failure() -> None:
    io = FakeIo(error=OSError("read failed"))

    assert_words_failure(io, "<stdin>: cannot read the input")


@pytest.mark.parametrize(
    "data",
    [
        b"\xff",
        b"12\xff\n",
        b"\xc3(",
    ],
)
def test_private_decoder_rejects_each_malformed_utf8_sequence(data: bytes) -> None:
    assert_decoder_failure(data, "<stdin>: input is not valid UTF-8")


@pytest.mark.parametrize(
    "data",
    [
        b"\xff",
        b"12\xff\n",
        b"\xc3(",
    ],
)
def test_words_of_rejects_all_malformed_utf8_without_partial_output(data: bytes) -> None:
    assert_words_failure(FakeIo(data), "<stdin>: input is not valid UTF-8")


def test_io_protocol_declares_the_expected_methods() -> None:
    assert hasattr(Io, "read_stdin")
    assert hasattr(Io, "out")
    assert hasattr(Io, "err")
