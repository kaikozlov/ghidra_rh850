#!/usr/bin/env python3
"""Check that firmware pointer-table slots stay four bytes wide on the host."""
from tools.targets.camry.decomp.conversion.rewrite_types import (
    _rewrite_firmware_pointer_table_aliases,
)
from tools.targets.camry.decomp.execution.host_rewrite import (
    _pointer_table_word_is_host_pointer,
)

SOURCE = """void subject(uint index, int offset)
{
  undefined **slot;
  undefined *value;

  slot = &PTR_DAT_000266e8 + index;
  value = *slot;
  if ((*slot)[offset] == 7) {
    return;
  }
}
"""

EXPECTED = """void subject(uint index, int offset)
{
  uint32_t *slot;
  undefined *value;

  slot = &PTR_DAT_000266e8 + index;
  value = ((undefined *)camry_host_ptr((uint32_t)(*slot)));
  if (((undefined *)camry_host_ptr((uint32_t)(*slot)))[offset] == 7) {
    return;
  }
}
"""

actual = _rewrite_firmware_pointer_table_aliases(SOURCE)
assert actual == EXPECTED, actual
assert _pointer_table_word_is_host_pointer(actual) == EXPECTED
print("PASS firmware pointer-table slots use uint32_t words")
