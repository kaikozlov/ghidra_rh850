#!/usr/bin/env python3
"""Extract pinned offline GTS+/DS-4 VCI and transport lifecycle evidence.

No Windows APIs, drivers, network sockets or vehicles are invoked. Native roles
were established by Ghidra decompilation and decisive disassembly; this extractor
fails closed on source/body/branch drift and reconstructs the compact contracts.
Recovered setting-provider bodies require the separately reproducible main
recovery manifest. Cross-domain producers are owned by auth_settings/operations.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from tools import REPO_ROOT
from tools.techstream.extract_gtsplus_tss3_native_recorder import pe_info, read_va, sha256_bytes
from tools.techstream.extract_gtsplus_tse_managed_semantics import _open, _instructions, _method_pin
from tools.techstream.inspect_dotnet_il import format_operand

DEFAULT_TREE = REPO_ROOT / "software/Techstream/gtsplus/unpacked/gtsplus/Toyota Diagnostics"
DEFAULT_GTS = DEFAULT_TREE / "GTSPlus"
DEFAULT_DS4 = DEFAULT_TREE / "DS-4"
DEFAULT_RECOVERED = REPO_ROOT / "build/out/gtsplus-unprotected"
DEFAULT_OUT = REPO_ROOT / "data/generated/gtsplus_2026/lifecycle_vci_transport.json"
DOMAIN = "vci_transport"

SOURCE_PINS = {'j2534': {'root': 'gts',
           'relative': 'bin/J2534Ctrl.dll',
           'sha256': 'dd571d19c229dd484fe6da71280110e3362a7fe09e41a1ddb1279331fd326520',
           'size': 197136},
 'kgp': {'root': 'gts',
         'relative': 'bin/KGP_CommFrameCtrl.dll',
         'sha256': '5366aba0f1da6ec7806cb6c8346a4429ce61b9ac7b1495be53e35ee6263b9517',
         'size': 379920},
 'ds4': {'root': 'ds4',
         'relative': 'bin/J2534Ctrl.dll',
         'sha256': '9d2e96eb9202122c43dc5c33b89dc82fc6ec3e3f93f61a29e8caf91c5deef57e',
         'size': 182288},
 'settings': {'root': 'recovered',
              'relative': 'bin/GTSPlusSettingFileManager.dll',
              'sha256': '20fd47aac7d0e427f4012d9421fe039e309e5d1f704a11c40de280bf3e7c8f8d',
              'size': 389648},
 'settings_stub': {'root': 'gts',
                   'relative': 'bin/GTSPlusSettingFileManager.dll',
                   'sha256': '7b072b893e6f3e0a92004bed66cc5a57bf6c9c7bd608544a1dfe09230ef6ea61',
                   'size': 90128},
 'settings_sidecar': {'root': 'gts',
                      'relative': 'bin/GTSPlusSettingFileManager.dll._',
                      'sha256': '9e5f6431d41363baed9d88b986481f7bd79b149c8f39e29fd67a87565e5a260e',
                      'size': 363952},
 'nic': {'root': 'gts',
         'relative': 'bin/GtsPlus-NicManager.dll',
         'sha256': 'a3ac41c87c65e48f2f7e9d5d49b91c0e22b77c06f0f1e7c9419ec08a4ee1ff6b',
         'size': 16400},
 'winsock': {'root': 'gts',
             'relative': 'bin/WinsockLogger.dll',
             'sha256': 'e310929d9a4c6ebf9c304a086dfb3535ae8c597242e7437cf75e72f207bb72a1',
             'size': 52752},
 'wrap': {'root': 'gts',
          'relative': 'bin/PassThruWrapNK.dll',
          'sha256': 'd6de0a03bc8cecd31ace44508277dddb965150c3adcace77aa850ededb3b48e3',
          'size': 57360},
 'front': {'root': 'gts',
           'relative': 'bin/PassThruWrapFrontNK.dll',
           'sha256': '636c395728abf795ba10a7eb09504b54217b42562bfe1055d9c56e57163672c4',
           'size': 59408},
 'ds4_kgp': {'root': 'ds4',
             'relative': 'bin/KGP_CommFrameCtrl.dll',
             'sha256': 'c49948cea8c84a11dffbdcdcc0606d00d95bb40c1c9c138b13d3f753aa6b1961',
             'size': 317968},
 'shim0404': {'root': 'gts',
              'relative': 'bin/ptshim32.dll',
              'sha256': '2d420374d703d28c8a38480c808ba1d39c0bd8848956af359ba28f4f849aed6e',
              'size': 2105872},
 'shim0500': {'root': 'gts',
              'relative': 'bin/ptshim32_0500.dll',
              'sha256': 'df41cef16cae1ab5272ceffb7568eb195948b03ace3a795000d07919c4795673',
              'size': 2119696}}
SOURCE_PINS.update({
    "ds4_shim0404": {"root": "ds4", "relative": "bin/ptshim32.dll",
                     "sha256": "1c1e61da748104032c2b3826e386b1eadd37d0f4efa1d33f8076f4766fa806c9", "size": 2106384},
    "ds4_shim0500": {"root": "ds4", "relative": "bin/ptshim32_0500.dll",
                     "sha256": "664fa06364c0599dc9fa54d0fadd31642219d10d4f03e93cd72f7f79ff14da64", "size": 2119696},
})

NATIVE_PINS = {'j2534': {'initialize': {'va': 268508416,
                          'size': 2581,
                          'sha256': 'a0f59f4ad17c13289b44be72e93b62c700ff0be8652f2c461e50003f8f905ab8'},
           'finalize': {'va': 268508256,
                        'size': 158,
                        'sha256': 'c222743125fef13e1b3c91bba560ca75de2b89a310ccd5d2ea6f40d1586407f2'},
           'driver_constructor': {'va': 268525200,
                                  'size': 1253,
                                  'sha256': 'f1a7622fe2298167f356b60c58b8278d966dbf900afe9127ac717ca5aa33ef90'},
           'open0404': {'va': 268535280,
                        'size': 504,
                        'sha256': 'b81684ff7733dbfead28f3cdf900f70066d0962a46ed7c337b74019de8d6df14'},
           'scan_open0500': {'va': 268535792,
                             'size': 502,
                             'sha256': '6e3007783cadbbc6d36b96bf94e962343f7b27c6444dc74a6197897ae8cb9d5b'},
           'connect0404': {'va': 268537296,
                           'size': 4897,
                           'sha256': '4ddc71c90b63c7a128c0b59ef00e07b9295dbe906c3448a218d103614914a6d6'},
           'disconnect0404': {'va': 268542416,
                              'size': 461,
                              'sha256': '0da8e6bb4f41aca6df0fa79b1393848d554e41e4443b732bdd6c023efed3f081'},
           'close': {'va': 268533440,
                     'size': 464,
                     'sha256': '5527bf782e2afccb5742cee9f63493f19a4226797e229a2a3ed9cabbfc308ff1'},
           'device_info': {'va': 268502464,
                           'size': 3063,
                           'sha256': '1bda26afbad45558c725273bc0639033dac4a4519b384f0262336e3caf5cb643'},
           'device_info0500': {'va': 268505536,
                               'size': 2390,
                               'sha256': '360d8a1465b939743dbf1b0d97879bbac42d8336e87c42f97f2921fc9986cabb'},
           'save_worker': {'va': 268533264,
                           'size': 134,
                           'sha256': 'a77cbbe1df129577f1ce5902e9581082f9feb5e902d72227885108e953a52ef7'},
           'save_log': {'va': 268550080,
                        'size': 1581,
                        'sha256': '272082c84eb49dc3638424826064c4ce0dc3eb67c6ee0f45d239d447d43a64d8'},
           'ndis_connect': {'va': 268511008,
                            'size': 3488,
                            'sha256': 'f78be125e2ca1ea1d21c4472e8b7313c32a8238e2241ae153a6e1f24f3b49fad'},
           'ndis_disconnect': {'va': 268514512,
                               'size': 289,
                               'sha256': 'a0327b71d3aa9f29f07e3894f8c670434d12023b4a8b8385eb5914cedf101690'},
           'ndis_send': {'va': 268516016,
                         'size': 1008,
                         'sha256': '526d06ad4cd4dfc498cde1f021a2af5daad198788fa231dbaf35aa58597dea64'},
           'ndis_receive': {'va': 268514816,
                            'size': 1188,
                            'sha256': 'ce05537cc4a70d31dee97742feb555f732f41a7531f5e412f0c6c33db493a60f'},
           'vehicle_id': {'va': 268501008,
                          'size': 888,
                          'sha256': '94d8aa66cb9feeaf4a00b8165595ba87e36d615d42bb87c208e42e0dcfe3cece'},
           'vehicle_id_receive': {'va': 268500256,
                                  'size': 737,
                                  'sha256': 'b50937ac43c0700a776e02d1a547949f504950317fca40cf29252d4471210d25'},
           'ndis_ack': {'va': 268499216,
                        'size': 1027,
                        'sha256': 'b35bbf9c267708bba163e25af42b163eff29cd5b98c80ddec925524b8743bc0d'},
           'filter': {'va': 268552256,
                      'size': 3260,
                      'sha256': '908ece8da0681fc30bb59fd758cf7b2dc0ea2c8b4c4b15b69e7707763d4fd49d'},
           'destructor': {'va': 268526576,
                          'size': 354,
                          'sha256': '724555f67ce4725286ae4c6fa12e210e81ce2637a4b544453c0bc4fc7ea80b63'}},
 'kgp': {'open': {'va': 268658208,
                  'size': 366,
                  'sha256': '54dd7e67d5d2d0e100a6ab35030c0261aafbf6fd4caa8f28f59c6a8d6ed1794c'},
         'open_j2534_2': {'va': 268658576,
                          'size': 369,
                          'sha256': '32eac1733860c898024d91a1c1a3f1ace8fafe3957bab5754298c5d468a0e9cf'},
         'change_interface': {'va': 268637424,
                              'size': 3454,
                              'sha256': '62b76e0b9e7cfcc9d1d2e3306e46bc2474c8cf37b5e40ae471c3cce46bc1e1cf'},
         'connect_general': {'va': 268644160,
                             'size': 2144,
                             'sha256': '64dbb7f4d531252dbc9c893c8e44f49c76c3e820c607be2d9e7184c454a7b543'},
         'disconnect': {'va': 268648720,
                        'size': 448,
                        'sha256': 'bee0fb37b8bf53393e8200bc99d2feaddff57646cacb3b60f15681f6b003a02c'},
         'finalize': {'va': 268649456,
                      'size': 96,
                      'sha256': 'fa18eb98d576977774a8dd42c06c82d4914e9309e39be4509fdc5faed0d32d69'},
         'close': {'va': 268642336,
                   'size': 55,
                   'sha256': '16015a3db0936f2ac34260e6f9ce7e751a2e0890a329a15f8893f2b90aa7071e'},
         'abort': {'va': 268642976,
                   'size': 601,
                   'sha256': 'e57691892732ab288c52377532ee6045d46353d6e64c7cfcfe94450a4d5363ea'},
         'base_constructor': {'va': 268512480,
                              'size': 2077,
                              'sha256': '76fae7e53de0996f496799c4609bcd1f252e289d400c334ee1f4e9613ca4fe33'},
         'ndis_constructor': {'va': 268559776,
                              'size': 160,
                              'sha256': '398724cfe49fc1c6eb1093f67713c191e68699b338ba472dac70c1546b80b177'},
         'ndis_connect': {'va': 268561184,
                          'size': 2067,
                          'sha256': '152ab25d7b7fadb17440695c37f059738fb946f763fcd7b12c8e1c24b7540cfd'},
         'ndis_disconnect': {'va': 268564160,
                             'size': 100,
                             'sha256': 'b0e4163eece3a457fc877646881674e7e77626e6b85af0ec252b0846fd598412'},
         'ndis_disconnect_backend': {'va': 268564272,
                                     'size': 38,
                                     'sha256': 'bb0db154d310e0733c1ca300397ace4716d0d2661c02b051182817404fe7998d'},
         'ndis_db_parameters': {'va': 268564464,
                                'size': 349,
                                'sha256': '94f122e97ff4ec7b184fa7522644f90cbf44f8a66dab165f12becfc738d73f1c'},
         'device_capabilities': {'va': 268651088,
                                 'size': 2414,
                                 'sha256': 'b09f43f877b9ddbd4edbf9a6c96dffef69069df3d04cf11f8ca5016bc956de43'},
         'can_iso15765': {'va': 268568624,
                          'size': 150,
                          'sha256': 'e526102cd1262de91cf343276bd4e767e0416e8a6167585b6248488ca8cb9912'},
         'can_phase5': {'va': 268600272,
                        'size': 59,
                        'sha256': 'f06946d886bc696648107163419a3acb9b3d999af1e9219ef771aa01406d3a13'},
         'can_obd_zev': {'va': 268581824,
                         'size': 46,
                         'sha256': '38b93f941ae5c253d89e6417ce0249dec08f7ca5698042c785d778054a7ffe41'},
         'can_wwh': {'va': 268605888,
                     'size': 39,
                     'sha256': '35b8a37eb3db493b5386fd476e096fd378df33aad9d4ff8d85e6eab5c76b127a'},
         'can_29bit': {'va': 268584592,
                       'size': 66,
                       'sha256': '92a8c6c94230debd461588bf40ccbbbccf43e3d57b7587451d8edf57a8e4b6f1'},
         'can_fd': {'va': 268624816,
                    'size': 66,
                    'sha256': '1b27498f83bbfe2412bca49fb2d576aaf64e20dab8ebbbbf08cce7a2dbded689'},
         'iso9141': {'va': 268608384,
                     'size': 48,
                     'sha256': 'fec8cea0d92054a61d30ea90e30ada64681f1699586aadc070c20ba73e30da9a'},
         'iso9141dk': {'va': 268618496,
                       'size': 48,
                       'sha256': 'afc35308b6423eabbfa7cac0641ab86e8f49a049642b3d1b0c32fa2dac97694f'},
         'j1850': {'va': 268621648,
                   'size': 39,
                   'sha256': '7326d3180a4a9cea98d0a98d0009adbf8f89662e612ed8babbc18b2c1682bc99'},
         'direct_can': {'va': 268536816,
                        'size': 39,
                        'sha256': '3824b7af2accbb8fed6dcd8e46f0ddde367e38627c0b254aed577f7350be614d'},
         'set_connect_info': {'va': 268668352,
                              'size': 457,
                              'sha256': 'd499973af2a66018e570716ff1a8e99658538786c9d63ead19ad25abd782a192'},
         'adopt_connection': {'va': 268668816,
                              'size': 73,
                              'sha256': '5d9cfe429a689f693d33c319327045dd3ebbc1cd6659eac099706f729ef2220e'},
         'read_version': {'va': 268659440,
                          'size': 404,
                          'sha256': '51ba6cab926dc9e0b012e80fdce418e6502e956b2283f38a9e9b9bef9387ee57'},
         'read_versions': {'va': 268659856,
                           'size': 2270,
                           'sha256': 'cf1dcccc0d5893e3a8b154491e20fbf9a0738e612c30e62a03116f71fa7b5c77'}},
 'ds4': {'initialize': {'va': 268505616,
                        'size': 3333,
                        'sha256': 'c873bb9d1578ea85b65c2ccccbb08eb50d54fd96b56c988d3817045040006648'},
         'finalize': {'va': 268505408,
                      'size': 194,
                      'sha256': '68884fb460e8a263d6f4e8932e2f72d9cfb51621c1c7730f66f561d0526d1e05'}},
 'settings': {'file_type': {'va': 268483392,
                            'size': 1077,
                            'sha256': '6a9c6e070ffd3bc526aaf15286304006f3c1d06abc8792f84eabe12db4a08f48'},
              'get_type': {'va': 268446336,
                           'size': 353,
                           'sha256': '5d9e3551596abb024fbdff7b5513b42b5ef7d5913a98559c73123040d5c192da'}},
 'winsock': {'send': {'va': 268448192,
                      'size': 99,
                      'sha256': '68359f860ec6667dce2ac813a52e04c4cecde49db48f55044f92cc59f9f12107'},
             'receive': {'va': 268447472,
                         'size': 96,
                         'sha256': '15f0153c866634b807dd050e5dbb92ecf417c2dd4c2242e4bb402802ebd10879'},
             'log_write': {'va': 268450240,
                           'size': 425,
                           'sha256': 'a1e87f54d1c38d95901da6920799a686a414d356c7a93abbea249bb1f79ca551'}},
 'wrap': {'initialize': {'va': 268440864,
                         'size': 104,
                         'sha256': '803bfcef15ce861e09d5c7b5cc9fb23c0c305573b71d8a4fca76a49527099e42'},
          'connect': {'va': 268441696,
                      'size': 104,
                      'sha256': '2d2e972e116c4f6b509bb83fe8e595fe3b0c6cdd32c0b655b8df0263c3752a35'},
          'load_modules': {'va': 268441424,
                           'size': 261,
                           'sha256': '0fe87b784eebccce4f4345b48fc4d7fbd35ac64ef6e97288dad0f08c7c4a73cc'},
          'bind': {'va': 268444224,
                   'size': 326,
                   'sha256': 'a4528e984c28a8a598f3deb23dc14cbcb64a51a26f54a36be1526d0a9685107f'},
          'lookup': {'va': 268444672,
                     'size': 163,
                     'sha256': '6310295413dc5230424a687c3900752364f9854163c60946483021a798c2d48e'}},
 'front': {'initialize': {'va': 268441856,
                          'size': 104,
                          'sha256': '41b0bc5e0d193ebdcf2f6989660fc90a8e097ac036f5795ee288e4df1ae4e60e'},
           'set_handle': {'va': 268445936,
                          'size': 57,
                          'sha256': '0bf3758a4bf2268102e87fc62d15556cc25fd9b2baf8413dd251fe2bf2e62d69'},
           'reset_handle': {'va': 268445824,
                            'size': 42,
                            'sha256': '85c5a6dd2e612f32739775c1660226ad24bac086ec68d0ac2e04d097149bb4af'},
           'bind': {'va': 268446000,
                    'size': 326,
                    'sha256': '094bda5341c149e371b398f1de27ddb851f57bc2da68bad036c3a97924f961a4'},
           'lookup': {'va': 268446688,
                      'size': 163,
                      'sha256': '614ff42920df7b98b45eaf054edb913a6cf43cd3b40338ab495ab9f0e9627d16'},
           'reset_storage': {'va': 268445872,
                             'size': 20,
                             'sha256': '2d3bfd4b7c836ac61ee45396dee515716c9aeb0c4ae070905b0e93cee4a644c5'}},
 'ds4_kgp': {'change_interface': {'va': 268596048,
                                  'size': 2662,
                                  'sha256': '1f66039b6dac54696ab095742defda6bbccce8396773b141d39694f2edac66e4'},
             'disconnect': {'va': 268607008,
                            'size': 443,
                            'sha256': '837302a682900c587cc50c39780efce072fcdc96fbf186f16a17b675698f3c98'},
             'open': {'va': 268614160,
                      'size': 364,
                      'sha256': 'bb8536fdf9598064529fe38c2d6af73f25f5aee509e26eb7b7296d459f8a1760'},
             'ethernet_constructor': {'va': 268531760,
                                      'size': 235,
                                      'sha256': 'b38cdaf4c0bba36a2b971537c56d50c4276c9b1ed0efd23752e28485952e84cf'},
             'can29_constructor': {'va': 268527296,
                                   'size': 39,
                                   'sha256': '0ab807cf56c69f5594560e5805f2815761bd188b2caae653a35c4ef8d25fc5a2'},
             'can29_normal_constructor': {'va': 268528592,
                                          'size': 39,
                                          'sha256': '179de8885ddb695dd358efe977e84977c1c97974395b7381495482cad5aa81f1'},
             'ethernet_connect': {'va': 268536240,
                                  'size': 880,
                                  'sha256': 'c89f912d0aca91f688d4c9f98eccbd14d22a1e9b02eafa3ecaa0b7b56e3dbf89'},
             'ethernet_disconnect': {'va': 268537920,
                                     'size': 100,
                                     'sha256': '9a03001a2de9f6cc8bf1a502ef7f69287802a50c47a008161e88febd9dd58fe8'},
             'ethernet_physical': {'va': 268539904,
                                   'size': 401,
                                   'sha256': 'de1f7ff5a93043f78d00f548e2a9d9d7d8382c1412ea19557f74880539bc0109'},
             'ethernet_logical': {'va': 268541456,
                                  'size': 1583,
                                  'sha256': '0cdce26adf5e0e3013eb68fc0b5a747362af887250f892a41b4cd75d7dcca4db'},
             'ethernet_udp': {'va': 268552256,
                              'size': 530,
                              'sha256': 'd804b22268d1cf71767ae3d502cb28d718dd0701754e3028b693aa04310648ca'},
             'ethernet_routing': {'va': 268551776,
                                  'size': 480,
                                  'sha256': '29b80559f152cffc726c9bd0d73517da5a0e01ad6370ba3ed9a0f6832f617b91'},
             'ethernet_teardown': {'va': 268538032,
                                   'size': 1857,
                                   'sha256': '562ca268dfa41896eab0e4fdfbaa9f325df1e156f614b4262ede03ee6f08e107'},
             'ethernet_send': {'va': 268550448,
                               'size': 546,
                               'sha256': '9632077c8f37f48d7647f9c9b7f14acf90ad0029c4a74502569d506bdc488fbe'},
             'ethernet_receive': {'va': 268543056,
                                  'size': 2830,
                                  'sha256': 'd69cd353d7a1653edc0fb57cc3b018bbd2b21a191cee647728192f5482fa6a79'}}}

MANAGED_PINS = {'nic_info': {'type': 'GtsPlus_NicManager.NicManager',
              'method': 'GetPrivateIpInfo',
              'rva': 8292,
              'body_size': 172,
              'body_sha256': '37f222b070eb8d952bab872e964db8df3c3660ae18fc0d51b9ba17d3ee757633'},
 'nic_enumerate': {'type': 'GtsPlus_NicManager.Component.NicComponent',
                   'method': 'GetPrivateIpAdrresses',
                   'rva': 8656,
                   'body_size': 65,
                   'body_sha256': 'a5ec595965395389ddb743b27277efb16e9c96f91a6bf6bd810eec474d4b9a9b'},
 'nic_filter': {'type': '<>c__DisplayClass0_0',
                'method': '<GetPrivateIpAdrresses>b__0',
                'rva': 8740,
                'body_size': 114,
                'body_sha256': '87cb6678809aa74b4c8d54460fbf1246bf104466ca527df6d05586163b725482'},
 'nic_ipv4': {'type': '<>c__DisplayClass0_0',
              'method': '<GetPrivateIpAdrresses>b__1',
              'rva': 8854,
              'body_size': 38,
              'body_sha256': '9fca32dbda1860d7d5dd6616899953d51b4443d7128d103c3f441ebeca791cf1'}}

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

FINDINGS = {'j2534.initialize': 'Reject null output=4, existing process singleton=0xE and API selector other than1/2=7. '
                     'Read setting type3, vim.registry0404 or vim.registry0500; require matching '
                     'PassThruSupport.04.04/.05.00 prefix; query HKLM selected key '
                     'FunctionLibrary/Vendor/Name. Construct CJ2534v2 then vtable+34 (04.04) or+78 (05.00) '
                     'open; on open failure destroy/reset singleton and return error. '
                     'Registry/config/allocation failures are not an automatic device retry.',
 'j2534.driver_constructor': 'For API1 with exact Vendor DENSO CORPORATION and Name TIS Techstream VIM load '
                             'physical DLL directly (LoadLibraryW). Otherwise load install-directory '
                             'ptshim32.dll/API1 or ptshim32_0500.dll/API2 with LoadLibraryExW(flags8), call '
                             'PassThruLoadLibrary(physical FunctionLibrary path), create save/finish/stop '
                             'events and logger worker. Logger insertion is deliberate controller routing, '
                             'not DLL-search-path replacement.',
 'j2534.open0404': 'Require API1 and loaded module; already-open byte+5C returns0xE. Resolve/call '
                   'PassThruOpen(name,&deviceID); only success stores ID at+78 and sets open+5C. Missing '
                   'DLL/export or open failure returns7 with stored last-error text.',
 'j2534.scan_open0500': 'API2 uses PassThruScanForDevices(&count), then exactly one PassThruGetNextDevice '
                        'call; parses its device name and calls PassThruOpen("J2534-2:%s",&deviceID). Empty '
                        'parsed name returns0x22; open success stores+78 and+5C. This body does not iterate '
                        'all discovered devices.',
 'j2534.connect0404': 'Require API1/module/open+5C and channel+5D clear (8/0x14 otherwise). Validate flag '
                      'masks and protocol IDs. Non-DENSO custom0x1000C becomesISO15765(6),0x1000D '
                      'becomesISO9141(3); direct DENSO IDs gain0x10000. Zero baud '
                      'defaults:1/3/4=10400,2=41600,5/6/0x1000B/0x8012/0x1000C=500000,0x8005=125000,0x8013=0. '
                      'Call physical PassThruConnect(device,protocol,flags,baud,&channel), store+74; for '
                      'applicable legacy protocols install PASS_FILTER defaults. Failure attempts controller '
                      'disconnect before connected+5D is set; its guard returns2 without calling physical '
                      'PassThruDisconnect. Thus a physical channel may remain despite setup failure until '
                      'later driver/device close. Channel+5D is set only on successful setup.',
 'j2534.filter': 'Require module/open/channel. Replace controller-created default filters with '
                 'Ioctl10(CLEAR_MSG_FILTERS); invoke real PassThruStartMsgFilter with mask/pattern/flow. '
                 'Track real driver filterID in an internal linked list, expose a controller-local index as '
                 'returned filterID. Failures return driver/error status; no retry loop.',
 'j2534.disconnect0404': 'Require API1/module/open/channel. Call physical PassThruDisconnect(channel); even '
                         'if it fails, clear tracked filters and default-filter flag+7C, flag '
                         'bytes+7E/+7F/+80 and connected+5D. Return driver status; software disconnected '
                         'does not prove hardware acknowledged disconnect.',
 'j2534.close': 'Require loaded module and open+5C. If connected, disconnect via API-specific path; then '
                'PassThruClose(deviceID). Only success clears+5C and deviceID and calls save-log vtable+B0; '
                'close failure returns7 and preserves open bookkeeping until destruction.',
 'j2534.finalize': 'No singleton=>8. Invoke vtable+38 close, obtain last error on7, then deleting destructor '
                   'and singleton reset regardless of returned close status.',
 'j2534.destructor': 'If still open call PassThruClose and clear open/channel bytes. Close communication-log '
                     'handle. Non-direct-DENSO route calls PassThruUnloadLibrary, signals worker stop, '
                     'waits5000ms then TerminateThread if wait is not signaled; closes four worker/event '
                     'handles. FreeLibrary physical/shim module and free filter list.',
 'j2534.device_info': 'Read selected API04 registry metadata. Probe up to11 registry-supported protocol IDs '
                      'by connect/disconnect through live singleton. Exact DENSO/TIS pair yields device '
                      'kind1 or4 (probe success); other vendors2 or8. This is a device-capability probe, not '
                      'a pure registry enumeration operation.',
 'j2534.device_info0500': 'Read selected API05 registry metadata and ETHERNET capability; probe '
                          'protocol0x800F at100000000 baud with resource parameters, disconnect afterward, '
                          'return device kind8 on success else2. Registry metadata alone is not proof the '
                          'channel opens.',
 'j2534.save_worker': 'Wait indefinitely for stop or SAVE_J2534_LOG_FILE_EVENT; on save reset event, call '
                      'save-log vtable+B0, signal FINISH_J2534_LOG_FILE_EVENT and return to wait. Finish '
                      'signals completion of the attempt, not necessarily successful persistence.',
 'j2534.save_log': 'For non-direct-DENSO route resolve PassThruSaveLog. Read common setting type1 '
                   'path.productFolder; prefix CSIDL0x2E, append ErrorReport/j2534_MMDDYYYYhhmmss.log using '
                   'GetLocalTime and call shim save. Current filename policy is settings-backed; hard-coded '
                   'legacy Techstream directory is not the current source of truth. Provider errors '
                   'return7/A0040005/C0040102. Both current shipped shim SaveLog bodies are no-op success; '
                   'this requested pathname does not establish that a file is created.',
 'j2534.ndis_connect': 'Validate NIC/address pointers and two-byte logical source address. Read '
                       'ethernet.connectIPTimeout from setting type1; WSAStartup2.2; UDP '
                       'socket(AF_INET,SOCK_DGRAM,UDP), exclusive-address and broadcast options. Poll '
                       'SIO_GET_INTERFACE_LIST for selected NIC IPv4/up state at1000ms until timeout. '
                       'Vehicle-ID discovery precedes TCP bind(selectedIPv4,port0), connect(peer,13400), '
                       'and15-byte routing-activation request(type0005,length7). Require response '
                       'type0006,length>=5 and matching tester source-address echo; this body does not check '
                       'the activation-response status byte. Many early errors return with global '
                       'sockets/WSA state still allocated; caller must execute teardown.',
 'j2534.vehicle_id': 'Bind UDP to selected NIC and supplied source port; broadcast 8-byte vehicle-ID request '
                     'FF00000100000000 to255.255.255.255 at the supplied port. Clear stale UDP input first. '
                     'On ReceiveVehicleIdMessage timeout0x8001 retry once (two requests total); all other '
                     'failures return immediately.',
 'j2534.vehicle_id_receive': 'select/recvfrom within supplied timeout, skip self-originated packets, accept '
                             'datagram length>=40 and payload type0004; remember sender IPv4 and '
                             'protocol-version byte. VIN/EID/GID identity is not checked in this function.',
 'j2534.ndis_send': 'Require two-byte source/target logical addresses, nonempty bounded payload and TCP '
                    'socket. Clear stale TCP receive buffer, build DoIP type8001 with four address bytes and '
                    'length(payload+4), send once and await diagnostic acknowledgment. Return send/ack '
                    'error, no transparent resend.',
 'j2534.ndis_ack': 'Read8-byte TCP header and declared body; allow types8002/8003 with nonzero body>=4, '
                   'match reversed source/target addresses. Type8003=>0x8000;8002 succeeds. '
                   'WSAETIMEDOUT10060=>0x8003, EOF/other recv errors=>0x8017; address mismatch=>0x8002.',
 'j2534.ndis_receive': 'Read TCP header then body, require type8001,length>=4 and caller capacity>=length-4. '
                       'Validate source/target match last send, copy diagnostic bytes after four '
                       'logical-address bytes, return actual payload length. Timeout=>0x8003, EOF/socket '
                       'error=>0x8017, address mismatch=>0x8002, invalid length/type=>0x8000.',
 'j2534.ndis_disconnect': 'shutdown(SD_BOTH) and close TCP; close UDP; WSACleanup if startup succeeded. Log '
                          'but suppress cleanup failures, invalidate socket globals, clear '
                          'protocol-version/NIC/address globals, always return0.',
 'kgp.open': 'Resolve installed J2534Ctrl.dll with LoadLibraryExW(flags8), call '
             'Initialize(API,&deviceID,null), map nonzero status with0x91010000, set log-collection mode and '
             'load-version/device fields, initialize disconnected CONNECT_INFO. Load/export '
             'failures=>C0040301/C0040302.',
 'kgp.open_j2534_2': 'Same loader, but Initialize third argument is J2534-2:. Used for Ethernet/extended bus '
                     'routes; this is not equivalent to automatically selecting API05.',
 'kgp.read_version': 'Return cached API version if available; otherwise when no module, try API1 first, '
                     'CloseDevice on failure, then API2, CloseDevice if that fails. Resolve version API by '
                     'active load-version and encode major*256+minor; version-read error clears '
                     'cached/output version.',
 'kgp.read_versions': 'Detailed version API requires null-initialized three output arrays; visits configured '
                      'registry0404 and registry0500, prioritizing currently loaded API, allocates80-byte '
                      'version buffers and switches device/module on second API. It returns caller-owned '
                      'arrays; corresponding FreeReadVersion API is separate.',
 'kgp.change_interface': 'App bus low nibble selects transport class independently of category-byte low5 '
                         'support/session family. Reuse only when bus/addressing/mode/category compatibility '
                         'checks pass. Incompatible CAN11/29/FD, legacy or Ethernet transitions stop '
                         'communication, Disconnect and sometimes FinalizeDevice; create/reinitialize '
                         'selected protocol object. P5 low5=14/15/16 gates session cleanup separately; '
                         'low5=16 forces additional finalize when changing family.',
 'kgp.connect_general': 'Select same protocol class from CONNECT_INFO bus low nibble, but adopt '
                        'caller-supplied device/protocol/channel state through SetConnectParameterGeneral '
                        'instead of opening a new ordinary channel. Setup error calls Disconnect; special '
                        'device checks reject VIM-only incompatibilities with90020204.',
 'kgp.set_connect_info': 'Copy connection state, ECU, bus, DLL API version, device ID, protocol count and128 '
                         'bytes of protocol/channel pairs into controller-owned storage; repoint protocol '
                         'array into own copied storage. This is in-process numeric-ID handoff, not a '
                         'durable handle file.',
 'kgp.adopt_connection': 'Set protocol object connected+0C, assign provided deviceID to+20E0, install first '
                         'protocolID and channelID through vtable+128/+120; no physical PassThruConnect call '
                         'in this method.',
 'kgp.ndis_db_parameters': 'Resolve DB class10D(category,bus)->155(Ethernet config)->156(software ECU '
                           'config). Copy logical source from software row+2, timing values+6/+8/+A. Missing '
                           'row=>90020104. Ethernet route is DB-selected, not inferred from P6 support '
                           'family alone.',
 'kgp.ndis_connect': 'Require selected VCI capability Ioctl800C selector54 results1/1. Read common ethernet '
                     'sourcePortNumberUDP/TCP defaultsC000 and connectIPTimeout default0. Open auxiliary '
                     'PassThru protocol8013, poll Ioctl800F for one nonzero NIC IPv4 with1000ms waits until '
                     'timeout, then call NDISConnect. Success sets connected; setup failures=>91020306. The '
                     'TCP source-port setting is passed, while current J2534Ctrl NDIS implementation binds '
                     'TCP port0.',
 'kgp.ndis_disconnect': 'Stop communication service when connected, clear ECU/service/connected fields, then '
                        'invoke vtable198 backend disconnect.',
 'kgp.ndis_disconnect_backend': 'Call J2534CtrlNDISDisconnect first, then disconnect auxiliary PassThru '
                                'channel if present and zero its ID.',
 'kgp.device_capabilities': 'Selectors4D/52/54 obtain device capabilities through Ioctl800C; selector52 '
                            'checks configured API05. Selector54 additionally branches on persisted VCI '
                            'display-name Mongoose-Plus MFC3 and DST-010 plus version string. Vendor/support '
                            'identity gates capability policy, not protocol family selection.',
 'kgp.abort': 'Signal keepalive/idle worker cancellation events, wait up to185000ms for keepalive '
              'completion; stop P5/P6 session activity, protocol stop-communication and ISO9141DK stop '
              'service, clear ECU/session/timeouts. This abort preserves the protocol/device object; it is '
              'not CloseDevice.',
 'kgp.disconnect': 'Optionally stop keepalive first; P5/P6 cleanup invokes stop/default-session paths, then '
                   'protocol disconnect and deleting destructor. Clear protocol '
                   'pointer,bus,ECU,current-session and reset timeout10000. Device kinds1/4 additionally '
                   'FinalizeDevice; other devices can remain open for reconnect.',
 'kgp.close': 'If module exists, Disconnect(1) if protocol object, then FinalizeDevice if still loaded, and '
              'reset CONNECT_INFO to no connection. Returns0.',
 'kgp.finalize': 'Call J2534CtrlFinalize if export exists but ignore its result; FreeLibrary and clear '
                 'module/device/load-version fields. Returns0.',
 'kgp.base_constructor': 'Resolve both API04 and API05 function pointers plus '
                         'NDISConnect/Send/Receive/Disconnect from one J2534Ctrl module; missing exports use '
                         'internal stubs. ReadVersion populates API numeric version. No new process is '
                         'spawned here.',
 'ds4.initialize': 'Parallel DS-4 controller has the same API1/2 selected-registry configuration and device '
                   'singleton contract, protected by process-local critical section. This is a different '
                   'source/build, not a byte-identical GTSPlus copy.',
 'ds4.finalize': 'Under the DS-4 critical section, close via vtable38, retain returned status, destroy '
                 'singleton and reset it; missing singleton returns8. No NDIS exports exist in this '
                 'installed DS-4 controller.',
 'settings.file_type': 'Native setting-file type1 maps GTSPlusCommon.gstg, type3 maps PcSettings.gstg. '
                       'Selected VCI configuration persists in type3; Ethernet and productFolder '
                       'configuration are type1.',
 'settings.get_type': 'GetFileDataFromType returns allocated caller-owned plaintext buffer; settings '
                      'provider owns reading/decrypting serialized file and caller releases via FreeMemory.',
 'winsock.send': 'Log timestamp/API arguments and outgoing bytes before calling WS2_32 send, then log '
                 'result; return actual socket result unchanged.',
 'winsock.receive': 'Call WS2_32 recv, log received bytes only when result>0, log result and return it '
                    'unchanged.',
 'winsock.log_write': 'Format CRLF-terminated message and invoke configured callback only when nonnull, '
                      'under critical section. This routine does not itself write a disk file.',
 'wrap.load_modules': 'EbReadPara/EbGetString(0x6F) supplies install root; LoadLibraryW '
                      'root/bin/J2534Ctrl.dll and MsgDatComm.dll into wrapper-owned module fields. Broker '
                      'supplies configuration, not a remote PassThru channel.',
 'wrap.initialize': 'MFC module-state guard then call cached J2534CtrlInitialize function pointer with '
                    'original arguments.',
 'wrap.connect': 'MFC module-state guard then call cached PassThruConnect pointer; return status unchanged.',
 'wrap.bind': 'Populate cached API pointers from selected module, including NDIS APIs. Wrapper exports call '
              'these pointers; no IPC serialization appears in this dispatch body.',
 'wrap.lookup': 'GetProcAddress against stored module handle; absent module returnsnull.',
 'front.initialize': 'MFC module-state guard then call cached J2534CtrlInitialize pointer.',
 'front.set_handle': 'Store caller module handle at wrapper object+CC and populate API pointers from it. '
                     'Front wrapper does not load a second driver here.',
 'front.reset_handle': 'ResetDllHandle clears stored handle through reset helper; does not call FreeLibrary '
                       'or disconnect.',
 'front.reset_storage': 'If stored module handle nonzero, set it to0. Cached function pointers are not '
                        'cleared by this helper.',
 'front.bind': 'Resolve cached ordinary and NDIS API pointers using stored module handle.',
 'front.lookup': 'GetProcAddress on caller-supplied stored module; absent handle returnsnull.',
 'kgp.can_iso15765': 'Constructor installs CCommCtrlISO15765 vtable; factory caller and protocol argument '
                     'are pinned by ChangeCommIF/ConnectCommIFGeneral, not deduced from filename.',
 'kgp.can_phase5': 'Constructor installs CCommCtrlISO15765_Phase5 vtable; factory caller and protocol '
                   'argument are pinned by ChangeCommIF/ConnectCommIFGeneral, not deduced from filename.',
 'kgp.can_obd_zev': 'Constructor installs CCommCtrlISO15765_11BitOBDZEVonUDS vtable; factory caller and '
                    'protocol argument are pinned by ChangeCommIF/ConnectCommIFGeneral, not deduced from '
                    'filename.',
 'kgp.can_wwh': 'Constructor installs CCommCtrlISO27145_Phase5 vtable; factory caller and protocol argument '
                'are pinned by ChangeCommIF/ConnectCommIFGeneral, not deduced from filename.',
 'kgp.can_29bit': 'Constructor installs CCommCtrlISO15765_29BitCan vtable; factory caller and protocol '
                  'argument are pinned by ChangeCommIF/ConnectCommIFGeneral, not deduced from filename.',
 'kgp.can_fd': 'Constructor installs CCommCtrl_FD_ISO15765_PS vtable; factory caller and protocol argument '
               'are pinned by ChangeCommIF/ConnectCommIFGeneral, not deduced from filename.',
 'kgp.iso9141': 'Constructor installs CCommCtrlISO9141 vtable; factory caller and protocol argument are '
                'pinned by ChangeCommIF/ConnectCommIFGeneral, not deduced from filename.',
 'kgp.iso9141dk': 'Constructor installs CCommCtrlISO9141DK vtable; factory caller and protocol argument are '
                  'pinned by ChangeCommIF/ConnectCommIFGeneral, not deduced from filename.',
 'kgp.j1850': 'Constructor installs CCommCtrlJ1850 vtable; factory caller and protocol argument are pinned '
              'by ChangeCommIF/ConnectCommIFGeneral, not deduced from filename.',
 'kgp.direct_can': 'Constructor installs CCommCtrlDirectCan vtable; factory caller and protocol argument are '
                   'pinned by ChangeCommIF/ConnectCommIFGeneral, not deduced from filename.',
 'kgp.ndis_constructor': 'Constructor installs CCommCtrlISO13400_NDIS vtable; factory caller and protocol '
                         'argument are pinned by ChangeCommIF/ConnectCommIFGeneral, not deduced from '
                         'filename.',
 'ds4_kgp.change_interface': 'DS-4 app bus low-nibble4 explicitly selects API2/J2534v05.00 and '
                             'CCommCtrlISO13400 with physical protocol800F. Other low-nibble cases select '
                             'API1:1/9=>ISO9141(4),2=>ISO15765(6 '
                             'or8005),3=>CAN(5),6=>J1850PWM(2),7=>J1850VPW(1),8=>29-bitCAN via protocol5/6 '
                             'flags100 (device/custom selector dependent),A=>custom1000C,C=>custom1000D. '
                             'Support-family low5 checks14/15 are separate. This installed factory has no '
                             'dedicated FD8012 case; do not transfer GTSPlus NDIS/FD behavior to DS-4.',
 'ds4_kgp.open': 'Load installed J2534Ctrl.dll, call Initialize(API,&deviceID), apply log mode, record '
                 'device/API. Errors map91010000 orC0040301/C0040302.',
 'ds4_kgp.disconnect': 'Stop tester/idle activity; support low5=14/15 gets session cleanup, then protocol '
                       'disconnect/destruct, clear bus/ECU/session and timeout10000. Device kinds1/4 '
                       'finalize module, others retained.',
 'ds4_kgp.ethernet_constructor': 'Installs CCommCtrlISO13400 vtable, initializes physical and three logical '
                                 'channel slots. DS-4 Ethernet is driver-mediated J2534v05.00, not current '
                                 'GTSPlus NDIS.',
 'ds4_kgp.can29_constructor': 'Installs CCommCtrl29BitCan, selected by DS-4 factory nibble8 under '
                              'device/selector guard.',
 'ds4_kgp.can29_normal_constructor': 'Installs CCommCtrl29BitCanNormal, alternate nibble8 route using CAN '
                                     'protocol5 rather thanISO15765 protocol6.',
 'ds4_kgp.ethernet_connect': 'Disconnect if already connected, obtain source parameters, read '
                             'ethernet.connectEtherDelay (initial200,missing key0), create physical Ethernet '
                             'then logical8203(IP4),8205(UDP); perform vehicle-ID exchange; '
                             'logical8206(TCP), then routing activation. Failure=>91020306, success records '
                             'protocol/connected. No socket API in this body.',
 'ds4_kgp.ethernet_physical': 'PassThruConnect_v0500(device,800F,flags0,100000000,resource parameters1/4 '
                              '[3,B,C,D],&physicalID); Ioctl2 sets805F=1; ReadMsgs_v0500 verifies status '
                              'flag10000. Maps driver failures with91010000; no link flag=>81020000.',
 'ds4_kgp.ethernet_logical': 'PassThruLogicalConnect_v0500 creates8203 from physical ID with '
                             'connectIPTimeout,8205 from IP4 with configured UDP source port,8206 from IP4 '
                             'with configured TCP source port and discovered destination address/port. Store '
                             'IDs at2240/2244/2248; missing output/unknown protocol=>90020701.',
 'ds4_kgp.ethernet_udp': 'Clear UDP Rx via Ioctl8, form vehicle-ID payload, queue one8205 message then read '
                         'response; require length>=2E and payload type0004, copy response sender data. Read '
                         'errors map91010000; short=>91020324,unexpected type=>81020000.',
 'ds4_kgp.ethernet_routing': 'Clear TCP Rx via Ioctl8, build routing activation type0005, queue8208 '
                             'byte-stream message then read response; require length>=0D and payload '
                             'type0006. This body does not check routing-activation status byte; errors '
                             'map91010000/91020310/91020324/81020000.',
 'ds4_kgp.ethernet_send': 'Build DoIP type8001 diagnostic frame, mark J2534 byte-stream protocol8208, '
                          'optionally Ioctl8 clear, queue via PassThruQueueMsgs_v0500 on TCP logicalID. '
                          'Cache sent frame and request for receive/classifier retry. Queue failure returned '
                          'with91010000.',
 'ds4_kgp.ethernet_receive': 'Read ACK(type8002) then diagnostic header(type8001), validate declared '
                             'size/capacity and source, assemble body/chunks up to1020 each. Pass response '
                             'to protocol classifier:90020323 loops pending until180000ms;90020326 requeues '
                             'cached request while counter<100(hex), then exits; other classifier errors '
                             'returned. ERR_BUFFER_EMPTY10 maps91010009; short/type/source errors remain '
                             'distinct. Timing comes from Ethernet DB rows; no blanket infinite retry.',
 'ds4_kgp.ethernet_disconnect': 'Stop communication if connected and clear service/ECU/connected fields, '
                                'then backend teardown vtable198.',
 'ds4_kgp.ethernet_teardown': 'Disconnect TCP logicalID, UDP logicalID, IP4 logicalID with '
                              'PassThruLogicalDisconnect_v0500, then physicalID with '
                              'PassThruDisconnect_v0500; zero each ID. Sleep between stages using common '
                              'ethernet disconnectWaitTimeTcp/Udp/Ip4/Ether (defaults0); return0 despite '
                              'ignored driver disconnect results.'}

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

# Disassembled initialization windows, including conditional callback registration.
REGISTRATION_PINS = {
    "shim0404": (0x10001150, "687c631b10ff15f8e31710a3c4f01d1085c07411689c631b1050ff15f4e31710a3c8f01d1068f0d81710e80470140059c3", 0x101B637C, 0x101B639C),
    "shim0500": (0x10001150, "68a4971b10ff15f8f31710a3ac201e1085c0741168c4971b1050ff15f4f31710a3b0201e106850e91710e8057f140059c3", 0x101B97A4, 0x101B97C4),
    "winsock": (0x10001036, "681c840010ff1578700010a3a8b3001085c07411683c84001050ff1574700010a3acb30010", 0x1000841C, 0x1000843C),
    "ds4_shim0404": (0x10001150, "6800741b10ff15f8f31710a3cc001e1085c074116820741b1050ff15f4f31710a3d0001e106840da1710e85e71140059", 0x101B7400, 0x101B7420),
    "ds4_shim0500": (0x10001150, "68a4971b10ff15f8f31710a3ac201e1085c0741168c4971b1050ff15f4f31710a3b0201e106850e91710e8057f140059", 0x101B97A4, 0x101B97C4),
}


def _id(value: str) -> str:
    return f"{DOMAIN}.{value}"


def _relative(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()


def build(gts_root: Path = DEFAULT_GTS, ds4_root: Path = DEFAULT_DS4,
          recovered_root: Path = DEFAULT_RECOVERED) -> dict[str, Any]:
    roots = {"gts": Path(gts_root), "ds4": Path(ds4_root), "recovered": Path(recovered_root)}
    sources: list[dict[str, Any]] = []
    images: dict[str, tuple[Any, bytes, int]] = {}
    for key, pin in SOURCE_PINS.items():
        path = roots[pin["root"]] / pin["relative"]
        raw = path.read_bytes()
        if len(raw) != pin["size"] or sha256_bytes(raw) != pin["sha256"]:
            raise ValueError(f"source identity drift: {key}: {path}")
        representation = "installed-original"
        if key == "settings":
            representation = "installer-recovered-native-plaintext"
        elif key == "settings_stub":
            representation = "installed-CP-stub"
        elif key == "settings_sidecar":
            representation = "installed-CP-sidecar"
        sources.append({"id": _id("source." + key), "path": _relative(path),
                        "sha256": pin["sha256"], "size": len(raw), "representation": representation})
        if key in NATIVE_PINS:
            images[key] = pe_info(path)

    manifest_path = Path(recovered_root) / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    recovery = next(row for row in manifest["binaries"]
                    if row["path"] == "bin/GTSPlusSettingFileManager.dll")
    if (recovery["plaintext"]["sha256"] != SOURCE_PINS["settings"]["sha256"]
            or recovery["protected"]["stub_sha256"] != SOURCE_PINS["settings_stub"]["sha256"]
            or recovery["protected"]["sidecar_sha256"] != SOURCE_PINS["settings_sidecar"]["sha256"]
            or not recovery["package_identity"]["cp_stub_matches_installed"]
            or not recovery["package_identity"]["cp_sidecar_matches_installed"]):
        raise ValueError("setting-provider recovered/original identity linkage drift")
    next(row for row in sources if row["id"] == _id("source.settings"))["recovery"] = {
        "manifest": _relative(manifest_path), "installer": recovery["installer"],
        "original_stub": _id("source.settings_stub"), "original_sidecar": _id("source.settings_sidecar"),
        "method": "tools.techstream.recover_gtsplus_bodies; matching installer CP stub and sidecar"}

    evidence: list[dict[str, Any]] = []
    for source, functions in NATIVE_PINS.items():
        pe, data, base = images[source]
        for name, pin in functions.items():
            label = source + "." + name
            body = read_va(pe, data, base, pin["va"], pin["size"])
            if not any(body) or sha256_bytes(body) != pin["sha256"]:
                raise ValueError(f"unmaterialized or changed native body: {label}")
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

    nic = _open(Path(gts_root) / "bin/GtsPlus-NicManager.dll")
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
        if not body.instructions or not any(body.raw_bytes):
            raise ValueError(f"unmaterialized managed body: {key}")
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
    return {"schema": "gtsplus-lifecycle-domain-v1", "domain": DOMAIN, "sources": sources,
            "evidence": evidence, "states": states, "transitions": transitions,
            "handoffs": handoffs, "persistence": persistence, "transport_families": transports,
            "support_family_distinction": "GTSPlus and DS-4 are parallel application/support builds; ECU category low5 controls support/session strategy, application bus low nibble selects transport. P6 does not imply DoIP, nor P5 only CAN.",
            "coverage": {"components": ["GTSPlus native frame controller and J2534 singleton", "DS-4 native factory and driver-mediated ISO13400", "v04.04/v05.00 loader and shim interposition", "managed NIC enumeration", "pass-through wrappers and adopted channels", "settings/config ownership"],
                         "entrypoints": ["Initialize/Finalize", "Open/Connect/Filter/Disconnect/Close", "ReadVersion fallback", "ChangeCommIF/SetConnectInfo/general adoption", "NDISConnect/Send/Receive/Disconnect", "DS-4 ISO13400 physical/logical/vehicle-ID/routing", "CommunicationAbort", "Save/Finish log events", "GetPrivateIpInfo"],
                         "branches": ["selected API04/API05 registry paths", "direct DENSO versus shim", "default-filter rollback rejected by unset connected flag", "disconnect failure bookkeeping", "two-attempt UDP identification", "TCP setup/EOF/timeout/address/type errors", "DS-4 pending180000ms/classifier requeue limit256", "same-protocol reuse versus finalize/reopen", "adopted versus newly opened IDs", "best-effort teardown and worker forced-stop5000ms", "current shim SaveLog no-ops versus MsgDatComm log callback"]},
            "residuals": [
                {"question": "Which installed Windows registry entries and physical VCIs are actually usable?", "why_unclosed": "Offline shipped application has no target Windows registry/device state; selected FunctionLibrary implementations and VCI firmware are external transport owners.", "next_evidence": "Authorized Windows registry/device metadata and driver-specific source/capture, without network/vehicle interaction in this pass."},
                {"question": "Actual physical close/connect/reset acknowledgement and recovery behavior", "why_unclosed": "Driver error contracts are propagated or suppressed as pinned; software state does not measure a device. No generic reconnect loop or hardware reset can be inferred from module teardown.", "next_evidence": "Offline Windows driver-contract harness with preauthorized inert implementation; no live device required."}],
            "reproduction": {"command": "uv run --locked python -m tools.techstream.extract_gtsplus_lifecycle_vci_transport", "recovery_prerequisite": "build/out/gtsplus-unprotected with matching main recovery manifest", "network_or_vehicle_access": False}}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gts-root", type=Path, default=DEFAULT_GTS)
    parser.add_argument("--ds4-root", type=Path, default=DEFAULT_DS4)
    parser.add_argument("--recovered-root", type=Path, default=DEFAULT_RECOVERED)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    artifact = build(args.gts_root, args.ds4_root, args.recovered_root)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n")
    print(f"Wrote {args.out}: {len(artifact['evidence'])} evidence, {len(artifact['transitions'])} transitions")


if __name__ == "__main__":
    main()
