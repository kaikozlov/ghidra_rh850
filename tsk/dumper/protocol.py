#!/usr/bin/env python3
"""Wire protocol for the conservative addressed-word CodeFlash dumper."""

from __future__ import annotations

import struct
from dataclasses import dataclass
from enum import Enum

PROTOCOL_VERSION = 1
CODEFLASH_BASE = 0x00000000
CODEFLASH_SIZE = 0x00100000
WORD_SIZE = 4
WORD_COUNT = CODEFLASH_SIZE // WORD_SIZE

CONTROL_PREFIX = 0xD00D0000
CONTROL_MASK = 0xFFFF0000
CTRL_HELLO = CONTROL_PREFIX | 0x0001
CTRL_RANGE_START = CONTROL_PREFIX | 0x0002
CTRL_RANGE_LENGTH = CONTROL_PREFIX | 0x0003
CTRL_WORD_COUNT = CONTROL_PREFIX | 0x0004
CTRL_PROGRESS = CONTROL_PREFIX | 0x0010
CTRL_DONE = CONTROL_PREFIX | 0x00FF
CTRL_ERROR = CONTROL_PREFIX | 0x00EE


class FrameKind(str, Enum):
    DATA = "data"
    HELLO = "hello"
    RANGE_START = "range-start"
    RANGE_LENGTH = "range-length"
    WORD_COUNT = "word-count"
    PROGRESS = "progress"
    DONE = "done"
    ERROR = "error"
    UNKNOWN_CONTROL = "unknown-control"


@dataclass(frozen=True)
class DumpFrame:
    kind: FrameKind
    value: int
    data: int | None = None
    raw: bytes = b""


class DumpProtocolError(ValueError):
    pass

def _validate_range(start: int, length: int) -> None:
    if start < 0 or start > 0xFFFFFFFF or start & (WORD_SIZE - 1):
        raise DumpProtocolError("range start must be a word-aligned uint32")
    if length <= 0 or length & (WORD_SIZE - 1):
        raise DumpProtocolError("range length must be positive and word aligned")
    if start + length > 0x1_0000_0000:
        raise DumpProtocolError("range exceeds the uint32 address space")



def encode_words(word0: int, word1: int) -> bytes:
    if not 0 <= word0 <= 0xFFFFFFFF or not 0 <= word1 <= 0xFFFFFFFF:
        raise DumpProtocolError("frame words must fit uint32")
    return struct.pack("<II", word0, word1)


def encode_data(
    address: int,
    value: int,
    *,
    start: int = CODEFLASH_BASE,
    length: int = CODEFLASH_SIZE,
) -> bytes:
    _validate_range(start, length)
    if address & (WORD_SIZE - 1):
        raise DumpProtocolError("data address must be 4-byte aligned")
    if not start <= address <= start + length - WORD_SIZE:
        raise DumpProtocolError("data address is outside expected CodeFlash")
    return encode_words(address, value)


def encode_control(control: int, value: int) -> bytes:
    if (control & CONTROL_MASK) != CONTROL_PREFIX:
        raise DumpProtocolError("control word is outside dumper namespace")
    return encode_words(control, value)


def decode_frame(raw: bytes) -> DumpFrame:
    if len(raw) < 8:
        raise DumpProtocolError("dump frame must contain at least 8 bytes")
    frame = bytes(raw[:8])
    word0, word1 = struct.unpack("<II", frame)
    if (word0 & CONTROL_MASK) != CONTROL_PREFIX:
        return DumpFrame(FrameKind.DATA, word0, word1, frame)

    kind = {
        CTRL_HELLO: FrameKind.HELLO,
        CTRL_RANGE_START: FrameKind.RANGE_START,
        CTRL_RANGE_LENGTH: FrameKind.RANGE_LENGTH,
        CTRL_WORD_COUNT: FrameKind.WORD_COUNT,
        CTRL_PROGRESS: FrameKind.PROGRESS,
        CTRL_DONE: FrameKind.DONE,
        CTRL_ERROR: FrameKind.ERROR,
    }.get(word0, FrameKind.UNKNOWN_CONTROL)
    return DumpFrame(kind, word1, None, frame)


def startup_frames(
    *,
    start: int = CODEFLASH_BASE,
    length: int = CODEFLASH_SIZE,
) -> tuple[bytes, bytes, bytes, bytes]:
    _validate_range(start, length)
    return (
        encode_control(CTRL_HELLO, PROTOCOL_VERSION),
        encode_control(CTRL_RANGE_START, start),
        encode_control(CTRL_RANGE_LENGTH, length),
        encode_control(CTRL_WORD_COUNT, length // WORD_SIZE),
    )
