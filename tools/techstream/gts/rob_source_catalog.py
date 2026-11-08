"""ROB source records independent of the selected live-monitor protocol.

Some P5-selected databases also contain modern ROB tables163/164. Their
presence, not the category's live-monitor support mode, controls projection.
The native layout and physical joins remain owned by p6_catalog.
"""
from types import SimpleNamespace
from typing import Any, Callable
from tools.techstream.gts.p6_catalog import p6_catalog


def rob_source_catalog(db: Any, strings: Any, source: str, *,
                       resolve_variable: Callable[[int], bytes]) -> dict[str, Any]:
    """Decode every163/164 source row without invoking unrelated monitor tables."""
    tables=(13,14,15,89,90,163,164)
    selected=SimpleNamespace(sections={t:db.sections[t] for t in tables if t in db.sections})
    return p6_catalog(selected,strings,source,resolve_variable=resolve_variable)["rob"]
