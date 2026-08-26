# RH850 EPS 探测报告 (RH850 EPS Probe Report)

## 元信息 (Metadata)
- timestamp: 2026-08-26T01:49:18Z
- addr: 0x7A1
- serial: None
- depth: shellcode
- app_f181: 023839363546313230383030300000000038413331313132303230303000000000
- boot_f181: 022121212121212121212121212121212121212121212121212121212121212121

## Layer 1 UDS 枚举 (UDS Enumeration)
- 会话 0x01: 0/0 SID 响应 (responded)
- 会话 0x03: 0/0 SID 响应 (responded)
- 会话 0x02: 0/0 SID 响应 (responded)
- DID: 1/7 读取成功 (read OK)
- 例程: 0/7 响应 (responded)
- RequestDownload: ram: nrc, flash: nrc

## 车辆指纹 (Vehicle Fingerprint)
- 指纹探测失败 (fingerprint failed): 'UdsClient' object has no attribute 'close'

## Layer 2 SecurityAccess
- SecurityAccess: 通过 (OK)
- 信封 0x10F0 鉴权 (envelope auth): 通过 (OK)

## Layer 3 深探 (Deep Probe)
- 信封 0x10F0 鉴权 (envelope auth): 通过 (OK)
- 流 CRC 校验 (stream CRC): 通过 (OK)
- egg 签名扫描 (egg scan): 启用 (enabled)
### 寄存器快照 (Register Snapshot)
| 寄存器名 (Register) | 地址 (Addr) | 宽度 (Width) | 值 (Value) |
|---|---|---|---|
| FPMON | 0xFFA10000 | 1 | 0x80 |
| FASTAT | 0xFFA10010 | 1 | 0x00 |
| FAREASELC | 0xFFA10020 | 2 | 0x0000 |
| FSADDR | 0xFFA10030 | 4 | 0x000061FC |
| FEADDR | 0xFFA10034 | 4 | 0x000061FC |
| FSTATR | 0xFFA10080 | 4 | 0x00008000 |
| FENTRYR | 0xFFA10084 | 2 | 0x0000 |
| FPROTR | 0xFFA10088 | 2 | 0x0000 |
| FSUINITR | 0xFFA10090 | 1 | 0x00 |
| FLKSTAT | 0xFFA10098 | 1 | 0x00 |
| FPCKAR | 0xFFA100E4 | 2 | 0x0028 |
| SELFID0 | 0xFFA08000 | 4 | 0xFFFFFFFF |
| SELFID1 | 0xFFA08004 | 4 | 0xFFFFFFFF |
| SELFID2 | 0xFFA08008 | 4 | 0xFFFFFFFF |
| SELFID3 | 0xFFA0800C | 4 | 0xFFFFFFFF |
| SELFIDST | 0xFFA08010 | 4 | 0x00000000 |
| FHVE15 | 0xFFF8A430 | 4 | 0x00000000 |
| FHVE3 | 0xFFF82410 | 4 | 0x00000000 |
| DCRA1CIN | 0xFFD51000 | 4 | 0x6DAAE993 |
| DCRA1COUT | 0xFFD51004 | 4 | 0xFFFFFFFF |
| DCRA1CTL | 0xFFD51020 | 4 | 0x00000000 |
| PRDNAME1 | 0xFFCD00D0 | 4 | 0x37463752 |
| PRDNAME2 | 0xFFCD00D4 | 4 | 0x38333130 |
| PRDNAME3 | 0xFFCD00D8 | 4 | 0x20202033 |
| PRDNAME4 | 0xFFCD00DC | 4 | 0x20202020 |
- 指纹状态 (fingerprint): MISMATCH
- egg 签名 (egg signature): 存在-地址不同 (present, relocated from FW-PATCH)
- egg 候选 (egg candidates): 0x88C62(NO_DATA,重定位)
- 调整字 0xFFDEC (adjust word): 0xAD59D70C (unknown)

## 下一步 (Next Steps)
- 存在 egg 但地址与 FW-PATCH (0x8E6C6) 不同，patch 点可能重定位，需离线对照新指纹 (Egg present but not at the FW-PATCH address; the patch point may be relocated — compare against a new fingerprint offline)
