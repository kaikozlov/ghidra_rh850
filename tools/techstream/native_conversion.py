"""Native CommandDataLib scalar conversion (2026 CComDataConvert::GetValue).

Kgp ROB metadata is consumed by CommandDataLib.dll 0x10022AC0. Integer
operations below reproduce its u32 input, sign modes, signed i64 product,
truncating division, and wrapped i32 return.
"""
from __future__ import annotations


def signed32(value: int) -> int:
    value &= 0xFFFFFFFF
    return value - 0x100000000 if value & 0x80000000 else value


def convert_scalar(value: int, width: int, mul: int, div: int, offset: int, sign_mode: int) -> int:
    """Apply the host conversion, including x86 masking of the sign-bit shift."""
    value &= 0xFFFFFFFF
    sign_bit = (width - 1) & 31
    if sign_mode == 1 and value & (1 << sign_bit):
        value = signed32(value | ((0xFFFFFFFF << sign_bit) & 0xFFFFFFFF))
    elif sign_mode == 3 and value & (1 << sign_bit):
        value = -(value & ((1 << sign_bit) - 1))
    product = value * signed32(mul)
    # Native __allmul retains its low 64 bits.
    product &= 0xFFFFFFFFFFFFFFFF
    if product & (1 << 63):
        product -= 1 << 64
    divisor = signed32(div)
    if (divisor & 0xFFFFFFFF) >= 2:
        quotient = abs(product) // abs(divisor)
        product = -quotient if (product < 0) != (divisor < 0) else quotient
    return signed32(product + signed32(offset))
