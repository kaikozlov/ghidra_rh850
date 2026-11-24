#!/usr/bin/env python3
"""Extract pinned offline GTS+/DS-4 VCI and transport lifecycle evidence.

No Windows APIs, drivers, network sockets or vehicles are invoked. Native roles
were established by Ghidra decompilation and decisive disassembly; this extractor
fails closed on source/body/branch drift and reconstructs the compact contracts.
Recovered setting-provider bodies default to the aggregate's GTSPlus component
and require exact manifest-relative qualification against the pinned installed
CP pair; explicit component roots never fall back to old recovery corpora.
Managed NIC admission validates full IL and preserves native/bodyless
classifications. Cross-domain producers are owned by auth_settings/operations.
Failure/reconnect contracts include independent controller/protocol flags and
API04/API05 differences. Receive ownership follows exact native callees through
the API05 shim; byte-stream fulfillment is not attributed to an opaque wrapper.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

from tools import REPO_ROOT
from tools.techstream.extract_gtsplus_tss3_native_recorder import pe_info, read_va, sha256_bytes
from tools.techstream.extract_gtsplus_tse_managed_semantics import _open, _instructions, _method_pin, _body
from tools.techstream.inspect_dotnet_il import format_operand, validate_managed_bodies
from tools.techstream.recover_all_gtsplus_bodies import DEFAULT_OUTPUT as DEFAULT_RECOVERED, qualify_recovered_source
from tools.techstream.parse_ddb import DDBParser

DEFAULT_TREE = REPO_ROOT / "software/Techstream/gtsplus/unpacked/gtsplus/Toyota Diagnostics"
DEFAULT_GTS = DEFAULT_TREE / "GTSPlus"
DEFAULT_DS4 = DEFAULT_TREE / "DS-4"
DEFAULT_MAIN = DEFAULT_RECOVERED / "GTSPlus"
DEFAULT_OUT = REPO_ROOT / "data/generated/gtsplus_2026/lifecycle_vci_transport.json"
DOMAIN = "vci_transport"

_evidence = json.loads(
    (REPO_ROOT / "data/techstream/lifecycle/vci_transport.json").read_text(encoding="utf-8")
)
SOURCE_PINS = _evidence["SOURCE_PINS"]
NATIVE_PINS = _evidence["NATIVE_PINS"]
MANAGED_PINS = _evidence["MANAGED_PINS"]
FINDINGS = _evidence["FINDINGS"]
# Current source-qualified transport and driver semantics; each native method is stored once.
COMPLETE_NATIVE = _evidence["COMPLETE_NATIVE"]
PLATFORM_SESSION = _evidence["PLATFORM_SESSION"]
del _evidence

SOURCE_PINS.update({
    "ds4_shim0404": {"root": "ds4", "relative": "bin/ptshim32.dll",
                     "sha256": "1c1e61da748104032c2b3826e386b1eadd37d0f4efa1d33f8076f4766fa806c9", "size": 2106384},
    "ds4_shim0500": {"root": "ds4", "relative": "bin/ptshim32_0500.dll",
                     "sha256": "664fa06364c0599dc9fa54d0fadd31642219d10d4f03e93cd72f7f79ff14da64", "size": 2119696},
})

BRANCH_ANCHORS = {'j2534.connect0404': [(268537422, '807e5c00'),
                       (268537479, '807e5d00'),
                       (268537941, 'c7451420a10700'),
                       (268538406, 'c6465d01')],
 'j2534.vehicle_id': [(268501102, 'c70580c80210ff000001'),
                      (268501737, '81ff01800000'),
                      (268501781, '83f802'),
                      (268501784, '0f8c57feffff')],
 'j2534.ndis_connect': [(268512720, '6858340000'),
                        (268513125, 'c70582c8021000050000'),
                        (268513135, '66c70586c802100007')],
 'kgp.change_interface': [(268637725, '241f'), (268637727, '3c14'), (268637731, '3c15'), (268637735, '3c16')],
 'j2534.driver_constructor': [(268525273, 'c707a84f0210')],
 'kgp.ndis_constructor': [(268559844, 'c706c4750410')]}

NATIVE_PINS["ds4_kgp"]["base_binding"] = {
    "va": 0x10011E50, "size": 1911,
    "sha256": "6ee970e87384df0c0773dfda746438c383f4e1befd85ba47109a53ea8e3be4a0",
}
FINDINGS["ds4_kgp.base_binding"] = (
    "Resolve PassThruConnect_v0500 at object+2170, LogicalConnect+2178, "
    "LogicalDisconnect+217C, ReadMsgs+2184, QueueMsgs+2188 and Ioctl+21A4 "
    "from the loaded J2534Ctrl. These bindings establish indirect-call roles "
    "in the DS-4 Ethernet physical/logical/message/teardown bodies."
)
BRANCH_ANCHORS["j2534.connect0404"].extend([
    (0x100192B0, "8bceff7674e8160f0000"),
])
BRANCH_ANCHORS["j2534.disconnect0404"] = [
    (0x1001A246, "807f5d017426"),
    (0x1001A268, "b802000000"),
]

# Current shims forward to MsgDatComm; their compatibility save exports are no-ops.
SHIM_PINS = {
    "shim0404": {
        "loadlibrary": (0x10009D60, 329, "f3384584fa8d57a683c41fadd1e5f5f1928f4d0327e4c9440d083f74d95f5da6"),
        "unloadlibrary": (0x10009EC0, 480, "66b28ab48ebcf00ffbf56a4c1296e3ac205608252661f0eab455f69cfd8493ab"),
        "savelog": (0x1000A170, 5, "5fed5afb29946811bf02359627a94bc01d08d31b779528feaadde3866af9c855"),
        "log_forward": (0x1000CD50, 299, "d25e1f466332ba3c15a86974b1daf97e02ada9e6260cddc957e093bf2232d9cb"),
        "load_driver": (0x1000CB50, 507, "74bfd1871c9627b4ddbd0488d9a1ee16956e1f4f81f6c5daf554bc3a8d872172"),
    },
    "shim0500": {
        "loadlibrary": (0x1000AD90, 329, "32c216b1079123fff6186aae30e99c960540c95e74d2ee89e2fd4c0146ec64e9"),
        "unloadlibrary": (0x1000AEE0, 420, "a8f295599ab5a23612b0a3f201d65ff34f1922a33f3f12d4a0e2149e91513c14"),
        "savelog": (0x1000B160, 5, "5fed5afb29946811bf02359627a94bc01d08d31b779528feaadde3866af9c855"),
        "log_forward": (0x1000DC50, 294, "d2ef7356873851f6ae5c74b35744b8f80f50f05990134778a2a5611f55f7b5e6"),
        "load_driver": (0x1000DAC0, 399, "cdd38f06e693701b26a2f104db1cd10d75b710a97919fcaca50be286ba7342a0"),
    },
    "ds4_shim0404": {
        "savelog": (0x1000A180, 5, "5fed5afb29946811bf02359627a94bc01d08d31b779528feaadde3866af9c855"),
        "log_forward": (0x1000CEB0, 299, "70428b091006a752fad2665b1322ca188b6dd5092b8b082af542e23b5821941a"),
    },
    "ds4_shim0500": {
        "savelog": (0x1000B160, 5, "5fed5afb29946811bf02359627a94bc01d08d31b779528feaadde3866af9c855"),
        "log_forward": (0x1000DC50, 294, "d2ef7356873851f6ae5c74b35744b8f80f50f05990134778a2a5611f55f7b5e6"),
    },
}
SHIM_FINDINGS = {
    "loadlibrary": "Serialize API access; null FunctionLibrary=>4. Convert supplied physical path then invoke DLL loader; failure=>7,success0.",
    "unloadlibrary": "When loaded, clear cached API pointers and FreeLibrary real driver; return0 under API lock.",
    "savelog": "CURRENT RELEASE: XOR EAX,EAX; RET4 returns success0 without reading path, flushing buffers or creating a file. V18 append/truncate behavior does not apply.",
    "log_forward": "Format UTF16 log message, copy temporary buffer and call optional ER_PutLogCommunication callback from MsgDatComm.dll. No disk-write operation in this body.",
    "load_driver": "LoadLibraryW physical driver path, set loaded flag and resolve API pointers. API05 includes QueueMsgs/ScanForDevices/GetNextDevice/LogicalConnect/LogicalDisconnect/Select. Module-load success does not guarantee every resolved API is nonnull.",
}
for _source, _functions in SHIM_PINS.items():
    NATIVE_PINS[_source] = {
        name: {"va": va, "size": size, "sha256": digest}
        for name, (va, size, digest) in _functions.items()
    }
    FINDINGS.update({_source + "." + name: SHIM_FINDINGS[name] for name in _functions})
    BRANCH_ANCHORS[_source + ".savelog"] = [(_functions["savelog"][0], "33c0c20400")]

# Failure/reconnect and parser callees: complete native bodies, not wrapper inference.
NATIVE_PINS['j2534'].update({'connect0500': {'va': 268542288,
                 'size': 125,
                 'sha256': '5b944efe2c050ceede2492ce6360f2b579c183d72d7ae5aa308721a375844e6d'},
 'disconnect0500': {'va': 268542880,
                    'size': 75,
                    'sha256': '3e754d0a0f99bc3ab07b8ec2d941ba50f751420dad7761d74375944585222867'},
 'read0500': {'va': 268547632,
              'size': 111,
              'sha256': 'b98c0afb6f900f0001eca75c91aad39890d02cd00540ac394d120c580a6e1fc2'},
 'address_compare': {'va': 268497008,
                     'size': 137,
                     'sha256': '0cebb06a50bcd2f9de9e3cd5e301f3191d7af4056dc9e3eddcb807fb95de7884'},
 'read0404': {'va': 268545648,
              'size': 1977,
              'sha256': '22b1457052e7f0be5378bd744d343eeb40a730634954bae7dfd18b76e1c5cd8a'}})
NATIVE_PINS['ds4'].update({'connect0404': {'va': 268530464,
                 'size': 4801,
                 'sha256': '3fdb37a79a27853998b9859a8f63653231c99d99ac6cc7aac5f38c44fb359d24'},
 'disconnect0404': {'va': 268535488,
                    'size': 454,
                    'sha256': '02b69675db5fb4a7aa8cd893c6c744fe1bdec2c3902c117e4ac2ba18182804be'},
 'close': {'va': 268526624,
           'size': 464,
           'sha256': '26901a1cad5176434309a0ea6457adb5e0c8975e77d446d9a0c182b6cdc6b475'},
 'connect0500': {'va': 268535360,
                 'size': 125,
                 'sha256': 'd7082bb9b46d43f41faa721f90a3d87207464c01b4f86268ebd6db075e12158d'},
 'disconnect0500': {'va': 268535952,
                    'size': 75,
                    'sha256': '4f3c51958d69a140b1368d28af531643447c1019530ecb917a0459a59e998b9d'},
 'read0500': {'va': 268540688,
              'size': 111,
              'sha256': '7a75e4dc60c17c120820f521b73bc39ea89d8ac626fee7ea820e6a8d071f0577'},
 'logical_connect0500': {'va': 268538464,
                         'size': 59,
                         'sha256': 'f20ec1d76f3b5ffd9e5f8b57ebd7914ffe3621073ce58b0254b5f7cdae86922d'},
 'logical_disconnect0500': {'va': 268538528,
                            'size': 59,
                            'sha256': '13753ca3eaff574ea377207446b52246045105e066a1380df3dcd142c231db86'}})
NATIVE_PINS['kgp'].update({'base_connect': {'va': 268518320,
                  'size': 273,
                  'sha256': '6dd8c219b8bdc8194e0951bc76bb331b02c64dbb4f74fca2e22f99cfa27462df'},
 'base_disconnect': {'va': 268518608,
                     'size': 189,
                     'sha256': 'f26dfee363225fca029bb724f0be4116b9cf2f600aea7d9d43ab98504a8bd366'}})
NATIVE_PINS['ds4_kgp'].update({'ethernet_classifier': {'va': 268534768,
                         'size': 81,
                         'sha256': '51f541c8e1f19d538f52742b58a3ee1edbaa09c35b45898b14a62270fd88c901'}})
FINDINGS.update({'j2534.connect0500': 'API2/module/open required, but unlike API04 there is no connected+5D rejection or '
                      'default-filter setup. Forward explicit device/resource/output arguments. Success '
                      'replaces last physical channel+74 and sets+5D; failure preserves prior+74/+5D. '
                      'Multiple physical API05 channels are therefore not represented by a channel-count '
                      'flag.',
 'j2534.disconnect0500': 'API2/module/open required; does not require connected+5D. Resolve and invoke '
                         'physical disconnect for the supplied channel even when+5D=0, then clear+5D '
                         'regardless of driver result. Missing export returns7 without clearing flags. Does '
                         'not erase+74 or clear API04 filter list/translation flags.',
 'j2534.read0500': 'API2/module/open required, but no connected+5D gate. Call driver ReadMsgs with original '
                   'byte-count/message pointers and timeout; optional logging afterward, no DoIP reassembly. '
                   'API05 stream fulfillment belongs to the selected external FunctionLibrary, not this '
                   'wrapper.',
 'j2534.address_compare': 'Complete address-value comparator: first compare length at+8, then every byte. '
                          'False means equality, true means different. ACK/diagnostic receiver compare '
                          'two-byte wire source with cached sent target and wire target with cached sent '
                          'source; no wildcard match.',
 'j2534.read0404': 'API1/module/open and connected+5D=1 required; failed setup or failed disconnect followed '
                   'by clear flag returns2 before driver ReadMsgs. Successful read consumes '
                   'sticky+7E/+7F/+80 translation flags to mask RxStatus80/100/180000; custom1000C mode+84 '
                   'changes status handling. Generic connect only sets requested translation bytes, not '
                   'clears unrequested ones; a failed-connect retry can inherit them until an actually '
                   'executed disconnect or destruction.',
 'kgp.base_connect': 'If KGP connected+0C, dispatch disconnect first but ignore its result. Driver connect '
                     'callback+2144 writes channel+8; set protocol+20D8 even on error, set+0C only on '
                     'success. Failure maps91010000. KGP and CJ2534 connected flags are distinct; an API04 '
                     'filter failure leaves both clear even after driver-created numeric ID.',
 'kgp.base_disconnect': 'If KGP connected+0C=0 return0 without driver call or clearing channel+8. Otherwise '
                        'stop services, invoke bound controller disconnect+2148, clear '
                        'channel/ECU/service/connected fields even on nonzero result, return mapped error. '
                        'Next ordinary connect can invoke driver again; an absent cleanup call does not '
                        'prove external hardware allocation survives.',
 'ds4_kgp.ethernet_classifier': 'Complete classifier only inspects diagnostic data after four address bytes: '
                                'payload>=7 and 7F xx 78=>90020323 pending, 7F xx 21=>90020326 retry, other '
                                '7F=>90020321 negative response. It does not validate logical destination, '
                                'DoIP version/inverse, ACK code, or stream fragmentation; those checks '
                                'cannot be attributed to this callee.',
 'ds4.connect0404': 'DS-4 API04 shares late+5D commit and guarded rollback: physical connect success '
                    'stores+74, missing/default-filter failure calls disconnect while+5D=0, so no physical '
                    'disconnect occurs. Subsequent API04 connect is permitted and overwrites+74 on success. '
                    'DS-4 generic flags80/100 set+7E/+7F without clearing absent bits; custom-mode dword '
                    'is+80 (main uses+84). No main-only8012/8013 cases.',
 'ds4.disconnect0404': 'DS-4 API1/module/open/channel guards; missing export preserves bookkeeping. After '
                       'driver invocation, clear filter list,+7C,+7E/+7F,+5D despite driver failure, retain '
                       'numeric+74 and custom-mode+80. Main additionally clears translation byte+80, whose '
                       'role differs in DS-4.',
 'ds4.close': 'Same close ordering as main with DS-4 vtable slots: if+5D set, API04 guarded disconnect or '
              'API05 direct physical disconnect; ignore disconnect status. Then physical Close; success '
              'clears only open+5C/device+78 and calls save slot+B4; failure maps7 and preserves '
              'open/device. Missing disconnect export can leave+5D set even after successful Close. Next '
              'connect then fails open gate8, not a hardware observation.',
 'ds4.connect0500': 'DS-4 API05 matches main API05: no already-connected rejection; physical Connect success '
                    'replaces last+74/sets+5D, failure preserves these. No default-filter setup.',
 'ds4.disconnect0500': 'DS-4 API05 matches main: call supplied channel even if+5D=0; clear+5D after '
                       'invocation regardless of status. Missing export or unopened device returns without '
                       'state reset.',
 'ds4.read0500': 'DS-4 API05 forwards ReadMsgs unchanged after API/module/open gates, even with+5D=0. No '
                 'short-read accumulation in controller; only optional log callback. KGP requests exact '
                 'stream-byte counts, so external driver must fulfill each requested block or KGP reports '
                 'short response.',
 'ds4.logical_connect0500': 'API2/module/open guard then tail-dispatch physical driver LogicalConnect with '
                            'caller stack unchanged. Does not update+5D/+74 or track logical IDs. KGP owns '
                            'IP4/UDP/TCP slots2240/2244/2248.',
 'ds4.logical_disconnect0500': 'API2/module/open guard then tail-dispatch physical driver LogicalDisconnect, '
                               'no ID/flag bookkeeping. KGP backend zeros every supplied logical slot after '
                               'attempted driver teardown even on error.'})
BRANCH_ANCHORS.update({'j2534.connect0500': [(268542387, '894674'), (268542392, 'c6465d01')],
 'j2534.disconnect0500': [(268542936, 'c6465d00')],
 'ds4.connect0404': [(268530647, '807e5d00'), (268530704, 'c7868000000000000000')],
 'ds4.disconnect0404': [(268535606, '807f5d01'), (268535933, 'c6475d00')],
 'ds4.close': [(268527065, 'c6465c00'), (268527069, 'c7467800000000')]})
FINDINGS["j2534.disconnect0404"] += (
    " Missing PassThruDisconnect export returns7 BEFORE cleanup, preserving+5D/list/flags; "
    "only a driver invocation reaches unconditional resets. Numeric channel+74 is never zeroed."
)
FINDINGS["j2534.close"] += (
    " Disconnect status is ignored. Missing disconnect export can preserve+5D even after Close success; "
    "Open then sets only+5C/+78, so API04 next Connect can still reject14. A failed Close leaves+5C=1: "
    "Open rejectsE while Connect can proceed if+5D cleared. Finalize destroys regardless and destructor "
    "attempts another physical Close while+5C remains set; repeated error does not prove hardware leak."
)
FINDINGS["ds4.initialize"] += (
    " Unlike main, failed post-constructor API04/API05 Open returns without deleting/resetting singleton "
    "100287E0. Next Initialize returnsE until explicit Finalize; KGP Open failure calls CloseDevice, "
    "which finalizes this retained singleton. Do not transfer main failed-open reset to DS-4."
)
FINDINGS["j2534.ndis_receive"] += (
    " Header and body each accumulate positive short recv results to exact requested size; WinsockLogger "
    "does not parse. Invalid type/too-small length/caller-capacity rejection consumes header only, leaving "
    "body queued; partial-body timeout consumes bytes with no persistent assembly state for next call. "
    "Neither version/inverse bytes nor fixed global scratch capacityFFFF are checked against declared "
    "length before body recv; caller payload capacity is not a scratch-buffer bound. High-bit lengths "
    "reach signed-positive helper check8005 when caller capacity passes."
)
FINDINGS["j2534.ndis_ack"] += (
    " Positive short reads are accumulated separately for header/body; declared body is read into shared "
    "FFFF-byte scratch without an explicit maximum check. Version/inverse and ACK code byte are not "
    "checked. A four-byte address-only8002 body succeeds;8003 fails regardless of code. Rejected header "
    "does not drain body, and timeout/EOF does not close socket or retain partial parser state."
)
FINDINGS["ds4_kgp.ethernet_receive"] += (
    " Chunk limit1020 is HEX (4128 bytes), not decimal1020. ACK requests exactly13 bytes and only checks "
    "minimum13,type8002,source==requested ECU; no ACK-declared-length/status/destination check. Header "
    "requests8 bytes; body requires declared>=5 and capacity>=declared-4, then exact driver DataSize for "
    "each min(remaining,1020) block; positive short blocks are errors, not accumulated. Version/inverse "
    "and logical destination are unchecked. Classifier runs on first body block; success then source "
    "comparison precedes later raw chunk concatenation. Driver ReadMsgs and shim supply byte-stream "
    "fulfillment; host TCP fragmentation loop is absent in this DS-4 route."
)

NATIVE_PINS["j2534"].update({
    "logical_connect0500": {"va": 0x1001AD70, "size": 59,
        "sha256": "d3062afc887142d9ea753f6999d7d7a6abc2177c4898180795c9d5b8bdb38f51"},
    "logical_disconnect0500": {"va": 0x1001ADB0, "size": 59,
        "sha256": "93b568845fc5bec2c05fef622e3ffd00220e9c0bb8f7f630cffdb379a7c2b0aa"},
})
FINDINGS["j2534.logical_connect0500"] = FINDINGS["ds4.logical_connect0500"]
FINDINGS["j2534.logical_disconnect0500"] = FINDINGS["ds4.logical_disconnect0500"]
for _source in ("shim0500", "ds4_shim0500"):
    NATIVE_PINS[_source].update({
        "read_stream": {"va": 0x1000B900, "size": 455,
            "sha256": "bf36a2dd5bc9fc4cce64696566b81a92017fd2ec2b8a305b0847cdb612c62324"},
        "read_clock": {"va": 0x1000DA30, "size": 137,
            "sha256": "cd8781d5704524c0e0f250250ccde3e0bcf6cc829e3b198b22bb8dec0cc2e6df"},
    })
    FINDINGS[_source + ".read_stream"] = (
        "Under API critical section, reject unloaded driver7; invoke cached physical ReadMsgs exactly once "
        "with original channel/message/count/timeout arguments, then log output. Channel-table lookup "
        "only changes byte/message logging. No accumulation, DoIP length/type/address parsing or retry; "
        "selected external FunctionLibrary owns API05 byte-stream fulfillment."
    )
    FINDINGS[_source + ".read_clock"] = (
        "ReadMsgs pre-call helper only initializes/query performance frequency/counter under lock and "
        "converts timing; it does not receive message arguments or consume/assemble bytes."
    )
FINDINGS["kgp.adopt_connection"] += (
    " No independent owned/borrowed flag is set: adopted +0C=1 takes the same later disconnect path "
    "as newly connected channels. Adoption changes KGP fields, not J2534 singleton +5C/+5D; API04 "
    "can therefore reject later reads/disconnect with2 if caller did not also establish controller state."
)
FINDINGS["kgp.change_interface"] += (
    " Compatible reuse exits without a new physical Connect; cached bus/category, WWH and OBD-on-UDS "
    "modes and FD ECU identity gate reuse. Main nibble4 reuse explicitly backend-disconnects and clears "
    "KGP +0C before reusing the NDIS object. Any backend-connect error flows Disconnect(0): ordinary "
    "base skips physical disconnect if+0C was never set; NDIS override always calls backend teardown."
)
FINDINGS["ds4_kgp.ethernet_receive"] = FINDINGS["ds4_kgp.ethernet_receive"].replace(
    "chunks up to1020 each", "chunks up to0x1020 (4128) bytes each"
)
NATIVE_PINS["kgp"].update({
    "set_adopted_channel": {"va": 0x10016940, "size": 13,
        "sha256": "7dd3c0df92e475b5ecdbd89e4b18571bfe34961f32b51a9f9c3b8326dfd56f3c"},
    "set_adopted_protocol": {"va": 0x10016D00, "size": 16,
        "sha256": "3c3eb59953385e180b0c3dbc6477950c5cfeeb08a6d5a4b2a1b53449be441e82"},
})
FINDINGS["kgp.set_adopted_channel"] = "Vtable+120 setter stores supplied numeric channel at protocol object+08; no driver call or ownership flag."
FINDINGS["kgp.set_adopted_protocol"] = "Vtable+128 setter stores supplied protocol at protocol object+20D8; no driver call."
NATIVE_PINS["ds4"]["open0404"] = {
    "va": 0x10016B50, "size": 487,
    "sha256": "780f5f8ec8d7f8bc5698070c8f1a8256f72c031225e5797d8b91c76157454884",
}
FINDINGS["ds4.open0404"] = (
    "API1/module required. Open+5C already set returnsE; driver Open(null,&device) success sets+78/+5C "
    "but does not reset connected+5D. Following a Close whose disconnect export was absent, this "
    "reopen can succeed yet subsequent API04 Connect returns14 due to stale+5D."
)
for _source in ("j2534", "ds4"):
    FINDINGS[_source + ".disconnect0404"] += (
        " Exceptional direct-DENSO path: driver status7 and+7D set resolves GetLastError; "
        "if absent, code logs FUNC_ADDRESS_FAILED but still calls null before software resets. "
        "Thus unconditional post-invocation reset describes normally returning paths, not this fault."
    )
BRANCH_ANCHORS["j2534.disconnect0404"].append((0x1001A35A, "ffd0"))
BRANCH_ANCHORS["ds4.disconnect0404"].append((0x1001884A, "ffd0"))
FINDINGS["j2534.ndis_connect"] += (
    " Direct repeated NDISConnect has no existing-socket/startup guard: WSAStartup and newly created "
    "UDP/TCP handles overwrite process globals. Normal ChangeCommIF failure invokes KGP NDIS "
    "disconnect override even when+0C=0, closing partial globals; bypassing that owner is not equivalent. "
    "No allocation-liveness conclusion follows solely from omitted calls."
)

# Disassembled initialization windows, including conditional callback registration.
REGISTRATION_PINS = {
    "shim0404": (0x10001150, "687c631b10ff15f8e31710a3c4f01d1085c07411689c631b1050ff15f4e31710a3c8f01d1068f0d81710e80470140059c3", 0x101B637C, 0x101B639C),
    "shim0500": (0x10001150, "68a4971b10ff15f8f31710a3ac201e1085c0741168c4971b1050ff15f4f31710a3b0201e106850e91710e8057f140059c3", 0x101B97A4, 0x101B97C4),
    "winsock": (0x10001036, "681c840010ff1578700010a3a8b3001085c07411683c84001050ff1574700010a3acb30010", 0x1000841C, 0x1000843C),
    "ds4_shim0404": (0x10001150, "6800741b10ff15f8f31710a3cc001e1085c074116820741b1050ff15f4f31710a3d0001e106840da1710e85e71140059", 0x101B7400, 0x101B7420),
    "ds4_shim0500": (0x10001150, "68a4971b10ff15f8f31710a3ac201e1085c0741168c4971b1050ff15f4f31710a3b0201e106850e91710e8057f140059", 0x101B97A4, 0x101B97C4),
}
# Source qualification checks exact deployed/recovered PEs, qualified managed bodies,
# native database bytes, and the canonical current installer artifact. It never
# consumes a decompiler dump, an IL inventory, or a session-local analysis file.
SOURCE_PINS.update(COMPLETE_NATIVE["source_updates"])
FINDINGS["j2534.initialize"] += (
    " Actual main API1 forwards its third name argument; the required deviceOut is not written by API1."
)
FINDINGS["ds4.initialize"] += (
    " Its API1 name is NULL. Failed Open retains the singleton and does not copy its private error; "
    "the required API1 deviceOut is not written."
)
FINDINGS["kgp.open_j2534_2"] += " The FD factory passes API selector1 and ASCII J2534-2:, not API2."


# Generic caller policy composes, but does not replace, the concrete transport algorithms above.
PLATFORM_PREFIX = DOMAIN + "."
PLATFORM_READ_VA = lambda path, va, size: read_va(*pe_info(path), va, size)

def _platform_session_contracts(installed: dict[str, Path], recovered: dict[str, Path],
                                sources: list[dict[str, Any]], evidence: list[dict[str, Any]]) -> dict[str, Any]:
    paths: dict[str, Path] = {}
    for spec in PLATFORM_SESSION["sources"]:
        _, product, filename = spec["unit_id"].split(".", 2)
        original = installed[product] / "bin" / filename
        path = (recovered[product] / "bin" / filename
                if spec["kind"] == "analysis" and spec["path"].startswith("build/") else original)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != spec["sha256"]:
            raise ValueError(f"PlatformSession qualified source drift: {spec['unit_id']}")
        qualification = None
        if path != original and original.with_name(original.name + "._").is_file():
            component = recovered[product] if product == "GTSPlus" else recovered[product].parent
            qualification = qualify_recovered_source(path, original, component_root=component)
        sid = next((s["id"] for s in sources if s["sha256"] == digest),
                   PLATFORM_PREFIX + "platform.source." + digest)
        if not any(s["id"] == sid for s in sources):
            sources.append({"id": sid, "path": str(path.resolve().relative_to(REPO_ROOT)),
                            "sha256": digest, "size": path.stat().st_size,
                            "representation": "qualified current PlatformSession native/managed source",
                            "qualification": qualification})
        evidence.append({"id": PLATFORM_PREFIX + "platform.source." + digest, "source": sid,
                         "kind": "source-qualified-platform-session-definition",
                         "sha256": digest, "qualification": qualification,
                         "finding": PLATFORM_SESSION["proof_policy"]})
        paths[digest] = path
    for pin in PLATFORM_SESSION["native_pins"]:
        raw = PLATFORM_READ_VA(paths[pin["source_sha256"]], pin["va"], pin["size"])
        if hashlib.sha256(raw).hexdigest() != pin["sha256"]:
            raise ValueError(f"PlatformSession native entry drift: {pin['va']:#x}")
        evidence.append({"id": PLATFORM_PREFIX + "platform.native." + pin["source_sha256"] + f".{pin['va']:08x}",
                         "source": next(s["id"] for s in sources if s["sha256"] == pin["source_sha256"]),
                         "kind": "native-instruction-dataflow", **pin})
    return PLATFORM_SESSION



def _native_image(images: dict[str, Any], source: str) -> tuple[Any, bytes, int]:
    return images[source.removeprefix(DOMAIN + ".source.")]


def _pin_native_bytes(images: dict[str, Any], source: str, va: int, size: int,
                      expected: str, label: str) -> None:
    pe, data, base = _native_image(images, source)
    if sha256_bytes(read_va(pe, data, base, va, size)) != expected:
        raise ValueError(f"native source bytes drift: {label} at {va:#x}")


def _complete_regions(images: dict[str, Any], evidence: list[dict[str, Any]]) -> None:
    for key, regions in COMPLETE_NATIVE["native_regions"].items():
        source = _id("source." + key)
        for region in regions:
            _pin_native_bytes(images, source, region["va"], region["size"],
                              region["sha256"], key + region["section"])
        evidence.append({"id": _id("complete.native_code." + key), "source": source,
                         "kind": "native-code-and-data-spans", "regions": regions,
                         "finding": "Exact current code, constant tables and initial data are authenticated. "
                         "Hashes authenticate bytes, not inferred CFG completeness; algorithm semantics, "
                         "concrete dispatch and independently pinned switch/unwind maps are separate."})
    methods = COMPLETE_NATIVE["native_methods"]
    for identity, method in methods.items():
        _pin_native_bytes(images, method["source"], method["va"], method["entry_size"],
                          method["entry_sha256"], identity)
    for cls in COMPLETE_NATIVE["protocol_classes"]:
        pe, data, base = _native_image(images, cls["source"])
        actual = read_va(pe, data, base, cls["vtable"], 4 * len(cls["slots"]))
        expected = b"".join(struct.pack("<I", methods[entry]["va"]) for entry in cls["slots"])
        if actual != expected:
            raise ValueError(f"concrete native vtable drift: {cls['id']}")
    for profile in COMPLETE_NATIVE["facade_virtuals"]:
        source = _id("source." + ("kgp" if profile["source_variant"] == "main" else "ds4_kgp"))
        raw = bytes.fromhex(profile["vtable_hex_12bytes"])
        _pin_native_bytes(images, source, int(profile["vtable_va"], 16), len(raw),
                          sha256_bytes(raw), "frame facade virtuals")
    for table in COMPLETE_NATIVE["switch_tables"]:
        raw = bytes.fromhex(table["hex"])
        _pin_native_bytes(images, table["source"], int(table["table"], 16), len(raw),
                          sha256_bytes(raw), "native switch table")
        remap = table["byte_remap"]
        if remap:
            raw = bytes.fromhex(remap["hex"])
            _pin_native_bytes(images, table["source"], int(remap["va"], 16), len(raw),
                              sha256_bytes(raw), "native switch byte remap")
    for scope in COMPLETE_NATIVE["unwind_scopes"]:
        for address, raw in [(scope["info"], scope["info_hex"]),
                             (scope["map"], scope["map_hex"])]:
            encoded = bytes.fromhex(raw)
            if encoded:
                _pin_native_bytes(images, scope["source"], int(address, 16), len(encoded),
                                  sha256_bytes(encoded), "native C++ unwind state map")
    for handoff in COMPLETE_NATIVE["typed_handoffs"]:
        pins = handoff.get("additional_caller_pins", [])
        if handoff.get("caller_pin"):
            pins = [handoff["caller_pin"], *pins]
        for pin in pins:
            _pin_native_bytes(images, pin["source"], pin["va"], pin["size"],
                              pin["sha256"], handoff["caller"])


def _complete_driver_exports(images: dict[str, Any]) -> None:
    exports: dict[str, dict[str, int]] = {}
    for alias in COMPLETE_NATIVE["driver_aliases"]:
        source = alias["source"]
        if source not in exports:
            pe, _, base = _native_image(images, source)
            exports[source] = {entry.name.decode("ascii"): base + entry.address
                               for entry in pe.DIRECTORY_ENTRY_EXPORT.symbols if entry.name}
        if exports[source].get(alias["export"]) != alias["va"]:
            raise ValueError(f"source-qualified driver export drift: {alias['id']}")


def _complete_managed(roots: dict[str, Path], nic: Any,
                      evidence: list[dict[str, Any]]) -> None:
    modules = {"nic": nic}
    for pin in COMPLETE_NATIVE["managed_pins"]:
        key = pin["source"]
        if key not in modules:
            path = roots[SOURCE_PINS[key]["root"]] / SOURCE_PINS[key]["relative"]
            modules[key] = _open(path)
            validate_managed_bodies(path)
        pe = modules[key]
        row = pe.net.mdtables.MethodDef.rows[(pin["methoddef_token"] & 0xFFFFFF) - 1]
        actual = _method_pin(row, _body(pe, row))
        if any(actual[field] != pin[field] for field in ("rva", "body_size", "body_sha256")):
            raise ValueError(f"qualified managed body drift: {key}:{pin['methoddef_token']:#x}")
        evidence.append({"id": _id(f"complete.managed.{key}.{pin['methoddef_token']:08x}"),
                         "source": _id("source." + key), "kind": "managed-IL",
                         "methoddef_token": f"0x{pin['methoddef_token']:08X}",
                         "locator": pin["type"] + "::" + pin["method"], **actual})


def _regional_protocols(roots: dict[str, Path], sources: list[dict[str, Any]]) -> dict[str, Any]:
    parser = DDBParser()
    raw_tables: dict[tuple[str, int], list[Any]] = {}
    tables = []
    for spec in COMPLETE_NATIVE["database_sources"]:
        path = roots[spec["root"]] / spec["relative"]
        encoded = path.read_bytes()
        if sha256_bytes(encoded) != spec["sha256"]:
            raise ValueError(f"regional native database source drift: {path}")
        sources.append({"id": spec["id"], "path": _relative(path),
                        "sha256": spec["sha256"], "size": len(encoded),
                        "representation": "installed-original native database"})
        db = parser.parse_master_db(path)
        for table in (0, 13, 14, 15, 16, 17, 18, 26, 51, 85, 86):
            section = db.sections.get(table)
            if section is None:
                continue
            rows = list(section.iter_records())
            raw_tables[(spec["id"], table)] = rows
            tables.append({"source": spec["id"], "table": table,
                           "count": len(rows), "encoded_payload_offset": section.data_offset,
                           "encoded_payload_sha256": sha256_bytes(section.raw_data),
                           "decoded_sha256": sha256_bytes(section.decoded_data),
                           "record_width": None if table == 0 else section.decoded_record_size,
                           "rows": [{"index": row.index, "hex": row.raw.hex(),
                                     "decoded_offset": row.decoded_offset,
                                     **({"directory_hex": row.directory_raw.hex()} if table == 0 else {})}
                                    for row in rows]})
    configurations: dict[tuple[str, int], dict[int, list[int]]] = {}
    for spec in COMPLETE_NATIVE["database_sources"]:
        for table, offset in [(14, 8 if spec["build"] == "DS-4" else 12),
                              (15, 4), (51, 0), (85, 0), (86, 0)]:
            index: dict[int, list[int]] = {}
            for row in raw_tables.get((spec["id"], table), []):
                index.setdefault(int.from_bytes(row.raw[offset:offset + 2], "little"), []).append(row.index)
            configurations[(spec["id"], table)] = index
    contexts: dict[tuple[str, int], list[dict[str, Any]]] = {}
    frame_variables: dict[tuple[str, int], dict[str, Any]] = {}
    def frame_context(spec: dict[str, Any], category: int) -> list[dict[str, Any]]:
        cache_key = (spec["id"], category)
        if cache_key in contexts:
            return contexts[cache_key]
        result = []
        for candidate in COMPLETE_NATIVE["database_sources"]:
            if (candidate["build"], candidate["region"]) != (spec["build"], spec["region"]):
                continue
            source = candidate["id"]
            selectors = [row for row in raw_tables.get((source, 18), [])
                         if int.from_bytes(row.raw[:2], "little") == category]
            frame_ids = {int.from_bytes(row.raw[6:8], "little") for row in selectors}
            frames = [row for row in raw_tables.get((source, 17), [])
                      if int.from_bytes(row.raw[:2], "little") in frame_ids]
            pool_size = len(raw_tables.get((source, 0), []))
            for frame in frames:
                variable_key = (source, frame.index)
                if variable_key in frame_variables:
                    continue
                variables = []
                for field, offset in [("send", 2), ("mask", 4), ("check", 6)]:
                    raw_id = int.from_bytes(frame.raw[offset:offset + 2], "little")
                    candidates = []
                    for flag in (0, 1):
                        normalized = raw_id - 10000 if flag == 0 and raw_id > 10000 else raw_id
                        candidates.append({"one_shot_flag": flag, "normalized_id": normalized,
                                           "pool_row": normalized - 1 if normalized else None,
                                           "within_pool": 0 < normalized <= pool_size})
                    variables.append({"field": field, "raw_id": raw_id,
                                      "namespace_candidates": candidates})
                frame_variables[variable_key] = {
                    "source": source, "frame_row": frame.index, "fields": variables,
                }
            result.append({"source": source, "partition": candidate["partition"],
                           "selector_rows": [row.index for row in selectors],
                           "frame_rows": [row.index for row in frames]})
        contexts[cache_key] = result
        return result
    routes = []
    for route in COMPLETE_NATIVE["route_specs"]:
        route_selector = int(route["route_selector"], 16)
        bindings = []
        for spec in COMPLETE_NATIVE["database_sources"]:
            if spec["build"] != route["build"]:
                continue
            for row in raw_tables.get((spec["id"], 13), []):
                raw = row.raw
                if len(raw) != 28:
                    raise ValueError("native protocol record must be28bytes")
                if raw[0x18] != route_selector:
                    continue
                word = lambda offset: int.from_bytes(raw[offset:offset + 2], "little")
                category, key = word(0), word(2)
                table = 15 if route_selector & 15 in (1, 9, 12) else 51 if route_selector & 15 in (6, 7) else 85 if route_selector & 15 == 4 else 14
                bindings.append({"source": spec["id"], "protocol_row": row.index,
                                 "native_keys": {"class": "0x10D", "category": category, "route_selector": route_selector},
                                 "fields": {"configuration": key, "initial_address": word(4),
                                            "functional_address": word(6), "physical_address": word(8),
                                            "extended_address": word(10), "pending_limit": word(18),
                                            "alternate_address": word(20), "timeout_override_flag": raw[26]},
                                 "configuration_candidates": {"table": table, "key": key,
                                     "rows": configurations[(spec["id"], table)].get(key, [])},
                                 "frame_context": {"source": spec["id"], "category": category}})
                frame_context(spec, category)
        routes.append({**route, "bindings": bindings,
                       "fresh_main_factory_error": "0x90020201" if route["build"] == "GTSPlus" and route_selector == 0x15 else None})
    return {"schema": "gtsplus-regional-protocol-routes-v2",
            "routes": routes, "tables": tables,
            "frame_variables": list(frame_variables.values()),
            "frame_variable_reference": "A context's source and each ordered frame_rows entry "
            "identify one frame_variables row; fields preserve send, mask, check order.",
            "frame_contexts": [{"key": {"source": source, "category": category}, "contexts": value}
                               for (source, category), value in contexts.items()],
            "selection_contracts": ["MetadataMain.Query.Main", "MetadataDS4.native.ActiveIndex",
                                    "MetadataDS4.native.GenSpeMerge", "MetadataDS4.native.VariableDirectory"],
            "selection_rule": "Ordered duplicate-preserving source candidates only. Active index, event, "
            "Gen/Spe, CommSet and timer policies remain native metadata-owner decisions, not first/last "
            "or category0 fallback. One-shot variable normalization resets before bounds/error. "
            "No route is asserted observed on a car."}


def _current_comtol_absence() -> dict[str, Any]:
    path = REPO_ROOT / "data/generated/gtsplus_2026/lifecycle_install_update.json"
    artifact = json.loads(path.read_text())
    sources = {source["id"]: source for source in artifact["sources"]}
    archive = sources["install_update.archive"]
    expected_archive = "fb65ac31b1c0a0c1b28d53af8cf540d12eb46d77ba1e6645a014473352ce00c4"
    if archive["sha256"] != expected_archive:
        raise ValueError("current installer archive identity drift")
    with (REPO_ROOT / archive["path"]).open("rb") as stream:
        if hashlib.file_digest(stream, "sha256").hexdigest() != expected_archive:
            raise ValueError("current installer archive bytes drift")
    evidence = {entry["id"]: entry for entry in artifact["evidence"]}
    total = 0
    for pin in COMPLETE_NATIVE["cabinet_pins"]:
        entry = evidence[pin["id"]]
        encoded = json.dumps(entry["members"], ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        if (entry["kind"] != "cabinet-member-table" or entry["source"] != pin["source"]
                or sources[entry["source"]]["sha256"] != pin["header_sha256"]
                or len(entry["members"]) != pin["count"] or entry["member_count"] != pin["count"]
                or sha256_bytes(encoded) != pin["sha256"] or entry["member_names_sha256"] != pin["sha256"]):
            raise ValueError(f"qualified installer cabinet table drift: {pin['id']}")
        if any(member.replace("\\", "/").rsplit("/", 1)[-1].casefold() == "comtol32.dll"
               for member in entry["members"]):
            raise ValueError("current ComTol32 cabinet distribution absence changed")
        total += len(entry["members"])
    return {"id": _id("current.ComTol32.distribution_absence"), "canonical_artifact": _relative(path),
            "source": archive["id"], "evidence": [pin["id"] for pin in COMPLETE_NATIVE["cabinet_pins"]],
            "cabinet_count": len(COMPLETE_NATIVE["cabinet_pins"]), "member_count": total,
            "case_insensitive_basename_matches": 0,
            "boundary": "Absence from the current12 cabinet member tables only, not external VIM/runtime "
            "search directories or registry-selected FunctionLibrary/VCI firmware. No V18 implementation substitution."}


def _complete_native_contracts(roots: dict[str, Path], images: dict[str, Any],
                               sources: list[dict[str, Any]], evidence: list[dict[str, Any]],
                               nic: Any) -> dict[str, Any]:
    _complete_regions(images, evidence)
    _complete_driver_exports(images)
    _complete_managed(roots, nic, evidence)
    regional = _regional_protocols(roots, sources)
    return {"native_protocol_contracts": {
                "algorithms": COMPLETE_NATIVE["protocol_algorithms"],
                "native_methods": COMPLETE_NATIVE["native_methods"],
                "classes": COMPLETE_NATIVE["protocol_classes"],
                "facades": COMPLETE_NATIVE["facade_aliases"],
                "facade_virtuals": COMPLETE_NATIVE["facade_virtuals"],
                "driver_calls": COMPLETE_NATIVE["driver_calls"],
                "switch_tables": COMPLETE_NATIVE["switch_tables"],
                "unwind_scopes": COMPLETE_NATIVE["unwind_scopes"],
                "owner_joins": COMPLETE_NATIVE["owner_joins"],
                "unit_resolution": COMPLETE_NATIVE["protocol_unit_resolution"],
                "semantics": "Static current-source behavior, not car observations. Native method semantics "
                "occur once; concrete vtables, facade aliases and caller/callee joins reference that pool. "
                "Resolved native ABI overrides incomplete decompiler signatures, including common-pushed "
                "OEM output and original-stack tail forwarding. Byte authentication is not a CFG proof."},
            "native_driver_contracts": {
                "algorithms": COMPLETE_NATIVE["driver_algorithms"],
                "interfaces": COMPLETE_NATIVE["driver_interfaces"],
                "export_aliases": COMPLETE_NATIVE["driver_aliases"],
                "types": COMPLETE_NATIVE["driver_type_definitions"],
                "layouts": COMPLETE_NATIVE["driver_layouts"],
                "behavior_matrix": COMPLETE_NATIVE["driver_key_behavior_matrix"],
                "unit_resolution": COMPLETE_NATIVE["driver_units"],
                "managed_module_mvids": COMPLETE_NATIVE["managed_source_mvid"],
                "physical_boundary": "Actual selected FunctionLibrary, Windows registry/settings/runtime "
                "resolution and VCI firmware are external. Current shipped shim SaveLog no-ops do not "
                "erase distinct real callback/file logging. Managed NIC helper caller remains unproven."},
            "regional_protocol_routes": regional,
            "typed_native_handoffs": COMPLETE_NATIVE["typed_handoffs"],
            "current_distribution_boundary": _current_comtol_absence(),
            "unexecuted_native_scenarios": COMPLETE_NATIVE["scenarios"],
            "source_present_remaining_caller_work": [],
            "complete_native_coverage": {"protocol_classes": len(COMPLETE_NATIVE["protocol_classes"]),
                "facade_functions": len(COMPLETE_NATIVE["facade_aliases"]),
                "routes": len(regional["routes"]),
                "ordered_route_bindings": sum(len(route["bindings"]) for route in regional["routes"]),
                "unique_native_methods": len(COMPLETE_NATIVE["native_methods"]),
                "driver_export_aliases": len(COMPLETE_NATIVE["driver_aliases"]),
                "driver_units": len(COMPLETE_NATIVE["driver_units"]), "primary_plugins": 0}}




def _id(value: str) -> str:
    return f"{DOMAIN}.{value}"


def _relative(path: Path) -> str:
    resolved = path.resolve()
    return resolved.relative_to(REPO_ROOT.resolve()).as_posix() if resolved.is_relative_to(REPO_ROOT.resolve()) else str(resolved)


def build(gts_root: Path = DEFAULT_GTS, ds4_root: Path = DEFAULT_DS4,
          recovered_root: Path = DEFAULT_MAIN) -> dict[str, Any]:
    roots = {"gts": Path(gts_root), "ds4": Path(ds4_root), "recovered": Path(recovered_root),
             "cuw": Path(gts_root).parent / "CUWPlus",
             "recovered_ds4": Path(recovered_root).parent / "Auxiliary/DS-4"}
    sources: list[dict[str, Any]] = []
    images: dict[str, tuple[Any, bytes, int]] = {}
    for key, pin in SOURCE_PINS.items():
        path = roots[pin["root"]] / pin["relative"]
        raw = path.read_bytes()
        qualification = None
        if pin["root"] in {"recovered", "recovered_ds4"}:
            protected = roots["gts" if pin["root"] == "recovered" else "ds4"] / pin["relative"]
            component = roots["recovered"] if pin["root"] == "recovered" else roots["recovered_ds4"].parent
            qualification = qualify_recovered_source(path, protected, component_root=component)
            if len(raw) != pin["size"] or sha256_bytes(raw) != pin["sha256"]:
                raise ValueError(f"qualified recovered source identity drift: {key}: {path}")
        elif len(raw) != pin["size"] or sha256_bytes(raw) != pin["sha256"]:
            raise ValueError(f"source identity drift: {key}: {path}")
        representation = "installed-original"
        if qualification is not None:
            representation = "manifest-qualified recovered PE"
        elif key == "settings_stub":
            representation = "installed-CP-stub"
        elif key == "settings_sidecar":
            representation = "installed-CP-sidecar"
        sources.append({"id": _id("source." + key), "path": _relative(path),
                        "sha256": sha256_bytes(raw), "size": len(raw), "representation": representation})
        if qualification is not None:
            sources[-1]["recovery"] = qualification
        if key in NATIVE_PINS or key in COMPLETE_NATIVE["native_regions"]:
            images[key] = pe_info(path)


    evidence: list[dict[str, Any]] = []
    for source, functions in NATIVE_PINS.items():
        pe, data, base = images[source]
        for name, pin in functions.items():
            label = source + "." + name
            body = read_va(pe, data, base, pin["va"], pin["size"])
            if sha256_bytes(body) != pin["sha256"]:
                raise ValueError(f"changed native body: {label}")
            anchors = []
            for va, expected in BRANCH_ANCHORS.get(label, []):
                raw = read_va(pe, data, base, va, len(bytes.fromhex(expected)))
                if raw.hex() != expected:
                    raise ValueError(f"decisive instruction drift: {label} at {va:#x}")
                anchors.append({"va": f"0x{va:08X}", "bytes": expected})
            evidence.append({"id": _id(label), "source": _id("source." + source),
                             "kind": "native-body", "locator": f"0x{pin['va']:08X}",
                             "size": pin["size"], "body_sha256": pin["sha256"],
                             "anchors": anchors, "finding": FINDINGS[label]})

    nic_path = Path(gts_root) / "bin/GtsPlus-NicManager.dll"
    nic_proof = validate_managed_bodies(nic_path)
    evidence.append({"id": _id("nic.materialization"), "source": _id("source.nic"),
                     "kind": "managed-body-materialization",
                     "locator": "all MethodDef classifications; complete valid IL bodies", **nic_proof,
                     "finding": "Every required IL body passes full decoding, framing, operand and branch validation; native and legitimately bodyless methods remain separately classified."})
    nic = _open(nic_path)
    nic_findings = {
        "nic_info": "GetPrivateIpInfo requests NIC types6(Ethernet) and71(Wireless80211), returns first collected address plus display-screen setting; no addresses => Result=false/error enum1; caught exception=>false/error enum0.",
        "nic_enumerate": "Enumerate GetAllNetworkInterfaces and collect matching addresses through closure callbacks; no socket connections or traffic are emitted by this enumeration.",
        "nic_filter": "Require at least one gateway, OperationalStatus.Up(1), and selected interface type; then enumerate unicast addresses. Method name private does not impose RFC1918 filtering.",
        "nic_ipv4": "Keep only AddressFamily.InterNetwork(2), append address.ToString; no RFC1918/subnet test occurs."}
    for key, expected in MANAGED_PINS.items():
        row, instructions, body = _instructions(nic, expected["type"], expected["method"])
        actual = _method_pin(row, body)
        if any(actual[field] != expected[field] for field in actual):
            raise ValueError(f"managed body drift: {key}")
        start = instructions[0].offset
        il_anchors = []
        for ins in instructions:
            op = str(ins.opcode)
            operand = format_operand(nic, ins.operand)
            if (op.startswith(("br", "beq", "bne", "ldc.i4"))
                    or (op in ("call", "callvirt") and "object at" not in operand)):
                il_anchors.append({"offset": ins.offset - start, "opcode": op, "operand": operand})
        evidence.append({"id": _id(key), "source": _id("source.nic"), "kind": "managed-IL",
                         "locator": expected["type"] + "::" + expected["method"],
                         **actual, "anchors": il_anchors, "finding": nic_findings[key]})

    for source, (va, expected, dll_va, export_va) in REGISTRATION_PINS.items():
        pe, data, base = images[source]
        anchors = [(va, expected),
                   (dll_va, ("MsgDatComm.dll" + "\0").encode("utf-16le").hex()),
                   (export_va, b"ER_PutLogCommunication\0".hex())]
        for address, raw in anchors:
            if read_va(pe, data, base, address, len(bytes.fromhex(raw))).hex() != raw:
                raise ValueError(f"log callback registration drift: {source}")
        evidence.append({"id": _id(source + ".registration"), "source": _id("source." + source),
                         "kind": "native-instruction-dataflow", "locator": f"0x{va:08X}",
                         "anchors": [{"va": f"0x{address:08X}", "bytes": raw} for address, raw in anchors],
                         "finding": "LoadLibraryW(MsgDatComm.dll), test returned module, GetProcAddress(ER_PutLogCommunication), store callback; no callback means forwarding is skipped."})

    exports = lambda key: sorted(sym.name.decode("ascii") for sym in images[key][0].DIRECTORY_ENTRY_EXPORT.symbols
                                 if sym.name)
    if any(name.startswith("J2534CtrlNDIS") for name in exports("ds4")):
        raise ValueError("DS-4 transport export boundary drift")
    evidence.append({"id": _id("ds4.export_boundary"), "source": _id("source.ds4"),
                     "kind": "export-table", "locator": "PE export directory",
                     "finding": "DS-4 controller has ordinary/v0500 PassThru APIs but no J2534CtrlNDIS exports; its Ethernet implementation is driver-mediated.",
                     "api0500_exports": [name for name in exports("ds4") if "0500" in name]})

    state_specs = [
        ("selected", "settings provider/UI", "Selected VCI registry04/05 paths persisted; no channel assumed"),
        ("device_open", "J2534Ctrl singleton", "Driver API opened, device ID stored; API version is explicit"),
        ("channel_open", "CJ2534v2/KGP protocol object", "Physical protocol channel established and required filter setup succeeded"),
        ("ndis_discover", "GTSPlus CCommCtrlISO13400_NDIS", "VCI supplies selected NIC; UDP identification/TCP setup in progress"),
        ("ndis_active", "GTSPlus J2534Ctrl process globals", "TCP routing-activation exchange passed current checks"),
        ("ds4_ethernet_physical", "DS-4 CCommCtrlISO13400", "API05 Ethernet physical channel800F open"),
        ("ds4_ethernet_logical", "DS-4 CCommCtrlISO13400", "IP4/UDP/TCP logical channels established and routing response accepted"),
        ("adopted", "KGP general interface caller", "In-process supplied numeric device/protocol/channel IDs copied; ownership contract is caller-dependent"),
        ("aborted", "KGP CCommFrameCtrl", "Communication service stopped and ECU/session cleared; module may remain open"),
        ("fault_returned", "calling diagnostic layer", "Failure returned; channel/socket cleanup must be determined from the failing path, not assumed"),
        ("disconnected", "KGP CCommFrameCtrl", "Protocol object cleared; device may remain open for non-DENSO reconnect"),
        ("finalized", "KGP/J2534Ctrl", "Controller singleton destroyed and module unloaded after best-effort close"),
        ("log_pending", "CJ2534v2 save worker", "Save event signaled"),
        ("log_attempted", "CJ2534v2 save worker", "Save hook completed and finish signaled; current shipped shim hook returns0 without persisting")]
    states = [{"id": _id(name), "owner": owner, "meaning": meaning} for name, owner, meaning in state_specs]
    transitions = []
    def edge(name: str, source: str, dest: str, trigger: str, guard: str,
             action: str, *proof: str) -> None:
        transitions.append({"id": _id(name), "from": _id(source), "to": _id(dest),
                            "trigger": trigger, "guard": guard, "action": action,
                            "evidence": [_id(p) for p in proof]})
    edge("initialize", "selected", "device_open", "KGP OpenDevice", "valid selected registry/API and open succeeds",
         "Load provider/driver or shim; initialize singleton and deviceID", "kgp.open", "j2534.initialize", "j2534.open0404", "j2534.scan_open0500")
    edge("initialize_failure", "selected", "fault_returned", "initialize/open fails", "null/already-open/bad API/config/registry/load/open failure",
         "Return exact error; failed post-constructor open destroys singleton", "j2534.initialize")
    edge("version_fallback", "fault_returned", "device_open", "ReadVersion API1 open failure", "ReadVersion had no module, API2 open succeeds",
         "Close failed API1 and try API2 once", "kgp.read_version")
    edge("connect", "device_open", "channel_open", "protocol selected by bus", "protocol/flags valid; channel and filters succeed",
         "Choose transport class, connect real driver, install filters and mark channel connected", "kgp.change_interface", "j2534.connect0404", "j2534.filter")
    edge("filter_failure", "device_open", "fault_returned", "default-filter installation fails", "PassThruConnect succeeded but required setup fails",
         "Attempt controller disconnect, but +5D guard returns2 before physical disconnect; return setup failure with possible physical channel retained", "j2534.connect0404", "j2534.disconnect0404")
    edge("adopt", "device_open", "adopted", "SetConnectInfo + ConnectCommIFGeneral", "caller supplies numeric device/protocol/channel IDs",
         "Copy128-byte protocol table and attach first existing channel, not another PassThruConnect", "kgp.set_connect_info", "kgp.connect_general", "kgp.adopt_connection")
    edge("ndis_start", "device_open", "ndis_discover", "bus nibble4 in current GTSPlus", "VCI selector54 reports1/1",
         "Open auxiliary8013 and poll selected NIC; read Ethernet DB parameters", "kgp.change_interface", "kgp.ndis_connect", "kgp.ndis_db_parameters")
    edge("ndis_activate", "ndis_discover", "ndis_active", "NIC available and vehicle identification succeeds", "routing response type6 and source echo match",
         "Bind TCP(selectedIPv4,0), connect port13400, routing activation type5", "j2534.ndis_connect")
    edge("ndis_discovery_retry", "ndis_discover", "ndis_discover", "vehicle-ID receive timeout8001", "fewer than2 attempts",
         "Rebroadcast once; non-timeout failures return immediately", "j2534.vehicle_id", "j2534.vehicle_id_receive")
    edge("ndis_setup_failure", "ndis_discover", "fault_returned", "NIC/UDP/TCP/routing failure", "timeout, socket error, invalid response",
         "Return error without guaranteed immediate socket cleanup; use teardown", "j2534.ndis_connect")
    edge("ndis_exchange", "ndis_active", "ndis_active", "diagnostic send/receive", "two-byte logical addresses; bounded payload; ACK and response checks pass",
         "Send8001, validate8002 ACK, receive8001 response; no implicit resend in current NDIS send", "j2534.ndis_send", "j2534.ndis_ack", "j2534.ndis_receive")
    edge("ndis_exchange_failure", "ndis_active", "fault_returned", "socket timeout/EOF, invalid type/length/address or negative ACK", "corresponding byte checks fail",
         "Return8000/8002/8003/8017 or specific API error; do not assume reconnect", "j2534.ndis_ack", "j2534.ndis_receive")
    edge("ds4_ethernet_open", "device_open", "ds4_ethernet_physical", "DS-4 bus nibble4", "API2 selected and physical setup succeeds",
         "Connect_v0500 protocol800F100Mbps, resource parameters and link flag", "ds4_kgp.change_interface", "ds4_kgp.ethernet_physical")
    edge("ds4_ethernet_activate", "ds4_ethernet_physical", "ds4_ethernet_logical", "DS-4 Ethernet setup", "logical connects and type4/type6 responses accepted",
         "Logical8203->8205, vehicle-ID; logical8206, routing activation over8208 stream", "ds4_kgp.ethernet_connect", "ds4_kgp.ethernet_logical", "ds4_kgp.ethernet_udp", "ds4_kgp.ethernet_routing")
    edge("ds4_ethernet_exchange", "ds4_ethernet_logical", "ds4_ethernet_logical", "diagnostic send/receive", "DoIP type/address/length and classifier checks pass",
         "Queue cached type8001 byte stream, receive ACK/response with bounded pending/requeue policy", "ds4_kgp.ethernet_send", "ds4_kgp.ethernet_receive")
    edge("ds4_ethernet_failure", "ds4_ethernet_physical", "fault_returned", "DS-4 logical setup fails", "logical open/discovery/routing error",
         "Return91020306; owner teardown closes any established intermediate IDs", "ds4_kgp.ethernet_connect", "ds4_kgp.ethernet_teardown")
    edge("abort", "channel_open", "aborted", "CommunicationAbort", "protocol object exists",
         "Signal workers and stop protocol service; clear ECU/session, retain transport object", "kgp.abort")
    edge("disconnect", "channel_open", "disconnected", "Disconnect", "protocol exists",
         "Stop activity, protocol disconnect/destruct and clear channel/session state", "kgp.disconnect", "j2534.disconnect0404")
    edge("ndis_stop", "ndis_active", "disconnected", "NDIS protocol disconnect", "backend may be partially allocated",
         "Close TCP/UDP+WSA then auxiliary PassThru channel, suppress socket cleanup errors", "kgp.ndis_disconnect", "kgp.ndis_disconnect_backend", "j2534.ndis_disconnect")
    edge("ndis_failed_stop", "fault_returned", "disconnected", "explicit NDIS teardown after failure", "socket globals indicate partial startup",
         "Best-effort shutdown/close/WSACleanup and clear globals", "j2534.ndis_disconnect")
    edge("ds4_ethernet_stop", "ds4_ethernet_logical", "disconnected", "DS-4 Ethernet disconnect", "logical/physical IDs may be partial",
         "Stop service; closeTCP,UDP,IP4 logical then physical, with configured inter-stage waits", "ds4_kgp.ethernet_disconnect", "ds4_kgp.ethernet_teardown")
    edge("reconnect", "disconnected", "channel_open", "subsequent ChangeCommIF", "compatible retained driver or successful reopen",
         "Rebuild selected protocol object; transport/family changes may finalize/reopen first", "kgp.change_interface", "kgp.disconnect")
    edge("close", "disconnected", "finalized", "CloseDevice/diagnostic owner destruction", "module loaded",
         "Best-effort close, singleton destruction, worker stop, unload; outer status can be0 despite close error", "kgp.close", "kgp.finalize", "j2534.finalize", "j2534.destructor")
    edge("failed_close", "fault_returned", "finalized", "explicit CloseDevice/owner cleanup after startup failure", "singleton/module remains loaded",
         "Close still-open physical device, destroy controller and unload; no automatic hardware-reset/reconnect guarantee", "j2534.close", "j2534.finalize", "j2534.destructor", "kgp.close")
    edge("log_flush", "log_pending", "log_attempted", "SAVE_J2534_LOG_FILE_EVENT", "non-direct-DENSO shim route and worker alive",
         "Call settings-backed SaveLog hook and signal finish; current04/05 shim hook is no-op success", "j2534.save_worker", "j2534.save_log", "shim0404.savelog", "shim0500.savelog")

    edge("filter_failure_reconnect", "fault_returned", "channel_open", "next API04 Connect after default-filter failure",
         "open+5C=1, connected+5D=0, next driver Connect and setup succeed",
         "Overwrite last channel+74; old numeric channel not disconnected by guarded rollback; inherited translation flags can survive",
         "j2534.connect0404", "j2534.read0404", "kgp.base_connect", "kgp.base_disconnect", "ds4.connect0404")
    edge("disconnect_driver_failure", "channel_open", "disconnected", "physical Disconnect returns nonzero",
         "API04 export resolved and invoked; error-reporting callbacks return normally",
         "Clear software connected/filter/translation state despite error; next Connect allowed, retained ID is not proof of live hardware",
         "j2534.disconnect0404", "ds4.disconnect0404", "kgp.base_disconnect")
    edge("disconnect_export_failure", "channel_open", "fault_returned", "Disconnect export missing",
         "API04 module/open/channel gates pass",
         "Return7 without clearing controller bookkeeping; subsequent API04 Connect rejects14 until state-changing teardown",
         "j2534.disconnect0404", "ds4.disconnect0404")
    edge("api05_repeated_connect", "channel_open", "channel_open", "another API05 physical Connect",
         "module/open gates pass; driver returns success",
         "No connected guard: invoke driver again and replace last physical ID; API05 logical IDs are separately KGP-owned",
         "j2534.connect0500", "ds4.connect0500", "ds4.logical_connect0500")
    edge("api05_repeat_disconnect", "disconnected", "disconnected", "API05 Disconnect after software flag cleared",
         "module/open and export present",
         "Invoke supplied physical channel again even with+5D=0; clear+5D after invocation, preserve numeric+74",
         "j2534.disconnect0500", "ds4.disconnect0500")
    edge("close_error_reconnect", "channel_open", "fault_returned", "Close returns driver failure",
         "disconnect attempted before Close; Close nonzero",
         "Return7 and preserve open/device; when disconnect cleared+5D next API04 Connect is allowed, while Open rejectsE",
         "j2534.close", "ds4.close", "j2534.open0404")
    edge("adopted_disconnect", "adopted", "disconnected", "ordinary KGP Disconnect",
         "adoption set KGP+0C without separate borrowed-ownership marker",
         "Use ordinary disconnect callback for adopted channel; controller API04 may reject2 if its independent+5D is clear",
         "kgp.adopt_connection", "kgp.base_disconnect", "j2534.disconnect0404")
    edge("ds4_failed_open_retry", "fault_returned", "fault_returned", "DS-4 Initialize repeated after failed Open",
         "post-constructor singleton retained",
         "ReturnE before another Open; explicit Finalize or KGP CloseDevice is required to release singleton",
         "ds4.initialize", "ds4.finalize", "ds4_kgp.open")
    edge("ndis_parser_retry", "ndis_active", "fault_returned", "invalid header or partial-body timeout",
         "header consumed; rejected body left queued or partially consumed",
         "Return parser error without drain/socket close/persistent assembly; next receive starts a new8-byte header, not continuation",
         "j2534.ndis_receive", "j2534.ndis_ack")

    handoffs = [
        {"to_domain": "auth_settings", "caller": "J2534CtrlInitialize/GetDeviceInfo", "callee": "GetFileDataFromType(3)",
         "mechanism": "in-process DLL API + persisted settings", "payload": "vim.name, registry0404, registry0500; then selected HKLM FunctionLibrary/Vendor/Name",
         "evidence": [_id("j2534.initialize"), _id("settings.file_type")],
         "producer_evidence": ["auth_settings.vim_select", "auth_settings.vim_registry0404", "auth_settings.vim_registry0500"]},
        {"to_domain": "operations", "caller": "diagnostic CCommCtrlSub destructor", "callee": "CCommFrameCtrl::Disconnect(1), CloseDevice",
         "mechanism": "in-process destruction contract", "payload": "stop service/session then dispose channel/device",
         "evidence": [_id("kgp.disconnect"), _id("kgp.close")],
         "caller_evidence": ["operations.diagnosis_exit", "operations.adapt_cleanup", "operations.aggregate_exit"]},
        {"to_domain": "operations", "caller": "PassThruWrapNK/PassThruWrapFrontNK", "callee": "J2534Ctrl exports",
         "mechanism": "GetProcAddress + cached function pointer in same process", "payload": "raw API arguments and numeric IDs; broker installation root key6F or caller-supplied HMODULE",
         "evidence": [_id("wrap.load_modules"), _id("wrap.bind"), _id("front.set_handle"), _id("front.bind")]},
        {"to_domain": "vci_transport", "external_owner": "Windows VCI driver", "caller": "CJ2534v2", "callee": "registry-selected physical FunctionLibrary",
         "mechanism": "direct DENSO DLL or ptshim04/05 dispatch", "payload": "J2534 device/channel/filter/message/resource structures",
         "evidence": [_id("j2534.driver_constructor"), _id("j2534.connect0404"), _id("ds4_kgp.ethernet_physical")]},
        {"to_domain": "persistence", "caller": "ptshim04/05 and WinsockLogger", "callee": "MsgDatComm.ER_PutLogCommunication",
         "mechanism": "in-process UTF16 callback, then persistence-owned named-pipe IPC", "payload": "API arguments, outgoing/received message bytes and status",
         "evidence": [_id("shim0404.log_forward"), _id("shim0500.log_forward"), _id("ds4_shim0404.log_forward"), _id("ds4_shim0500.log_forward"), _id("winsock.log_write"), _id("shim0404.registration"), _id("shim0500.registration"), _id("ds4_shim0404.registration"), _id("ds4_shim0500.registration"), _id("winsock.registration")],
         "consumer_evidence": ["persistence.comm_log_send", "persistence.comm_log_pull", "persistence.comm_log_clear"]},
        {"to_domain": "cuw_utility", "caller": "KGP/J2534Ctrl transport owner", "callee": "independent CUW backend transport owner",
         "mechanism": "ownership boundary, not a direct KGP-to-CUW call or numeric channel-handle transfer",
         "payload": "GTS releases VIM/transport; CUW model independently supplies selected J2534 identity to its native engine",
         "evidence": [_id("kgp.close"), _id("kgp.base_constructor"), _id("kgp.set_connect_info")],
         "counterpart_evidence": ["cuw_utility.ui-admission", "cuw_utility.cal-read", "cuw_utility.progress", "cuw_utility.native-clear"]}]
    persistence = [
        {"path_pattern": "<setting-provider-root>/PcSettings.gstg", "producer": "auth_settings ExecuteChangeSelectVim",
         "consumer": "J2534CtrlInitialize/GetDeviceInfo; KGP version/capability queries", "created": "settings subsystem SavePartialData(type3)",
         "flushed": "settings provider save contract (auth_settings)", "deleted": "not deleted by transport teardown",
         "evidence": [_id("settings.file_type"), _id("j2534.initialize")], "producer_evidence": ["auth_settings.vim_select"]},
        {"path_pattern": "<setting-provider-root>/GTSPlusCommon.gstg", "producer": "shipped/common settings subsystem",
         "consumer": "NDIS/DS-4 Ethernet setup, disconnect timing, J2534 log path", "created": "installation/settings owner",
         "flushed": "settings owner; transport reads only", "deleted": "not deleted by inspected transport methods",
         "evidence": [_id("settings.file_type"), _id("kgp.ndis_connect"), _id("ds4_kgp.ethernet_teardown"), _id("j2534.save_log")]},
        {"path_pattern": "HKLM/SOFTWARE/PassThruSupport.04.04/<selected key> or .05.00/<selected key>", "producer": "VCI driver installer",
         "consumer": "J2534Ctrl selected-driver loader", "created": "external installer", "flushed": "Windows registry owner",
         "deleted": "not deleted by inspected transport teardown", "evidence": [_id("j2534.initialize")]},
        {"path_pattern": "<CSIDL0x2E><path.productFolder>/ErrorReport/j2534_MMDDYYYYhhmmss.log",
         "producer": "J2534Ctrl save worker + selected shim", "consumer": "error report/capture tooling",
         "created": "not created by the current04/05 shim SaveLog stubs; controller constructs only the requested compatibility path",
         "flushed": "none through PassThruSaveLog; real log forwarding goes to MsgDatComm/persistence owner",
         "deleted": "not applicable to the no-op SaveLog hooks",
         "evidence": [_id("j2534.close"), _id("j2534.save_log"), _id("j2534.save_worker"), _id("shim0404.savelog"), _id("shim0500.savelog")]}]
    transports = [
        {"application_bus_low_nibble": "1/9", "transport": "ISO9141", "driver_protocol": "4", "evidence": [_id("kgp.change_interface"), _id("kgp.iso9141")]},
        {"application_bus_low_nibble": "2", "transport": "ISO15765 CAN (ordinary, P5, WWH/ISO27145, OBD ZEV-on-UDS)", "driver_protocol": "6; bus62 uses8005 and DB baud", "evidence": [_id("kgp.change_interface"), _id("kgp.can_phase5"), _id("kgp.can_wwh"), _id("kgp.can_obd_zev")]},
        {"application_bus_low_nibble": "3", "transport": "direct CAN", "driver_protocol": "5", "evidence": [_id("kgp.change_interface"), _id("kgp.direct_can")]},
        {"application_bus_low_nibble": "4", "transport": "ISO13400/DoIP", "driver_protocol": "GTSPlus API04 auxiliary8013 + host NDIS; DS-4 API05 physical800F + logical8203/8205/8206/8208", "evidence": [_id("kgp.ndis_connect"), _id("ds4_kgp.change_interface"), _id("ds4_kgp.ethernet_logical")]},
        {"application_bus_low_nibble": "6/7", "transport": "J1850PWM/VPW", "driver_protocol": "2/1", "evidence": [_id("kgp.change_interface"), _id("kgp.j1850")]},
        {"application_bus_low_nibble": "8", "transport": "29-bit CAN or CAN-FD", "driver_protocol": "GTSPlus18/38:6 flags800;78/88:8012 flags100800. DS-4:5/6 flags100, not this FD factory", "evidence": [_id("kgp.change_interface"), _id("kgp.can_29bit"), _id("kgp.can_fd"), _id("ds4_kgp.change_interface")]},
        {"application_bus_low_nibble": "A/C", "transport": "custom1000C CAN /1000D ISO9141DK", "driver_protocol": "DENSO extension or generic6/3 remapping", "evidence": [_id("kgp.change_interface"), _id("j2534.connect0404"), _id("kgp.iso9141dk")]}]
    complete = _complete_native_contracts(roots, images, sources, evidence, nic)
    platform = _platform_session_contracts({"GTSPlus": roots["gts"], "DS-4": roots["ds4"]},
                                          {"GTSPlus": roots["recovered"], "DS-4": roots["recovered_ds4"]}, sources, evidence)
    return {**complete, "schema": "gtsplus-lifecycle-domain-v1", "domain": DOMAIN, "sources": sources,
            "evidence": evidence, "states": states, "transitions": transitions,
            "handoffs": handoffs, "persistence": persistence, "transport_families": transports,
            "generic_communication_contracts": platform,
            "native_state_contracts": {
                "controller": {
                    "module": "+04", "open": "+5C", "connected_summary": "+5D",
                    "api_selector": "+60", "last_physical_channel": "+74", "device": "+78",
                    "default_filters": "+7C; linked list+64/+68/+6C/+70",
                    "translation": "main+7E/+7F/+80; DS-4+7E/+7F",
                    "custom_mode": "main dword+84; DS-4 dword+80",
                    "summary_not_channel_count": True,
                    "evidence": [_id(name) for name in (
                        "j2534.connect0404", "j2534.disconnect0404", "j2534.read0404",
                        "j2534.connect0500", "j2534.disconnect0500", "j2534.read0500",
                        "j2534.close", "ds4.connect0404", "ds4.disconnect0404", "ds4.close")]},
                "protocol_owner": {
                    "connected": "+0C", "channel": "+08", "device": "+20E0", "protocol": "+20D8",
                    "adoption": "sets KGP connected/device/protocol/channel; no separate borrowed marker",
                    "independent_flags": "adoption does not set controller open/connected bytes",
                    "evidence": [_id("kgp.base_connect"), _id("kgp.base_disconnect"), _id("kgp.adopt_connection")]},
                "physical_outcome_boundary": "Missing/guarded driver call is proven absence of a call; driver-returned failure and numeric IDs do not establish live hardware allocation or leak."},
            "receive_parser_ownership": [
                {"route": "main host NDIS", "owner": "J2534Ctrl",
                 "fragmentation": "accumulate exact8-byte header then exact declared body from positive short recv results",
                 "checks": "diagnostic8001,length>=4,caller payload capacity,both reversed logical addresses; ACK8002/8003 and body>=4",
                 "not_checked": "version/inverse,ACK code,declared length against fixedFFFF-byte global scratch",
                 "failure_continuation": "no body drain on rejected header; no persistent partial frame; no parser-triggered socket teardown",
                 "evidence": [_id("j2534.ndis_receive"), _id("j2534.ndis_ack"), _id("j2534.address_compare"), _id("winsock.receive")]},
                {"route": "DS-4 API05 Ethernet", "owner": "KGP DoIP framing; external FunctionLibrary fulfills each requested stream block",
                 "fragmentation": "controller and shim make one ReadMsgs call; KGP requires exact block DataSize, splits long body at0x1020=4128",
                 "checks": "ACK minimum13,type8002,ECU source; diagnostic header minimum8,type8001,length>=5,caller capacity,exact first/subsequent body sizes",
                 "not_checked": "version/inverse,logical destination,ACK declared length or code",
                 "classifier": "diagnostic7F xx78 pending;7F xx21 requeue;other7F negative response; no framing/address checks",
                 "evidence": [_id("ds4_kgp.ethernet_receive"), _id("ds4_kgp.ethernet_classifier"),
                              _id("ds4.read0500"), _id("ds4_shim0500.read_stream"), _id("ds4_shim0500.read_clock")]}],
            "support_family_distinction": "GTSPlus and DS-4 are parallel application/support builds; ECU category low5 controls support/session strategy, application bus low nibble selects transport. P6 does not imply DoIP, nor P5 only CAN.",
            "coverage": {"components": ["GTSPlus native frame controller and J2534 singleton", "DS-4 native factory and driver-mediated ISO13400", "v04.04/v05.00 loader and shim interposition", "managed NIC enumeration", "pass-through wrappers and adopted channels", "settings/config ownership"],
                         "entrypoints": ["Initialize/Finalize", "Open/Connect/Filter/Disconnect/Close", "ReadVersion fallback", "ChangeCommIF/SetConnectInfo/general adoption", "NDISConnect/Send/Receive/Disconnect", "DS-4 ISO13400 physical/logical/vehicle-ID/routing", "CommunicationAbort", "Save/Finish log events", "GetPrivateIpInfo"],
                         "branches": ["selected API04/API05 registry paths", "direct DENSO versus shim", "default-filter rollback rejected by unset connected flag", "disconnect failure bookkeeping", "two-attempt UDP identification", "TCP setup/EOF/timeout/address/type errors", "DS-4 pending180000ms/classifier requeue limit256", "same-protocol reuse versus finalize/reopen", "adopted versus newly opened IDs", "best-effort teardown and worker forced-stop5000ms", "current shim SaveLog no-ops versus MsgDatComm log callback"]},
            "residuals": [
                {"question": "Which installed Windows registry entries and physical VCIs are actually usable?", "why_unclosed": "Offline shipped application has no target Windows registry/device state; selected FunctionLibrary implementations and VCI firmware are external transport owners.", "next_evidence": "Authorized Windows registry/device metadata and driver-specific source/capture, without network/vehicle interaction in this pass."},
                {"question": "Actual selected-driver allocation/release acknowledgement and byte-stream fulfillment", "why_unclosed": "Complete host paths prove calls, arguments, software resets and parser boundaries, not the physical FunctionLibrary implementation or VCI firmware state. No hardware leak/reset or API05 stream-fulfillment guarantee follows from numeric IDs or returned host status.", "next_evidence": "Selected external FunctionLibrary source or authorized offline driver contract."}],
            "reproduction": {"command": "uv run --locked python -m tools.techstream.extract_gtsplus_lifecycle_vci_transport",
                             "recovery_prerequisite": str(DEFAULT_MAIN) + " with exact manifest-qualified installed CP sources",
                             "network_or_vehicle_access": False}}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gts-root", type=Path, default=DEFAULT_GTS)
    parser.add_argument("--ds4-root", type=Path, default=DEFAULT_DS4)
    parser.add_argument("--recovered-root", type=Path, default=DEFAULT_MAIN)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    artifact = build(args.gts_root, args.ds4_root, args.recovered_root)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n")
    print(f"Wrote {args.out}: {len(artifact['evidence'])} evidence, {len(artifact['transitions'])} transitions")


if __name__ == "__main__":
    main()
