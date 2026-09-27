"""Toyota support-plugin selection: CDbDllTable::GetQuery role/category fallback plus family/mode dispatch shared by the registry and bundle builders."""

from __future__ import annotations

from typing import Any


def support_plugin(rows: list[Any], category_id: int, role: int) -> dict[str, Any] | None:
    """Apply current CDbDllTable::GetQuery role/category fallback exactly."""
    role_rows = [row for row in rows if int(row.dll_role_id) == role]
    if not role_rows:
        return None
    selected = next((row for row in role_rows if int(row.category_id) == category_id), role_rows[0])
    return {
        "role": role,
        "requested_category_id": category_id,
        "binding_category_id": int(selected.category_id),
        "exact_category_binding": int(selected.category_id) == category_id,
        "dll": selected.dll_name,
    }


def support_family(single: dict[str, Any] | None, multi: dict[str, Any] | None) -> str | None:
    """Name the family Toyota's selected support plugin actually implements."""
    for selected in (multi, single):
        dll = str(selected.get("dll") or "") if selected is not None else ""
        for family in ("P6", "P5", "P4", "P3"):
            if family in dll:
                return family.casefold()
    return None


def support_mode(category_id: int, generation: int, family: str | None) -> str | None:
    """Mirror the family-local dispatch performed by Toyota's support-list builders.

    `GetSupportP5_DT.dll` is not itself one bitmap protocol. CommandCommon further
    dispatches current P5 categories by generation mode and three Hino ECU IDs.
    Export that distinction so consumers never turn a shared DLL name into a local
    permission/compatibility assumption.
    """
    if family == "p6":
        return "p6-standard"
    if family != "p5":
        return family
    low5 = generation & 0x1F
    high3 = generation & 0xE0
    if low5 == 0x15:
        return "p5-mazda"
    if high3 == 0x60:
        return "p5-suzuki"
    if category_id in {0x13A9, 0x13B9, 0x13BA}:
        return "p5-hino"
    if high3 == 0x20:
        return "p5-subaru"
    return "p5-standard"
