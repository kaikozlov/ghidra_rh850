# System Mode Cluster Analysis

Decompilation and state-transition map for the three-function cluster
`0xBA43A`, `0xBEC4C`, and `0xCBCC8`, their callers, and the
`system_mode_coordinator @ 0xB0518` that drives them.

## 1. Cluster topology

```
FUN_000fdd40 (thunk)
  └─ system_mode_transition_step  @ 0xBEC4C  (full path, 1330B)
       ├─ application_input_snapshot_update          (tail, every step)
       ├─ application_system_transition_phase_step   @ 0xB2912 (phase byte 0/0x11/0x22)
       ├─ system_mode_coordinator                    @ 0xB0518 (event → next mode)
       │     ├─ system_mode_event_set                @ 0xB02BC (event-bit set, 50 slots)
       │     ├─ FUN_000b03cc(event)                  @ 0xB03CC (event-bit consume test)
       │     ├─ FUN_000b0404(next_mode)              @ 0xB0404 (mode switch + entry callbacks)
       │     │     ├─ PTR_LAB_000aeb04[old_mode>>8]  (exit callback)
       │     │     ├─ system_mode_transition_callbacks[new_mode>>8] (entry callback)
       │     │     └─ FUN_000b0330(mode)             @ 0xB0330 (store DAT_febeb11a = mode)
       │     ├─ FUN_000b0448(event)                  @ 0xB0448 (ack/consume event bit)
       │     └─ FUN_000b0974()                       @ 0xB0974 (read current mode)
       ├─ system_mode_state_worker                   @ 0xBA43A (telemetry snapshot, 2732B)
       └─ FUN_000b893e (if flag bit 0x10)
            └─ application_state_machine_worker      @ 0xCBCC8 (app-level substate, 1182B)

FUN_000fdd54 (thunk)
  └─ FUN_000bf17e                                 @ 0xBF17E (fast path, 2696B)
       ├─ [same callee set as 0xBEC4C but skips first-entry init blocks]
       ├─ system_mode_state_worker                @ 0xBA43A  (shared)
       └─ system_mode_coordinator                 @ 0xB0518  (shared)
```

### Role of each function

| Function | Size | Role |
|---|---|---|
| **`system_mode_transition_step @ 0xBEC4C`** | 1330B | **Full transition dispatcher.** Takes `(flags, new_mode, old_mode)`. For each subsystem band it runs init calls on first-entry (`old_mode < band`) and steady-state calls otherwise; the `flags & 2` arm runs extra setup. Ends every step by calling `application_input_snapshot_update`, `application_system_transition_phase_step`, and `system_mode_coordinator`. |
| **`FUN_000bf17e @ 0xBF17E`** | 2696B | **Fast/steady-state variant** of the dispatcher. Identical gate structure and callee set but omits the first-entry init sequences (the `old_mode < boundary` branches). It is the "already in-band" path; `0xBEC4C` is the "entering band" path. Both converge on the same `system_mode_state_worker` + `system_mode_coordinator` tail. |
| **`system_mode_state_worker @ 0xBA43A`** | 2732B | **Telemetry/status snapshot worker.** Reads ~200 status bytes/words from the live state block (`LAB_febeb800` + offsets) and copies them into the telemetry/report shadow block. Contains one mode-conditional: when the current mode word `== 0x400` and a watchdog tick (`thunk_FUN_00049404(0x1b) != 0x5A`) is not set, it derives a flag. Otherwise it is a pure field-copy — it does **not** decide transitions. |
| **`application_state_machine_worker @ 0xCBCC8`** | 1182B | **Generic application substate machine.** Operates on a callback table (`param_3` = `PTR_LAB_000aecb8`), running phase callbacks indexed by transition-kind codes `0x11`, `0x22`, `0x33`, `0x44` and steady codes `0x1100`, `0x2200`. This is a reusable two-axis (request-count vs. threshold) state machine used for application-level sequencing outside the motor domain; it is reached only when the dispatcher flag bit `0x10` is set. |
| **`system_mode_coordinator @ 0xB0518`** | 7173B | **The actual mode state machine.** Reads current mode (`DAT_febeb11a & 0xFF00`), tests event bits via `FUN_000b03cc(event)`, and calls `FUN_000b0404(next_mode)` to switch. This is where event 9 → mode 0x900 lives. |

## 2. Modes and their transition rules

The coordinator (`0xB0518`) reads the current mode from `DAT_febeb11a` (masked
`& 0xFF00`) and dispatches on it. Modes and the events that drive transitions:

| Mode | Name (inferred) | Exit events checked (in priority order) |
|---|---|---|
| `0x100` | INIT / startup | event 0 → `0x700`; **event 9 → `0x900`**; event 5 → `0x200` |
| `0x200` | pre-OPERATIONAL | events 0/1 → `0x700`; **event 9 → `0x900`**; event 3 → `0x300` |
| `0x300` | OPERATIONAL (base) | events 0/1 → `0x700`; **event 9 → `0x900`**; event 6 → `0x500`; event 0xC → `0x400` |
| `0x400` | OPERATIONAL (alt / degraded) | events 0/1 → `0x700`; **event 9 → `0x900`**; event 6 → `0x500`; event 0xB → `0x700`; event 7 → `0x600` |
| `0x500` | OPERATIONAL (high) | events 0/1 → `0x700`; **event 9 → `0x900`**; event 4 → `0x300` (or `0x400` if flag set); event 7 → `0x600` |
| `0x600` | transitional | event 0 → `0x700`; **event 9 / 0xD → `0x900`**; events 8/1 → `0x700` |
| `0x700` | pre-shutdown | event 0 → `0x800`; **event 9 → `0x900`**; event 2 → (NvM commit, then `0x800`); events 10/7 → `0x800`/`0x600` |
| `0x800` | shutdown sequencing | event 0xF → final reset (`FUN_000ff0d8`); **event 9 → `0x900`**; event 2 → NvM commit; event 7 → `0x600` |
| `0x900` | PROGRAMMING shutdown | event 0xE → `0x800` (advance to reset) |

### Key observations

1. **Event 9 is checked in every operational mode (0x100–0x800)** and always targets
   `0x900`. This is the universal "PROGRAMMING handoff / shutdown" trigger.

2. **Mode 0x900's entry callback** is `system_programming_shutdown_mode_entry @ 0xB20EA`,
   which writes paired subsystem shutdown requests `0x70017001` (both subsystems)
   and `0x00020002` (both subsystems, two command slots). This matches
   APPLICATION_DIAGNOSTICS.md §"Reset/shutdown behavior" (lines 708–713).

3. **From 0x900 the only exit is event 0xE → 0x800**, which then performs the
   final reset sequencing (`FUN_000ff0d8` → hardware disable → reset/watchdog
   registers → infinite loop at `0x608AA`).

4. **Modes 0x300/0x400/0x500 form the normal operational triad.** The
   `application_system_transition_phase_step @ 0xB2912` advances a phase byte
   (`0` → `0x11` → `0x22`) around these modes and fires `system_mode_event_set(0x23)`
   when transitioning out of `0x300` — event 0x23 is a separate application-level
   signal, distinct from event 9.

## 3. Relationship to the PROGRAMMING handoff

The PROGRAMMING handoff path (APPLICATION_DIAGNOSTICS.md §3, lines 699–726):

```
application_programming_reset_request @ 0x4C98C
  └─ (if GP-0x36AE clear and one-shot marker clear)
       └─ system_mode_event_set @ 0xB02BC  with event 9
            └─ sets bit 9 in the 50-slot event array @ DAT_febeb098
```

Once event 9 is queued:

1. The next scheduler tick calls `system_mode_transition_step @ 0xBEC4C`
   (or its fast-path twin `FUN_000bf17e @ 0xBF17E`).
2. The dispatcher tail calls `system_mode_coordinator @ 0xB0518`.
3. The coordinator reads the current mode; regardless of which operational mode
   is active (0x100–0x800), `FUN_000b03cc(9)` returns 1 and the coordinator
   calls `FUN_000b0404(0x900)`.
4. `FUN_000b0404` runs the **exit callback** for the current mode
   (`PTR_LAB_000aeb04[old_mode>>8]`), then the **entry callback** for `0x900`
   (`system_mode_transition_callbacks[9]` = `0xB20EA`), then stores
   `DAT_febeb11a = 0x900`.
5. The entry callback `0xB20EA` writes the shutdown request words.
6. On the next tick, the coordinator (now in mode 0x900) waits for event 0xE,
   then advances to `0x800` for final reset.

This confirms the documented behavior: queuing event 9 is **sufficient** to
drive any operational mode into shutdown (`0x900`) and then reset (`0x800`).
The UDS response remains pending (NRC `0x78`) because `0x8A244` latches
`FEBF3B19 = 0x5A` and returns internal value 10 (pending) — the reset overtakes
the response.

## 4. The two dispatcher variants (0xBEC4C vs 0xBF17E)

| Aspect | `0xBEC4C` (full) | `0xBF17E` (fast) |
|---|---|---|
| Called by | `FUN_000fdd40` | `FUN_000fdd54` |
| Params | `(flags, new_mode, old_mode)` | `(flags, new_mode)` — uses live mode as old |
| First-entry init blocks | **Yes** — runs init calls when `old_mode < band` | **No** — skips them |
| `param_1 & 2` extra setup | Yes | Yes |
| `system_mode_state_worker` | Yes (mode ≥ 0x300 band) | Yes (mode ≥ 0x300 band) |
| `system_mode_coordinator` | Yes | Yes |
| `application_state_machine_worker` (via `0xB893E`) | Yes (flag `0x10`) | Yes (flag `0x10`) |
| `application_system_transition_phase_step` | Yes | Yes |

`0xBF17E` is the steady-state scheduler tick; `0xBEC4C` is invoked when a mode
transition has just been committed (it knows both old and new mode and can run
the band-entry init sequences). Both share the same coordinator and state worker.

## 5. `application_state_machine_worker @ 0xCBCC8` detail

This is a **table-driven, two-axis state machine** reused for application
sequencing. Its callback table (`param_3`) has 13 slots (indices 0–0xC):

- Slots 0–5: phase-check functions (called to get a transition-kind code).
- Slots 6, 8: pre-transition cleanup callbacks.
- Slots 7, 9, 0xA: band-specific callbacks.
- Slots 0xB, 0xC: completion callbacks.

Transition-kind codes returned by the phase checks:
- `0x11` — threshold met, advance.
- `0x22` — count-based advance.
- `0x33` / `0x44` — reset to idle.
- Default → `0xFFFF` (no-op).

The worker maintains a request counter (`param_1[1]`), a completion counter
(`param_1[6]`), and a high-water mark (`param_1[2]`), comparing against a
threshold pair in `param_2`. It is instantiated once (via `0xB893E` with table
`PTR_LAB_000aecb8`) and is **independent of the system-mode coordinator's
0x100–0x900 mode enum** — it handles application-internal substates gated by
the dispatcher flag bit `0x10`.

## 6. Summary

- **`0xBEC4C`** and **`0xBF17E`** are the two scheduler dispatchers (full and
  fast-path) that run per-tick subsystem update sequences and then invoke the
  coordinator. They are the wiring, not the decision logic.
- **`0xB0518`** (system_mode_coordinator) is the actual mode state machine
  containing all transition rules. Event 9 → 0x900 is checked from every mode.
- **`0xBA43A`** (system_mode_state_worker) is a telemetry/snapshot copier with
  one mode-0x400 conditional; it does not decide transitions.
- **`0xCBCC8`** (application_state_machine_worker) is a reusable substate
  machine for application-level sequencing, independent of the system-mode enum.
- The PROGRAMMING handoff queues event 9 via `0xB02BC`; the coordinator then
  drives the mode to `0x900` (entry callback `0xB20EA` writes shutdown requests)
  and onward to `0x800` (reset). This matches APPLICATION_DIAGNOSTICS.md §3.
