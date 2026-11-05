"""Shared role/plugin operation model for Toyota Techstream/GTS diagnostics.

The classification covers *recovered shared-runtime edges*. A plugin may invoke
transport directly, delegate support discovery to CommandCommon, or use a path
that has not yet been recovered.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pefile
from tools.techstream.pe_utils import imports as pe_imports
from tools.techstream.ddb_semantics import NativeSelectionContext, native_context
from tools.techstream.gts.execution_model import _resolve_plugin_path


# CommandCommon primitives that directly materialize or execute communication
# frames in the plugin itself.
DIRECT_TRANSPORT_MARKERS = (
    "GetCommFrmInfo@",
    "GetCommFrmSndRcv",
    "CommFrameSendReceive",
    "CommCacheSndRcv",
    "CommCacheEverSndRcv",
    "DeleteCommCacheSndRcv",
)

# These labels describe V18 executable proof for stable imported API names.
# Current recovered CommandCommon bytes are available, but import-name matching
# alone does not establish their current implementation's transport behavior.
V18_PROVEN_DELEGATED_TRANSPORT_MARKERS = (
    "?CheckSupportPid@CCommCachePlusP5@@",
    "?CheckSupportDid@CCommCachePlusP5@@",
    "?CheckSupportBit@CCommCachePlusP5@@",
    "?CheckSupportItemValue@CCommCachePlusP5@@",
    "?CreateEnableDataIdList@CCmdSupportDataIdList@@",
    "?CreateEnableRIdList@CCmdSupportDataIdList@@",
    "?CheckSupportPid@CCommCachePlus@@",
    "?CheckSupportDid@CCommCachePlus@@",
    "?CheckSupportFrzPid@CCommCachePlus@@",
)

V18_PROVEN_SUPPORT_CACHE_MARKERS = (
    "?CheckSupportBitP4@CCmdSupportEcu@@",
    "?DidCheckSupportBitP4@CCmdSupportEcu@@",
    "?CheckSupportBit@CCmdSupportEcu@@",
)

SUPPORT_ORCHESTRATION_MARKERS = (
    "CheckSupport",
    "CreateEnableDataIdList",
    "CreateEnableRIdList",
    "GetCommSupportBit",
    "GetSupportPid",
    "GetSupportRid",
)


def _matches(name: str, markers: tuple[str, ...]) -> bool:
    return any(marker in name for marker in markers)


def plugin_operation_signature(path: Path) -> dict[str, Any]:
    pe = pefile.PE(str(path), fast_load=True)
    pe.parse_data_directories(
        directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]]
    )
    rows = pe_imports(pe)
    command_common = [row["name"] for row in rows if row["dll"].lower() == "commandcommon.dll"]
    direct = sorted({name for name in command_common if _matches(name, DIRECT_TRANSPORT_MARKERS)})
    delegated = sorted({
        name for name in command_common
        if _matches(name, V18_PROVEN_DELEGATED_TRANSPORT_MARKERS)
    })
    support = sorted({
        name for name in command_common
        if _matches(name, SUPPORT_ORCHESTRATION_MARKERS)
    })
    cache_only = sorted({
        name for name in command_common
        if _matches(name, V18_PROVEN_SUPPORT_CACHE_MARKERS)
    })
    direct_frame_ctrl = sorted({
        row["name"] for row in rows
        if row["dll"].lower() == "kgp_commframectrl.dll"
        and any(token in row["name"] for token in ("Send", "Receive"))
    })
    if direct or direct_frame_ctrl:
        surface = "direct_transport"
    elif delegated:
        surface = "delegated_transport_v18_proven"
    elif cache_only:
        surface = "support_cache_v18_proven"
    elif support:
        surface = "support_orchestration_unclosed"
    else:
        surface = "no_recovered_shared_transport_edge"
    return {
        "surface": surface,
        "direct_transport_imports": direct,
        "direct_frame_ctrl_imports": direct_frame_ctrl,
        "delegated_transport_imports_v18_proven": delegated,
        "support_cache_imports_v18_proven": cache_only,
        "support_orchestration_imports": support,
    }


def role_operation_catalog(parser: Any, master: Any, bin_root: Path) -> dict[str, Any]:
    context = (
        native_context(master)
        if isinstance(master, NativeSelectionContext) or master.schema_family in ("gtsplus", "ds4")
        else None
    )
    by_role: dict[int, list[Any]] = {}
    entries = context.raw_records(19) if context is not None else parser.extract_master_dlls(master.sections[19])
    for entry in entries:
        by_role.setdefault(entry.dll_role_id, []).append(entry)

    signature_cache: dict[str, dict[str, Any]] = {}
    roles: list[dict[str, Any]] = []
    global_plugin_surfaces: dict[str, int] = {}
    global_binding_surfaces: dict[str, int] = {}

    for role, entries in by_role.items():
        counts: dict[str, int] = {}
        for entry in entries:
            counts[entry.dll_name] = counts.get(entry.dll_name, 0) + 1
        plugins = []
        role_plugin_surfaces: dict[str, int] = {}
        role_binding_surfaces: dict[str, int] = {}
        for dll, binding_count in sorted(counts.items(), key=lambda item: (-item[1], item[0].casefold())):
            if dll not in signature_cache:
                path = _resolve_plugin_path(bin_root, dll)
                if not path.is_file():
                    signature_cache[dll] = {
                        "surface": "plugin_file_missing",
                        "direct_transport_imports": [],
                        "direct_frame_ctrl_imports": [],
                        "delegated_transport_imports_v18_proven": [],
                        "support_cache_imports_v18_proven": [],
                        "support_orchestration_imports": [],
                    }
                else:
                    try:
                        signature_cache[dll] = plugin_operation_signature(path)
                    except pefile.PEFormatError:
                        signature_cache[dll] = {
                            "surface": "plugin_pe_unparseable",
                            "direct_transport_imports": [],
                            "direct_frame_ctrl_imports": [],
                            "delegated_transport_imports_v18_proven": [],
                            "support_orchestration_imports": [],
                        }
            signature = signature_cache[dll]
            surface = signature["surface"]
            role_plugin_surfaces[surface] = role_plugin_surfaces.get(surface, 0) + 1
            role_binding_surfaces[surface] = role_binding_surfaces.get(surface, 0) + binding_count
            global_plugin_surfaces[surface] = global_plugin_surfaces.get(surface, 0) + 1
            global_binding_surfaces[surface] = global_binding_surfaces.get(surface, 0) + binding_count
            plugins.append({"dll": dll, "binding_count": binding_count, "surface": surface})
        roles.append({
            "role": role,
            "role_hex": f"0x{role:X}",
            "binding_count": len(entries),
            "category_count": len({entry.category_id for entry in entries}),
            "plugin_count": len(plugins),
            "plugin_surface_counts": dict(sorted(role_plugin_surfaces.items())),
            "binding_surface_counts": dict(sorted(role_binding_surfaces.items())),
            "plugins": plugins,
        })
        if context is not None:
            roles[-1]["native_default"] = context.query(19, role, 0x10000).as_dict()

    roles.sort(key=lambda row: (-row["binding_count"], row["role"]))
    return {
        "scope": "shared-runtime edges recovered from plugin imports",
        "catalog": "raw-occurrences",
        "native_context": context.as_dict() if context is not None else None,
        "binding_count": sum(row["binding_count"] for row in roles),
        "role_count": len(roles),
        "unique_plugin_count": len(signature_cache),
        "plugin_surface_counts": dict(sorted(global_plugin_surfaces.items())),
        "binding_surface_counts": dict(sorted(global_binding_surfaces.items())),
        "roles": roles,
    }
