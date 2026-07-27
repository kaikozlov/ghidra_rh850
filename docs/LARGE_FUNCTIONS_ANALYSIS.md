# Large unnamed functions — cross-reference index

The 24 largest functions (≥1024 bytes) that were initially `FUN_*` have been
fully classified via decompilation, call-graph tracing, and structural
verification. Their findings are documented in their respective domain docs:

## Boot / reset
- `boot_reset_startup` (`0x1F2`) — `FIRMWARE_ARCHITECTURE.md` §2
- `boot_shutdown_reset_path` (`0x7059E`) — `FIRMWARE_ARCHITECTURE.md` §7
- `eps_subsystem_init_orchestrator` (`0xBD10E`) — `FIRMWARE_ARCHITECTURE.md` §3.2
- `application_ram_default_init` (`0x57BFE`) — `APPLICATION_RECEIVE_MAP.md` §5.2
- `application_peripheral_init` (`0x61DD4`) — `FIRMWARE_ARCHITECTURE.md` §8

## Application AES primitives
- `app_aes128_ecb_decrypt_block` (`0x853EE`) — `APPLICATION_SECURITY_ACCESS.md` §2
- `app_aes128_encrypt_round` (`0x8496C`) — `APPLICATION_SECURITY_ACCESS.md` §2

## Generated AUTOSAR Os/RTE/COM
- `autosar_os_task_signal_dispatch` (`0x58404`, 12.9 KiB) — `FIRMWARE_ARCHITECTURE.md` §3.2
- `autosar_com_rx_dispatch_group_a` (`0x5DB6E`) — `FIRMWARE_ARCHITECTURE.md` §3.2
- `autosar_com_rx_dispatch_group_b` (`0x5D3CE`) — `FIRMWARE_ARCHITECTURE.md` §3.2
- COM signal deadline monitors (`0x69824`, `0x6AD24`, `0x69DEC`, `0x6A28A`) — `APPLICATION_RECEIVE_MAP.md` §7
- RTE input staging copies (`0x5C666`, `0x5C0B6`, `0x5B9C4`) — `APPLICATION_RECEIVE_MAP.md` §8

## Hand-written OEM motor control
- Calibration-change handlers (`0x47C3C`, `0x32B80`, `0xB98BC`) — `APPLICATION_RECEIVE_MAP.md` §9

## System mode coordination
- `system_mode_per_tick_dispatcher` (`0xBEC4C`) — `SYSTEM_MODE_CLUSTER_ANALYSIS.md`
- `system_mode_telemetry_snapshot` (`0xBA43A`) — `SYSTEM_MODE_CLUSTER_ANALYSIS.md`
- `application_substate_machine` (`0xCBCC8`) — `SYSTEM_MODE_CLUSTER_ANALYSIS.md`

## Hardware
- `hardware_register_access_helper` (`0x48312`) — `APPLICATION_RECEIVE_MAP.md` §10

Annotation script: `ghidra/scripts/annotate/AnnotateLargeFunctions.java`
