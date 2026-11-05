#!/usr/bin/env python3
"""Extract offline installer, prerequisite and process-recovery lifecycle evidence.

Requires the manifest-qualified GTSPlus aggregate component and the MIT InstallScript decoder
at revision1d5edb7b022cc1573a1f3971382391b9c5457cc9, with its source checkout
under REFERENCE/installscript-decompiler and executable under build/cache.
The artifact records the locked Cargo recipe and exact decoder provenance.
Recovered images are admitted by exact source-relative manifest/installed-CP
qualification and full managed IL validation with native/bodyless classifications.
Selected semantic byte pins remain exact; explicit component roots do not fall
back to old recovery corpora.
Fresh source-pinned scripts are decoded; no installer/application is run.
Packaging passphrases are never emitted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import pefile

from tools import REPO_ROOT
from tools.techstream.extract_gtsplus_lifecycle_ui_ipc import _operand
from tools.techstream.extract_gtsplus_tse_managed_semantics import (
    _instructions, _method_pin, _open, sha256_file,
)
from tools.techstream.gtsplus_local_crypto import decrypt_file
from tools.techstream.inspect_dotnet_il import validate_managed_bodies
from tools.techstream.recover_all_gtsplus_bodies import DEFAULT_OUTPUT as DEFAULT_RECOVERED, qualify_recovered_source
from tools.techstream.recover_gtsplus_bodies import (
    _extract_member, _extract_sfx_payload, _parse_unshield_listing, _sevenzip,
)

DEFAULT_ROOT = REPO_ROOT / "software/Techstream/gtsplus/unpacked/gtsplus"
DEFAULT_MAIN = DEFAULT_RECOVERED / "GTSPlus"
DEFAULT_DECODER = REPO_ROOT / "build/cache/installscript-decompiler/release/installscript-decompiler"
DEFAULT_OUT = REPO_ROOT / "data/generated/gtsplus_2026/lifecycle_install_update.json"
DOMAIN = "install_update"
ARCHIVE_SHA = 'fb65ac31b1c0a0c1b28d53af8cf540d12eb46d77ba1e6645a014473352ce00c4'
VERIFIER_PINS = {'CUWPlusPF.exe': '6b358a9e7d3b68d5bd900d96e09c6855d1451fd1bd27cc4bdbc84cfbc8313bc9', 'Setup_DataSync.exe': 'f94f90a141e16f9b5f7961e2b6d84ee3bb3d273a01c4ef6b7e279c5ef1dbf096', 'Setup_GUI.exe': '6b358a9e7d3b68d5bd900d96e09c6855d1451fd1bd27cc4bdbc84cfbc8313bc9', 'Setup_GuiServer.exe': '6b358a9e7d3b68d5bd900d96e09c6855d1451fd1bd27cc4bdbc84cfbc8313bc9', 'Setup_InfoCenter.exe': 'f94f90a141e16f9b5f7961e2b6d84ee3bb3d273a01c4ef6b7e279c5ef1dbf096', 'Setup_NativeGraphViewer.exe': '6b358a9e7d3b68d5bd900d96e09c6855d1451fd1bd27cc4bdbc84cfbc8313bc9', 'Setup_PCSDataViewer.exe': '6b358a9e7d3b68d5bd900d96e09c6855d1451fd1bd27cc4bdbc84cfbc8313bc9', 'Setup_PF.exe': 'f94f90a141e16f9b5f7961e2b6d84ee3bb3d273a01c4ef6b7e279c5ef1dbf096', 'Setup_TSEConverter.exe': '6b358a9e7d3b68d5bd900d96e09c6855d1451fd1bd27cc4bdbc84cfbc8313bc9'}
SOURCE_PINS = {'Toyota Diagnostics/GTSPlus/Ver/Manifest.json': '728a36e67b157ad81e8f385e5a7c011d86a4a65bd24c0ce9c5e1ffef18bcd187', 'Toyota Diagnostics/GTSPlus/Env/GtsPlus-PcCheckerTool.yml': '63ba44c71373ee88b276242b53bd3102e139f9970a285201a52ab139833b6caa', 'Toyota Diagnostics/GTSPlus/GtsPlus-PcCheckerTool/PCT.pp': 'b76596dc548e23056bde89b13638c4ef5a3032257ee4a2c3c31f2f86ebbff0be', 'AgentLite/logs/AgentLite_Service.log': 'f238b6f03460d191f00e6051f7479748eae9c9bdb2d2c3889e43cc7269b1116c', 'Toyota Diagnostics/GTSPlus/GtsPlus-InfoCenter/GtsPlus-InfoCenter.exe.config': '93b465ca9d46a4f9a2044e3b5e7b10997b867ea37cc7aeec7d1133bac09edae3', 'Toyota Diagnostics/GTSPlus/Ver/CUW+ PF.json': '73fdcc23ebe06225a8a7455101cc722caab8c448f5b4de4c7c73f3d34091e8d1', 'Toyota Diagnostics/GTSPlus/Ver/GTS+ DB.json': '7581154013906f845f852531145c087977e1b61abee8b1636e7a1b1122f32a55', 'Toyota Diagnostics/GTSPlus/Ver/GTS+ DataSync.json': '7831c56a6d50e6fdf0fdab71ffb530c74e0d9ee56de6318512029f2f7ea6744d', 'Toyota Diagnostics/GTSPlus/Ver/GTS+ GUI.json': '6a69dc04dc4cade033d64bdfe6277e1b7d6f07772c68abbd770aa774275fe553', 'Toyota Diagnostics/GTSPlus/Ver/GTS+ InfoCenter.json': '649f42c2a313343a1dd40aeea88eb2c349a04a56548ed6d345148b89fb8a9dd2', 'Toyota Diagnostics/GTSPlus/Ver/GTS+ PF.json': 'c078a02785aa44893b283c013575e822b5bdf89daff41333ff92c2874501bfef', 'Toyota Diagnostics/GTSPlus/Ver/GTS+ TSEConverter.json': '46f9def4673b563a9fb47ca98f34df570e36ce48bde590fb8fc887fec028fc05', 'Toyota Diagnostics/GTSPlus/Ver/GTS+GUIServer.json': '6bed23ecd0511cfcb10dd572702bc70cec474b7cd49ccd7cf46fdf7c5d76124f', 'Toyota Diagnostics/GTSPlus/Ver/GTS+_NativeGraphViewer.json': 'd7784350ae090f84bcaba7228c7aaf0acce798b3b9f6563c50c94c88ff69aae8', 'Toyota Diagnostics/GTSPlus/Ver/PCS Data Viewer.json': '25c80756d8225e17874875410661bb1f9369f951796fcc5c80da54b5bae95c2b'}
RECORD_PINS = {'0x0407.ini': 'b4d2bf8ddeee1e2acc5dfaa14ac602a69f52195c38eab4660408fd879ad41a56', '0x0409.ini': 'cdb316d7f9aa2d854eb28f7a333426a55cc65fa7d31b0bdf8ae108e611583d29', '0x040a.ini': '4e42d96cf24224d3ed43e7e14227b96fde3b43235636480f8861db0b048ffddf', '0x0410.ini': '4b13428baab7405a1125efd93f3569875cd19477b38608d4dd2fe2ccd3861e0f', '0x0411.ini': '3f0778538202a35483c084fb0b109f693a9853f64d6452daa5c92ac75620aadc', '0x0804.ini': 'df5b127369bfdf09264a69a38c0d999340f50948bed1624c429ddf17b49e97cb', '0x0c0c.ini': 'a2d09f95526954ea9833f6f03f319256f9e9d498e09e975b59add725127856b1', 'data1.cab': '0484977bdbf044b5e0e13cd74be054d8c591c3abd124c9a873ec74b84194a891', 'data1.hdr': 'c43f57fd3a0f7b832f2dfaf1f42ac0c398d91345af31dfd8d4fc2d7d1d874a63', 'data2.cab': '2532c9fec8f31d86e05e269817610830bcd5ed074c9173df7ff4f057c4d7eea8', 'ISSetup.dll': '462ad24e32884802cd02194b95b67ad57d0c35df9c91c31defc6ac701603c1a1', 'Microsoft Visual C++ 2015 Redistributable Package (x64).prq': '2dc37cde843105e84367d6d89f1e5009e2850fcbda460782e3375f3af93a232e', 'Microsoft Visual C++ 2015 Redistributable Package (x86).prq': '7c2cdd1bf54a172834df80b7eb0b9878921b9d38d46e826ef47eb82512d4684a', 'vc_redist.x86.exe': 'fdd1e1f0dcae2d0aa0720895eff33b927d13076e64464bb7c7e5843b7667cd14', 'vc_redist.x64.exe': '5eea714e1f22f1875c1cb7b1738b0c0b1f02aec5ecb95f0fdb1c5171c6cd93a3', 'layout.bin': '6866d4ff0c71c4c616e4a8f9b02df761cae7549d3adace13a00ab6af3d396f13', 'setup.exe': '1ab464cdc266d61882995b954ae68cd2679c7f8fbf1053bf973cf12eb3c24c20', 'setup.ini': '938e187f15886552e305b4b9c39fbd6cd8989d8b1ab1a921812cdc7896eb4e43', 'setup.inx': '97bcad56a86801ac61e1c10aeb56548699853669541592be8f43f86b8d957a5e', 'setup.iss': 'db95ed7c82ae3df50339f6b019fb3e2d8071ff85f2e07aae335af85b90f9da2c'}
METHODS = [{'key': 'pc.App.Main', 'source': 'pc', 'type': 'GtsPlus_PcCheckerTool.App', 'method': 'Main', 'pin': {'rva': 11696, 'body_size': 156, 'body_sha256': '665495ef8c564839b96164a8bdbab8450bb4b0c84a90245848656a171b846310'}, 'needles': ['Global\\', 'WaitOne', 'brfalse.s', 'Thread::Join', 'ReleaseMutex'], 'finding': 'Global\\GtsPlus-PcCheckerTool mutex is acquired nonblocking; duplicate instance displays error; first launches STA UI thread, joins, then releases mutex.'}, {'key': 'pc.App.OnStartup', 'source': 'pc', 'type': 'GtsPlus_PcCheckerTool.App', 'method': 'OnStartup', 'pin': {'rva': 12128, 'body_size': 328, 'body_sha256': '5ef7faa037846c4f4a5645795f5fdc0d059b7e53c5e683d931183c23c57b2c7d'}, 'needles': ['InitializeAuthentication', 'GtsPlus-PcCheckerTool.yml', 'PCT.pp', 'SkipFirstLine', 'Shutdown'], 'finding': 'Authenticates local property decryptor, decrypts ../Env/GtsPlus-PcCheckerTool.yml with PCT.pp, skips first line and deserializes; exception logs then shuts down.'}, {'key': 'pc.PropertyManager.ReadEncryptedExternalProperty', 'source': 'pc', 'type': 'GtsPlus_PcCheckerTool.Common.Manager.PropertyManager', 'method': 'ReadEncryptedExternalProperty', 'pin': {'rva': 19944, 'body_size': 64, 'body_sha256': '0e24953a7b06f1ccf4d12be706a73c0ccb74629243c5eed22c7d65bc6549911f'}, 'needles': ['ldc.i4.1', 'Decryption', 'brfalse.s', 'throw'], 'finding': 'Passes key type1 to native decryption; nonzero native result throws instead of continuing with invalid configuration.'}, {'key': 'pc.CheckPage.CreateCheckerList', 'source': 'pc', 'type': 'GtsPlus_PcCheckerTool.CheckPage', 'method': 'CreateCheckerList', 'pin': {'rva': 9212, 'body_size': 136, 'body_sha256': '7a05c6aaabee4b99a347b18fb4b4661bfab005d6b334f13f10f98a2b4f96a723'}, 'needles': ['get_Checkers', 'CreateChecker', 'brfalse.s', 'Initialize', 'ldnull'], 'finding': 'Configuration order owns checker order; missing checker construction returns null list instead of silently skipping.'}, {'key': 'pc.CheckPage.CreateChecker', 'source': 'pc', 'type': 'GtsPlus_PcCheckerTool.CheckPage', 'method': 'CreateChecker', 'pin': {'rva': 9348, 'body_size': 220, 'body_sha256': 'f14d33938507edc5c42e51ab9ceddd846015c6626b8ba1eda60ff9a4316ff39a'}, 'needles': ['GtsPlus_PcCheckerTool.Checker.', 'Split', 'GetType', 'CreateInstance', 'ldnull'], 'finding': 'Transforms hyphenated checker id into Checker type name, creates by reflection; construction exception logs and returns null.'}, {'key': 'pc.<DoCheck>d__5.MoveNext', 'source': 'pc', 'type': 'GtsPlus_PcCheckerTool.CheckPage+<DoCheck>d__5', 'method': 'MoveNext', 'pin': {'rva': 21924, 'body_size': 888, 'body_sha256': 'cf7bebbf41eb50d91abad0781614acbf97b04787558bdbaf8190c3d92e5f466a'}, 'needles': ['ShowProcessRing', 'set_IsEnabled', 'GetResult', 'brtrue.s', 'get_TextResultError', 'SetIcon', 'set_IsEnabled', 'HideProcessRing'], 'finding': 'Disables Next while current checker runs; false execution result shows error icon; always reenables Next after handled result, not installation gating.'}, {'key': 'pc.<<DoCheck>b__0>d.MoveNext', 'source': 'pc', 'type': 'GtsPlus_PcCheckerTool.CheckPage+<>c__DisplayClass5_0+<<DoCheck>b__0>d', 'method': 'MoveNext', 'pin': {'rva': 25936, 'body_size': 276, 'body_sha256': '266061260994b032907b97938ee1059686ef400da8ab25a8a284866353f6428b'}, 'needles': ['DoCheckAsync', 'GetResult', 'ldc.i4.1', 'log4net.ILog::Error', 'ldc.i4.0', 'SetResult'], 'finding': 'Checker task exception is caught/logged and produces false; normal completion produces true.'}, {'key': 'pc.<ButtonClick>d__14.MoveNext', 'source': 'pc', 'type': 'GtsPlus_PcCheckerTool.CheckPage+<ButtonClick>d__14', 'method': 'MoveNext', 'pin': {'rva': 21672, 'body_size': 236, 'body_sha256': '265c3a61603fd0ea13ac9e67bd45b489857de69ee308f04fd390f2303656b81b'}, 'needles': ['ldfld step', 'add', 'get_Count', 'blt.s', 'Navigate', 'DoCheck'], 'finding': 'Next increments index; remaining checks execute DoCheck, otherwise navigates to completion independently of warning icon.'}, {'key': 'pc.CheckPage..ctor', 'source': 'pc', 'type': 'GtsPlus_PcCheckerTool.CheckPage', 'method': '.ctor', 'pin': {'rva': 8972, 'body_size': 172, 'body_sha256': 'e92e443af6e819eb89894cd1cb95daab917e85e49209d998e344cbb5ff2dbb1c'}, 'needles': ['Result-', 'yyyyMMddHHmmss', '.txt', 'StringBuilder::.ctor', 'CreateCheckerList'], 'finding': 'Report text is accumulated in memory, named Result-yyyyMMddHHmmss.txt; checker list built once.'}, {'key': 'pc.CheckCompletePage.OutputButtonClick', 'source': 'pc', 'type': 'GtsPlus_PcCheckerTool.CheckCompletePage', 'method': 'OutputButtonClick', 'pin': {'rva': 8552, 'body_size': 208, 'body_sha256': '7c48ce020fa18dad2f251e413690d84c02c8843ae47f19b72d8ddd5243e73106'}, 'needles': ['Downloads', 'ShowDialog', 'bne.un.s', 'get_FileName', 'WriteAllText', 'FileOutputException'], 'finding': 'Folder picker cancellation returns without writing; accept writes report; output exception logs and returns.'}, {'key': 'pc.CheckCompletePage.FinishButtonClick', 'source': 'pc', 'type': 'GtsPlus_PcCheckerTool.CheckCompletePage', 'method': 'FinishButtonClick', 'pin': {'rva': 8760, 'body_size': 18, 'body_sha256': '64437381f5f407aa5bd6cf6e3cbbff2df449b11d477f0e7b4e5d431a5b1f4923'}, 'needles': ['get_MainWindow', 'Window::Close'], 'finding': 'Finish closes main window.'}, {'key': 'pc.App.OnExit', 'source': 'pc', 'type': 'GtsPlus_PcCheckerTool.App', 'method': 'OnExit', 'pin': {'rva': 12618, 'body_size': 57, 'body_sha256': '7d21979cd44c9bc50b2f865da5a6e5193d41e1aba723282cede2df7414f6a482'}, 'needles': ['OnExit', 'Application::OnExit'], 'finding': 'Exit logs then delegates Application.OnExit.'}, {'key': 'pc.RebootPage..ctor', 'source': 'pc', 'type': 'GtsPlus_PcCheckerTool.RebootPage', 'method': '.ctor', 'pin': {'rva': 10172, 'body_size': 271, 'body_sha256': 'e10612195a06e3e16b7c871e7b456499bdba711b11e09bba10720163a2c757b6'}, 'needles': ['GTSPlusArbitration.exe', 'CuwBackendServiceConsoleApp.exe', 'GTSPlus.exe', 'GtsPlus-InfoCenter.exe'], 'finding': 'Recovery target order is Arbitration, CUW backend, GTSPlus and InfoCenter.'}, {'key': 'pc.RebootPage.GetPid', 'source': 'pc', 'type': 'GtsPlus_PcCheckerTool.RebootPage', 'method': 'GetPid', 'pin': {'rva': 10684, 'body_size': 228, 'body_sha256': '9db655b2af4835e05cf78d0ba7874c83111109543c2d4a388bd878182cb5c6c6'}, 'needles': ['ExecutablePath, ProcessID', 'ExecutablePath', 'StartsWith', 'brfalse.s', 'ProcessId'], 'finding': 'Recovery PID lookup requires process executable path to start with installation-derived target prefix.'}, {'key': 'pc.<ExecReboot>d__7.MoveNext', 'source': 'pc', 'type': 'GtsPlus_PcCheckerTool.RebootPage+<ExecReboot>d__7', 'method': 'MoveNext', 'pin': {'rva': 23632, 'body_size': 584, 'body_sha256': '0aa3431ff3950c0bad092d39ea48f2b0658d92d2e6f4081fc3051f6749ec48fb'}, 'needles': ['GetPidList', 'get_Count', 'brtrue.s', 'There are no processes', 'Process::Kill', '0x2710', 'WaitForExit', 'Failed to stop', 'bin', 'Process::Start', '0x2710', 'Task::Delay', 'GetPid', 'ble.s', 'Failed to start AB app.'], 'finding': 'Process recovery: no PID fails; Kill and WaitForExit10000 each; timeout aborts; starts ../bin/GTSPlusArbitration.exe, delays10000 then requires PID; exceptions fail. No OS reboot call.'}, {'key': 'pc.<DoReboot>d__6.MoveNext', 'source': 'pc', 'type': 'GtsPlus_PcCheckerTool.RebootPage+<DoReboot>d__6', 'method': 'MoveNext', 'pin': {'rva': 23092, 'body_size': 524, 'body_sha256': 'f3566a54a998942617f7a7f54d2c6dd897015a8a7cf708165afe1c8d07f49824'}, 'needles': ['ExecReboot', 'GetResult', 'isSuccess', 'brfalse.s', 'get_RebootComplete', 'get_RebootFailure', 'set_IsEnabled'], 'finding': 'Recovery result selects RebootComplete or RebootFailure; both reenable Finish.'}, {'key': 'pc.<DoCheckAsync>d__0.MoveNext', 'source': 'pc', 'type': 'GtsPlus_PcCheckerTool.Checker.UrlChecker+<DoCheckAsync>d__0', 'method': 'MoveNext', 'pin': {'rva': 24888, 'body_size': 684, 'body_sha256': '4ea7180f5fef49f2c89ec73fd23548ef71b17c7fcbf1f6a6028a4de3337206ff'}, 'needles': ['5000.0', 'set_Timeout', 'get_ServerUrls', 'GetAsync', 'get_IsSuccessStatusCode', '0x190', 'blt.s', '0x1f4', 'bge.s', 'HttpStatus', 'hasError', 'MoveNext', 'SetIcon'], 'finding': 'URL check GET timeout5000ms; success OR400..499 accepted; other status/exception marks failure and proceeds to next configured URL. No retry loop per URL.'}, {'key': 'pc.AdministratorsChecker.DoCheckSync', 'source': 'pc', 'type': 'GtsPlus_PcCheckerTool.Checker.AdministratorsChecker', 'method': 'DoCheckSync', 'pin': {'rva': 18332, 'body_size': 432, 'body_sha256': '5e66c7f3d31026ca34a0d3f181c2740aed83694df275cbd825110c1fc037be67'}, 'needles': ['AppendResultToScreen'], 'finding': 'Enumerates localized administrators group SID S-1-5-32-544 and compares uppercased member/current username; absent membership sets icon2.'}, {'key': 'pc.UacChecker.DoCheckSync', 'source': 'pc', 'type': 'GtsPlus_PcCheckerTool.Checker.UacChecker', 'method': 'DoCheckSync', 'pin': {'rva': 17232, 'body_size': 224, 'body_sha256': '22b7664657fe534bf24a738cbeb5d9e550870b93f6a45edcf923b93e13808c42'}, 'needles': ['AppendResultToScreen'], 'finding': 'Reads EnableLUA/ConsentPromptBehaviorAdmin/PromptOnSecureDesktop; disabled UAC reports status, enabled with prompt values nonzero gives icon1; no registry modification.'}, {'key': 'pc.HostsChecker.DoCheckSync', 'source': 'pc', 'type': 'GtsPlus_PcCheckerTool.Checker.HostsChecker', 'method': 'DoCheckSync', 'pin': {'rva': 15216, 'body_size': 237, 'body_sha256': 'ff2c62683b1c0540a09459b81e258506e87b4218be31d0ffdf2dc435a0e7d050'}, 'needles': ['AppendResultToScreen'], 'finding': 'Finds non-comment 127.0.0.1 mapping whose captured name equals LOCALHOST; absent sets icon2.'}, {'key': 'pc.AntivirsChecker.DoCheckSync', 'source': 'pc', 'type': 'GtsPlus_PcCheckerTool.Checker.AntivirsChecker', 'method': 'DoCheckSync', 'pin': {'rva': 14784, 'body_size': 392, 'body_sha256': '72b9aa4466d4078584246c1e30f855390be646aa2ffa822792887cbc1582c428'}, 'needles': ['AppendResultToScreen'], 'finding': 'Compiled but disabled config: compares configured exclusions to Defender exclusions; registry access exception and missing exclusion set icon2.'}, {'key': 'pc.BaseboardChecker.DoCheckSync', 'source': 'pc', 'type': 'GtsPlus_PcCheckerTool.Checker.BaseboardChecker', 'method': 'DoCheckSync', 'pin': {'rva': 14176, 'body_size': 572, 'body_sha256': '816baafa3d8ce51bf5effaaf0403ce7b9780a30f08c478847e60f4e567b33bd7'}, 'needles': ['AppendResultToScreen'], 'finding': 'Compiled but disabled config: serial length below5 or literal Failed sets icon2.'}, {'key': 'pc.FirefoxChecker.DoCheckSync', 'source': 'pc', 'type': 'GtsPlus_PcCheckerTool.Checker.FirefoxChecker', 'method': 'DoCheckSync', 'pin': {'rva': 15456, 'body_size': 452, 'body_sha256': 'e7ff2c8bb3c5cffc79249609e7d3545dfdcd82a0f07a4296f2f59e8442dd07c2'}, 'needles': ['AppendResultToScreen'], 'finding': 'Compiled but disabled config: scans64/default uninstall registry views for DisplayName containing Firefox; presence sets icon1.'}, {'key': 'pc.SleepChecker.DoCheckSync', 'source': 'pc', 'type': 'GtsPlus_PcCheckerTool.Checker.SleepChecker', 'method': 'DoCheckSync', 'pin': {'rva': 15908, 'body_size': 836, 'body_sha256': '655135a6a8dbf4185290e5c8a97d150f92671f9673536f7be72e3e2d6bd05535'}, 'needles': ['AppendResultToScreen'], 'finding': 'Reads active/fallback power indices for display/sleep AC/DC; battery absence suppresses DC; nonzero total gives icon2; no power setting change.'}, {'key': 'pc.PortPreChecker.DoCheckSync', 'source': 'pc', 'type': 'GtsPlus_PcCheckerTool.Checker.PortPreChecker', 'method': 'DoCheckSync', 'pin': {'rva': 15176, 'body_size': 38, 'body_sha256': 'ac0fd73536ac751117b9bc8dc18afe424a5b3b92ac37702ce87fc9c12f04f607'}, 'needles': ['AppendResultToScreen'], 'finding': 'Informational prelude only; displays two texts without checking ports.'}, {'key': 'pc.PortExecChecker.DoCheckSync', 'source': 'pc', 'type': 'GtsPlus_PcCheckerTool.Checker.PortExecChecker', 'method': 'DoCheckSync', 'pin': {'rva': 17456, 'body_size': 504, 'body_sha256': 'a15b413b4de4ef53e1b0a3968169558c9c06392b4225d8585deb20fc6bb58c2a'}, 'needles': ['AppendResultToScreen'], 'finding': 'Parses netstat TCP local/remote ports against configured WSS ports and reports PID/name; any hit gives icon2; no socket connection.'}, {'key': 'pc.StartupChecker.DoCheckSync', 'source': 'pc', 'type': 'GtsPlus_PcCheckerTool.Checker.StartupChecker', 'method': 'DoCheckSync', 'pin': {'rva': 17128, 'body_size': 103, 'body_sha256': 'cb5e94500b5d1803b6801c4b5b340e6804a505b54d32fb2be9b62a3affaea1cf'}, 'needles': ['AppendResultToScreen'], 'finding': 'Checks common StartUp/GTSPlusArbitration.lnk; missing gives icon2.'}, {'key': 'pc.ProxyChecker.DoCheckSync', 'source': 'pc', 'type': 'GtsPlus_PcCheckerTool.Checker.ProxyChecker', 'method': 'DoCheckSync', 'pin': {'rva': 16976, 'body_size': 84, 'body_sha256': '41a53a82e35b63b804ae452d8c1c3b1d293cbf5964b4482f9c53ce7cd4e4ff30'}, 'needles': ['AppendResultToScreen'], 'finding': 'GetSystemWebProxy.IsBypassed(google URI), not HTTP request; configured proxy reports text, bypass gives icon1.'}, {'key': 'pc.ProcessChecker.DoCheckSync', 'source': 'pc', 'type': 'GtsPlus_PcCheckerTool.Checker.ProcessChecker', 'method': 'DoCheckSync', 'pin': {'rva': 13300, 'body_size': 440, 'body_sha256': 'f2b1d3eec8b29c952d3c7c7761575879665ba6a8f056a53190575cec06a527ce'}, 'needles': ['AppendResultToScreen'], 'finding': 'Requires configured application PID under install prefix and configured service PID>0; any absent gives icon2.'}, {'key': 'info.MainWindow.UpdateStatus', 'source': 'info', 'type': 'GtsPlus_InfoCenter.MainWindow', 'method': 'UpdateStatus', 'pin': {'rva': 23100, 'body_size': 1020, 'body_sha256': '460ba76b6032d3d2ce9b9051aa78e531245c24aa836c83b041cf9d1ce14f2955'}, 'needles': ['CheckNetworkAvailability', 'UpdateApplicationStatus', 'ds_unsent_req', 'ER_NotifyAppCommunicationCS', 'CUWPlusExePath', 'File::Exists', 'DataSyncExePath', 'File::Exists', 'Manifest.json', 'SoftwareVersion', 'Exception occurred while reading manifest json file.'], 'finding': 'Refresh is status/report UI, not application updater: calls network/running status, DataSync ds_unsent_req, checks CUW/DataSync files, loads ../Ver/Manifest.json[0].SoftwareVersion; missing/unparseable manifest logs and displays empty version.'}, {'key': 'info.MainWindow.UpdateApplicationStatus', 'source': 'info', 'type': 'GtsPlus_InfoCenter.MainWindow', 'method': 'UpdateApplicationStatus', 'pin': {'rva': 22768, 'body_size': 331, 'body_sha256': '7cb85db9ace22d2e67a4af1bdaf5cf8347784e5784f4168452aed9edc234f08f'}, 'needles': ['ER_GetAllRunningStatusCS', 'brtrue.s', 'result is failure', 'isGtsPlusHealth', 'isGUIServerHealth', 'and', 'isCUWPlusHealth', 'isGUIServerHealth', 'and'], 'finding': 'Running status API failure shows error icons; GTS and CUW healthy require respective owner and GUIServer health conjunction.'}, {'key': 'info.MainWindow.OnClickUpdateStatus', 'source': 'info', 'type': 'GtsPlus_InfoCenter.MainWindow', 'method': 'OnClickUpdateStatus', 'pin': {'rva': 24462, 'body_size': 24, 'body_sha256': 'f1c9d63252dd41d71775b840e87843205cdf49377fc65b09594d415cadb3315e'}, 'needles': ['UpdateEnvironment'], 'finding': 'Environment update button only refreshes UpdateEnvironment.'}, {'key': 'notify.Program.Main', 'source': 'notify', 'type': 'GTSPlusNotifyEnd.Program', 'method': 'Main', 'pin': {'rva': 8292, 'body_size': 76, 'body_sha256': 'd5b5cfffa96c9bfd2b62f0ac151c7057319262b2a11212bc63e96c9b04b7240f'}, 'needles': ['IsExecuteProcess', 'brfalse.s', 'GTSPlusNotifyEndExec'], 'finding': 'If Arbitration absent return0; running owner invokes safe-end protocol; uncaught error returns1.'}, {'key': 'notify.Program.GTSPlusNotifyEndExec', 'source': 'notify', 'type': 'GTSPlusNotifyEnd.Program', 'method': 'GTSPlusNotifyEndExec', 'pin': {'rva': 8368, 'body_size': 167, 'body_sha256': '03c60834b15631d5011a711aea87a0cb48bf40310dffcae728e87ca8adadcbd3'}, 'needles': ['StartNew', 'NORTIFY_END_WAIT_SEC', 'NORTIFY_END_WAIT_INTERVAL_SEC', 'div', 'INITIALIZE_VALUE', 'Thread::Sleep', 'IsTerminateGtsProcessMonitoring', 'NO_REPLY'], 'finding': 'Requests asynchronous safe-end; waits up to600 seconds at1-second interval; no reply2; reply error or owner not gone1; reply success and gone0.'}, {'key': 'notify.Program.IsTerminateGtsProcessMonitoring', 'source': 'notify', 'type': 'GTSPlusNotifyEnd.Program', 'method': 'IsTerminateGtsProcessMonitoring', 'pin': {'rva': 8536, 'body_size': 64, 'body_sha256': '87cf9957829fd7320d40d0db479ea84297df39237bad91a2cf4dcae04ad6334e'}, 'needles': ['IsExecuteProcess', 'END_MONITOR_INTERVAL_MILLI_SEC', 'Thread::Sleep', 'END_MONITOR_COUNT'], 'finding': 'Polls Arbitration absence at most10 times at500ms; owner still present returns false.'}, {'key': 'notify.CommonConst..cctor', 'source': 'notify', 'type': 'GTSPlusNotifyEnd.Consts.CommonConst', 'method': '.cctor', 'pin': {'rva': 8645, 'body_size': 45, 'body_sha256': 'e38350ece0c049d33d7a2140e0574052d4792839449369a056eafc300a5b30ea'}, 'needles': ['0x258', 'NORTIFY_END_WAIT_SEC', 'ldc.i4.1', 'GTSPlusArbitration', '0xa', '0x1f4'], 'finding': 'Safe-end owner GTSPlusArbitration; notification timeout600s, interval1s, termination poll10x500ms.'}, {'key': 'notify.<>c.<GTSPlusNotifyEndExec>b__2_0', 'source': 'notify', 'type': 'GTSPlusNotifyEnd.Program+<>c', 'method': '<GTSPlusNotifyEndExec>b__2_0', 'pin': {'rva': 8768, 'body_size': 60, 'body_sha256': '434f1a404ce8d875abf8553842c5c2feabe1a21014868a9c89c6d88ff710140a'}, 'needles': ['ER_EndABAppCS', 'VALUE', 'ERROR'], 'finding': 'Background call uses ER_EndABAppCS; exception stores end-notification ERROR0.'}, {'key': 'notify.ProgramReturn..cctor', 'source': 'notify', 'type': 'GTSPlusNotifyEnd.Program+ProgramReturn', 'method': '.cctor', 'pin': {'rva': 8726, 'body_size': 20, 'body_sha256': 'dfe6448c0225f5f2cce2804da85c09cbc950e2eb2b0f862ca891335a0d37359f'}, 'needles': ['ldc.i4.0', 'NORMAL', 'ldc.i4.1', 'ERROR', 'ldc.i4.2', 'NO_REPLY'], 'finding': 'Helper process exit codes NORMAL0, ERROR1, NO_REPLY2.'}]
SCRIPTS = [{'name': 'OnShowUI', 'decompiled_sha256': '493483620dbee40701defe5956336db2e6ac19f7a93980addf1e0911e7f89e56', 'actions_sha256': '85e196b34e1631fdad4ff79273e7df0d0eacbde1a42cad5583eb9e4bb31a2bbc', 'needles': ['OnUpdateUIBefore', 'OnMaintUIBefore', 'OnFirstUIBefore', 'OnMoveData', 'OnUpdateUIAfter'], 'finding': 'Select update/maintenance/first-install pre-handler, transfer, then matching after-handler.'}, {'name': 'OnFirstUIBefore', 'decompiled_sha256': 'bdd48cd12b09f1c6329379a13ca98d87a0061b1a9613d6514b8e9b08b64aa0f1', 'actions_sha256': 'b00db36066d6456abc169ff8c1c42d2a8e11bd1eec34c13ec356677c55947578', 'needles': ['Func_2364', 'abort', '== 12', 'OnSQLServerInitialize'], 'finding': 'Initial setup UI has backward-navigation label loops; unsupported first-install mode aborts.'}, {'name': 'OnMaintUIBefore', 'decompiled_sha256': 'db6c6ce1b93c6e4cd40b7291964d746ca733589231c0c12c7eee495a694ec66e', 'actions_sha256': 'a47a013a5208877664e117917dcfc1cd0a5fa0be19e299aa8553e5b90282b07e', 'needles': ['LclVarNum2 = 303', '!= 6', 'SafetyShutdown', 'nLaunchResult > 0', 'Func_714'], 'finding': 'Maintenance selects removal303, requires yes6; if SafetyShutdown exists calls helper and aborts exit>0; then removes logged/all components.'}, {'name': 'OnMoved', 'decompiled_sha256': '2f1d7610bdc2d19796442e423cce4c8fa333fedb8f8bbf34648539990b9a715a', 'actions_sha256': '992983023e29dec61ff06994991f5e7ba184b10de38e543e933438010def1369', 'needles': ['Setup_DataSync.exe', 'VerifyTest2.exe', 'nLaunchResult == 0', '/clone_wait -s', '0 == Func_694', 'nLaunchResult != 0'], 'finding': 'Pure uninstall dispatches11 registry uninstall commands with -s, ignoring return; otherwise ten optional sibling installers run in fixed order /clone_wait -s. Only DataSync/GUI are signature checked. Nonzero child exit aborts only when launch wrapper returns0; absent child and failed launch do not enter that abort.'}, {'name': 'OnEnd', 'decompiled_sha256': '3b6b04e4fe4f266fdf7700050226a57fdbc7191c2cd3761cc4f9dd320a42f41b', 'actions_sha256': 'df9c420919eadd872e3a8c4ec183f7fbab730e93cab85f224ee7ea37b77e0489', 'needles': ['GTS+GUIServer', 'Users\\\\Public\\\\Documents\\\\GTSPlus\\\\UserData', 'GTSE File', 'Work', 'Func_792'], 'finding': 'Except pure uninstall, starts GTS+GUIServer; creates UserData, GTSE File shortcut, Work and permissions.'}, {'name': 'OnCustomizeUninstInfo', 'decompiled_sha256': '0e77818b7832124f0f8bcd017c4de737f6710c4e6b6afeb9e7247c77174ee4d7', 'actions_sha256': 'ceff967ad3fa79b9ca741268de71d02267efd231a6e424a85d180668fa2cef49', 'needles': ['setup.iss', ' -f1', 'Func_770', 'SafetyShutdown'], 'finding': 'Persists setup.iss and adds -f1 response path to uninstall string; copies SafetyShutdown helper and dependencies into uninstall location.'}, {'name': 'OnMoveData', 'decompiled_sha256': '775e16369dd97dd12af3e3bb074d5c2891ab5c3caec62f14aa41940b1649f619', 'actions_sha256': '90ee99a07852232589a49251f1e48f3c5cf1ba1152bd2571a85fa4f7b932c07a', 'needles': ['Func_704', 'OnComponentError', 'abort', 'OnCustomizeUninstInfo'], 'finding': 'Component transfer error invokes OnComponentError and abort; successful disk transfer customizes uninstall metadata.'}, {'name': 'OnFirstUIAfter', 'decompiled_sha256': '081eb9248fb7c5353dc3d8f093681bb330d12be3548038b889f99b55397658cc', 'actions_sha256': '5cbe5a6f837726812c1ff8529b0842f148ddad806f3c7d44cd5de172110adfec', 'needles': ['GblVarNum1', 'Func_1216', 'Func_1189'], 'finding': 'Reboot-needed flag selects SdFinishReboot path; otherwise ordinary finish.'}, {'name': 'OnUpdateUIAfter', 'decompiled_sha256': '066e92f66a0738020183708edd3914007e3c15022544407aed0a628586fa5a0a', 'actions_sha256': 'a580decf48cc9a4a6fd85588f91f6cbf930c47a86bdc98896051c8e76eee843f', 'needles': ['GblVarNum1', 'Func_1216', 'Func_1189'], 'finding': 'Update uses same reboot-needed finish policy.'}, {'name': 'OnMaintUIAfter', 'decompiled_sha256': '10aafd8b09abf2b645548ce09d779c4f01ad9831f90cf60e4b21f3bd170d9220', 'actions_sha256': '1710814f928e9467df252d07e3332be9ae55aea97a6aa3274f3e47177f1f0a67', 'needles': ['GblVarNum1', 'Func_1216', 'Func_1189'], 'finding': 'Maintenance uses same reboot-needed finish policy.'}, {'name': 'OnCanceling', 'decompiled_sha256': 'ba91049007d543e827a6de2480790d2fa7a6b104ba2896a0cc029d4f7233e2d0', 'actions_sha256': 'c4c1febe85f2f606e8a7a7055c7410ad3e03317e053b64ce0090e4d845c23310', 'needles': ['6 == Func_1284', 'Func_511', 'Func_1189', 'abort'], 'finding': 'Confirmation result6 closes current dialog, displays cancellation finish and aborts; decline returns.'}, {'name': 'OnAbort', 'decompiled_sha256': '9de629289be929f09a10455e993c27d5f3458f083cab6074c6ea6103f168ae79', 'actions_sha256': 'f8483089ee77302a9f652ddd873ade517c07eb31998ab90e893013bd21e55c6d', 'needles': ['return'], 'finding': 'Abort callback returns without Toyota child compensation.'}, {'name': 'OnRebooted', 'decompiled_sha256': 'd15e9a7aa92734d79b3326daf5fffe0cc0eac643bb749784547de4a29d64ee39', 'actions_sha256': '8ea2e065f86a4e0b307170a77d45f9d9119c41d0ef74c5f9f6f8dfaec86c2b03', 'needles': ['return'], 'finding': 'Rebooted callback returns; no Toyota custom recovery action.'}, {'name': 'OnFileLocked', 'decompiled_sha256': '7df534e87d174ac9f17690253a5e9da3206e926c68ee1594c56a607d74206650', 'actions_sha256': 'c76f377e135359c4cf1db7e0ced5ff722f54d1ffd331291969f1136ef158d44c', 'needles': ['return 100'], 'finding': 'File-locked callback returns100 to setup engine.'}, {'name': 'OnFileError', 'decompiled_sha256': '1688e005b908b56bacef9f32d7aa21e2af194879ed88c63c2f2d1b5ba5eef783', 'actions_sha256': 'c149a2cc9a7f69748060be1fc3197993a615326a90cc21a6ea1b0835ae755fb9', 'needles': ['== 3', 'goto label_1', 'return LclVarNum2'], 'finding': 'File error UI repeats while result3; other result returned to engine.'}, {'name': 'OnInternetError', 'decompiled_sha256': 'e80a9c936bc50f298857839e9410650a7e88e6ce9b256a505b64a9f75d432c2c', 'actions_sha256': '3e79714989e05152d582e6964a526729c63550c3261635571e79d58071341066', 'needles': ['== 3', 'goto label_1', 'return LclVarNum3'], 'finding': 'Internet error normalizes error code and repeats dialog while result3; other result returned.'}, {'name': 'OnMD5Error', 'decompiled_sha256': '35efd4b60df81f4449637a3e0b9a4345f6e53a75d84bad19cb5df07132c76434', 'actions_sha256': '2253090e462cdf5bcdcb1548dab7d0c2ae52987753525ea8806b4fc9f8f7a78a', 'needles': ['== 3', 'goto label_1', 'return LclVarNum1'], 'finding': 'MD5 error repeats dialog while result3; other result returned.'}, {'name': 'Func_629', 'decompiled_sha256': '8e1b17d71bfd09b04fad433055139cbd77eede8051eefbcf467f9de2db488418', 'actions_sha256': '0406b4b46bf666b430d416107fdbd77daaec8423e585b96c31cce2156a67bdfa', 'needles': ['CreateProcess', 'nLaunchResult = Err.LastDllError', 'Func_674(-1', 'Func_652'], 'finding': 'Launch wrapper uses CreateProcess; creation failure records LastDllError and returns-1; success waits and queries exit code.'}, {'name': 'Func_694', 'decompiled_sha256': 'b02f605a35a13571dce4c98c446297b94d6b3459a03c92b1e895a64238840458', 'actions_sha256': '32a7a32190ced89de92083d7eafee9a0946b4e9a4d9331580350a2e0b5fc627c', 'needles': ['Func_629', '1024 | 512'], 'finding': 'LaunchAppAndWait wrapper adds options1024|512.'}, {'name': 'Func_1834', 'decompiled_sha256': 'd789a9e0bf11e1085717b2fe4c603b09772533dc584b6d877f786965603912db', 'actions_sha256': 'e9f021c42b96ae12d18f9afff4e340d8a3be60cfb1d3399a6c00a39ef4221642', 'needles': ['-2147483647', 'UninstallString', '-2147483646'], 'finding': 'Uninstall command lookup reads HKCU then HKLM Uninstall/<GUID>/UninstallString.'}, {'name': 'Func_1216', 'decompiled_sha256': '3726558096f86ef64efed94fd45c8a4effa6109c2b3ca699aabcf0db289b8c8c', 'actions_sha256': '41a8ece0c5dd6d5603b29d21cd87c57a791f539df812c912ed53e75473839779', 'needles': ['SdFinishReboot', 'BootOption', 'Func_1376'], 'finding': 'SdFinishReboot handles silent BootOption3 or interactive selected reboot control by invoking Func_1376(3).'}, {'name': 'Func_1376', 'decompiled_sha256': '0639d2d768d9d96661de31046ead8fd8a6bdeeb76fd6c47bb7ee08e2c525037d', 'actions_sha256': '33575b8825d3339a90c7d408c176a283912d32cd233443b6032b263ca6404d7f', 'needles': ['!= 3', 'GblVarObj4.Reboot'], 'finding': 'Reboot option3 delegates to setup engine object.Reboot; other options return-1.'}, {'name': 'Func_2018', 'decompiled_sha256': 'f880d3569e7661f92e1ead47acda52bb1efca45b8fc43df553af37199e7a3e4a', 'actions_sha256': '82cdddfcc1eb58fa54bc98e777e2cb517b02dfdc8581119a385bc19be8786a2c', 'needles': ['StartServiceW', 'Func_2007'], 'finding': 'Service-start wrapper calls StartServiceW and waits running state4; reports failure.'}, {'name': 'Func_704', 'decompiled_sha256': '64015ac384f87e3f1467a80923c0db409659ab32813d2ed39ae9240f823d11f6', 'actions_sha256': 'cc0af592e9109476f08885de690888bdf2183f4faa07554a102e76056e7b37bf', 'needles': ['_ComponentTransferData', '-2147213312', 'abort', '-2147213311', 'exit'], 'finding': 'Component transfer delegates to ISRT; special errors abort/exit; others returned.'}, {'name': 'IfxOnAbortInstall', 'decompiled_sha256': '2a1eee1026397cbbc4ee6b08f0a498a4af936ecf76c1ad4e676f48ac11ddd500', 'actions_sha256': '1deedbf0be2a33c30084be89c73722359afc6e68d0791dadaf908b450c12d7c8', 'needles': ['OnAbort', 'Func_1670', 'IfxOnUnhandledException'], 'finding': 'Runtime abort delegates empty Toyota OnAbort then setup-engine exit cleanup.'}]
METHODS.append({
    "key": "pc.App..ctor", "source": "pc",
    "type": "GtsPlus_PcCheckerTool.App", "method": ".ctor",
    "pin": {"rva": 11964, "body_size": 163, "body_sha256": "e4f68829e487aa205a15be9a818fbb0d952998ad8e45cd5077497664007748ee"},
    "needles": ["0x2e", "PCT_LOG_DIR", "PcCheckerTool", "SetEnvironmentVariable", "GetLogger"],
    "finding": "Sets PCT_LOG_DIR to CommonDocuments/PcCheckerTool/Log before logger construction.",
})
RECOVERED_SOURCES = {
    "pc": "GtsPlus-PcCheckerTool/GtsPlus-PcCheckerTool.exe",
    "info": "GtsPlus-InfoCenter/GtsPlus-InfoCenter.exe",
    "cm": "GtsPlus-PcCheckerTool/GtsPlus-CM.dll",
}
PROTECTED_PINS = {
    "pc": {"stub_sha256": "c76f4682a8b7e8f796977a54a6a6a71aff112ceac5d3c6010a951e0f86522b0e",
           "sidecar_sha256": "7453b231fa30fa4f77750e0e3df30dc71b9e81431a81f8c31bb11ac005a4311a"},
    "info": {"stub_sha256": "2514d8764baa006656e5d655221262c6f3a350c7f2b490ca0760673aaf9270c7",
             "sidecar_sha256": "ac794b8f208154edd07945e101c28a4efcb76dc868b749989b78bec85c1f59f1"},
    "cm": {"stub_sha256": "6816de2916dfde134ebe035fef08c8c7229601fd1f0005a43e73a6611faa1306",
           "sidecar_sha256": "e1f2c6d500dce48b79b9d189d1c059f491ce0917cddb2264068971029cddfa5f"},
}
CHILD_ORDER = ["Setup_DataSync.exe", "Setup_InfoCenter.exe", "Setup_DB.exe", "Setup_PF.exe", "Setup_GUI.exe", "Setup_GuiServer.exe", "Setup_NativeGraphViewer.exe", "Setup_PCSDataViewer.exe", "CUWPlusPF.exe", "Setup_TSEConverter.exe"]
COMPONENTS = [{'installer': 'CUWPlusPF.exe', 'sha256': '1f05534b5a6435797cb61c9eec12936af922a3d7ed374669d7790d03fe9aa247', 'record_count': 17, 'inx_sha256': '8b823604cc7f0bc243b7c71946d350dcd7864978fa5c5c9aaea572cb39d3a894', 'inx_size': 242086, 'inx_offset': 35107618, 'parent_installer': None, 'functions': [{'name': 'OnFirstUIBefore', 'decompiled_sha256': '03b13e8c2740aec73dee150a037c02ffdb6031cf9fcc82902fb7b0a595f5cd10', 'actions_sha256': '5d7178fae6992f03dc1627d02cd6c97a889a5cde9777b986626230e71d7b5f1f', 'anchors': ['abort;']}, {'name': 'OnMaintUIBefore', 'decompiled_sha256': 'c66934d048c3c994585035aad395a00ef4ad082f794e3011185550581cfa00db', 'actions_sha256': '36acaf7b324ead6234aaddc74b9c069a1a6c982c454c9173c01f941f19daf626', 'anchors': ['abort;', 'abort;']}, {'name': 'OnFirstUIAfter', 'decompiled_sha256': 'ec7b01a9e7c7b94c047d1d82d4f4f07b4608aaafbacbe712f0d90ccec82b6359', 'actions_sha256': '97b05c00c31587e83a447fb443500cfe8d92c4dac3d173f5cc1722412cbad88b', 'anchors': ['return;']}, {'name': 'OnMaintUIAfter', 'decompiled_sha256': '0f4192fc8f27d54025510d3ddf72730c446b0a5980fab44c8cde22431db393d5', 'actions_sha256': '878f621b3a4cf1f4abd21d65145c1ae13f178ab5866f808313e8eae31c9f3d61', 'anchors': ['return;']}, {'name': 'OnUpdateUIAfter', 'decompiled_sha256': '9c27b63b7f439995340cf7ebd32f59858cb627708dc9b38cb6f6af0aa1947fff', 'actions_sha256': '23f5508a1dbcbed5301f7dbb9127049f42b2796c9a5da385b4a48057f4f164e1', 'anchors': ['return;']}, {'name': 'OnMoving', 'decompiled_sha256': '06d2793d6c8f08f9e75692536c5bf0c3b837fa4649399c4a11775083adab0767', 'actions_sha256': 'dca788527bf591813cc0ac8e0e79e4f14649ba85456a3ea02a6430031d54cc0a', 'anchors': ['return;']}, {'name': 'OnMoved', 'decompiled_sha256': '1bccd8efdbe480e57944b634c14ebd15a2f1e46dd875d8f73d5a71142450e626', 'actions_sha256': '0188869e4135aa3dffac113898596b39e62459982b2a52bd53cf8b7a2847321f', 'anchors': ['return;']}, {'name': 'OnEnd', 'decompiled_sha256': '640ecaea2cfe406c359aaf69bb1c0ad96c217adb2af29daacc353e624359ff6d', 'actions_sha256': '18bd8ee5618103156c6ba3e2cf910194711ab77aad27c93a65da3ef7bff64ae4', 'anchors': ['LclVarStr13 = "CUW+ PF.txt";']}, {'name': 'OnBegin', 'decompiled_sha256': '7cf40f1616c55323ddf90ec9157a486996fc738898791a0d2b9790c5276486ce', 'actions_sha256': '6e8bf08af39a362840659eaf283fd813b1a838cc6a3b343b9a4977bc26cb4d5c', 'anchors': ['return;']}, {'name': 'OnAbort', 'decompiled_sha256': '9de629289be929f09a10455e993c27d5f3458f083cab6074c6ea6103f168ae79', 'actions_sha256': '2beba2465b7af32d15b4f8cf417de5a294f4419e1efe2bd886981c8ab6471331', 'anchors': ['return;']}, {'name': 'OnRebooted', 'decompiled_sha256': 'd15e9a7aa92734d79b3326daf5fffe0cc0eac643bb749784547de4a29d64ee39', 'actions_sha256': '3ebc3087791a29923b58e19a2562cc68d42e47352299ab9fd913802bb4344686', 'anchors': ['return;']}, {'name': 'OnCanceling', 'decompiled_sha256': 'ce20029c302ddc8f1289681d1a349e0020d5b858c4b56199be91bff74b80e0b5', 'actions_sha256': 'f6b7cffce703860765d837917e9fe25b12baf5cfce6f18c444e7ef5460ffd327', 'anchors': ['abort;']}, {'name': 'OnCustomizeUninstInfo', 'decompiled_sha256': '05499c43b02bd4c9e9b31996519db253134b6af30e7bf2b404ff53eb0eef5308', 'actions_sha256': '972c4b98ac949dd66dede793443952c1ac6a8b3b2b6866844f0d2bcd836f57d0', 'anchors': ['return;']}, {'name': 'CUWPlusPF_UnInstalled', 'decompiled_sha256': 'f3bdf4e2d6f7b553fca6ab6c095b98d1f245de59ed8be5fad42b71f90f57e901', 'actions_sha256': '11a484cf4e670f8b0d7d86f28265cef5b460aa5492d30c54416d0cd85e463fb4', 'anchors': ['function LONG CUWPlusPF_UnInstalled()']}, {'name': 'CUWPlusPF_Installed', 'decompiled_sha256': 'f9fae2cad03463f076b62ca106cb234284b1579456215ec9ac84bdb427602770', 'actions_sha256': '4e30bf75a1ba3e5ca25638cbc66cb9c52c5f24b5450df50a6aa1fc4ea59f3e7a', 'anchors': ['Func_649(GblVarStr4 ^ "CUWLauncher_Setup.exe", "/clone_wait -s", 134217729);', 'LclVarStr1 = Func_2206() ^ "VerifyTest2.exe";', 'LclVarNum1 = Func_662(GblVarStr1, LclVarStr4, "CUWDLL\\\\" + "*.dll", LclVarNum2, 32768);', 'if (GblVarObj15.nLaunchResult == 0) then', 'Func_1204(-65533, "Signature Check Error", "(%d)\\nFollwing file has an invalid signature or no signature.\\n\\n%s", GblVarObj15.nLaunchResult, LclVarStr2);', 'abort;', 'LclVarNum1 = Func_662(GblVarStr1, LclVarStr4, LclVarStr5 + "*.dll", LclVarNum3, 32768);', 'if (GblVarObj15.nLaunchResult == 0) then']}], 'embedded_runtime_packages': [], 'cabinet_file_count': 841, 'finding': 'Feature hook launches embedded CUWLauncher_Setup /clone_wait -s without checking result, then signature-verifies CUWDLL/CUWPlusPF DLL/exe sets and aborts on helper0. Uninstall hook dispatches launcher GUID uninstall -s. Completion writes temp/CUW+ PF.txt.'}, {'installer': 'Setup_DB.exe', 'sha256': 'e3782befd6ee4ffe56f63ddcaf8b07221fb0579a3a2ac548bdefb88315979520', 'record_count': 16, 'inx_sha256': 'b008c71c1380688b9d3e043ba4579a638e9be3b86721777236142f98d974561a', 'inx_size': 229313, 'inx_offset': 262207877, 'parent_installer': None, 'functions': [{'name': 'OnFirstUIBefore', 'decompiled_sha256': 'aade4c4e92f9335cff8b5c27face6c52853b5b43deeaf1f4f1fc423871303059', 'actions_sha256': '4e0f075e40aa9dcccd287f1aeaa1a415f649f02ad94edf5e8f3afa909599b6b4', 'anchors': ['abort;']}, {'name': 'OnMaintUIBefore', 'decompiled_sha256': 'ecbcc544724af9c7b652ab5ac90e570b8b42ade2137de19a2b479301a709b8e7', 'actions_sha256': '15090fc9966334efd9d0368b0b5984c033dd9c66e9fc5b6c7efbefca6b4fb357', 'anchors': ['abort;', 'abort;']}, {'name': 'OnFirstUIAfter', 'decompiled_sha256': 'c977d81630ca7ac62e47cf8bd81cff9ff84f041530333194bd963b000a92f7c3', 'actions_sha256': 'a5c13fc906362b8cd9e59094dcc5e9ae92dd42d3391cb143438b44a7af1491fc', 'anchors': ['return;']}, {'name': 'OnMaintUIAfter', 'decompiled_sha256': 'a32db00b25d361446d15c2389c1b2458e45602971fc37e24ff687f3404e38fb9', 'actions_sha256': '1f0e79f8735f97c3fda2f5f41f8629aa4df70d81e1d0decd1ebbbde5c79e3513', 'anchors': ['return;']}, {'name': 'OnUpdateUIAfter', 'decompiled_sha256': '7bfc22909c91cd42600c51122adf1e31af171bfdd1d5c14453c91f6756a6f17b', 'actions_sha256': '4a7e5c97e7f06a200f62b84621e5b5466a35a09d58f24c4fdf6920b52f52fe19', 'anchors': ['return;']}, {'name': 'OnMoving', 'decompiled_sha256': '06d2793d6c8f08f9e75692536c5bf0c3b837fa4649399c4a11775083adab0767', 'actions_sha256': '300f2aa2bb84733ba6a8b10902a0792b4514e410f1d52149fc744258a4efd8a2', 'anchors': ['return;']}, {'name': 'OnMoved', 'decompiled_sha256': '1bccd8efdbe480e57944b634c14ebd15a2f1e46dd875d8f73d5a71142450e626', 'actions_sha256': '0b1716f6414387a07b599a719de5a88467f6c801b3f7dca7c8605c08a1ba6f62', 'anchors': ['return;']}, {'name': 'OnEnd', 'decompiled_sha256': 'b009d06e17e4c751bfdfb9cc07479ad1071c5382ef8b6e63ddbac39dc87eab3a', 'actions_sha256': '551079a74e93bab0548b1e9acdf2babed56b850fe7049a98b893280f42d55755', 'anchors': ['return;']}, {'name': 'OnBegin', 'decompiled_sha256': '7cf40f1616c55323ddf90ec9157a486996fc738898791a0d2b9790c5276486ce', 'actions_sha256': '37b0389e1aea86b49b101ab7f715da97ec539ecc82acdfba528593e5a15646be', 'anchors': ['return;']}, {'name': 'OnAbort', 'decompiled_sha256': '9de629289be929f09a10455e993c27d5f3458f083cab6074c6ea6103f168ae79', 'actions_sha256': 'c310fe363fb3e76c66be76747bab10b6ae658441f5049eedbaae2fb57f008c17', 'anchors': ['return;']}, {'name': 'OnRebooted', 'decompiled_sha256': 'd15e9a7aa92734d79b3326daf5fffe0cc0eac643bb749784547de4a29d64ee39', 'actions_sha256': '9861c87b176d26850ea3fca11a0a74f78f97db9c5acb9b01f7a8f9142f65a0ce', 'anchors': ['return;']}, {'name': 'OnCanceling', 'decompiled_sha256': '84eab9fd26b63ce18e2d6e95cf8b78b199ac46c772c3b16b0b654a0b12d5892e', 'actions_sha256': '4705bcb7fcdd392f30ad889503372e6980301110f607dc43a211af1f81c39d70', 'anchors': ['abort;']}, {'name': 'OnCustomizeUninstInfo', 'decompiled_sha256': 'a8c7dd9ea3c99c15bbd4d9c925997298c0e6a6aedd5e129bdfed3014db8f9e00', 'actions_sha256': 'f5c7e42cfd26edc62a0fc3aa8f735c68e87bb85e0aaf370893866eac518f4a78', 'anchors': ['return;']}], 'embedded_runtime_packages': [], 'cabinet_file_count': 2053, 'finding': 'Database setup uses standard first/maintenance/update transfer and cancel/finish paths; OnMoved/OnEnd/OnAbort/OnRebooted return without Toyota custom action.'}, {'installer': 'Setup_DataSync.exe', 'sha256': '8466c3d039794bcec23df57b6fa487717bb2514545987dbefa3f96fa8f10a2bc', 'record_count': 16, 'inx_sha256': '3f8ca3d92af03f24a1233bdd9e7fe3a6a091ce7dd010ea5df0112231c48723b0', 'inx_size': 254519, 'inx_offset': 14429056, 'parent_installer': None, 'functions': [{'name': 'OnFirstUIBefore', 'decompiled_sha256': 'e6227e5abd112bfbf4ef069cd5258552e5bd37c4fe5b1e8e473180fc68674074', 'actions_sha256': '43578e8e5e816a9ba60a77e2ef38bda4c0c20770249338d18ea888b14497a2d5', 'anchors': ['abort;']}, {'name': 'OnMaintUIBefore', 'decompiled_sha256': 'db5914479e2e016534fcd7ad26dce6ca8521512c157f2342bb98fa00ec15c224', 'actions_sha256': 'b864fa903c6cbc7e7fcb3802b364e929017331691ee315ac9de5e9cf57e88e94', 'anchors': ['abort;', 'abort;']}, {'name': 'OnFirstUIAfter', 'decompiled_sha256': '9714a136c07aaa717167721252caa27719cc6aa13e2c093b84161d45d2a7ffa5', 'actions_sha256': '00fb8127d96652e3cc6a07beaed75b169ef52f8adea9b1317b3e82e4da32ef70', 'anchors': ['return;']}, {'name': 'OnMaintUIAfter', 'decompiled_sha256': '499371647b5cda9ed8e74aa38858ca166dc631728cf26c62c7d078146bb72a67', 'actions_sha256': 'd3861bd57ec75e6895ec9d338640d9ca782d5777f31b4fb26ef1f3e279dc4071', 'anchors': ['return;']}, {'name': 'OnUpdateUIAfter', 'decompiled_sha256': 'a988669938d1f2385c5873e56d05218a1a5d2e0983c59dbd95af83f63d7f8062', 'actions_sha256': '9ca4086a08f92f1b1c85731e11398ff5612c0fc7fa8bd053e93e7ec4244a4851', 'anchors': ['return;']}, {'name': 'OnMoving', 'decompiled_sha256': '5d092daf4127d9a1ff172482a33cf326dd6277c8fd9890e07708e378b5ce3a44', 'actions_sha256': '844267321d11f0c077a5405da44383914c8904b079a12b82b3fd56354ad0d40d', 'anchors': ['GblVarObj17.nStopServiceWaitCount = 5;', 'KERNEL32.Sleep(1000);', 'KERNEL32.Sleep(1000);', 'until ((LclVarNum1 == 5) | (LclVarNum2 >= 0));', 'LclVarStr3 = Func_2320() ^ "cmd.exe";', 'Func_2243(LclVarStr4, "/C (for /l %%i in (1,1,5) do (tasklist | findstr %s && taskkill /F /IM %s & tasklist | findstr %s || exit)) & (exit)", "GtsPlus-ProxyManager.exe", "GtsPlus-ProxyManager.exe", "GtsPlus-ProxyManager.exe");']}, {'name': 'OnMoved', 'decompiled_sha256': 'eeccb83add4ebbab66652dfec12691dea446e2bb9b91484102487a4a43577f47', 'actions_sha256': 'dddb42ea0ec639677e0a7f87c841ba247335b06e9cd10f3efd334071ae8c25fe', 'anchors': ['LclVarStr2 = GblVarStr49 ^ "GTSPlusDataSync.exe";', 'LclVarStr4 = Func_2320() ^ "cmd.exe";', 'LclVarStr6 = "GtsPlus-ProxyManager.exe";', 'if (GblVarObj15.nLaunchResult == 1) then']}, {'name': 'OnEnd', 'decompiled_sha256': 'b009d06e17e4c751bfdfb9cc07479ad1071c5382ef8b6e63ddbac39dc87eab3a', 'actions_sha256': '0adc0b8c6b45b035a12aaa5bce59f91a0e5885a0f9f47eed51151093dafae797', 'anchors': ['return;']}, {'name': 'OnBegin', 'decompiled_sha256': '7cf40f1616c55323ddf90ec9157a486996fc738898791a0d2b9790c5276486ce', 'actions_sha256': '6db2a72685275070b1b75c36be754e42edbe517decf97e2456e329e0c26cc0ba', 'anchors': ['return;']}, {'name': 'OnAbort', 'decompiled_sha256': '9de629289be929f09a10455e993c27d5f3458f083cab6074c6ea6103f168ae79', 'actions_sha256': '404fd39dabc9c8b00fe7a0ed3c3ff32a838c8cccc7cb04db6e2f3534b52373fd', 'anchors': ['return;']}, {'name': 'OnRebooted', 'decompiled_sha256': 'd15e9a7aa92734d79b3326daf5fffe0cc0eac643bb749784547de4a29d64ee39', 'actions_sha256': '720eb48b3aab80a182a59efbab001d3e26e80443735bec9715dc6c148a86344f', 'anchors': ['return;']}, {'name': 'OnCanceling', 'decompiled_sha256': '2702657c850084cacc05eef6d3a0ead80744b5605b577cafcb25c41cd539f706', 'actions_sha256': 'b4db7f077560dda90dfe14181e27cc7e81deced68b899735347eea7caee9218a', 'anchors': ['abort;']}, {'name': 'OnCustomizeUninstInfo', 'decompiled_sha256': 'c6d320f85258439e2aa1554a72d4098cc392390ecedd34e86d309b538669376f', 'actions_sha256': '7bba87ccebe836e3289a26f1f13c57ab25e8960da8101ac5a9e8c4a1d17d8b19', 'anchors': ['return;']}, {'name': 'DataSyncCP_Proxy_Installed', 'decompiled_sha256': '022a21de0fe8ba1512f9a3ef73eca922c5f92995eec18baebea883a236577ba8', 'actions_sha256': 'd63bc5c2f576932cfd3c86940d9f5836f034452c68444fce6070af3c4391ef99', 'anchors': ['LclVarStr1 = "GtsPlus-ProxyManager.exe";']}, {'name': 'DataSync_Installed', 'decompiled_sha256': '55cbaa45c65829ddafb860a922b8b945f14319d24cbfb6003684c2f63b13fc40', 'actions_sha256': 'd2ba8ec2c50f4c7be3e84800cbc556d56ebe04a9d7d54f20bff9628bcc375800', 'anchors': ['return;']}, {'name': 'GTSPlus_Installed', 'decompiled_sha256': '095f4f0fe39aff1595dbbcefd06148ac467df0be83941070b2af60b5e1cf5a4a', 'actions_sha256': '70aba8dd1ba5c65dd035cfb991991fa34e43775111eb000a17cea600ff299471', 'anchors': ['return;']}, {'name': 'DataSyncCP_Installed', 'decompiled_sha256': '6612fde8eea2b7aabb2418043d5431fc44ac549b6a14ef6a76c83fbe9cca9c4a', 'actions_sha256': '5c77a4e2907ca2fca599deaf459422384a6559a0364dfcf713a60392517f16eb', 'anchors': ['return;']}, {'name': 'Verifying_Certificate', 'decompiled_sha256': 'de1503e5ffa6fc40f42026178a77e86d288f94a6fac425482df46d499227adfe', 'actions_sha256': 'aedabac979c81dc41d4132d9e6149951591087351bdb15ab6562bb71e10988b4', 'anchors': ['LclVarStr3 = Func_2322() ^ "VerifyTest2.exe";', 'LclVarNum1 = Func_676(GblVarStr1, LclVarStr1, LclVarStr2 + "*.dll", LclVarNum2, 32768);', 'if (GblVarObj15.nLaunchResult == 0) then', 'Func_1220(-65533, "Signature Check Error", "(%d)\\nFollwing file has an invalid signature or no signature.\\n\\n%s", GblVarObj15.nLaunchResult, LclVarStr4);', 'abort;', 'LclVarNum1 = Func_676(GblVarStr1, LclVarStr1, LclVarStr2 + "*.exe", LclVarNum3, 32768);', 'if (GblVarObj15.nLaunchResult == 0) then', 'Func_1220(-65533, "Signature Check Error", "(%d)\\nFollwing file has an invalid signature or no signature.\\n\\n%s", GblVarObj15.nLaunchResult, LclVarStr4);']}, {'name': 'Func_1924', 'decompiled_sha256': '46a4012eb0e7b1f3897a69d371e8fb87050e398b844ff222ac2597aad26b6f39', 'actions_sha256': '780b5bb7b57845237d2fbd37120c01a170cbce6c5e1251d2e944aca06a2843ff', 'anchors': ['if (Advapi32.ChangeServiceConfigW(LclVarNum4, GblVarObj17.dwServiceType, GblVarObj17.dwStartType, GblVarObj17.dwErrorControl, &LclVarStr4, GblVarObj17.lpLoadOrderGroup, GblVarObj17.lpdwTagId, GblVarObj17.lpDependencies,', 'LclVarNum4 = Advapi32.CreateServiceW(LclVarNum3, &LclVarStr1, &LclVarStr2, GblVarObj17.dwDesiredAccess, GblVarObj17.dwServiceType, GblVarObj17.dwStartType, GblVarObj17.dwErrorControl, &LclVarStr4, GblVarObj17.lpLoadOrderGroup,', 'UnUseDLL("advapi32.dll");']}, {'name': 'Func_1935', 'decompiled_sha256': 'eb4568aaef13f0bcb5c75fbd70722f4edab917e58461eab27f31a74aef5a9419', 'actions_sha256': 'db42ffae98da49d56934eaca2d2a450502a10230a4eca96cc70d18ebed6e9c17', 'anchors': ['return Func_1982(LclVarNum2, LclVarStr2);']}, {'name': 'Func_1938', 'decompiled_sha256': '14af95b93cafddcd5d805d5f9987349979eb797d522c8da85e57d009a4dd93f3', 'actions_sha256': '3ac0e3980d424b9e56904d267f1950a6878b4ea92d167f607b47c6500781cb93', 'anchors': ['if (Advapi32.DeleteService(LclVarNum1) == 0) then']}, {'name': 'Func_1982', 'decompiled_sha256': '72a2c348ff2bc5cc0d00feebddc1209f6a47450bbff0b86ea369512b4195c54f', 'actions_sha256': '604b085f636367dc33540644c3ab248a1b3d214d4997caa3bac7f713fa11ae0f', 'anchors': ['if (Advapi32.StartServiceW(LclVarNum1, SizeOf(LclVarObj1), LclVarNum3) == 0) then', 'if (Func_1971(LclVarNum1, 4, 2, GblVarObj17.nStartServiceWaitCount) == 0) then']}], 'embedded_runtime_packages': [], 'cabinet_file_count': 98, 'finding': 'Before transfer, attempts bounded DataSync service stop and up-to-five ProxyManager taskkills; stop/launch failures do not abort here. After transfer creates/changes and starts GTS+ DataSync, starts ProxyManager if tasklist reports absent; uninstall deletes service. Feature hooks verify DLL/exe groups; Proxy feature creates startup shortcut.'}, {'installer': 'Setup_GUI.exe', 'sha256': '2f686fff3251c09ce2213941a8d3cb15bcbfe83e5ce4fc6c815886da0082868f', 'record_count': 16, 'inx_sha256': '2ff9f69486c7286a3753c45976bc1fb0e1d0639d5ac780eaa3bfc5f912fb23b0', 'inx_size': 241373, 'inx_offset': 30711573, 'parent_installer': None, 'functions': [{'name': 'OnFirstUIBefore', 'decompiled_sha256': '5ee7ccd733fc456a1535500dfde5fe915976b8a301fbc826e8a182539e7fe93b', 'actions_sha256': '18d1c4ed2f5573c9e0909ebb1fd3c79eb23ae509588a00ba7130c9faaf0f2325', 'anchors': ['abort;']}, {'name': 'OnMaintUIBefore', 'decompiled_sha256': 'e167b80d0b03d21e95f1a2d76fccfcb22840cfb2edabe11c443b88a5268e2ee9', 'actions_sha256': '01b800595d93c8c8fded58341a20522d73dae12d4da899c6f1e2b153db04022b', 'anchors': ['abort;', 'abort;']}, {'name': 'OnFirstUIAfter', 'decompiled_sha256': 'ac9ceb82c7632d3710c23966a2544abf22c8a44c89fae358d0481aae91372042', 'actions_sha256': '812a7f6c4f940ceb12a33e5781afb16d2417174fd7d6c3f0272fb08f2f5dd778', 'anchors': ['return;']}, {'name': 'OnMaintUIAfter', 'decompiled_sha256': '67be9482b1963bcb3b3c6852612c8f06651324e7b067102668bf2dc88b3e0a4b', 'actions_sha256': 'a36076eabdac6192544b0942a4caa7b1a7330281edc1724969fac078b19d65fa', 'anchors': ['return;']}, {'name': 'OnUpdateUIAfter', 'decompiled_sha256': '5d0e0cfa69191ab11d82cbb4458857226bf0f41c812f41ef17375d374a69e859', 'actions_sha256': 'c4ce8bc1df67ecb34c0514754dd8c2119d754288de87bb0f065a6df373f988a9', 'anchors': ['return;']}, {'name': 'OnMoving', 'decompiled_sha256': '06d2793d6c8f08f9e75692536c5bf0c3b837fa4649399c4a11775083adab0767', 'actions_sha256': '1c586d86299094ef3c3825b6d34eb6a13b61772ff49be17176239949da03a23e', 'anchors': ['return;']}, {'name': 'OnMoved', 'decompiled_sha256': '1bccd8efdbe480e57944b634c14ebd15a2f1e46dd875d8f73d5a71142450e626', 'actions_sha256': '5fa312a60b15da92a93c48f40a090042dc5111048a100918fd0f4bce2ad0d3ba', 'anchors': ['return;']}, {'name': 'OnEnd', 'decompiled_sha256': 'c4ae08366e242b5bbfbe568fa23b522e6c2f68c6e81df8c3491dcaf0af734d68', 'actions_sha256': 'f3d26bdb30d293c9882eec10bdec49c0a6cc282ab08cf52944c8bc3d6959d0f4', 'anchors': ['LclVarStr7 = "SOFTWARE\\\\Classes\\\\.gtse";', 'Func_1673(LclVarStr7, "", 1, GblVarStr3 + "\\\\GTSE\\\\GTSPlusTSEStartup.exe %1", -1);', 'LclVarStr14 = "GTS+ GUI.txt";']}, {'name': 'OnBegin', 'decompiled_sha256': '8734e36e33e891688f55fd3b146cc38ed84d9045a72a2dee655345092d46cd8f', 'actions_sha256': '43cb0ace24c53a0877d49c1b18eba8c6d8a88c20511467ee014dd3574dc7b8bb', 'anchors': ['return;']}, {'name': 'OnAbort', 'decompiled_sha256': '9de629289be929f09a10455e993c27d5f3458f083cab6074c6ea6103f168ae79', 'actions_sha256': '63842b7d03f4acd8181e1b6284fe2f9fe3b1e4927695c9cdfe0259a7f07c99e7', 'anchors': ['return;']}, {'name': 'OnRebooted', 'decompiled_sha256': 'd15e9a7aa92734d79b3326daf5fffe0cc0eac643bb749784547de4a29d64ee39', 'actions_sha256': '5ff6fe5dacde02ab7e2054cee1051cce3f4ec85e3fb68850c9d3e18da9d99b7f', 'anchors': ['return;']}, {'name': 'OnCanceling', 'decompiled_sha256': '7d50ca34b5505ed835fc227c707e95794698052c82f2b690500d542499fcc19a', 'actions_sha256': 'f86b949b2027a0812d0135546c62845539b965ee9f6d7b2fe43df08b3a4f9479', 'anchors': ['abort;']}, {'name': 'OnCustomizeUninstInfo', 'decompiled_sha256': '0056f9ab227c8b45e2df52f8310f32db8cfcfd91dcb3f448bef759f7a2f2926a', 'actions_sha256': '7c5884d18e934cdb4aa2363204f760ebfaa9de22d5a7b68e08e105b74c84ac1b', 'anchors': ['return;']}, {'name': 'GTSPlusGUI_Installed', 'decompiled_sha256': '8012d7583ad4af3aaa7471e7a44139fa057f4cd85e32bd82c2c4ecf2df1cc046', 'actions_sha256': '36c9fa9f0d6f73ffe1065f18b2515b13822cdd38da0b1984123d2cb3b6dbae52', 'anchors': ['LclVarStr1 = Func_2202() ^ "VerifyTest2.exe";', 'LclVarNum1 = Func_659(GblVarStr1, LclVarStr4, LclVarStr5 + "*.dll", LclVarNum2, 32768);', 'if (GblVarObj15.nLaunchResult == 0) then', 'Func_1201(-65533, "Signature Check Error", "(%d)\\nFollwing file has an invalid signature or no signature.\\n\\n%s", GblVarObj15.nLaunchResult, LclVarStr2);', 'abort;', 'LclVarNum1 = Func_659(GblVarStr1, LclVarStr4, LclVarStr5 + "*.exe", LclVarNum3, 32768);', 'if (GblVarObj15.nLaunchResult == 0) then', 'Func_1201(-65533, "Signature Check Error", "(%d)\\nFollwing file has an invalid signature or no signature.\\n\\n%s", GblVarObj15.nLaunchResult, LclVarStr2);']}, {'name': 'Func_1674', 'decompiled_sha256': '7875c3ca1e00d2b64e30ccfd1c22ae5e47f9fd0a298d93d5084ed52a54df47f1', 'actions_sha256': '3a164752e6ff7ca2af72f2ee018e9116aa5ad342475d7b03889f6e147e8e89f9', 'anchors': ['return ISRT._RegDeleteValue(GblVarNum0, GblVarNum8, LclVarStr1, LclVarStr2);']}, {'name': 'Func_1673', 'decompiled_sha256': '57e35b0fe665a0bcd054dbfefd4a64d884a699a3016dfbc9ec562d21ed088b8f', 'actions_sha256': 'c53d7eb39a85d5b2f9d71557b45add14d44121135bd26fee1a59dc2c7b138eaf', 'anchors': ['return Func_1803(GblVarNum8, LclVarStr1, LclVarStr2, LclVarNum1, LclVarStr3, LclVarNum2);']}, {'name': 'Func_1666', 'decompiled_sha256': 'a4e89d73d9d369a594b77cdf438cfe6a708d7cab9013e95bccd78e86bd92c94f', 'actions_sha256': '6412783de02546f6f4f97ac168bd8c1331c7cec90f4ad9205078f3a8eebeb95f', 'anchors': ['return ISRT._RegCreateKey(GblVarNum0, GblVarNum8, LclVarStr1, LclVarStr2, 0);']}], 'embedded_runtime_packages': [], 'cabinet_file_count': 97, 'finding': 'Feature hook verifies GTSE DLL/exe sets, aborting helper0. OnBegin deletes old public desktop GTSPlus.url; OnEnd sets .gtse open command to GTSPlusTSEStartup.exe %1 and writes temp/GTS+ GUI.txt; hides child uninstall DisplayName.'}, {'installer': 'Setup_GuiServer.exe', 'sha256': '328788d4b4930fc37b5f542f68d19991b2361395a40366d3f3b370fc33162e82', 'record_count': 16, 'inx_sha256': 'b7076bbe0c7216a1d33f68e8f12c9e22dd1762fa153192cb14da9e02652e199c', 'inx_size': 252653, 'inx_offset': 7796434, 'parent_installer': None, 'functions': [{'name': 'OnFirstUIBefore', 'decompiled_sha256': 'bb45c12528c9aca776aefa90cb1c9422681d18c5e5bbfc6395e72c6766d9deaf', 'actions_sha256': '1220d334c4c6b2eaa5d9346a344034ab99d09d246d3d18c3c73e3a5d27cfcad2', 'anchors': ['abort;']}, {'name': 'OnMaintUIBefore', 'decompiled_sha256': '1fb4512e7fa40666330a0d07f9ce640195bc6fc25042842160be4093da9af923', 'actions_sha256': '1cb6cd3908ba28249c9ca5db07053251a279913cdeee729eb1239106da8f88c4', 'anchors': ['abort;']}, {'name': 'OnFirstUIAfter', 'decompiled_sha256': '1493d45cbcddc320ee2a8b7b6602a3c5de875d712d3bcd65b58e281e4b323384', 'actions_sha256': 'd0fa3df230940c9793cb9e67faac8941c697606b7de06115219af0d7971bb59b', 'anchors': ['LclVarNum3 = Func_651(Func_2306() ^ "CertsInstall\\\\CertInstaller.exe", "", 1);', 'Func_1929("GTS+GUIServer", "GTS+GUIServer", "Web server to provide GTS+ web contents", GblVarStr3 + "\\\\ContentServer\\\\LocalWebServerWindowsService.exe", 1, "");']}, {'name': 'OnMaintUIAfter', 'decompiled_sha256': '55055411088ee72ef1dacedd5d3c7c90ce0ce4646277e50377e0bf7b87e7ffc8', 'actions_sha256': 'fb406148ef68ffae3f5318a2160f1998b82baa2faec5c41495ee1eda21b674fc', 'anchors': ['return;']}, {'name': 'OnUpdateUIAfter', 'decompiled_sha256': '0a2824cbd4f06e23419049fddd032f56a995e382745e95010aacc7ec2e30848b', 'actions_sha256': '800e12dd19dc21e65ca53493a502772e8d565dc22bb1101bb35c45185f2f34f2', 'anchors': ['return;']}, {'name': 'OnMoving', 'decompiled_sha256': '4c04581e13e2cb65f92242822522a72a028e674257dee17f427419790912fd7d', 'actions_sha256': 'c13d91787e3449e768fba9f11afbca612f3fd230f097f29d0d2b2e67f8c80da1', 'anchors': ['GblVarObj17.nStopServiceWaitCount = 5;', 'KERNEL32.Sleep(1000);', 'KERNEL32.Sleep(1000);', 'until ((LclVarNum1 == 5) | (LclVarNum2 >= 0));']}, {'name': 'OnMoved', 'decompiled_sha256': '1bccd8efdbe480e57944b634c14ebd15a2f1e46dd875d8f73d5a71142450e626', 'actions_sha256': 'e149cd80ef03e92fcbd899f575f7421b33f80e87c55e2ece8b40a4c427946ced', 'anchors': ['return;']}, {'name': 'OnEnd', 'decompiled_sha256': 'a7c5de38521e7cac4cd66cce8f2d1357114d77e9d4c6004e74826fd9ea1a0917', 'actions_sha256': '11ea5407f9134319d867cc4ed641f2c3885f0e3a1cb817aaeb6676bec283c20d', 'anchors': ['LclVarStr4 = "GTS+GUIServer.txt";']}, {'name': 'OnBegin', 'decompiled_sha256': '7cf40f1616c55323ddf90ec9157a486996fc738898791a0d2b9790c5276486ce', 'actions_sha256': '55e3c65c5bc25e75e0f0d83f5078e6e072921fec3a13a903a4529e1bbfffede9', 'anchors': ['return;']}, {'name': 'OnAbort', 'decompiled_sha256': '9de629289be929f09a10455e993c27d5f3458f083cab6074c6ea6103f168ae79', 'actions_sha256': 'a13b5b8af8e7c635f2f2b84450c1d8c296c2c2e061f19ee728ff7aa088b72513', 'anchors': ['return;']}, {'name': 'OnRebooted', 'decompiled_sha256': 'd15e9a7aa92734d79b3326daf5fffe0cc0eac643bb749784547de4a29d64ee39', 'actions_sha256': '5073945dace9fe1d8e32a3685d490fb73cfd1663e5c59971f73bc964f8e963bf', 'anchors': ['return;']}, {'name': 'OnCanceling', 'decompiled_sha256': '3b7a6bfd218867c163c65d4497257d66abfac17ae89833a939a1c262a426413c', 'actions_sha256': 'ed071e227d040912e7cde822ad7b6a42719c39d46bb85bac13f10e6d3e367eb9', 'anchors': ['abort;']}, {'name': 'OnCustomizeUninstInfo', 'decompiled_sha256': 'b68b3c0f560ff40386c1861e95581d5bf4bafd463e0199e21e925a447fd16e5c', 'actions_sha256': '5fb0dca02a6918c1387b2594b77e8c5fa9cd2a4325fc0444305e46d93454fb5d', 'anchors': ['return;']}, {'name': 'GTSPlusGUIServer_UnInstalling', 'decompiled_sha256': '169d19ed2c0fac6a5ce25823e65c765ad98ed94e82be8d251a9fb70e09948726', 'actions_sha256': '812d9b202da062e80287a85a62dacba395f01357c4ed847214a416bdded00066', 'anchors': ['return;']}, {'name': 'GTSPlusGUIServer_Installed', 'decompiled_sha256': 'a4f4dce051d685e179dae025d7723e10f960c2faf04ea524255e8030b459f53a', 'actions_sha256': 'f7b43853c4e1bd6b4495aa01df3dff0113b142c43790bff57f6200dc2a9321f8', 'anchors': ['LclVarStr1 = Func_2306() ^ "VerifyTest2.exe";', 'LclVarNum1 = Func_664(GblVarStr1, LclVarStr4, LclVarStr5 + "*.dll", LclVarNum2, 32768);', 'if (GblVarObj15.nLaunchResult == 0) then', 'Func_1225(-65533, "Signature Check Error", "(%d)\\nFollwing file has an invalid signature or no signature.\\n\\n%s", GblVarObj15.nLaunchResult, LclVarStr2);', 'abort;', 'LclVarNum1 = Func_664(GblVarStr1, LclVarStr4, LclVarStr5 + "*.exe", LclVarNum3, 32768);', 'if (GblVarObj15.nLaunchResult == 0) then', 'Func_1225(-65533, "Signature Check Error", "(%d)\\nFollwing file has an invalid signature or no signature.\\n\\n%s", GblVarObj15.nLaunchResult, LclVarStr2);']}], 'embedded_runtime_packages': [], 'cabinet_file_count': 64, 'finding': 'Before transfer bounded service-stop retry with1000ms sleeps; failure does not abort this hook. Feature hook verifies ContentServer DLL/exe sets; uninstall hook launches persisted removeCerts.bat; completion writes GTS+GUIServer.txt. CertInstaller helper and local TLS batch are separately pinned.'}, {'installer': 'Setup_InfoCenter.exe', 'sha256': '0d2b32bf441291b52764183ba9595e13102bf869fec2b4917c15a202a1b8655d', 'record_count': 16, 'inx_sha256': '5bfb321f64511a28c81343e2c327b288585ed484559803b69930aad86ce98f9a', 'inx_size': 241234, 'inx_offset': 28711719, 'parent_installer': None, 'functions': [{'name': 'OnFirstUIBefore', 'decompiled_sha256': '8d369b6abc863dfcc00c05fc3c18c1c72b6358dea9e99fb4deaa9fbe7f71ff2c', 'actions_sha256': 'f276cdc20732c658c153b9fb7f8689cdb664a49015a0a58d9e54d1eed76cd5c4', 'anchors': ['abort;']}, {'name': 'OnMaintUIBefore', 'decompiled_sha256': 'a6e82912f05c89c4b31a59673d8b5c2a551013921854288b302ba920f9d24662', 'actions_sha256': '2958f64362d633009fe3de5d4a900b139449a7c20d53bab90543f56b30244b91', 'anchors': ['abort;', 'abort;']}, {'name': 'OnFirstUIAfter', 'decompiled_sha256': '2309cc1c69cfcdadfe0991f22e10e53dbf95b7b95121428f7ddf0bd472ce9f23', 'actions_sha256': '2e86c9e4c2f05771b5191d6602613294dea42767b119c629e40caef7f53e1732', 'anchors': ['return;']}, {'name': 'OnMaintUIAfter', 'decompiled_sha256': '9693d850ff5ef9901cbef2947f5b6362f671ffef9bd05dbd41bc0ce99a32c114', 'actions_sha256': '14e008653a42a0625fe6f659a0eb43accb1a32a81f6f8bb487625bab72c7cfb8', 'anchors': ['return;']}, {'name': 'OnUpdateUIAfter', 'decompiled_sha256': 'aa442acd42ae5652f7bb2006dab17de34838b523b7b7cbe89402ce211354a3d7', 'actions_sha256': '7eb67afff2b3558c1689a380657bfe2696c3e16ea1ba0acfdcd2ca96982438d7', 'anchors': ['return;']}, {'name': 'OnMoving', 'decompiled_sha256': '06d2793d6c8f08f9e75692536c5bf0c3b837fa4649399c4a11775083adab0767', 'actions_sha256': 'e69888d8717e56d88503d7602281e04551af5bf475fe31e9da1111d29d9f95cc', 'anchors': ['return;']}, {'name': 'OnMoved', 'decompiled_sha256': '1bccd8efdbe480e57944b634c14ebd15a2f1e46dd875d8f73d5a71142450e626', 'actions_sha256': 'a4f3ef9ab867153bbb2ac5cad626b6c1bc37c81ef5b37f1c4630ec1ac9c477a5', 'anchors': ['return;']}, {'name': 'OnEnd', 'decompiled_sha256': 'b009d06e17e4c751bfdfb9cc07479ad1071c5382ef8b6e63ddbac39dc87eab3a', 'actions_sha256': '960c730404b1e39f9fff99a2b1a035f75beec2448684008e0615de5b270a531e', 'anchors': ['return;']}, {'name': 'OnBegin', 'decompiled_sha256': '7cf40f1616c55323ddf90ec9157a486996fc738898791a0d2b9790c5276486ce', 'actions_sha256': 'e1b219f10c8810a12b0adf9bd7d68e158c226babb1a148ee8e948573a7c142a6', 'anchors': ['return;']}, {'name': 'OnAbort', 'decompiled_sha256': '9de629289be929f09a10455e993c27d5f3458f083cab6074c6ea6103f168ae79', 'actions_sha256': 'd3fde2e61c969c0ad5d6c5b513d4bb9dc05997317c8e4c6ba60f091f4c3cc059', 'anchors': ['return;']}, {'name': 'OnRebooted', 'decompiled_sha256': 'd15e9a7aa92734d79b3326daf5fffe0cc0eac643bb749784547de4a29d64ee39', 'actions_sha256': '06d90f05582aa9881d4c81dfa5c0d56e2e0367051dae9e8fee2b425926861188', 'anchors': ['return;']}, {'name': 'OnCanceling', 'decompiled_sha256': '170b5e16996beef1111b7154a2b323ab5e729402e0dfbb697e15dfe1490e8762', 'actions_sha256': '03eb638849b30f38c5c1696d40fd232ba670c0f47f5f75b6bdc496632d8927af', 'anchors': ['abort;']}, {'name': 'OnCustomizeUninstInfo', 'decompiled_sha256': 'ec62d10aa3360bde5aa4b698dfa89064c0f8fae7c9b85ce40b09bbb44bd55a5f', 'actions_sha256': '79d52df5521c3ec0746936276019889d2b38581c73842c93ddac77a7058a7d9b', 'anchors': ['return;']}, {'name': 'GTSplus_Installed', 'decompiled_sha256': 'eb48364c6a5772079e73534ec85ef48b5f1f8888076e86af20e19288443689a4', 'actions_sha256': 'b4c84d2a44a933da3658987c675fa123c98d1cdda2d2769dbb3f81b2daab4bcc', 'anchors': ['return;']}, {'name': 'GTSPlusCP_Installed', 'decompiled_sha256': '83dae961fa0c987b4ecc28fc152cf26e6826516c9e1f99f11e8220e19ab716fa', 'actions_sha256': 'a05eead5b8c96dde08a4603f69e38463793d0360800870de060f191cafb1adb4', 'anchors': ['return;']}, {'name': 'Verifying_Certificate', 'decompiled_sha256': '8b31e4f517b3f3cb825456b32727312b7afb45c4533a5c67d2dff745f85119bc', 'actions_sha256': 'ce82633389b39535acbf9de04ca1385bf5386c0b8ae495159c62920385f503ef', 'anchors': ['LclVarStr3 = Func_2202() ^ "VerifyTest2.exe";', 'LclVarNum1 = Func_660(GblVarStr1, LclVarStr1, LclVarStr2 + "*.dll", LclVarNum2, 32768);', 'if (GblVarObj15.nLaunchResult == 0) then', 'Func_1203(-65533, "Signature Check Error", "(%d)\\nFollwing file has an invalid signature or no signature.\\n\\n%s", GblVarObj15.nLaunchResult, LclVarStr4);', 'abort;', 'LclVarNum1 = Func_660(GblVarStr1, LclVarStr1, LclVarStr2 + "*.exe", LclVarNum3, 32768);', 'if (GblVarObj15.nLaunchResult == 0) then', 'Func_1203(-65533, "Signature Check Error", "(%d)\\nFollwing file has an invalid signature or no signature.\\n\\n%s", GblVarObj15.nLaunchResult, LclVarStr4);']}], 'embedded_runtime_packages': [], 'cabinet_file_count': 172, 'finding': 'Feature hooks verify GTSPlus/GTSPlusCP DLL/exe groups, aborting helper0. OnMoved/OnEnd/OnAbort/OnRebooted have no Toyota custom operation.'}, {'installer': 'Setup_NativeGraphViewer.exe', 'sha256': '73fe91d0a38f21c2902de075625bf6171f8d106d2d2b92661fe5ec3e4631f8c3', 'record_count': 123, 'inx_sha256': '3ad2ae63f8f2c5d4e78682fb68738bf9a4d8cd2c2e3d08d83fd47948f1ad022d', 'inx_size': 256703, 'inx_offset': 309759454, 'parent_installer': None, 'functions': [{'name': 'OnFirstUIBefore', 'decompiled_sha256': 'ae1e63ed9ed30c8b6b137469dbdc7366473d19a96fef509a7760d9cc381b40f4', 'actions_sha256': '140d19e090d28ab920a678371e7ef2e7687d36e7a83d7d03c045dda654f9adf8', 'anchors': ['abort;']}, {'name': 'OnMaintUIBefore', 'decompiled_sha256': 'f6d787d57101ad8f9b56c2a83b45b9665a053bc4b587f2450e9a056b5ef44098', 'actions_sha256': '5113eb02b0a8e7a6b37af1e3aee98f6f777f880db7e46d615dcab6a73748c750', 'anchors': ['abort;']}, {'name': 'OnFirstUIAfter', 'decompiled_sha256': 'f726408491373398d9078f0bbbc261ed24bf72441258d362051a868f3da48578', 'actions_sha256': '511d1316cc74db413e513bd688760aded17141ce7e3a25c21c0b9e929cf7d7a5', 'anchors': ['Func_15();']}, {'name': 'OnMaintUIAfter', 'decompiled_sha256': 'cbae56e060cd02763ab126ff935d3320a964ddcb5d54747c4820e08dc6383a84', 'actions_sha256': '73537f40b1107ddd27e8a18903f8d8cdd058bbbe1a48c7af8b8d640421ab4fd0', 'anchors': ['Func_663(Func_2379() ^ "\\\\Toyota Diagnostics\\\\GTSPlusGraphViewer\\\\uninst.exe", "/qb " + Func_16("GTS+ GraphViewer"), 2306);', 'Func_15();']}, {'name': 'OnUpdateUIAfter', 'decompiled_sha256': 'af3f7b3c3adb7f30922318ec0425634ed535bc92bfaeab003cf6b5732018c15c', 'actions_sha256': '23a5229210302458d85d911f9fedcfed610d5b3ef66b06416964763c0a9b379e', 'anchors': ['Func_15();']}, {'name': 'OnMoving', 'decompiled_sha256': '06d2793d6c8f08f9e75692536c5bf0c3b837fa4649399c4a11775083adab0767', 'actions_sha256': 'b36afdd07808ea7d76698bb56bb284a6c79f940a8c568d003a5a69312643ca36', 'anchors': ['return;']}, {'name': 'OnMoved', 'decompiled_sha256': '1bccd8efdbe480e57944b634c14ebd15a2f1e46dd875d8f73d5a71142450e626', 'actions_sha256': '04397a8162ed0e37d193b223534ebfc0b39cb3302f4a437bce2d133a9b823d84', 'anchors': ['return;']}, {'name': 'OnEnd', 'decompiled_sha256': '62fcaead6129e66613c70d05526c3376fead1da7f468853b4abf306e18ccb7e4', 'actions_sha256': '1f4f6164aafc4b044a3cb52f74d41c8e6db893a380bcd8eea54304a00d8663a3', 'anchors': ['LclVarStr10 = "GTS+_NativeGraphViewer.txt";']}, {'name': 'OnBegin', 'decompiled_sha256': '7cf40f1616c55323ddf90ec9157a486996fc738898791a0d2b9790c5276486ce', 'actions_sha256': 'aca83ff29776b64383f72fd068e5b0c2045b64d352d2a1e4ea7e330188e05800', 'anchors': ['return;']}, {'name': 'OnAbort', 'decompiled_sha256': '9de629289be929f09a10455e993c27d5f3458f083cab6074c6ea6103f168ae79', 'actions_sha256': 'a3f606a740b1b7eb88e69a9bb88cfb535b37e8f7d17773e29c9c20527cca930a', 'anchors': ['return;']}, {'name': 'OnRebooted', 'decompiled_sha256': 'd15e9a7aa92734d79b3326daf5fffe0cc0eac643bb749784547de4a29d64ee39', 'actions_sha256': '8411c0d4366478110bbc7e6b091fc283e13d7eb11baa29179d6143a89c19dc6c', 'anchors': ['return;']}, {'name': 'OnCanceling', 'decompiled_sha256': '6081750d0a325b3a644f8a8a9bc13e22fb51805aec3a0068173e02651e283da1', 'actions_sha256': '73e2d212742830ddeceb45510e0a815bef56b180a1361201008e559b00374190', 'anchors': ['abort;']}, {'name': 'OnCustomizeUninstInfo', 'decompiled_sha256': 'b293706b51fd1779b146f171770c61265a597ea849491b6c3cde7b7930fb2836', 'actions_sha256': 'ddcab70ad2673c74700b201cc21bfd9a661be65dd9ad880eb05a078ec47eee16', 'anchors': ['return;']}, {'name': 'DefaultFeature_Installed', 'decompiled_sha256': '0f9197241c45f420e49e6238302c8fe2a0f8d3b2831d62d48fbe3d008d4b992c', 'actions_sha256': '43d6fb5b1d3a3bc9e37503f39f8319e4a796251439515dd42e68a579b3b0b70e', 'anchors': ['function LONG DefaultFeature_Installed()', 'LclVarStr1 = Func_2381() ^ "VerifyTest2.exe";', 'LclVarStr2 = GblVarStr4 ^ "\\\\NativeGraph\\\\Volume\\\\Install.exe";', 'if (GblVarObj15.nLaunchResult == 0) then', 'Func_1376(-65533, "Signature Check Error", "(%d)\\nFollwing file has an invalid signature or no signature.\\n\\n%s", GblVarObj15.nLaunchResult, LclVarStr2);', 'abort;']}, {'name': 'Func_15', 'decompiled_sha256': '530128adbc3c8bf05532ea5025bb44e6e0ec8e676234ca738c7c60ad79ead490', 'actions_sha256': 'e6ef72e7857aa2d8374910b5035aa2e68b671a34d6285040da31df141c4463c8', 'anchors': ['function LONG Func_15()', 'Func_663(GblVarStr4 ^ "\\\\NativeGraph\\\\Volume\\\\Install.exe", (GblVarStr4 ^ "\\\\NativeGraph\\\\Volume\\\\spec.iss ") + "/qb- /log " + (GblVarStr4 ^ "\\\\NativeGraph\\\\Volume\\\\result.log /r"), 2306);']}, {'name': 'Func_1852', 'decompiled_sha256': '0e9b8befda5db6efe9f49ff2495de9dafade5930bd67922e78ca79e915c324b3', 'actions_sha256': 'e2f8bd6047d93af85395bedf0b6dd32e54b0786f1b3d9f120864796515a0fc66', 'anchors': ['return ISRT._RegDeleteValue(GblVarNum0, GblVarNum8, LclVarStr1, LclVarStr2);']}], 'embedded_runtime_packages': ['UserInstaller.msi', 'MetaUninstaller.msi', 'EULADepot2.msi', 'KillBit.msi', 'KillBit64.msi', 'MSIProperties.msi', 'MSIProperties64.msi', 'MDFSupport.msi', 'CertInstaller_Wrapper.msi', 'DotNet462.msi', 'DotNet462_Wrapper.msi', 'DotNet480.msi', 'DotNet480_Wrapper.msi', 'VC2015-32Wrapper.msi', 'VC2015-64Wrapper.msi', 'VC2015Core.msi', 'MStudioUI.WPF.BooleansFx45Runtime32.msi', 'MStudioUI.WPF.NumericsFx45Runtime32.msi', 'MStudioUI.WPF.ControlsFx45Runtime32.msi', 'MStudioCommonFx40Runtime32.msi', 'MStudioCommonFx40Runtime32.msi', 'MStudioUI.WPF.GraphsFx45Runtime32.msi'], 'cabinet_file_count': 13, 'finding': 'Feature hook verifies NI NativeGraph/Volume/Install.exe, aborting helper0. After install/update invokes NI engine with spec.iss /qb- /log result.log /r; maintenance removal invokes graph uninst.exe /qb then deletes empty directories. Hides child/NI uninstall DisplayName values and writes marker.'}, {'installer': 'Setup_PCSDataViewer.exe', 'sha256': '4bb87da0cd00a18393b47666d20a4d59a912dac9a49b90626b62679744fc6827', 'record_count': 10, 'inx_sha256': 'a6388ffd8b60d5303f0dfe34d5b17f7fa2a5408774b56bc3ea31bac3e7c5730c', 'inx_size': 246740, 'inx_offset': 12379334, 'parent_installer': None, 'functions': [{'name': 'OnFirstUIBefore', 'decompiled_sha256': '2350ed4d3cc9f45661593490c204b1ec48bd1d6fb738b649fb7cd892c2b78744', 'actions_sha256': 'ceea284de8933936b1b0c9c1fd2bcaa5e815c66962970f6df53d8c520d8f0cc4', 'anchors': ['abort;']}, {'name': 'OnMaintUIBefore', 'decompiled_sha256': '0e6f57994080730d1c22b110f4d119c8da917a69dcab7bbdab1f660780a22b82', 'actions_sha256': '41e7b8f983a7a8657dfabd5054733996b76d61ffde3a9c0a4c7655f72076c2df', 'anchors': ['abort;']}, {'name': 'OnFirstUIAfter', 'decompiled_sha256': '79998ee59dc4ff9d36a8018b02e5c16456bc644bcdc5a3d633a060af1427bde1', 'actions_sha256': 'a769f4776235dcc2c4e80cafeedf7e5bf1e1f7d136a560a38a8b87c3d015f4d5', 'anchors': ['return;']}, {'name': 'OnMaintUIAfter', 'decompiled_sha256': 'ac70bc6d1c9b6afde48327b96ed820f70ec763c2c1c9c552bf34d4009fdb944c', 'actions_sha256': 'eef1f8efe1ad717e797e1364185df02afc5cad4f1843416b6f0983fc9ceca44f', 'anchors': ['return;']}, {'name': 'OnUpdateUIAfter', 'decompiled_sha256': '2032bd7d3331b05738f3c63fe20ef04e43f47f4e9885217c5d8206fde7db03c9', 'actions_sha256': 'f4d5281a4fce22040291d11b9737909f54edc079b97ef5d73f7f9cd1abd86c9a', 'anchors': ['return;']}, {'name': 'OnMoving', 'decompiled_sha256': '06d2793d6c8f08f9e75692536c5bf0c3b837fa4649399c4a11775083adab0767', 'actions_sha256': '95f5b9915f5be6d582597ba0d79b59cc2b826de086d9d5575fed096002136c09', 'anchors': ['return;']}, {'name': 'OnMoved', 'decompiled_sha256': '1bccd8efdbe480e57944b634c14ebd15a2f1e46dd875d8f73d5a71142450e626', 'actions_sha256': '362afee0bfbc971df4a93131643fdd710b8c43713f432cfc54a2c474d4447389', 'anchors': ['return;']}, {'name': 'OnEnd', 'decompiled_sha256': 'b5f11351f45d3d606c20f4e046a0ed689663af17966a8e7573860cf9f723d2a4', 'actions_sha256': '340098ee9da98efe34e7bde78eec5fb3bac17709ed4faa841823b5f57f44ef2f', 'anchors': ['LclVarStr5 = "PCS Data Viewer.txt";']}, {'name': 'OnBegin', 'decompiled_sha256': '7cf40f1616c55323ddf90ec9157a486996fc738898791a0d2b9790c5276486ce', 'actions_sha256': 'de82551ef0dadb0fe484c77fa1eb6d33a0d4185a04ffcee904ba405dbee434a2', 'anchors': ['return;']}, {'name': 'OnAbort', 'decompiled_sha256': '9de629289be929f09a10455e993c27d5f3458f083cab6074c6ea6103f168ae79', 'actions_sha256': '14bce32de703a9853dbb016fbd5d821cff3b04ed4f90bd81d10c17a0aab041ea', 'anchors': ['return;']}, {'name': 'OnRebooted', 'decompiled_sha256': 'd15e9a7aa92734d79b3326daf5fffe0cc0eac643bb749784547de4a29d64ee39', 'actions_sha256': 'c998104b99d5d16155bafeb1d6998759c24912b371f63c42245ddc199eeae44b', 'anchors': ['return;']}, {'name': 'OnCanceling', 'decompiled_sha256': '1611d2317edb83aad0a1f47caf543ea303867b5fd27210c1539ce6a010d77315', 'actions_sha256': 'ffc97b640cf8f8a7f432288de5c311a034743988c60f28bd75e15cc2c941425a', 'anchors': ['abort;']}, {'name': 'OnCustomizeUninstInfo', 'decompiled_sha256': '3ef0a56d711a408a6fbb834a3372f46cc2364aeb91796f1253fd8feb8c47ed0f', 'actions_sha256': '81b0b5700f46318bd5f39fa3541ad30f8ff38a439d726f6c63e7633efbffcb2e', 'anchors': ['return;']}, {'name': 'PCSDataViewer_UnInstalled', 'decompiled_sha256': 'b13f0ae0005fb4d8d712b5541b0d2168e442c38bc3e657799cf8549ccb7eedb0', 'actions_sha256': 'c56d522f4e9fd87a11ea5521825e0c40c69195965b3e4c9960e217d8e85a80e9', 'anchors': ['return;']}, {'name': 'PCSDataViewer_Installed', 'decompiled_sha256': '57d1aea6576e5f1870440a4ac0d3b2f4d4398d102e7ffa5078456160ea48280a', 'actions_sha256': '2b50d6ae301be5b7d8ba867fd02698afd404ab3ece6f2c26c52b064a4434a473', 'anchors': ['LclVarStr1 = Func_2259() ^ "VerifyTest2.exe";', 'LclVarNum1 = Func_663(GblVarStr1, LclVarStr4, LclVarStr5 + "*.dll", LclVarNum2, 32768);', 'if (GblVarObj15.nLaunchResult == 0) then', 'Func_1255(-65533, "Signature Check Error", "(%d)\\nFollwing file has an invalid signature or no signature.\\n\\n%s", GblVarObj15.nLaunchResult, LclVarStr2);', 'abort;', 'LclVarNum1 = Func_663(GblVarStr1, LclVarStr4, LclVarStr5 + "*.exe", LclVarNum3, 32768);', 'if (GblVarObj15.nLaunchResult == 0) then', 'Func_1255(-65533, "Signature Check Error", "(%d)\\nFollwing file has an invalid signature or no signature.\\n\\n%s", GblVarObj15.nLaunchResult, LclVarStr2);']}], 'embedded_runtime_packages': [], 'cabinet_file_count': 29, 'finding': 'Feature hook verifies installed DLL/exe groups; uninstall hook removes Help/application directories; completion writes PCS Data Viewer.txt.'}, {'installer': 'Setup_PF.exe', 'sha256': '5b62e7249372432aa9efb455ad46cf77d323eca889b27cec78b98eaac8ad4d11', 'record_count': 16, 'inx_sha256': '91e5eae7d75df894e2a1de1f6e767905c0b28d649801ec88d85b85ce2e69a11b', 'inx_size': 244402, 'inx_offset': 125229373, 'parent_installer': None, 'functions': [{'name': 'OnFirstUIBefore', 'decompiled_sha256': '3375b67db2ed7f6b2e015b73486d0577583feb53bdf29e01e05514f50709829c', 'actions_sha256': '6ad8b389e044d31a3fed69b2336032c630a52589e5c4e76d58d617ee55299214', 'anchors': ['abort;']}, {'name': 'OnMaintUIBefore', 'decompiled_sha256': '809d09757d8a41b66816465bedb818624abeaf11e4b7197ae380e8fa0e6d13c4', 'actions_sha256': '7baeb10e17db0717c73b95772658dcfa656e3b3b8358213638ae33b790fa9e1a', 'anchors': ['abort;', 'abort;']}, {'name': 'OnFirstUIAfter', 'decompiled_sha256': 'ebced4d79be773235497a83510511edb2c6d45085952314e0afe88a95c1fe3e2', 'actions_sha256': '0519feea1eac40a80f0c9ecd1076d29e40311aad060557a1f2e970fc84537c2c', 'anchors': ['return;']}, {'name': 'OnMaintUIAfter', 'decompiled_sha256': '6172c03d1c9659dbe35aba7a69a688e23bce3a4c427874446949e25643385695', 'actions_sha256': '106263557dd26b455197ab15e2278a5af52da5255fcbcd7e0e0182998cee9c96', 'anchors': ['return;']}, {'name': 'OnUpdateUIAfter', 'decompiled_sha256': '40f8e92453fa253edff26cc90e593fcf796e0e6c66f1e544e4f0aba62149a848', 'actions_sha256': '4237bf2d992e6ac19e329443e81229ef64755a0433d25a44e99a113052f6a92f', 'anchors': ['return;']}, {'name': 'OnMoving', 'decompiled_sha256': '06d2793d6c8f08f9e75692536c5bf0c3b837fa4649399c4a11775083adab0767', 'actions_sha256': '78971881de23db25ce4482c04aa3802ccd2456c934cc2f15f9304f0254aee5e2', 'anchors': ['return;']}, {'name': 'OnMoved', 'decompiled_sha256': '92e3f7178167ccef9becd52618cfbf6eea3952c765abe144b286b0c89ea57a70', 'actions_sha256': '4f105984ed5d426ac679046c8cbfb953dafb1404446f384bc93986cf71936e9b', 'anchors': ['LclVarStr3 = GblVarStr3 ^ "bin\\\\GTSPlusArbitration.exe";']}, {'name': 'OnEnd', 'decompiled_sha256': 'b009d06e17e4c751bfdfb9cc07479ad1071c5382ef8b6e63ddbac39dc87eab3a', 'actions_sha256': '7abcc43f3430787a807c21a2fa9c9065d687d3b361d5d99889fc5c0e075626cb', 'anchors': ['return;']}, {'name': 'OnBegin', 'decompiled_sha256': '7cf40f1616c55323ddf90ec9157a486996fc738898791a0d2b9790c5276486ce', 'actions_sha256': '4650c373e33b7fd9a5edf964442685f4c8be4a0e81d85466051f02e3bc0014b4', 'anchors': ['return;']}, {'name': 'OnAbort', 'decompiled_sha256': '9de629289be929f09a10455e993c27d5f3458f083cab6074c6ea6103f168ae79', 'actions_sha256': '3de2a5df8676365b377a49af7af1d356891f8be291f96ea90de72774f6fb3683', 'anchors': ['return;']}, {'name': 'OnRebooted', 'decompiled_sha256': 'd15e9a7aa92734d79b3326daf5fffe0cc0eac643bb749784547de4a29d64ee39', 'actions_sha256': '7d4c9f709742b5c71e7c852e6cc3c70905b0c536ff4c69109a7af9ac95a76805', 'anchors': ['return;']}, {'name': 'OnCanceling', 'decompiled_sha256': '6925b24bda56d00d0c8beabeef3ba76730ad2ee268bbf78c4b559d437e88cc7d', 'actions_sha256': '350246f4ee383c738578b1edc1806cd9a711915a90014db3033f8f348221199d', 'anchors': ['abort;']}, {'name': 'OnCustomizeUninstInfo', 'decompiled_sha256': '1b0c60c93bf51290120e01b436067539d22ca20395d4856fa3d33ff46ce23a0b', 'actions_sha256': 'a36279d1cac9e668e6775191e8231f25dfa76bd44d6a0b9fa688d08f021317e0', 'anchors': ['return;']}, {'name': 'NativeUtilityReg_Installed', 'decompiled_sha256': '42feb8debc5d3f390ff660c96b4f9e93948d43136d96d1387a52222dbb3381c8', 'actions_sha256': '261b886e654f164baa96ace088a25bb38327727aea5c05ab5bf8ff2cfa8c0382', 'anchors': ['LclVarStr1 = GblVarStr3 ^ "bin" ^ "ReplaceFromLegasy.dll";', 'LclVarNum1 = Func_659("", (Func_2220() ^ "RegAsm.exe") + " " + LclVarStr1 + " /codebase", 1);']}, {'name': 'NativeUtilityReg_UnInstalling', 'decompiled_sha256': 'c4db633dc3a61d850f4c9e9089400ca2a6674b89dfbdc0690c3b8373ab795169', 'actions_sha256': 'e80dd9c791688769e5bf18f3eab22fc4c4c1670bd2d7f1c2b8f00f9c95366077', 'anchors': ['LclVarStr1 = GblVarStr3 ^ "bin" ^ "ReplaceFromLegasy.dll";', 'LclVarNum1 = Func_659("", (Func_2220() ^ "RegAsm.exe") + " " + LclVarStr1 + " /u", 1);']}, {'name': 'GTSPlus_CA_Installed', 'decompiled_sha256': 'ac4c5d24e59bc82f09169a7479284d46a2529b4af088dd535c477281d4846e75', 'actions_sha256': 'c97753709afe87b3b46761cb9b14334513af20645254273b7898eb8d6f703ae8', 'anchors': ['if (0 > Func_594(Func_2229() ^ "cmd.exe", " /C certutil -addstore \\"Root\\" " + "\\"" + LclVarStr2 + "\\"", Func_2229(), 6, -1, 1)) then']}, {'name': 'GTSPlus_Installed', 'decompiled_sha256': '095f4f0fe39aff1595dbbcefd06148ac467df0be83941070b2af60b5e1cf5a4a', 'actions_sha256': 'f0c4116ad19b143238242cc4c2838d07ad8981031f906d15d52f2cc5c5d61359', 'anchors': ['return;']}, {'name': 'GTSPlusCP_Installed', 'decompiled_sha256': '83dae961fa0c987b4ecc28fc152cf26e6826516c9e1f99f11e8220e19ab716fa', 'actions_sha256': '134d74fe287a63e9847243125a03eba6a1e72f372cf0503a5abb7768282e25d7', 'anchors': ['return;']}, {'name': 'GTSPlusCP_ChinaSP_Installed', 'decompiled_sha256': '2b64ad5dcdb579e1ac7d433417a2fb6117509392273a048676c8459566d9183e', 'actions_sha256': 'ce92a50f20170133cd7d514bc813b27452a5bcd96d7fdef667832b950d5a0f9c', 'anchors': ['return;']}, {'name': 'DS4_Installed', 'decompiled_sha256': '38e391b060f090818149c83a1fa7440a258b8e9b775580db195b382c29c0311d', 'actions_sha256': '2e00b642ee8cf2681a5c2aedff0d5249f34a8749459b18da1bae78febe726d92', 'anchors': ['return;']}, {'name': 'DS4CP_Installed', 'decompiled_sha256': '73b4052d19906d456be7657f480eb3e5cf7f2b7c39fd38334ce21cbdbc93ee3e', 'actions_sha256': '32e761736c10ffbabc28dff921b1911ca46fb1da2dea44d1acbbc7b351679385', 'anchors': ['return;']}, {'name': 'GTSPlus_CA_UnInstalling', 'decompiled_sha256': '4b708a3c2eda830132d434c8f9c6d15d3984a090216a1282f19d014b2d6deff2', 'actions_sha256': '9a6fed19d4c40634175a85db28545abfcb3ed1f2214849e0c855d064c183ca7e', 'anchors': ['if (0 > Func_594(Func_2229() ^ "cmd.exe", " /C certutil -delstore \\"Root\\" " + "\\"" + "GTS+ Root CA" + "\\"", Func_2229(), 6, -1, 1)) then']}, {'name': 'Verifying_Certificate', 'decompiled_sha256': '2f9e62bdae5b4931f94c6b69c5fbfa2a6e99c8952652ab3c00bd4a9bf5fb20f7', 'actions_sha256': 'ec9ad3f8bd897524fa8a1a2ea0ef8d4a51cf60ef78ef86a5e5d43f1ce045ecd3', 'anchors': ['LclVarStr3 = Func_2231() ^ "VerifyTest2.exe";', 'LclVarNum1 = Func_672(GblVarStr1, LclVarStr1, LclVarStr2 + "*.dll", LclVarNum2, 32768);', 'if (GblVarObj15.nLaunchResult == 0) then', 'Func_1216(-65533, "Signature Check Error", "(%d)\\nFollwing file has an invalid signature or no signature.\\n\\n%s", GblVarObj15.nLaunchResult, LclVarStr4);', 'abort;', 'LclVarNum1 = Func_672(GblVarStr1, LclVarStr1, LclVarStr2 + "*.exe", LclVarNum3, 32768);', 'if (GblVarObj15.nLaunchResult == 0) then', 'Func_1216(-65533, "Signature Check Error", "(%d)\\nFollwing file has an invalid signature or no signature.\\n\\n%s", GblVarObj15.nLaunchResult, LclVarStr4);']}, {'name': 'Func_1903', 'decompiled_sha256': '9cc55e1f559f6afc01be5b9e7e97bcda9b2fd374d96a6d839ed9400e9ddd208b', 'actions_sha256': '46542a7878bc3326af277c433fd48e465d22230fd097faa9eec7454bf9831cca', 'anchors': ['return ISRT.AddIcon(GblVarNum0, LclVarStr7, LclVarStr2, LclVarStr3, LclVarStr4, LclVarStr5, LclVarNum1, LclVarStr6, LclVarNum2);']}, {'name': 'Func_2225', 'decompiled_sha256': '3ae25504d05f0afca8426a3ffc5220ff67d699346f71901a37494735a1411f31', 'actions_sha256': '9a222dc70465c2d9011e860dd3b6e27242aa6530b38d431dc72966795ac8aff1', 'anchors': ['return LclVarStr1;']}], 'embedded_runtime_packages': [], 'cabinet_file_count': 1229, 'finding': 'Creates Arbitration startup shortcut on first install; feature hooks verify GTSPlus/GTSPlusCP/DS4/DS4CP/native-registration groups. NativeUtilityReg runs RegAsm ReplaceFromLegasy.dll /codebase and /u. CA hook runs certutil addstore Root ca.crt, removal deletes GTS+ Root CA; command failures ignored by empty branches.'}, {'installer': 'Setup_TSEConverter.exe', 'sha256': '42a5d36e1b3c5c0c337f4595ff03a2efeacca648a5c495a7a7c26db96bbfb593', 'record_count': 16, 'inx_sha256': 'c6328d9a7a8284726cf8f11dc555058c357611c31aa32dbdd5b0a250a51c6871', 'inx_size': 240909, 'inx_offset': 6243279, 'parent_installer': None, 'functions': [{'name': 'OnFirstUIBefore', 'decompiled_sha256': 'ac1ec5b56d768376bb7cc1db3e1bdc1f77e19ac20047ae6618c6a681f96c4c47', 'actions_sha256': 'b69c4c2cdb9e4966c21c76e3fb1f4080b201da8b6286834261cd69d77f5e6633', 'anchors': ['abort;']}, {'name': 'OnMaintUIBefore', 'decompiled_sha256': '748b268d81f37e4736eaf5c6552c7501ada6581d1b12cb9fa83a6ba10bed5637', 'actions_sha256': '09cc7ac74b716c6c003da11ec795a4984e27c73e7b5f25d6769f807afaa7d207', 'anchors': ['abort;', 'abort;']}, {'name': 'OnFirstUIAfter', 'decompiled_sha256': '4ed629198193b080ea779d3146b334b0a7ce0f6d0df2ef0532dbd52866d5b30d', 'actions_sha256': 'b4c1f7ac1e162575b12db266af1a9b5ea2fd90e65d931ddf26126f11d9d63413', 'anchors': ['return;']}, {'name': 'OnMaintUIAfter', 'decompiled_sha256': '82a5dd326104fecfa0b04399d6595d5ecabe08f5e2780d659149193f69f6ed4b', 'actions_sha256': '1809222da9829c2a3681e30d594aba5e7037183548ac1907ce46e6a5dc50094c', 'anchors': ['return;']}, {'name': 'OnUpdateUIAfter', 'decompiled_sha256': '130d5d1cb43bfc951a3bcb049638cd09217bbc5f4878c4289f28f066cd5e3674', 'actions_sha256': '38477a23317d9ec988027493fbeb86141fb7aada88c469fdf5454f1cde72a356', 'anchors': ['return;']}, {'name': 'OnMoving', 'decompiled_sha256': '06d2793d6c8f08f9e75692536c5bf0c3b837fa4649399c4a11775083adab0767', 'actions_sha256': '04faa12a66fb93fa23adc1c8bcc8a82283141f0652a242f9c8f0f56ac309cce5', 'anchors': ['return;']}, {'name': 'OnMoved', 'decompiled_sha256': '1bccd8efdbe480e57944b634c14ebd15a2f1e46dd875d8f73d5a71142450e626', 'actions_sha256': 'c44887a168ec138bd0b212c00f5b8c8d125edb08be49a79c8fca55abc4b345ba', 'anchors': ['return;']}, {'name': 'OnEnd', 'decompiled_sha256': '22fc5b07a54dbdbf41ba6522e362b23a635982bf754f335e5d5183370d1f6257', 'actions_sha256': '39cf673a78c95a8fe04ed6800fdba6a52095e0ca2f1d5b3e7956c3227ed290fa', 'anchors': ['LclVarStr14 = "GTS+ TSEConverter.txt";']}, {'name': 'OnBegin', 'decompiled_sha256': '7cf40f1616c55323ddf90ec9157a486996fc738898791a0d2b9790c5276486ce', 'actions_sha256': '48907091dd799364d0aa7cbc2da59e0f6c8de1af275ee70c405a273613e27455', 'anchors': ['return;']}, {'name': 'OnAbort', 'decompiled_sha256': '9de629289be929f09a10455e993c27d5f3458f083cab6074c6ea6103f168ae79', 'actions_sha256': 'cac62a97d1592785390e0ac5df414bee588f7ddda97e63a460eab075dc81c45c', 'anchors': ['return;']}, {'name': 'OnRebooted', 'decompiled_sha256': 'd15e9a7aa92734d79b3326daf5fffe0cc0eac643bb749784547de4a29d64ee39', 'actions_sha256': 'e65a9ab58e33debb26f039a661a811393bfad5901d06bc22ca0d1e6fbb8d0582', 'anchors': ['return;']}, {'name': 'OnCanceling', 'decompiled_sha256': '87158ba2edbeb9254596760abd8a9ab2963da693ba727bfa29e7111aa1857dc5', 'actions_sha256': 'd57f0b99162d7640bc7e1fdcb6dc3b586e32ef7ad15aad28adfa9f1418b7cf35', 'anchors': ['abort;']}, {'name': 'OnCustomizeUninstInfo', 'decompiled_sha256': '6756c550987fe90ea2acdd175aed9aee83099437a3247b440e275b9d720902bb', 'actions_sha256': '04a3b7c046b485db819ca4fb2d38caf721589bca051c417d5910eff886976dc1', 'anchors': ['return;']}, {'name': 'GTSPlusTSEConverter_Installed', 'decompiled_sha256': '32f639a61a2bcfdeb48e671d832220c7bd6206fceb163574861ea85661bb9c15', 'actions_sha256': '4954cb623c9106125f2c621f07dd88aa8d0988ad381eb09eafdc49713eb64065', 'anchors': ['LclVarStr1 = Func_2198() ^ "VerifyTest2.exe";', 'LclVarNum1 = Func_656(GblVarStr1, LclVarStr4, LclVarStr5 + "*.dll", LclVarNum2, 32768);', 'if (GblVarObj15.nLaunchResult == 0) then', 'Func_1198(-65533, "Signature Check Error", "(%d)\\nFollwing file has an invalid signature or no signature.\\n\\n%s", GblVarObj15.nLaunchResult, LclVarStr2);', 'abort;', 'LclVarNum1 = Func_656(GblVarStr1, LclVarStr4, LclVarStr5 + "*.exe", LclVarNum3, 32768);', 'if (GblVarObj15.nLaunchResult == 0) then', 'Func_1198(-65533, "Signature Check Error", "(%d)\\nFollwing file has an invalid signature or no signature.\\n\\n%s", GblVarObj15.nLaunchResult, LclVarStr2);']}], 'embedded_runtime_packages': [], 'cabinet_file_count': 42, 'finding': 'Feature hook verifies GTSPlusTSEConverter DLL/exe sets; completion writes GTS+ TSEConverter.txt.'}, {'installer': 'CUWLauncher_Setup.exe', 'sha256': 'ecb6155d3a23c81bc3e92dd4e8a0d2545830802bec15b5f9ad46c0078a00779d', 'record_count': 11, 'inx_sha256': '074410abfae18b5ee4897f79f769792b25cb36cb79ebfefe38f1d92f51c3e406', 'inx_size': 230824, 'inx_offset': 4069616, 'parent_installer': 'CUWPlusPF.exe', 'functions': [{'name': 'OnFirstUIBefore', 'decompiled_sha256': '56ae6b1e152e65330453fb122422e061ff755d9b906d0817baa929b34f735d02', 'actions_sha256': '63f13a9fb2879ddf394eabfb272e59837ab005a515f467198105ec4c427734f9', 'anchors': ['abort;']}, {'name': 'OnMaintUIBefore', 'decompiled_sha256': 'a1dd859aebaf07be992b905b2f42ead7e8e02677aeeacba614f48725a9cd0580', 'actions_sha256': 'ceaa3d46d990f4829b6a3e7c896baf6a84a8dceb461e098a0ee29fca47cab3ed', 'anchors': ['abort;', 'abort;']}, {'name': 'OnFirstUIAfter', 'decompiled_sha256': 'af1d51014fad351a3282a0eba4e86db639008f28ced6424fb98b5e307f4d9555', 'actions_sha256': '7e845c79a834aef85fcc5d6115686106d244d91a23947d8409e2bc6d9b115548', 'anchors': ['return;']}, {'name': 'OnMaintUIAfter', 'decompiled_sha256': '1f72f82a80df5f807e499389c8871d91a9d2e13caf451b52c99066d78d6e4301', 'actions_sha256': 'f008f8f4f370d86231bb84bc7af88b7d6a69353c52ee58178f6ba1a96bfec7ef', 'anchors': ['return;']}, {'name': 'OnUpdateUIAfter', 'decompiled_sha256': 'ded7289637df25bbfbee60d58af8a445cb4b68cbe6c9a7d3fe47497ed6a34fd6', 'actions_sha256': '84a22f16cab5e98f07eff023818db2f74b6d42747684d57961ff2abd987b9c6e', 'anchors': ['return;']}, {'name': 'OnMoving', 'decompiled_sha256': '06d2793d6c8f08f9e75692536c5bf0c3b837fa4649399c4a11775083adab0767', 'actions_sha256': '901f7e924a1e2b951fe3b3c122492b6fdc5271433c1791eb9503173f48c14e89', 'anchors': ['return;']}, {'name': 'OnMoved', 'decompiled_sha256': '1bccd8efdbe480e57944b634c14ebd15a2f1e46dd875d8f73d5a71142450e626', 'actions_sha256': '0a4714ed5b294399e3acb61ad144424f71ab1e878da609ed1bcc7ace60e3a848', 'anchors': ['return;']}, {'name': 'OnEnd', 'decompiled_sha256': '22246d374a4c00a12a7d94e130e81f052ddfb444657377cbbdb75908b23825c1', 'actions_sha256': '4e90aeb879a201e416141abcc98e74f751870d7c8c316f322df9fd04743a9608', 'anchors': ['return;']}, {'name': 'OnBegin', 'decompiled_sha256': '4d80f308bf11ec4df3b079f6ffee236e30cd712c53e33eec702772bcd707de0c', 'actions_sha256': 'f5971177495f474be918b7c3329997a40934e8eda46b481775942004e046ee7c', 'anchors': ['abort;']}, {'name': 'OnAbort', 'decompiled_sha256': '9de629289be929f09a10455e993c27d5f3458f083cab6074c6ea6103f168ae79', 'actions_sha256': 'c5337e043da9f754eeeebe24f97dd05c1a6f360191758688e03b21637b98687c', 'anchors': ['return;']}, {'name': 'OnRebooted', 'decompiled_sha256': 'd15e9a7aa92734d79b3326daf5fffe0cc0eac643bb749784547de4a29d64ee39', 'actions_sha256': '610cdd98748874e08e2956782e6ee267d5b350ceb126e79504a7d68b3336b261', 'anchors': ['return;']}, {'name': 'OnCanceling', 'decompiled_sha256': '005698051df136e20befdb0b41a81f9430776cdc24db742581aa5e92af150880', 'actions_sha256': '4833aeb3356ffa7c27f672b57ee4876e1cd9219c4f6a6604bd9b8036b3959d57', 'anchors': ['abort;']}, {'name': 'OnCustomizeUninstInfo', 'decompiled_sha256': 'ab2e047b0f51c787b43986cd6903937a18b609db895bfe4a2bc4bd94ad419f49', 'actions_sha256': '5054ded46b1f4162881725fac8af0942c14cee95ef5d7c60fb070cf3e43617b9', 'anchors': ['return;']}, {'name': 'CUWLauncher_UnInstalled', 'decompiled_sha256': 'c22d1b037053afb17bb0e8262c4cbd7070407e7b1f9b143bbcbb8e3ffe076280', 'actions_sha256': '398abc82a7366c86fbdf0a0119c54bab25232f5958518add5edc2d79304a9ff2', 'anchors': ['Func_1583(".cuw");', 'Func_1583(".cuwc");', 'Func_1583(".cuwd");']}, {'name': 'CUWLauncher_Installed', 'decompiled_sha256': 'cae79d67007525069cdc38c3b0d111ceacefcffaef5da4328bcc17fa53f8adf4', 'actions_sha256': 'ee6ccf84114c1a8182b7b227acd5c39dd7b0b851dc637733239228a53b3e02d8', 'anchors': ['Func_1583(".cuw");', 'Func_1583(".cuwc");', 'Func_1583(".cuwd");', 'LclVarStr1 = "\\"" + GblVarStr3 + "\\\\CUWLauncher.exe\\" \\"%1\\"";', 'Func_1585(".cuw\\\\shell\\\\open\\\\command", "", 1, LclVarStr1, -1);', 'Func_1585(".cuwc\\\\shell\\\\open\\\\command", "", 1, LclVarStr1, -1);', 'Func_1585(".cuwd\\\\shell\\\\open\\\\command", "", 1, LclVarStr1, -1);', 'LclVarStr1 = "\\"" + GblVarStr3 + "\\\\CUWLauncher.exe\\",";']}, {'name': 'Func_1583', 'decompiled_sha256': 'f350768da3907c6a2e107adf509f1db921c7c304a98037aaf1a8cb3baf3fd2ad', 'actions_sha256': 'ceccc32ff92b7d72804d190cb8e53eb866d9ba2158c38f7cd07a92337de3d8d2', 'anchors': ['return ISRT._RegDeleteKey(GblVarNum0, GblVarNum8, LclVarStr1);']}, {'name': 'Func_1585', 'decompiled_sha256': '82ac17d30b306e1ea2e57d22904bcb3cbb38b369588a0d7bfcac579dfaf2d292', 'actions_sha256': '8aa9c045a02dbf6cb0e8fcf0979961d3a7723f999e3bc1960ce1cc6a65d97bae', 'anchors': ['return Func_1711(GblVarNum8, LclVarStr1, LclVarStr2, LclVarNum1, LclVarStr3, LclVarNum2);']}], 'embedded_runtime_packages': [], 'cabinet_file_count': 21, 'finding': 'Nested CUW installer owns shell associations: clears old .cuw/.cuwc/.scuw/.cuwd/.usbrepro keys, installs quoted CUWLauncher.exe "%1" open commands/default icons; uninstall removes extensions. OnAbort/OnRebooted empty.'}]
CERT_METHODS = [{'key': 'cert.Program.Main', 'source': 'cert', 'type': 'ConsoleApp1.Program', 'method': 'Main', 'pin': {'rva': 8816, 'body_size': 44, 'body_sha256': '20b88eb37da0003712e41af311e7ccaa1597f0cc3a4cfdca2ec98e5ba3b548d4'}, 'needles': ['ldlen', 'brfalse.s', 'installCerts', 'Equals', 'Start'], 'finding': 'First argument installCerts selects install mode; absent/different argument selects root-policy mode; Start owns behavior.'}, {'key': 'cert.Program.Start', 'source': 'cert', 'type': 'ConsoleApp1.Program', 'method': 'Start', 'pin': {'rva': 8948, 'body_size': 73, 'body_sha256': '8a14326978eb4e5c705074f1559df97c0ffe6dfcf579d1a5787368308cd23459'}, 'needles': ['GetInstallPathOfFirefox', 'brfalse.s', 'policies.json', 'AddCertificationPolicies', 'CopyCerts2AppData'], 'finding': 'If Firefox found, edits distribution/policies.json: install mode adds certificate filenames; other mode enables enterprise roots. Only install copies cert files to user profiles. No call to InstallCerts2OS here.'}, {'key': 'cert.Program.CopyCerts2AppData', 'source': 'cert', 'type': 'ConsoleApp1.Program', 'method': 'CopyCerts2AppData', 'pin': {'rva': 9080, 'body_size': 151, 'body_sha256': '2653587975ed15197a562c71444b6d3d47ecc1da8114534ac7b7c1a02cf0d20f'}, 'needles': ['GetUserNameListFromComputer', 'Directory::Exists', 'copyCertFiles', 'Default'], 'finding': 'Enumerates local user profile paths with full-name then name fallback and always Default profile; copies public CA certificates to Mozilla certificate directory.'}, {'key': 'cert.Program.copyCertFiles', 'source': 'cert', 'type': 'ConsoleApp1.Program', 'method': 'copyCertFiles', 'pin': {'rva': 9584, 'body_size': 91, 'body_sha256': '33e8e2bf39a24a912658be0e0ba5a1cf9d040d438962c273e928071e57e3bdb4'}, 'needles': ['CreateDirectory', 'rca.crt', 'ica.crt', 'ldc.i4.1', 'File::Copy'], 'finding': 'Creates destination directory and overwrites rca.crt/ica.crt.'}, {'key': 'cert.PolicyEditer.AddCertificationPolicies', 'source': 'cert', 'type': 'ConsoleApp1.PolicyEditer', 'method': 'AddCertificationPolicies', 'pin': {'rva': 8272, 'body_size': 192, 'body_sha256': '42aa77d178a3e8690428ebcfdd93acf8e664f1385c9a06b7d7923e6a50d3f7b1'}, 'needles': ['ReadJson', 'ContainsKey', 'brtrue.s', 'ImportRoots', 'ImportCerts', 'WriteJson', 'Console::WriteLine'], 'finding': 'Creates missing policies/Certificates JSON objects; conditionally imports roots/cert filenames; writes policy. Exceptions are caught, printed, and returned.'}, {'key': 'cert.PolicyEditer.ImportRoots', 'source': 'cert', 'type': 'ConsoleApp1.PolicyEditer', 'method': 'ImportRoots', 'pin': {'rva': 8464, 'body_size': 19, 'body_sha256': '5eeb823a55bbe4f20be6d11ee31911ee8e9b56f5f2d2c3e7f7bbc73bedd19a94'}, 'needles': ['ImportEnterpriseRoots', 'ldc.i4.1', 'set_Item'], 'finding': 'Sets ImportEnterpriseRoots=true.'}, {'key': 'cert.PolicyEditer.ImportCerts', 'source': 'cert', 'type': 'ConsoleApp1.PolicyEditer', 'method': 'ImportCerts', 'pin': {'rva': 8484, 'body_size': 184, 'body_sha256': 'fe38b86dfb5c3dcab99fa24b5499e093ff71c47ea84b016831d792ebb4ab18c1'}, 'needles': ['Install', 'rca.crt', 'ica.crt', 'brfalse.s', 'JArray::Add'], 'finding': 'Creates/reuses Install array and adds rca.crt/ica.crt only when absent.'}, {'key': 'cert.PolicyEditer.ReadJson', 'source': 'cert', 'type': 'ConsoleApp1.PolicyEditer', 'method': 'ReadJson', 'pin': {'rva': 8668, 'body_size': 112, 'body_sha256': '615b9baa31b5394a7dad87c5dd885209466012d584773c505bc19e54b824fed0'}, 'needles': ['JObject::.ctor', 'File::Exists', 'brfalse.s', 'get_EndOfStream', 'ReadFrom'], 'finding': 'Missing or empty policy begins as empty JObject; existing nonempty document parsed.'}, {'key': 'cert.PolicyEditer.WriteJson', 'source': 'cert', 'type': 'ConsoleApp1.PolicyEditer', 'method': 'WriteJson', 'pin': {'rva': 8780, 'body_size': 26, 'body_sha256': 'd925e76d17d1cf6132be42462721b3dbcc6b9b7d37bb8e0c0d4dcbb66d825882'}, 'needles': ['GetDirectoryName', 'CreateDirectory', 'WriteAllText'], 'finding': 'Creates policy parent directory and writes serialized policy JSON.'}, {'key': 'cert.Program.InstallCerts2OS', 'source': 'cert', 'type': 'ConsoleApp1.Program', 'method': 'InstallCerts2OS', 'pin': {'rva': 9021, 'body_size': 56, 'body_sha256': '37ec71a884a8f2a80bced660976ca6cb211f6edb68ef4da138c1bb293abbe7ca'}, 'needles': ['ProcessStartInfo::.ctor', 'set_FileName', 'set_UseShellExecute', 'Process::Start'], 'finding': 'Defined shell-launch helper has no call from Main/Start; cannot substitute its mere presence for OS certificate import execution.'}]
DEFAULT_DECODER_SOURCE = REPO_ROOT / "REFERENCE/installscript-decompiler"
DECODER_REPOSITORY = "https://github.com/jte/installscript-decompiler.git"
DECODER_REVISION = "1d5edb7b022cc1573a1f3971382391b9c5457cc9"
DECODER_SOURCE_PINS = {
    "Cargo.lock": "848f3de5b26e30c8ef7bb239b8fafebe9f2dffc071cb98ba0e9f861039a1e6d6",
    "Cargo.toml": "b4fcf90c9193887c2d04844ee1c1404a94f8e303710083f302d12107842be05f",
}
LAUNCHER_GATE_FUNCTIONS = [{'name': 'Func_2116',
  'decompiled_sha256': 'bb33c5cf6a74c678e55d5ea3347309bd3742e5f96a7c0b68e4008754e6ce70da',
  'actions_sha256': '1636ab330c9f8542dee954ecfa82fc6bc826170d3f95177ae926fa1b592b0b34',
  'anchors': ['return GblVarNum63;']},
 {'name': 'Func_2284',
  'decompiled_sha256': '53eb750fc217e2df27663ecc07d9cd6fd97ba943e23db16436b5ad6806cc471e',
  'actions_sha256': 'ecae2028fe13a4be2e5ee632d5de9c4d376d5fb3a99c5527702aead937b46e64',
  'anchors': ['if (GblVarObj3(38)) then', 'GblVarNum63 = 1;']},
 {'name': 'Func_2134',
  'decompiled_sha256': '01dd8916312521abc34342843a0be61dee65f5864f3abe9a7fb03cf282ae1b3d',
  'actions_sha256': 'bef3f5479a8c46fce827b8af142e10974378df2ef42d80159d5d3e1ae37ece4a',
  'anchors': ['GblVarNum85 = LclVarNum1;']},
 {'name': 'Func_2283',
  'decompiled_sha256': 'c66c8a57dae5ec1eaa40d569ef64129f4df745bc9fc4a132268674695e4e480e',
  'actions_sha256': 'd36f4a83395492ac17cce6f5da8aba5b9e5c4b65c54821214b81e9bb67faa66a',
  'anchors': ['GblVarNum110 = BindVariable(GblVarNum8, Func_2191);']},
 {'name': 'Func_2191',
  'decompiled_sha256': 'f62b4fc7fdc192e61f5f224333ca2b751658ee7e754e4577bb47f3634f223345',
  'actions_sha256': '16f33935e77765786cdc9b2bd9bf1cefb9e1121dbeb7cd2c427561bad08f588f',
  'anchors': ['elseif (LclVarNum1 == GblVarNum110) then', 'return GblVarNum85;']},
 {'name': 'Func_1581',
  'decompiled_sha256': '93bd6eaaac7e989fe870c18ed5b09288b19cbd09d7c417fe836d58207b6f2c57',
  'actions_sha256': '8b0e5e6f6f7a0f8ca3ca8e89b825eb5d57ac184a23037a9e9ed050521eadb9ea',
  'anchors': ['ISRT._RegExistsKey(GblVarNum0, GblVarNum8, LclVarStr1) == 1', 'return -1;']},
 {'name': 'IfxOnInitInstall',
  'decompiled_sha256': 'b9474483d51004ee6d9fcb414c0c900a34e053c70e1eb59576c1298988dbb98b',
  'actions_sha256': 'b65473e6a46b693515e0f125f60dd6ebe6ee7dfa4c45dd6b24444492045b43a3',
  'anchors': ['OnBegin();']},
 {'name': 'OnSuiteMaintBefore',
  'decompiled_sha256': '45547374480e33b72147b8f18ff2dec2b8f59ae818ccef30c8198ce6fc228673',
  'actions_sha256': '00758d46edc44fba7d8a73dc1a8f8408b8d4deef8b00d7d261c75f765f13f045',
  'anchors': ['elseif (Func_2116()) then', 'LclVarNum1 = 303;', 'Func_594();']}]
LAUNCHER_ONBEGIN_ANCHORS = ['if (Func_2116()) then',
 'Func_2134(-2147483646);',
 'LclVarNum2 = 0;',
 'if (Func_1581(LclVarStr1 + LclVarObj1(LclVarNum1)) == 1) then',
 'LclVarNum2 = LclVarNum2 + 1;',
 'if (LclVarNum2 > 1) then',
 'abort;']
LAUNCHER_CLIENT_KEYS = ['{5A03CEC0-8805-11D4-ADFB-00000EFB3A77}',
 '{96975DDD-D293-4BD3-83A9-6E0ECE092AD5}',
 '{EBB9FC33-DA35-404B-B38E-380FFD16CEE2}',
 '{896CAAA3-6AB7-4DE9-87C0-67161C9736DC}',
 '{D00C3401-0B5B-4ECB-9915-85D22131B9D2}',
 '{881DDF74-98AA-4162-8249-2015F69477CA}',
 '{6B06914F-57E9-4B79-8E3D-839174F97C1E}',
 '{C407DDDF-2576-49D4-BBAF-7DB9CBFAEC6A}',
 '{2943BC0E-B911-4C17-8AA6-F803E8F1CEF8}',
 '{859A35D9-D1DB-48D8-9806-22BA4C5ABBEF}',
 '{5630FDEF-3804-410B-AC11-FC9EBEC698C5}',
 '{980B1A1F-AF81-49C2-A247-10A4CA9B678B}']

CERT_METHODS.extend([{'finding': 'Probe HKLM Registry64 first; only null result falls back to Registry32. Empty string '
             'suppresses fallback.',
  'index': 0,
  'key': 'cert.Program.GetFirefoxPreferred',
  'method': 'GetInstallPathOfFirefox',
  'needles': ['ldc.i4.1', 'brtrue.s', 'ldc.i4.0'],
  'pin': {'body_sha256': '4988ee19d2636bc6f5d199bb64e8b39266837dc227bbe52fc355cf1bbf5b25f1',
          'body_size': 20,
          'rva': 9675},
  'source': 'cert',
  'type': 'ConsoleApp1.Program'},
 {'finding': 'HKLM SOFTWARE\\Mozilla\\Mozilla Firefox: selects greatest version subkey by String.Compare, '
             'not semantic version; reads <version>\\Main Install Directory. Missing key/Main returns null; '
             'registry exceptions escape.',
  'index': 1,
  'key': 'cert.Program.GetFirefoxView',
  'method': 'GetInstallPathOfFirefox',
  'needles': ['0x100', '0x200', 'GetSubKeyNames', 'Compare', '\\\\Main', 'GetValue'],
  'pin': {'body_sha256': 'b6e880569c83f2646c73cb40de5d4e7263bb57b8894c9d48a569e14edbb9dd5b',
          'body_size': 170,
          'rva': 9696},
  'source': 'cert',
  'type': 'ConsoleApp1.Program'},
 {'finding': 'Enabled local WMI accounts union domain-SID user profiles through HashSet<NTAccount>; '
             'translated names, not Win32_UserProfile.LocalPath, construct c:\\Users candidates. '
             'WMI/SID/translation failures escape; finally disposes enumerators.',
  'index': 0,
  'key': 'cert.Program.GetUserNameListFromComputer',
  'method': 'GetUserNameListFromComputer',
  'needles': ['Win32_UserAccount', 'disabled', 'Win32_UserProfile', 'Translate'],
  'pin': {'body_sha256': '0c779e25ca6abea2b5e5b9bb25bd0a46dfaf95111eee670cf72b93b26a69e367',
          'body_size': 352,
          'rva': 9232},
  'source': 'cert',
  'type': 'ConsoleApp1.Program'},
 {'finding': 'Source certificate directory is executable directory (baseDir), not baseDir\\certs. '
             'installCerts mode may fail copying because shipped public certificates are nested under certs; '
             'ordinary installer invokes no installCerts argument.',
  'index': 0,
  'key': 'cert.Program.ctor',
  'method': '.ctor',
  'needles': ['get_Location', 'Split', 'Join', 'baseDir'],
  'pin': {'body_sha256': '1a4a5f3ee77c0361a34ffba51d51f08cd17ab8925e04fb4057c93f9969aa34fd',
          'body_size': 88,
          'rva': 8860},
  'source': 'cert',
  'type': 'ConsoleApp1.Program'},
 {'finding': 'Install-array duplicate predicate is case-sensitive String.Equals negated; differently cased '
             'names remain and exact rca.crt/ica.crt are appended.',
  'key': 'cert.PolicyEditer.CertificateNamePredicate',
  'method': '<ImportCerts>b__0',
  'needles': ['Equals', 'ceq'],
  'pin': {'body_sha256': 'd634124f88cbaa0b1b01ad5238b84e255183b5f3a7766693df6cf4f0598a75f4',
          'body_size': 17,
          'rva': 9866},
  'source': 'cert',
  'type': 'ConsoleApp1.PolicyEditer+<>c__DisplayClass2_0'}])

CERTIFICATE_SCRIPT_PINS = {'Setup_GuiServer.exe': {'OnFirstUIAfter': ['1493d45cbcddc320ee2a8b7b6602a3c5de875d712d3bcd65b58e281e4b323384',
                                            'd0fa3df230940c9793cb9e67faac8941c697606b7de06115219af0d7971bb59b'],
                         'OnMaintUIAfter': ['55055411088ee72ef1dacedd5d3c7c90ce0ce4646277e50377e0bf7b87e7ffc8',
                                            'fb406148ef68ffae3f5318a2160f1998b82baa2faec5c41495ee1eda21b674fc'],
                         'OnUpdateUIAfter': ['0a2824cbd4f06e23419049fddd032f56a995e382745e95010aacc7ec2e30848b',
                                             '800e12dd19dc21e65ca53493a502772e8d565dc22bb1101bb35c45185f2f34f2'],
                         'GTSPlusGUIServer_UnInstalling': ['169d19ed2c0fac6a5ce25823e65c765ad98ed94e82be8d251a9fb70e09948726',
                                                           '812d9b202da062e80287a85a62dacba395f01357c4ed847214a416bdded00066'],
                         'OnMoving': ['4c04581e13e2cb65f92242822522a72a028e674257dee17f427419790912fd7d',
                                      'c13d91787e3449e768fba9f11afbca612f3fd230f097f29d0d2b2e67f8c80da1'],
                         'OnAbort': ['9de629289be929f09a10455e993c27d5f3458f083cab6074c6ea6103f168ae79',
                                     'a13b5b8af8e7c635f2f2b84450c1d8c296c2c2e061f19ee728ff7aa088b72513'],
                         'OnRebooted': ['d15e9a7aa92734d79b3326daf5fffe0cc0eac643bb749784547de4a29d64ee39',
                                        '5073945dace9fe1d8e32a3685d490fb73cfd1663e5c59971f73bc964f8e963bf'],
                         'Func_585': ['14ad92866cfcb79afd6ef548169c42d5b56845c6f19a5de70f38d209608bc204',
                                      '77efcd5e404b1b1f8c596b36c97a45c3f56692f801ea82bac0518146684d300c'],
                         'Func_586': ['2b775982a2e4dbe2c77ef368b5b74dc64955f2438f529ee8a4d617193fbf2da2',
                                      'a210349812366a7509e8ae3883e2e0e6381e5f105fe5d608ef7c01a61c97ae31'],
                         'Func_609': ['1cedb089ae104a6815600bef72585779556991331587691136dcc8c1289a27a5',
                                      '9ebd300360012824361f776cff2cc5bbd1467bf6c2afa3df12f739a9debe341e'],
                         'Func_624': ['2d1a4ed50c846caea7555aaa5cee06f78cb598a9a59d7f3c3f9905097d8ceb6a',
                                      'faa3a88f5ddd23f94c480982db2873ef40ea27a31829f336ff92ff85fe61350a'],
                         'Func_631': ['6cc824d7c80eac49e3fb623def000b5509b4d76b7000006df8f7415222fa51b1',
                                      '4dec764533bc52bc5d1de977de4e81d72bd6c45c43b50f777bd075b91c33a744'],
                         'Func_651': ['8f4c8be5a2591c12d4d074f64183d8c790874cc86d2091421884507d34f5b659',
                                      '8b22f874adb57d1c0d3ac7ef7bbac71846ffbc0d95976655410d03a7a5a14175'],
                         'Func_727': ['6ab24bd4b888d5563afe6deb321cafdd5c1e750c563e74d3bde91c91c0720e05',
                                      '22c18e5e321210e2a7e77b7a554eb2c0af3648f1ad2ac99c0f8aa5cea5143772'],
                         'Func_1929': ['0cb443b2c5f55f7d4a20650059fe1ce232eb5ab0addfd4308facfbc5dfc33d31',
                                       '1b8581a18dadebaf23fc6fff0f92f22bcb4e45db45b2171d425beb787114d897'],
                         'Func_1989': ['0be2f54c7a7970c42c20b41ec9bd906a6ddf596f6e07e7f4b3a3e65d8223bf83',
                                       'b9cc1b2bad23fd360c28a34d8f899232a18df713f58f22f9bed63574e70a59dd'],
                         'Func_2306': ['77242d69b6d00a7ab54659fb8584146a705bb4dcfed4863c463bc20d4594b549',
                                       '8e52312163dcfb87e5577ba3197f4ec990356fa11695e00abf5a1b1e57ec7745'],
                         'Func_2318': ['5e0112d65d32a5de51fcaaab05384735f63bb38a2e0335b7208eedba9306a670',
                                       '53df029a3be6820215a5bd117a9bafb38ec1d6879be8a71c5119680634c668ca'],
                         'Func_1928': ['9d6eac5ed13baa17df62ed85226cf48b4d83ee7166c1dd48f241cf2f46684b9b',
                                       '7b6cd8538c7459eda13ca57894706250c875ef560dbacc8d767c966a82df90ef'],
                         'Func_1980': ['c5c0246f17de40e7c4ecea697bfa953f4dc650c12ae3469bf8a3bdffc652cb96',
                                       'b59fcc908c5636afe71886159372ee89191c7f22153d84996b549643c83b0d7b'],
                         'Func_2391': ['934a9c6c389be1222b67a4283a365735a878be3dd3bdd8fb2d8e0eb27d0e5f43',
                                       'c22670b3c417435157beca579446853df198a8f5a01dda1fb2b74e54f9d73daa'],
                         'Func_2524': ['3664ffb5144eb7363091d9964ff9600a72903c29fd2029d861c230e90c570ac0',
                                       'fa9dee8801bba3255cb9b0548c2f5d9bbe27ea049e5ecbb344613ceaf56cf4ff'],
                         'OnShowUI': ['61c6109dac50a50445ca3bbaa3f0175839c490dce96a45f97665a2f57ca33439',
                                      'b8f18dea10794655914da1f624fabe844934c2a739bafbe4ba2d89e85c0102da']},
 'Setup_PF.exe': {'GTSPlus_CA_Installed': ['ac4c5d24e59bc82f09169a7479284d46a2529b4af088dd535c477281d4846e75',
                                           'c97753709afe87b3b46761cb9b14334513af20645254273b7898eb8d6f703ae8'],
                  'GTSPlus_CA_UnInstalling': ['4b708a3c2eda830132d434c8f9c6d15d3984a090216a1282f19d014b2d6deff2',
                                              '9a6fed19d4c40634175a85db28545abfcb3ed1f2214849e0c855d064c183ca7e']}}


def _id(key: str) -> str:
    return f"{DOMAIN}.{key}"


def _rel(path: Path) -> str:
    resolved = path.resolve()
    return resolved.relative_to(REPO_ROOT).as_posix() if resolved.is_relative_to(REPO_ROOT) else str(resolved)


def _hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _pin(path: Path, expected: str) -> None:
    if sha256_file(path) != expected:
        raise ValueError(f"source drift: {_rel(path)}")


def _source(key: str, path: Path, representation: str, **extra: Any) -> dict[str, Any]:
    return {"id": _id(key), "path": _rel(path), "sha256": sha256_file(path),
            "size": path.stat().st_size, "representation": representation, **extra}


def _settings(clear: bytes) -> dict[str, Any]:
    """Project selected fields from this hash-pinned, fixed YAML document."""
    text = clear.decode("utf-8-sig").replace("\r\n", "\n")
    sections = dict(re.findall(r"^  ([\w-]+):\n(.*?)(?=^  [\w-]+:|\Z)", text, re.M | re.S))
    result: dict[str, Any] = {}
    result["checkers"] = re.findall(r"^    - ([\w-]+)$", sections["checkers"], re.M)
    result["wss-ports"] = [int(v) for v in re.findall(r"^    - (\d+)$", sections["wss-ports"], re.M)]
    for key, target in (("applications", "process-name"), ("services", "service-name")):
        result[key] = [
            {"display-name": display, target: name}
            for display, name in re.findall(
                r'^    - display-name: "([^"]+)"\n      ' + target + r': "([^"]+)"$',
                sections[key], re.M,
            )
        ]
    return result


def _records(data: bytes) -> list[dict[str, Any]]:
    """InstallShield SFX [0]: count, four UTF-16Z fields and raw file bytes."""
    count = int.from_bytes(data[:4], "little")
    if count != 20:
        raise ValueError("parent SFX record count drift")
    pos = 4
    rows = []
    for _ in range(count):
        fields = []
        for _ in range(4):
            end = pos
            while end + 2 <= len(data) and data[end:end + 2] != b"\0\0":
                end += 2
            if end + 2 > len(data):
                raise ValueError("unterminated parent SFX header")
            fields.append(data[pos:end].decode("utf-16le"))
            pos = end + 2
        name, member, version, length = fields
        size = int(length)
        body = data[pos:pos + size]
        if len(body) != size or _hash(body) != RECORD_PINS.get(name):
            raise ValueError(f"parent SFX member drift: {name}")
        rows.append({"name": name, "member": member, "version": version,
                     "offset": pos, "size": size, "sha256": _hash(body), "body": body})
        pos += size
    if set(RECORD_PINS) != {r["name"] for r in rows} or any(data[pos:]):
        raise ValueError("parent SFX record boundary drift")
    return rows


def _rul_section(text: str, name: str) -> str:
    match = re.search(r"^function [^\n]+\b" + re.escape(name) + r"\([^\n]*\).*?^end;", text, re.M | re.S)
    if not match:
        raise ValueError(f"missing decoded function: {name}")
    return match.group()


def _script_evidence(inx: Path, directory: Path, decoder: Path) -> list[dict[str, Any]]:
    paths = [directory / "decoded.rul", directory / "decoded.actions"]
    for out, flag in zip(paths, ("--show-decompiled", "--show-actions")):
        subprocess.run([str(decoder), str(inx), str(out), flag], check=True, capture_output=True, text=True)
    rul, actions = [p.read_text() for p in paths]
    names = re.findall(r"^function [^\n]+\b([A-Za-z_][A-Za-z0-9_]*)\(", rul, re.M)
    sections = [s.rstrip() for s in re.split(r"(?=^(?:export )?prototype )", actions, flags=re.M) if s.strip()]
    # The entry program has an action body but no function in decompiled RUL.
    sections = [s for s in sections if not s.startswith("export prototype VOID program\n")]
    if len(names) != 506 or len(sections) != len(names):
        raise ValueError("InstallScript function/action mapping drift")
    rows = []
    for spec in SCRIPTS:
        sec = _rul_section(rul, spec["name"])
        act = sections[names.index(spec["name"])]
        if _hash(sec.encode()) != spec["decompiled_sha256"] or _hash(act.encode()) != spec["actions_sha256"]:
            raise ValueError(f"InstallScript control-flow drift: {spec['name']}")
        if any(n not in sec for n in spec["needles"]):
            raise ValueError(f"InstallScript decisive statement drift: {spec['name']}")
        labels = re.findall(r"^([0-9a-f]+):", act, re.M)
        # Keep statements, not the proprietary complete function representation.
        selected = [line.strip() for line in sec.splitlines() if any(n in line for n in spec["needles"])]
        rows.append({"id": _id("script." + spec["name"]), "source": _id("setup.inx"),
                     "kind": "decoded-installscript-actions", "locator": spec["name"],
                     "action_offset_first": "0x" + labels[0], "action_offset_last": "0x" + labels[-1],
                     "decompiled_sha256": spec["decompiled_sha256"], "actions_sha256": spec["actions_sha256"],
                     "anchors": selected[:12], "finding": spec["finding"]})
    return rows


def _managed_evidence(pes: dict[str, Any], methods: list[dict[str, Any]] = METHODS) -> list[dict[str, Any]]:
    rows = []
    for spec in methods:
        pe = pes[spec["source"]]
        row, ins, body = _instructions(pe, spec["type"], spec["method"], index=spec.get("index", 0))
        if _method_pin(row, body) != spec["pin"]:
            raise ValueError(f"IL body drift: {spec['key']}")
        lines = [f"{instruction.opcode} {_operand(pe, instruction.operand)}".rstrip() for instruction in ins]
        if any(not any(n in line for line in lines) for n in spec["needles"]):
            raise ValueError(f"IL anchor drift: {spec['key']}")
        selected = []
        for needle in spec["needles"]:
            for instruction, line in zip(ins, lines):
                if needle in line:
                    selected.append({"file_offset": instruction.offset,
                                     "text": line, "bytes": bytes(instruction.get_bytes()).hex()})
                    break
        rows.append({"id": _id(spec["key"]), "source": _id(spec["source"]), "kind": "managed-il",
                     "locator": f"{spec['type']}::{spec['method']}", **spec["pin"],
                     "anchors": selected, "finding": spec["finding"]})
    return rows


def _header_shortcuts(data: bytes, labels: dict[str, str] | None = None) -> list[dict[str, Any]]:
    """Read packed folder/shortcut descriptors consumed by ISSetup's native loop."""
    labels = labels or {}
    u32 = lambda offset: struct.unpack_from("<I", data, offset)[0]
    u16 = lambda offset: struct.unpack_from("<H", data, offset)[0]
    base = u32(12)
    if data[:4] != b"ISc(" or base != 0x200:
        raise ValueError("InstallShield descriptor representation drift")
    def text(pointer: int) -> str:
        if not pointer:
            return ""
        start = base + pointer
        end = start
        while data[end:end + 2] != b"\0\0":
            end += 2
            if end + 2 > len(data):
                raise ValueError("InstallShield descriptor string boundary")
        return data[start:end].decode("utf-16le")
    table = u32(base + 0x27e)
    if not table:
        return []
    result = []
    def folder(pointer: int, parts: list[str]) -> None:
        if not pointer:
            return
        at = base + pointer
        name = text(u32(at + 4)) or text(u32(at))
        path = parts + ([labels.get(name, name)] if name else [])
        shortcut_count, shortcut_array = u16(at + 14), u32(at + 16)
        for index in range(shortcut_count):
            record = base + u32(base + shortcut_array + index * 4)
            label = text(u32(record + 4)) or text(u32(record))
            component_count, component_array = u16(record + 44), u32(record + 46)
            result.append({"folder": "/".join(path), "name": text(u32(record)),
                           "label": labels.get(label, label), "flags": u16(record + 8),
                           "target": text(u32(record + 10)), "icon": text(u32(record + 31)),
                           "record_file_offset": hex(record),
                           "components": [text(u32(base + component_array + i * 4)) for i in range(component_count)]})
        child_count, child_array = u16(at + 8) & 0x7fff, u32(at + 10)
        for index in range(child_count):
            folder(u32(base + child_array + index * 4), path)
    # Native constructor preserves these four pointers;10055ac7 dispatches
    # slots0/1/2/3 using SF_DESKTOP0/SF_STARTMENU4/SF_PROGRAMS1/SF_STARTUP2.
    for index, root in enumerate(("Desktop", "StartMenu", "Programs", "Startup")):
        folder(u32(base + table + index * 4), [root])
    return result


def _gui_shortcut_evidence(work: Path, source_path: str, source_id: str,
                           sources: list[dict[str, Any]], evidence: list[dict[str, Any]]) -> None:
    header = (work / "data1.hdr").read_bytes()
    if _hash(header) != "a93568e8b5bd8f9b6057dbe06fe1cef763c1bc819eaa696b2254f4d90bb3b28f":
        raise ValueError("GUI declarative shortcut header drift")
    engine_path = work / "ISSetup.dll"
    _pin(engine_path, "462ad24e32884802cd02194b95b67ad57d0c35df9c91c31defc6ac701603c1a1")
    sources.append({"id": _id("shortcut-engine"), "path": source_path + ":[0]:Disk1\\ISSetup.dll",
                    "sha256": sha256_file(engine_path), "size": engine_path.stat().st_size,
                    "representation": "original native InstallShield engine", "container": source_id})
    output = work / "shortcut-labels"
    subprocess.run(["unshield", "-g", "<Support>0x0409 String Tables", "-d", str(output),
                    "x", str(work / "data1.cab")], check=True, capture_output=True, text=True)
    strings_path = output / "_Support_0x0409_String_Tables/StringTable_0x0409.ips"
    _pin(strings_path, "e48eca0dc59f0d914c6d31fc8a97a8cdbbe53e91027ea46c04580a042e6fc468")
    sources.append({"id": _id("shortcut-labels"), "path": source_path + ":[0]:Disk1\\data1.cab:<Support>0x0409 String Tables\\StringTable_0x0409.ips",
                    "sha256": sha256_file(strings_path), "size": strings_path.stat().st_size,
                    "representation": "original English shortcut string table", "container": source_id})
    labels = dict(line.split("=", 1) for line in strings_path.read_text(encoding="utf-16").splitlines() if "=" in line)
    shortcuts = _header_shortcuts(header, labels)
    expected = [("Desktop", "GTS+", "gts/GTSMain.html"),
                ("Programs/GTS+", "GTS+", "gts/GTSMain.html"),
                ("Programs/GTS+", "CUW+", "cuw/CUWMain.html")]
    if [(s["folder"], s["label"], s["target"]) for s in shortcuts] != [
            (folder, label, "https://127.0.0.1:50005/GetResource/" + target) for folder, label, target in expected]:
        raise ValueError("GUI browser shortcut target/folder drift")
    if any(s["flags"] != 1 or s["components"] != ["GTSPlus GUI"] for s in shortcuts):
        raise ValueError("GUI shortcut type/feature gate drift")
    native = pefile.PE(str(engine_path))
    resource = next(r for r in native.DIRECTORY_ENTRY_RESOURCE.entries if str(r.name) == "TYPELIB")
    entry = resource.directory.entries[0].directory.entries[0].data.struct
    tlb = native.get_data(entry.OffsetToData, entry.Size)
    # MSFT enum records carry typed immediate values, not just enum-name strings.
    if tlb[:4] != b"MSFT":
        raise ValueError("InstallShield typelib format drift")
    count = struct.unpack_from("<I", tlb, 0x20)[0]
    directory = 0x54 + count * 4
    typebase = struct.unpack_from("<I", tlb, directory)[0]
    namebase = struct.unpack_from("<I", tlb, directory + 7 * 16)[0]
    typeinfo = typebase + 0x1d4c
    member_data = struct.unpack_from("<I", tlb, typeinfo + 4)[0]
    if count != 190 or struct.unpack_from("<I", tlb, typeinfo + 24)[0] != 5 << 16:
        raise ValueError("special-folder enum shape drift")
    enum_members = []
    for index, expected_name in enumerate(("SF_DESKTOP", "SF_PROGRAMS", "SF_STARTUP", "SF_FAVORITES", "SF_STARTMENU")):
        value_offset = member_data + 4 + index * 20 + 16
        typed_value = struct.unpack_from("<I", tlb, value_offset)[0]
        name_pointer = struct.unpack_from("<I", tlb, member_data + 4 + 100 + 20 + index * 4)[0]
        name_at = namebase + name_pointer
        name = tlb[name_at + 12:name_at + 12 + tlb[name_at + 8]].decode("ascii")
        if name != expected_name or typed_value != 0x8c000000 | index:
            raise ValueError("special-folder enum value drift")
        enum_members.append({"name": name, "value": index, "typed_value": hex(typed_value),
                             "value_rva": hex(entry.OffsetToData + value_offset)})
    native_pins = [(0x55b7b, "e849000000"), (0x55bb6, "e80e000000"),
                   (0x55ceb, "e8a0000000"), (0x5668b, "f64308010f84aa050000"),
                   (0x56830, "8b3d60010d10"), (0x56853, "68ec6b0d10bea86b0d1056ffd7")]
    if any(native.get_data(rva, len(bytes.fromhex(value))) != bytes.fromhex(value) for rva, value in native_pins):
        raise ValueError("native shortcut branch/URL-write instruction drift")
    evidence.append({"id": _id("native.shortcut-engine"), "source": _id("shortcut-engine"),
                     "kind": "native-bytes-and-decompilation", "locator": "10011851 ->10055ac7 ->10055bc9 ->10055d90",
                     "anchors": [{"rva": hex(rva), "bytes": value} for rva, value in native_pins],
                     "typelib": {"resource": "TYPELIB/1", "rva": hex(entry.OffsetToData), "size": entry.Size,
                                 "sha256": _hash(tlb), "enum": "tagSpecialFolders", "members": enum_members},
                     "finding": "10011851 copies four header root pointers.10055ac7 dispatches slots0/1/2/3 with folder enums0/4/1/2; typed embedded enum proves Desktop/StartMenu/Programs/Startup.10055bc9 recursively enumerates folder and shortcut descriptor arrays.10055d90 reads flags+8 and URL pointer+10; mask0x1 selects InternetShortcut/.url.1005668b TEST/JZ separates normal links;10056830 loads WritePrivateProfileStringW and10056853..5e writes[InternetShortcut]URL. This write's return is not checked before continuing. It creates links, not browser processes."})
    evidence.append({"id": _id("declarative-shortcuts"), "source": _id("child.Setup_GUI.exe.hdr"),
                     "kind": "typed-installshield-shortcut-table", "locator": "descriptor base0x200 +field0x27e ->four root pointers; label string table",
                     "label_source": _id("shortcut-labels"), "native_consumer": _id("native.shortcut-engine"),
                     "shortcuts": shortcuts, "startup_shortcuts": [],
                     "finding": "GUI installs Desktop/GTS+.url and Programs/GTS+/{GTS+,CUW+}.url for GUI-selected feature; localized English labels resolve ID_STRING2/3/5 toGTS+ and ID_STRING6 toCUW+. Targets are local frontend pages. Startup root is empty; browser entry is user activation through Windows shell/default HTTPS handler, not InfoCenter tray click or automatic application startup."})


def _cabinet_inventory(name: str, source: str, entries: list[Any]) -> dict[str, Any]:
    members = [entry.path for entry in entries]
    return {
        "id": _id("cabinet_members." + name), "source": source,
        "kind": "cabinet-member-table", "installer": name,
        "locator": "unshield l data1.cab; complete cabinet member table",
        "member_count": len(members), "members": members,
        "member_names_sha256": _hash(json.dumps(
            members, ensure_ascii=False, separators=(",", ":"),
        ).encode("utf-8")),
        "finding": "Exact member paths from the source-qualified current installer cabinet.",
    }


def _component_evidence(archive: Path, directory: Path, decoder: Path,
                        sources: list[dict[str, Any]], evidence: list[dict[str, Any]]) -> None:
    directory.mkdir(parents=True)
    subprocess.run([_sevenzip(), "e", "-y", str(archive), "2026.03.002.02/*.exe", f"-o{directory}"],
                   check=True, capture_output=True, text=True)
    parent_paths: dict[str, str] = {}
    for spec in COMPONENTS:
        name = spec["installer"]
        path = directory / name
        if spec["parent_installer"]:
            source_path = parent_paths[spec["parent_installer"]] + ":[0]:Disk1\\" + name
        else:
            source_path = _rel(archive) + ":2026.03.002.02/" + name
        if sha256_file(path) != spec["sha256"]:
            raise ValueError(f"component installer source drift: {name}")
        parent_paths[name] = source_path
        source_id = _id("child." + name)
        sources.append({"id": source_id, "path": source_path, "sha256": spec["sha256"],
                        "size": path.stat().st_size, "representation": "original packaged component installer",
                        "container": _id("child." + spec["parent_installer"]) if spec["parent_installer"] else _id("archive")})
        work = directory / path.stem
        work.mkdir(exist_ok=True)
        # 7-Zip automatically descends GraphViewer's embedded MS cabinet, so
        # read the exact PE overlay bounds instead of selecting its [0] view.
        pe = pefile.PE(str(path), fast_load=True)
        raw = path.read_bytes()
        start = pe.get_overlay_data_start_offset()
        end = pe.OPTIONAL_HEADER.DATA_DIRECTORY[4].VirtualAddress
        payload = raw[start:end]
        count = int.from_bytes(payload[:4], "little")
        if count != spec["record_count"]:
            raise ValueError(f"component SFX record count drift: {name}")
        pos = 4
        inx = None
        direct_shortcuts = []
        for _ in range(count):
            fields = []
            for _ in range(4):
                stop = pos
                while payload[stop:stop + 2] != b"\0\0":
                    stop += 2
                    if stop + 2 > len(payload):
                        raise ValueError("component SFX UTF16 record boundary")
                fields.append(payload[pos:stop].decode("utf-16le"))
                pos = stop + 2
            filename, member, version, length = fields
            if re.search(r"\.(?:url|lnk)$", filename, re.I):
                direct_shortcuts.append(member)
            size = int(length)
            body = payload[pos:pos + size]
            if len(body) != size:
                raise ValueError("component SFX payload boundary")
            if filename in ("setup.inx", "data1.cab", "data1.hdr", "data2.cab") or (name == "Setup_GUI.exe" and filename == "ISSetup.dll"):
                (work / filename).write_bytes(body)
            if filename == "data1.hdr":
                sources.append({"id": _id("child." + name + ".hdr"), "path": source_path + ":[0]:" + member,
                                "sha256": _hash(body), "size": size, "representation": "original declarative cabinet header",
                                "container": source_id, "sfx_payload_offset": pos})
            if filename == "CUWLauncher_Setup.exe":
                (directory / filename).write_bytes(body)
            if filename == "setup.inx":
                if pos != spec["inx_offset"] or size != spec["inx_size"] or _hash(body) != spec["inx_sha256"]:
                    raise ValueError(f"component script identity drift: {name}")
                inx = work / filename
                sources.append({"id": _id("child." + name + ".inx"), "path": source_path + ":[0]:" + member,
                                "sha256": _hash(body), "size": size, "representation": "original SFX InstallScript",
                                "container": source_id, "sfx_payload_offset": pos})
            pos += size
        if inx is None or any(payload[pos:]):
            raise ValueError("component SFX final boundary")
        del payload, raw
        listing = subprocess.run(["unshield", "l", str(work / "data1.cab")], check=True, capture_output=True, text=True).stdout
        entries = [e for e in _parse_unshield_listing(listing) if e.path != "files"]
        if len(entries) != spec["cabinet_file_count"] or any(re.search(r"AgentLite|AgentLight", e.path, re.I) for e in entries):
            raise ValueError(f"component cabinet/updater census drift: {name}")
        evidence.append(_cabinet_inventory(name, _id("child." + name + ".hdr"), entries))
        if any(re.search(r"\.(?:url|lnk)$", e.path, re.I) for e in entries):
            raise ValueError("copied shortcut-member census drift")
        expected_verifier = VERIFIER_PINS.get(name)
        if bool(expected_verifier) != any(e.path.endswith("VerifyTest2.exe") for e in entries):
            raise ValueError("component signature helper inventory drift")
        if expected_verifier:
            verifier_out = work / "verifier"
            subprocess.run(["unshield", "-d", str(verifier_out), "x", str(work / "data1.cab"), "*VerifyTest2.exe"],
                           check=True, capture_output=True, text=True)
            verifier_path = verifier_out / "_Support_Language_Independent_OS_Independent_Files/VerifyTest2.exe"
            if sha256_file(verifier_path) != expected_verifier:
                raise ValueError("component signature helper identity drift")
            verifier_id = _id("verifier." + name)
            sources.append({"id": verifier_id, "path": source_path + ":[0]:Disk1\\data1.cab:<Support>Language Independent OS Independent Files\\VerifyTest2.exe",
                            "sha256": expected_verifier, "size": verifier_path.stat().st_size,
                            "representation": "original native cabinet helper", "container": source_id})
            dual = expected_verifier.startswith("f94f90")
            pins = ([(0x1101, "ffd73d00010b80"), (0x116d, "85c07413"), (0x119b, "ffd785c07412"),
                     (0x11bf, "c744242801000000"), (0x11c7, "c7400801000000"),
                     (0x11ce, "8b4c243c8b410c894104"), (0x11e7, "ffd785c07412"),
                     (0x1204, "be01000000"), (0x1221, "33f6"), (0x1243, "8bc6"), (0x1282, "e979fdffff")]
                    if dual else [(0x1101, "ffd73d00010b80"), (0x1169, "85c07410"),
                                  (0x11cc, "8bf0f7de1bf646"), (0x11e2, "33f6"), (0x1204, "8bc6")])
            verifier_pe = pefile.PE(str(verifier_path), fast_load=True)
            if any(verifier_pe.get_data(rva, len(bytes.fromhex(value))) != bytes.fromhex(value) for rva, value in pins):
                raise ValueError("component trust verdict byte drift")
            evidence.append({"id": verifier_id, "source": verifier_id, "kind": "native-bytes-and-decompilation",
                             "locator": "FUN_00401000; main " + ("FUN_00401260" if dual else "FUN_00401220"),
                             "anchors": [{"rva": hex(rva), "bytes": value} for rva, value in pins],
                             "finding": ("Initial WinVerifyTrust must succeed, then STATE_CLOSE must return0, then specific-signature verification with dwFlags1/dwIndex=cSecondarySigs must succeed. Only this path setsESI1 at401204; other paths clearESI. Final STATE_CLOSE result ignored;401243 returnsESI. Unlike parent helper this variant selects last reported secondary signature (index0 if none)."
                                         if dual else "Byte-identical to parent helper: WinVerifyTrust zero normalizes to exit1; errors exit0. Caller feature aborts on0.")})
        paths = [work / "decoded.rul", work / "decoded.actions"]
        for out, flag in zip(paths, ("--show-decompiled", "--show-actions")):
            subprocess.run([str(decoder), str(inx), str(out), flag], check=True, capture_output=True, text=True)
        rul, actions = [p.read_text() for p in paths]
        names = re.findall(r"^function [^\n]+\b([A-Za-z_][A-Za-z0-9_]*)\(", rul, re.M)
        sections = [s.rstrip() for s in re.split(r"(?=^(?:export )?prototype )", actions, flags=re.M)
                    if s.strip() and not s.startswith("export prototype VOID program\n")]
        if len(names) != len(sections):
            raise ValueError("component InstallScript action mapping drift")
        functions = []
        function_specs = spec["functions"] + (LAUNCHER_GATE_FUNCTIONS if name == "CUWLauncher_Setup.exe" else [])
        for fn in function_specs:
            if name == "CUWLauncher_Setup.exe" and fn["name"] == "OnBegin":
                fn = {**fn, "anchors": LAUNCHER_ONBEGIN_ANCHORS}
            sec = _rul_section(rul, fn["name"])
            act = sections[names.index(fn["name"]) ]
            if _hash(sec.encode()) != fn["decompiled_sha256"] or _hash(act.encode()) != fn["actions_sha256"]:
                raise ValueError(f"component callback drift: {name}:{fn['name']}")
            if any(anchor not in sec for anchor in fn["anchors"]):
                raise ValueError("component callback statement drift")
            labels = re.findall(r"^([0-9a-f]+):", act, re.M)
            functions.append({**fn, "action_offset_first": "0x" + labels[0], "action_offset_last": "0x" + labels[-1]})
        evidence.append({"id": _id("component." + name), "source": _id("child." + name + ".inx"),
                         "kind": "decoded-component-installscript", "locator": "selected lifecycle/feature callbacks",
                         "functions": functions, "cabinet_file_count": len(entries),
                         "declarative_shortcut_source": _id("child." + name + ".hdr"),
                         "declarative_shortcuts": _header_shortcuts((work / "data1.hdr").read_bytes()),
                         "copied_shortcut_file_members": [],
                         "sfx_shortcut_file_members": direct_shortcuts,
                         "agentlite_payloads": [], "embedded_runtime_packages": spec["embedded_runtime_packages"],
                         "finding": spec["finding"] + " OnAbort and OnRebooted return without custom compensation."})
        if name == "CUWLauncher_Setup.exe":
            actual_keys = re.findall(r'LclVarObj1\(\d+\) = "(\{[^\"]+\})";', _rul_section(rul, "OnBegin"))
            if actual_keys != LAUNCHER_CLIENT_KEYS:
                raise ValueError("launcher shared-client key set drift")
            evidence[-1]["finding"] += " Removal is gated: OnBegin aborts before feature deletion when remove-only mode and more than one shared-client uninstall key exists; caller ignores the nested result."
            evidence.append({"id": _id("launcher-preservation-gate"), "source": _id("child.CUWLauncher_Setup.exe.inx"),
                             "kind": "decoded-installscript-control-flow", "locator": "IfxOnInitInstall -> OnBegin; Func_2116 mode predicate; registry wrappers",
                             "functions": [fn for fn in functions if fn["name"] in {f["name"] for f in LAUNCHER_GATE_FUNCTIONS} | {"OnBegin"}],
                             "registry_root": "HKLM/0x80000002", "registry_prefix": "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\",
                             "shared_client_keys": LAUNCHER_CLIENT_KEYS, "abort_threshold": ">1 existing keys",
                             "finding": "Func_2116 returns GblVarNum63, set from engine option38 by Func_2284; OnSuiteMaintBefore classifies this predicate as removal303. OnBegin sets HKLM via bound registry root, counts exactly12 uninstall keys and aborts only in remove-only mode with count>1. Initialization calls OnBegin before feature removal. Outer CUWPlusPF_UnInstalled does not inspect launch/exit result; outer removal can continue while launcher and associations remain."})
        if name in CERTIFICATE_SCRIPT_PINS:
            evidence.append(_certificate_script_evidence(name, rul, actions))
        if name == "Setup_PF.exe":
            ca_out = work / "public-ca"
            subprocess.run(["unshield", "-g", "GTSPlus_CA", "-d", str(ca_out),
                            "x", str(work / "data1.cab")], check=True, capture_output=True, text=True)
            ca_path = ca_out / "GTSPlus_CA/ca.crt"
            _pin(ca_path, "e3ac980851b2dfa220d668d4633327c6ea81ff3aaf976d3e1c425bce198c3b82")
            sources.append({"id": _id("cert-public.pf-ca"), "path": source_path + ":[0]:Disk1\\data1.cab:GTSPlus_CA\\ca.crt",
                            "sha256": sha256_file(ca_path), "size": ca_path.stat().st_size,
                            "representation": "original public CA certificate", "container": source_id})
            evidence.append({"id": _id("certificate-pf-root"), "source": _id("cert-public.pf-ca"),
                             "kind": "public-x509-metadata", "locator": "GTSPlus_CA/ca.crt -> installed bin/ca.crt",
                             "target_store": "LocalMachine/ROOT",
                             **_public_certificate(ca_path, "e3ac980851b2dfa220d668d4633327c6ea81ff3aaf976d3e1c425bce198c3b82"),
                             "finding": "GTS+ Root CA is a separate DENSO certificate, not SS-RCA/SS-ICA/server chain. Installed-file existence gates PF addstore; removal uses subject selector GTS+ Root CA, not fingerprint, without ownership/reference counting. Both command failures are ignored by empty script branches."})
        if name == "Setup_GUI.exe":
            _gui_shortcut_evidence(work, source_path, source_id, sources, evidence)
        if name == "Setup_GuiServer.exe":
            support = work / "certificate-support"
            subprocess.run(["unshield", "-g", "<Support>Language Independent OS Independent Files", "-d", str(support),
                            "x", str(work / "data1.cab")], check=True, capture_output=True, text=True)
            cert_dir = support / "_Support_Language_Independent_OS_Independent_Files/CertsInstall"
            for key, filename, expected in (
                ("cert", "CertInstaller.exe", "407b6b2a11d9b297ffc3ed240dfd332241c867232218f8ec510f2b17f54d612b"),
                ("cert-import-batch", "importCerts_SS.bat", "fab4e18d8f57b8881357dfbc928cb347ae011b6a8d4398c0b1c2d154c4c03878"),
                ("cert-remove-batch", "removeCerts.bat", "027d2d37b4e5f2015f063c827a625cde04830b9868b7f512c584112058f0d2e0"),
                ("cert-public.rca", "certs/rca.crt", "419f07c526c96e5a3f522b2f8402cc3b2c3ed1861048e7ddb922ed0b820abae5"),
                ("cert-public.ica", "certs/ica.crt", "70f477ba72fa586cb981c082a3e28d3a42293fe560b1f0e7327d4e48de71239c"),
                ("cert-public.server", "certs/server.pfx", "72270c9763956d37924cabbf45e72f45cda1cfcc6801b010f2c0ac65bb6558c0"),
            ):
                extracted = cert_dir / filename
                if sha256_file(extracted) != expected:
                    raise ValueError("packaged certificate helper drift")
                sources.append({"id": _id(key), "path": source_path + ":[0]:Disk1\\data1.cab:<Support>Language Independent OS Independent Files\\CertsInstall\\" + filename,
                                "sha256": expected, "size": extracted.stat().st_size,
                                "representation": "original cabinet support member", "container": source_id})
            evidence.extend(_managed_evidence({"cert": _open(cert_dir / "CertInstaller.exe")}, CERT_METHODS))
            # Inspect only commands and fixed public endpoint anchors; never emit
            # the packaged PFX password, certificate body or private key material.
            imp = (cert_dir / "importCerts_SS.bat").read_text()
            rem = (cert_dir / "removeCerts.bat").read_text()
            required = ["netsh http delete sslcert ipport=127.0.0.1:50005", "certutil -addstore ROOT", "certutil -addstore CA", "-importPFX", "netsh http add sslcert ipport=127.0.0.1:50005"]
            if any(value not in imp for value in required) or "netsh http delete sslcert ipport=127.0.0.1:50005" not in rem:
                raise ValueError("local TLS batch command drift")
            evidence.append({"id": _id("certificate-batches"), "source": _id("cert-import-batch"),
                             "kind": "packaged-batch-commands", "locator": "importCerts_SS.bat + removeCerts.bat",
                             "anchors": required, "removal_source": _id("cert-remove-batch"),
                             "finding": "Import/removal batches describe attempted destructive store/binding replacement, not established outcomes. Certificate callbacks attempt direct CreateProcess of .bat without cmd.exe and ignore launch/child failures; see certificate-failure-prefixes. No Windows certificate store or installer is executed by extraction."})
            _certificate_contract(cert_dir, evidence)


def _certificate_script_evidence(name: str, rul: str, actions: str) -> dict[str, Any]:
    names = re.findall(r"^function [^\n]+\b([A-Za-z_][A-Za-z0-9_]*)\(", rul, re.M)
    sections = [s.rstrip() for s in re.split(r"(?=^(?:export )?prototype )", actions, flags=re.M)
                if s.strip() and not s.startswith("export prototype VOID program\n")]
    functions = []
    for function, (rul_hash, action_hash) in CERTIFICATE_SCRIPT_PINS[name].items():
        sec, act = _rul_section(rul, function), sections[names.index(function)]
        if _hash(sec.encode()) != rul_hash or _hash(act.encode()) != action_hash:
            raise ValueError(f"certificate lifecycle script drift: {name}:{function}")
        offsets = re.findall(r"^([0-9a-f]+):", act, re.M)
        functions.append({"name": function, "decompiled_sha256": rul_hash, "actions_sha256": action_hash,
                          "action_offset_first": "0x" + offsets[0], "action_offset_last": "0x" + offsets[-1]})
    return {"id": _id("certificate-script." + name), "source": _id("child." + name + ".inx"),
            "kind": "decoded-installscript-control-flow", "locator": "certificate feature/route and full launch/service wrapper bodies",
            "functions": functions,
            "url_acl_registration": {"netsh_urlacl_commands": [], "scope": "complete decoded component script plus its two certificate batches; SSL binding is not a URL reservation"},
            "finding": ("OnShowUI selects update before maintenance before first-install after-handler. Only OnFirstUIAfter with maintenance=false attempts import batch, CertInstaller with EMPTY arguments, remover copy, then service create/change/start. OnUpdateUIAfter/OnMaintUIAfter only finish UI; no certificate refresh, policy refresh or remover repair. UnInstalling attempts saved remover and ignores its result."
                        if name == "Setup_GuiServer.exe" else
                        "CA feature checks installed bin/ca.crt existence before cmd.exe /C certutil -addstore Root. Uninstall unconditionally attempts cmd.exe /C certutil -delstore Root by subject GTS+ Root CA. Empty failure branches ignore wrapper errors; child certutil exit code is not tested.")}


def _public_certificate(path: Path, expected_der_sha256: str, *, public_pem: bytes | None = None) -> dict[str, Any]:
    # OpenSSL receives only a public certificate, never a PFX in this helper.
    data = path.read_bytes() if public_pem is None else public_pem
    der = subprocess.run(["openssl", "x509", "-outform", "DER"], input=data,
                         check=True, capture_output=True).stdout
    if _hash(der) != expected_der_sha256:
        raise ValueError("public certificate DER identity drift")
    metadata = subprocess.run(["openssl", "x509", "-noout", "-subject", "-issuer", "-serial", "-dates",
                               "-ext", "subjectAltName,basicConstraints,keyUsage,extendedKeyUsage"],
                              input=der, check=True, capture_output=True).stdout.decode()
    details = subprocess.run(["openssl", "x509", "-noout", "-text"], input=der,
                             check=True, capture_output=True).stdout.decode()
    return {"der_sha256": _hash(der), "sha1_thumbprint": hashlib.sha1(der).hexdigest(),
            "public_metadata": metadata.splitlines(),
            "public_key_algorithm": re.search(r"Public Key Algorithm: ([^\n]+)", details).group(1),
            "public_key_bits": int(re.search(r"Public-Key: \((\d+) bit\)", details).group(1)),
            "signature_algorithm": re.search(r"Signature Algorithm: ([^\n]+)", details).group(1)}


def _certificate_contract(cert_dir: Path, evidence: list[dict[str, Any]]) -> None:
    imp = (cert_dir / "importCerts_SS.bat").read_text()
    # Decrypt only the certificate bag: -nokeys forbids private-key output. The
    # packaging password is sent on stdin, never argv, evidence or a new file.
    password = re.search(r"certutil -p (\S+) -importPFX", imp).group(1)
    public_pem = subprocess.run(["openssl", "pkcs12", "-legacy", "-nokeys", "-in",
                                 str(cert_dir / "certs/server.pfx"), "-passin", "stdin"],
                                input=(password + "\n").encode(), check=True, capture_output=True).stdout
    del password
    certificates = []
    for key, filename, digest, store in (
        ("rca", "rca.crt", "872a65d447f6e6e656a0ce811c8170c14d8a71d22dca336647ebd8054503d23f", "LocalMachine/ROOT"),
        ("ica", "ica.crt", "500da1991f1db01258ab7b4504eb199f18b16f41ab51bf9fb3f71bbc4b5e7d11", "LocalMachine/CA"),
        ("server", "server.pfx", "0775ed039c456a15542bb90d5d48e7263978fe01fed26ce9072076bd197ed16b", "LocalMachine/My"),
    ):
        certificates.append({"source": _id("cert-public." + key), "target_store": store,
                             **_public_certificate(cert_dir / "certs" / filename, digest,
                                                   public_pem=public_pem if key == "server" else None)})
    del public_pem
    thumbprint = "eb95376e91340877cc7b2950c68a693a1b52eba6"
    if certificates[-1]["sha1_thumbprint"] != thumbprint:
        raise ValueError("binding certhash does not identify the packaged server certificate")
    # Batch commands are data, not executed. Remove the one secret operand before
    # retaining any command. Reject drift instead of redacting a guessed shape.
    commands = [line.strip() for line in imp.splitlines() if line.startswith(("netsh ", "certutil "))]
    commands = [re.sub(r"(?<=certutil )-p \S+ ", "-p <redacted> ", line) for line in commands]
    rem = (cert_dir / "removeCerts.bat").read_text()
    remove = [line.strip() for line in rem.splitlines() if line.startswith(("netsh ", "certutil "))]
    evidence.append({"id": _id("certificate-public-identities"), "source": _id("cert-public.server"),
                     "kind": "public-x509-metadata", "locator": "certs/{rca.crt,ica.crt,server.pfx certificate bag only}",
                     "certificates": certificates, "binding": {"ipport": "127.0.0.1:50005", "certhash": thumbprint,
                     "appid": "{ed1dce3e-2c21-4e5b-a9c7-d1cd7b728462}", "certificate_store": "MY (netsh default)",
                     "url_acl": "No URL ACL command is present in either batch; add sslcert installs an SSL binding, not a URL reservation."},
                     "finding": "Three distinct SS chain identities are separate from PF's GTS+ Root CA. certutil commands lack -user and therefore target machine stores; PFX import lacks -user/-enterprise and uses My by default. Public fingerprint is checked against exact binding hash; metadata does not prove host trust or successful import."})
    evidence.append({"id": _id("certificate-failure-prefixes"), "source": _id("cert-import-batch"),
                     "kind": "batch-sequential-operation-contract", "locator": "complete import/remove command sequence",
                     "attempted_import_operations": commands, "attempted_remove_operations": remove,
                     "failure_prefix_contract": "No IF ERRORLEVEL, &&, ||, exit /b, rollback or reboot handling: a failed command does not gate any later command. Every prefix of effects may remain; command results and effects are separate, and later commands may still succeed. No all-or-nothing certificate/store/binding transaction.",
                     "stdout_redirection": "Literal > null creates/truncates a file named null, NOT Windows NUL; stderr is not redirected. Import first cd /d %~dp0 > null; remover has no cd and its relative null path depends on launch working directory.",
                     "exit_code_contract": "No explicit batch exit code. Command-processor completion (if used) exposes last netsh/certutil command status, not aggregated earlier failures. InstallScript does NOT invoke cmd.exe for these two batches: Func_651 options1 -> Func_586 options1537 uses CreateProcess, not ShellExecuteExW (bit256 clear). Thus these are attempted direct process launches; no command interpreter or successful .bat execution is inferred. Even launch failure is ignored by certificate callbacks.",
                     "finding": "First-install destructive prefix deletes existing SSL binding, then My thumbprint, CA SS-ICA and ROOT SS-RCA before attempting additions and replacement binding. Removal targets only that binding and those three store selectors, no Firefox policy/profile files, PF root or URL ACL. All command external outcomes remain inputs, not reported successes."})
    evidence.append({"id": _id("certificate-sequencing"), "source": _id("child.Setup_GuiServer.exe.inx"),
                     "kind": "source-owned-install-update-remove-contract", "locator": "OnShowUI/OnFirstUIAfter/OnMaintUIAfter/OnUpdateUIAfter/UnInstalling -> Func_651 -> Func_586/609/631; Func_1929",
                     "first_install_attempt_order": ["direct CreateProcess importCerts_SS.bat; wait option1", "direct CreateProcess CertInstaller.exe with empty arguments; wait option1", "copy removeCerts.bat to uninstall location", "create or change GTS+GUIServer service and attempt start"],
                     "existing_install": "Update route and maintenance repair/modify finish handlers do not call the certificate/policy/import/copy/service-create sequence; they do not repair missing remover or migrate stale binding. Removal feature invokes persisted remover independently of these after-handlers.",
                     "process_result_channels": {"wrapper": "CreateProcess failure sets nLaunchResult=LastDllError and returns -1 through Func_631; successful creation eventually returns0 even when child exit is nonzero. Func_631 restores saved show/current-dir state and returns wrapper status unchanged.",
                     "child": "GetExitCodeProcess writes nLaunchResult; return value of GetExitCodeProcess and Func_609 wait status are not gates in Func_586. Certificate callers overwrite local wrapper status then discard it; neither status nor nLaunchResult aborts or stops the sequence.",
                     "wait": "Func_585 defaults nTimeOut=-1, wait-input-idle max2000ms; Func_651 adds512|1024 to1. Func_609 waits through MsgWaitForMultipleObjects; no finite default deadline and no child-tree wait bit2048. Early wait termination does not prove child completion."},
                     "partial_failure": "Failed batch launch/import, Firefox helper, remover copy or service setup does not gate later attempts here; no compensating operation in empty OnAbort/OnRebooted. Signature verification in the installed feature is a separate earlier abort gate.",
                     "reboot": "These certificate launch options omit16, so no Func_639 pending-RunOnce comparison and no special3010/1641 handling. Service wrapper may set GblVarNum1 for an existing-service condition; certificate child result does not set it. Update/maintenance finish selects reboot UI using GblVarNum1, while first-install after-handler has no finish/reboot dialog in this script.",
                     "service": "Func_1928 defaults own-process16, auto-start2, null account/password; Func_1929 opens existing service or creates it, applies description, optionally starts, then logs Service Added. All returns ignored by caller. This service setup is not URL ACL registration.",
                     "evidence": [_id("certificate-script.Setup_GuiServer.exe"), _id("certificate-script.Setup_PF.exe")],
                     "finding": "Precise attempted-operation order is recoverable without Windows; store/process/filesystem/service outcomes are not. Missing/failed direct batch launch can be followed by apparently successful policy and service setup; successful child exit is not installer certificate success."})
    evidence.append({"id": _id("firefox-policy-failure-contract"), "source": _id("cert"),
                     "kind": "managed-il-dataflow-and-exception-contract", "locator": "Program.Main/Start/GetInstallPathOfFirefox; PolicyEditer.AddCertificationPolicies/ReadJson/ImportCerts/WriteJson",
                     "normal_installer_mode": "Empty arguments -> installCerts=false -> if Firefox found, ImportEnterpriseRoots=true. It does not invoke InstallCerts2OS, add Install filenames or copy CA files.",
                     "merge": "Missing/zero-byte file creates JObject. Existing nonempty JSON must parse as JObject; policies and Certificates must be JObjects if present, otherwise cast fails. Missing objects are inserted; unrelated properties survive. ImportEnterpriseRoots is overwritten with true in default mode. Explicit installCerts reuses only an array-valued Install; nonarray Install is replaced by fresh JArray, retaining other certificate keys. Exact case-sensitive rca.crt/ica.crt duplicates are suppressed; existing array order and differently cased names remain.",
                     "failure": "AddCertificationPolicies catches Exception, Console.WriteLine(exception.ToString()), returns void, no status/exit-code change. Invalid JSON/object shape or write failure skips remaining policy steps, not process failure. WriteJson creates distribution parent then WriteAllText directly, no atomic replace/backup/rollback; a write failure cannot establish old-file survival.",
                     "explicit_copy_mode": "installCerts=true still copies after missing Firefox or caught policy failure. WMI/registry/SID/copy errors outside AddCertificationPolicies escape Main. Profile iteration tests c:\\Users\\fullName then name, not WMI LocalPath; always attempts Default afterward. Each directory overwrites rca then ica; no per-profile catch/cleanup. Failure on ica leaves prior rca/profile writes attempted and stops later profiles/Default. baseDir is exe directory while packaged public CAs reside in certs subdirectory, so packaged explicit copy path is not an established successful deployment.",
                     "uninstall": "Saved removeCerts.bat never invokes CertInstaller and never edits/deletes Firefox distribution/policies.json or profile certificate files. PF root removal is a separate feature, not SS remover ownership.",
                     "evidence": [_id(s["key"]) for s in CERT_METHODS],
                     "finding": "Policy edit is a targeted merge with two intentional replacements (ImportEnterpriseRoots and non-array Install), not wholesale policy replacement. Caught policy failure may produce normal helper termination; unhandled platform/copy failure may terminate helper, but enclosing installer ignores both channels."})


def _decoder_provenance(decoder: Path, checkout: Path, sources: list[dict[str, Any]]) -> dict[str, Any]:
    revision = subprocess.run(["git", "-C", str(checkout), "rev-parse", "HEAD"],
                              check=True, capture_output=True, text=True).stdout.strip()
    if revision != DECODER_REVISION:
        raise ValueError("InstallScript decoder checkout revision drift")
    for name, expected in DECODER_SOURCE_PINS.items():
        _pin(checkout / name, expected)
        # REFERENCE entries may be symlinks into the shared reference cache;
        # publish the repository-visible path, never a machine-local target.
        sources.append({"id": _id("decoder." + name),
                        "path": (checkout / name).absolute().relative_to(REPO_ROOT).as_posix(),
                        "sha256": expected, "size": (checkout / name).stat().st_size,
                        "representation": "pinned external decoder build input"})
    sources.append(_source("decoder.executable", decoder, "locally built offline analysis tool"))
    return {"repository": DECODER_REPOSITORY, "revision": DECODER_REVISION, "license": "MIT",
            "source_checkout": checkout.absolute().relative_to(REPO_ROOT).as_posix(), "executable_source": _id("decoder.executable"),
            "source_pins": DECODER_SOURCE_PINS,
            "checkout_recipe": "git clone https://github.com/jte/installscript-decompiler.git REFERENCE/installscript-decompiler && git -C REFERENCE/installscript-decompiler checkout --detach " + DECODER_REVISION,
            "build_recipe": "cargo build --locked --release --manifest-path REFERENCE/installscript-decompiler/Cargo.toml --target-dir build/cache/installscript-decompiler -p cli",
            "invocations": [["<decoder>", "<fresh pinned setup.inx>", "<output.rul>", "--show-decompiled"],
                            ["<decoder>", "<fresh pinned setup.inx>", "<output.actions>", "--show-actions"]],
            "identity_contract": "Exact upstream revision and locked source inputs are checked; executable SHA identifies this local platform build. Decisive decompiled/action hashes enforce the expected output representation; no universal cross-platform binary digest is claimed."}


def build(root: Path = DEFAULT_ROOT, recovered_root: Path = DEFAULT_MAIN,
          decoder: Path = DEFAULT_DECODER, decoder_source: Path = DEFAULT_DECODER_SOURCE) -> dict[str, Any]:
    root, recovered_root, decoder = root.resolve(), recovered_root.resolve(), decoder.resolve()
    decoder_source = decoder_source.absolute()
    sources: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []
    decoder_provenance = _decoder_provenance(decoder, decoder_source, sources)
    for rel, expected in SOURCE_PINS.items():
        _pin(root / rel, expected)
        sources.append(_source("file." + rel, root / rel, "installed file"))
    archive = root / "gtsplus_msi.7z"
    _pin(archive, ARCHIVE_SHA)
    sources.append(_source("archive", archive, "downloaded installer 7z"))
    pes = {}
    for key, rel in RECOVERED_SOURCES.items():
        path = recovered_root / rel
        original = root / "Toyota Diagnostics/GTSPlus" / rel
        qualification = qualify_recovered_source(path, original, component_root=recovered_root)
        for suffix, label, pinfield in (("", "stub", "stub_sha256"), ("._", "sidecar", "sidecar_sha256")):
            installed = original.with_name(original.name + suffix)
            _pin(installed, PROTECTED_PINS[key][pinfield])
            sources.append(_source(key + "." + label, installed, "original CP " + label))
        sources.append(_source(key, path, "manifest-qualified recovered PE",
                               original_sources=[_id(key + ".stub"), _id(key + ".sidecar")],
                               recovery=qualification))
        if key != "cm":
            proof = validate_managed_bodies(path)
            pes[key] = _open(path)
            evidence.append({"id": _id(key + ".materialization"), "source": _id(key),
                             "kind": "managed-body-materialization",
                             "locator": "all MethodDef classifications; complete valid IL bodies",
                             **proof, "qualification": qualification,
                             "finding": "Every required IL body passes full decoding, framing, operand and branch validation; native and legitimately bodyless methods remain separately classified."})
    manifest_path = root / "Toyota Diagnostics/GTSPlus/Ver/Manifest.json"
    manifest = json.loads(manifest_path.read_text())[0]
    versions = []
    for component in manifest["Components"]:
        actual = json.loads((manifest_path.parent / (component["Name"] + ".json")).read_text())["Version"]
        if actual != component["Version"]:
            raise ValueError("component version disagreement")
        versions.append({"id": component["Id"], "name": component["Name"], "version": actual})
    evidence.append({"id": _id("versions"), "source": _id("file.Toyota Diagnostics/GTSPlus/Ver/Manifest.json"),
                     "kind": "json-config", "locator": "[0].SoftwareVersion and Components[*]; sibling Version files",
                     "software_version": manifest["SoftwareVersion"], "components": versions,
                     "finding": "Ten component-version files agree with package version2026.03.002.02. Installed manifest DownloadFilePath fields are DummySoft1.exe placeholders, not actual updater URLs; runtime AgentLite uses different SW_ID/CP_ID namespace."})
    clear = decrypt_file(root / "Toyota Diagnostics/GTSPlus/Env/GtsPlus-PcCheckerTool.yml",
                         root / "Toyota Diagnostics/GTSPlus/GtsPlus-PcCheckerTool/PCT.pp",
                         recovered_root / RECOVERED_SOURCES["cm"], key_type=1)
    if _hash(clear) != "6247bf1466a3c7fe30536f96263c9b328e336d587533d41d3b28725f0a1e50fc":
        raise ValueError("decrypted checker settings drift")
    settings = _settings(clear)
    evidence.append({"id": _id("checker-settings"), "source": _id("file.Toyota Diagnostics/GTSPlus/Env/GtsPlus-PcCheckerTool.yml"),
                     "kind": "decrypted-local-config", "locator": "application-setting",
                     "decrypted_sha256": _hash(clear), "key_type": 1,
                     "active_checkers": settings["checkers"], "compiled_disabled_checkers": ["antivirs", "baseboard", "firefox"],
                     "wss_ports": settings["wss-ports"], "applications": settings["applications"], "services": settings["services"],
                     "finding": "Checker order/targets are configuration-driven; advisory report tool is not a setup precondition."})
    sevenzip = _sevenzip()
    listing = subprocess.run([sevenzip, "l", "-ba", str(archive)], check=True, capture_output=True, text=True).stdout
    archived = [line.split()[-1] for line in listing.splitlines() if line.rstrip().endswith(".exe")]
    if len(archived) != 11:
        raise ValueError("downloaded installer census drift")
    with tempfile.TemporaryDirectory(prefix="gts-install-update-") as temp:
        directory = Path(temp)
        parent = _extract_member(archive, "2026.03.002.02/GTSPlusParentInstaller_NA.exe", directory / "parent", sevenzip)
        _pin(parent, "cdb2d3997036578da4c2bd15f1a59eb7268b5e794788fd7bf8bfa1f3660cf91b")
        parent_path = _rel(archive) + ":2026.03.002.02/GTSPlusParentInstaller_NA.exe"
        sources.append({"id": _id("parent"), "path": parent_path, "sha256": sha256_file(parent),
                        "size": parent.stat().st_size, "representation": "InstallShield28.0.700 SFX", "container": _id("archive")})
        payload = _extract_sfx_payload(parent, directory / "sfx", sevenzip)
        records = _records(payload.read_bytes())
        for rec in records:
            (directory / rec["name"]).write_bytes(rec["body"])
            sources.append({"id": _id(rec["name"]), "path": parent_path + ":[0]" + ":" + rec["member"],
                            "sha256": rec["sha256"], "size": rec["size"], "representation": "SFX file record",
                            "container": _id("parent"), "sfx_payload_offset": rec["offset"]})
        cabinet = directory / "data1.cab"
        cabinet_list = subprocess.run(["unshield", "l", str(cabinet)], check=True, capture_output=True, text=True).stdout
        entries = [entry for entry in _parse_unshield_listing(cabinet_list) if entry.path != "files"]
        if len(entries) != 50 or any("agentlite" in entry.path.casefold() for entry in entries):
            raise ValueError("parent cabinet census drift")
        evidence.append(_cabinet_inventory("GTSPlusParentInstaller_NA.exe", _id("data1.hdr"), entries))
        out = directory / "cabinet"
        subprocess.run(["unshield", "-d", str(out), "x", str(cabinet)], check=True, capture_output=True, text=True)
        support = out / "_Support_Language_Independent_OS_Independent_Files"
        for key, rel, expected in (
            ("notify", "SafetyShutdown/GTSPlusNotifyEnd.exe", "4eca92bd0b1d6ab25c225d87ea59db61972f2e96687100ff4b83d3f2934c4349"),
            ("verify", "VerifyTest2.exe", "6b358a9e7d3b68d5bd900d96e09c6855d1451fd1bd27cc4bdbc84cfbc8313bc9"),
        ):
            path = support / rel
            # A temporary extracted path is not evidence provenance.
            if sha256_file(path) != expected:
                raise ValueError(f"packaged helper drift: {key}")
            sources.append({"id": _id(key), "path": parent_path + ":[0]:Disk1\\data1.cab:<Support>Language Independent OS Independent Files\\" + rel.replace("/", "\\"),
                            "sha256": expected, "size": path.stat().st_size,
                            "representation": "cabinet extracted original PE", "container": _id("data1.cab")})
        pes["notify"] = _open(support / "SafetyShutdown/GTSPlusNotifyEnd.exe")
        evidence.extend(_managed_evidence(pes))
        evidence.extend(_script_evidence(directory / "setup.inx", directory, decoder))
        verify = pefile.PE(str(support / "VerifyTest2.exe"))
        native_pins = [(0x1101, "ffd73d00010b80"), (0x1169, "85c07410"),
                       (0x11cc, "8bf0f7de1bf646"), (0x11e2, "33f6"), (0x1204, "8bc6")]
        for rva, expected in native_pins:
            if verify.get_data(rva, len(bytes.fromhex(expected))) != bytes.fromhex(expected):
                raise ValueError("VerifyTest2 decisive byte drift")
        evidence.append({"id": _id("native.verify"), "source": _id("verify"), "kind": "native-bytes-and-decompilation",
                         "locator": "FUN_00401000; main FUN_00401220", "image_base": "0x00400000",
                         "anchors": [{"rva": hex(rva), "bytes": b} for rva, b in native_pins],
                         "finding": "WinVerifyTrust policy GUID00AAC56B-CD44-11D0-8CC2-00C04FC295EE. Errors return0; final success normalized EAX→ESI by NEG/SBB/INC returns1. Main with target argument forwards result; parent treats0 as signature error."})
        prerequisites = []
        import xml.etree.ElementTree as ET
        for rec in records:
            if rec["name"].endswith(".prq"):
                xml = ET.fromstring(rec["body"])
                prerequisites.append({"name": rec["name"], "condition": xml.find("conditions/condition").attrib,
                                      "execute": xml.find("execute").attrib, "behavior": xml.find("behavior").attrib})
        evidence.append({"id": _id("prerequisites"), "source": _id("setup.ini"), "kind": "installer-config",
                         "locator": "ISSetupPrerequisites + embedded .prq files", "prerequisites": prerequisites,
                         "finding": "Bundled VC++2015 x86/x64 version14.0.23026.0 uses registry version condition, quiet /q, reboot return codes1641/3010; behavior Reboot=2 is retained as engine configuration."})
        evidence.append({"id": _id("installer-census"), "source": _id("archive"), "kind": "archive-inventory",
                         "locator": "7z11 executables; parent SFX20 records; cabinet50 files",
                         "archive_members": archived, "parent_record_count": 20, "parent_cabinet_file_count": 50,
                         "additional_first_party_helpers": ["VerifyTest2.exe", "SafetyShutdown/GTSPlusNotifyEnd.exe"],
                         "copied_shortcut_file_members": [e.path for e in entries if re.search(r"\.(?:url|lnk)$", e.path, re.I)],
                         "sfx_shortcut_file_members": [r["member"] for r in records if re.search(r"\.(?:url|lnk)$", r["name"], re.I)],
                         "archive_shortcut_file_members": [line.split()[-1] for line in listing.splitlines() if re.search(r"\.(?:url|lnk)$", line.rstrip(), re.I)],
                         "declarative_shortcut_source": _id("data1.hdr"),
                         "declarative_shortcuts": _header_shortcuts((directory / "data1.hdr").read_bytes()),
                         "cabinet_application_payloads": [e.path for e in entries if e.path.startswith(("ComponentNA", "PCSettingsNA", "AutoSave"))],
                         "finding": "Parent embeds component settings/manifest, VC prerequisites and shutdown/signature helpers, but references sibling component installers. No AgentLite host/message/edit/service executable occurs in parent records or cabinet."})
        _component_evidence(archive, directory / "components", decoder, sources, evidence)
    log_path = root / "AgentLite/logs/AgentLite_Service.log"
    log = log_path.read_text()
    # Anchors deliberately exclude raw identity, authentication, certificate and URL payloads.
    log_needles = ["ManifestFileDownloader.DownloadManifest(Boolean isForced)", "NotifyReInstall: START", "SW_INST_Ver[], SW_MANI_Ver[2026.03.002.02]", "FileDownload.CopyFile", 'インストール引数:[/s /v"/qn"]', "UnauthorizedAccessException: Access to the path 'GTSPlusParentInstaller_NA.exe' is denied.", "インストール完了", "ReInstallResult: END", "ダウンロード済のインストーラーの強制インストール処理:START"]
    if any(needle not in log for needle in log_needles):
        raise ValueError("retained AgentLite observation drift")
    evidence.append({"id": _id("agent-observed"), "source": _id("file.AgentLite/logs/AgentLite_Service.log"),
                     "kind": "retained-runtime-log-observation", "locator": "lines17-27,286-469",
                     "anchors": log_needles,
                     "finding": "Retained reinstall run: manifest initially blocked by client-certificate validation; later manifest1.69 compared versions; no uninstall command skipped uninstall; eleven files downloaded; only parent launched /s /v\"/qn\". Polling deferred while another operation ran. Cleanup UnauthorizedAccessException was followed by installation-complete and ReInstallResult. This records one run, not a recovered general retry/failure policy."})
    families = sorted(p.name for p in (root / "Toyota Diagnostics").iterdir() if p.is_dir())
    if families != ['CUWPlus', 'ContentServer', 'DS-4', 'DiagMessageInput', 'GTSE', 'GTSPlus', 'GTSPlus DataSync', 'GTSPlusCSVConverter', 'GTSPlusGUI', 'GTSPlusGraphViewer', 'GTSPlusTSEConverter', 'PCS Data Viewer']:
        raise ValueError("installed family census drift")
    missing_agent = sorted(p.name for p in root.rglob("*.exe") if re.search(r"AgentLite|AgentLightHost|AgentLightService|AgentLightMessage|AgentLightEdit", p.name, re.I))
    if missing_agent:
        raise ValueError("previously omitted AgentLite executable became available; analyze its body")
    evidence.append({"id": _id("families"), "source": _id("archive"), "kind": "installed-directory-census",
                     "locator": "Toyota Diagnostics immediate directories + external CUWLauncher",
                     "families": families, "outside_tree_executable_family": "CUWLauncher",
                     "agentlite_executables_found": missing_agent,
                     "finding": "Twelve installed application directories plus external CUWLauncher; AgentLite tree retains state/logs but omits executable implementation."})
    def ev(*names: str) -> list[str]:
        return [_id(n) for n in names]
    states = [
        ("agent-idle", "AgentLite service (omitted executable)", "Retained log owner of manifest/version check and download/install scheduling"),
        ("agent-manifest-blocked", "AgentLite service", "Observed manifest attempt failed client-certificate validation"),
        ("downloaded", "AgentLite service", "All component installers downloaded; parent scheduled"),
        ("setup-route", "parent setup.inx", "Select initial/update/maintenance branch"),
        ("transferring", "parent setup.inx + InstallShield runtime", "Transfer settings and prepare uninstall metadata"),
        ("children", "parent setup.inx", "Optional sibling components processed serially"),
        ("certificate-setup-attempts", "GuiServer first-install after-handler", "Ordered import-process, Firefox helper, remover-copy and service-setup attempts; no aggregate success gate"),
        ("certificate-setup-continued", "GuiServer installer", "Sequence returned without establishing HTTPS trust/binding success"),
        ("certificate-removal-attempted", "GuiServer uninstall feature", "Saved remover launch attempted; Firefox policy/files retained"),
        ("shortcuts-installed", "GUI installer + native InstallShield engine", "Generated desktop/menu InternetShortcut files for local GTS/CUW pages"),
        ("browser-navigation-requested", "Windows shell/default HTTPS handler", "User activates an installed .url to request the local frontend"),
        ("setup-aborted", "InstallShield runtime", "Abort after explicit script failure/cancel or component error"),
        ("setup-finish", "parent setup.inx", "Finish UI or reboot-needed finish UI"),
        ("os-reboot", "InstallShield runtime", "Finish reboot option delegates engine.Reboot"),
        ("uninstall", "parent setup.inx", "Safe shutdown then logged component and registered child removals"),
        ("launcher-uninstall-check", "nested CUWLauncher setup.inx", "OnBegin shared-client preservation check before removal features"),
        ("launcher-preserved", "nested CUWLauncher setup.inx", "Shared-client count>1 aborts nested removal, retaining launcher and associations"),
        ("safe-end", "GTSPlusNotifyEnd", "ER_EndABAppCS reply and Arbitration termination monitoring"),
        ("safe-end-failed", "GTSPlusNotifyEnd", "Exit1 error/still-running; exit2 no reply"),
        ("pc-start", "PcCheckerTool", "Single-instance UI with decrypted checker configuration"),
        ("pc-check", "PcCheckerTool", "Advisory sequential checks and in-memory report"),
        ("pc-complete", "PcCheckerTool", "All configured checks visited; user may save report"),
        ("process-recovery", "PcCheckerTool", "Kill owned GTS processes and restart Arbitration"),
        ("process-recovery-failed", "PcCheckerTool", "No target, stop timeout, restart absence or exception"),
        ("process-recovered", "PcCheckerTool", "Arbitration PID observed after restart wait"),
        ("closed", "PcCheckerTool", "Window/application exit"),
        ("status", "InfoCenter", "Status refresh displays manifest version and process/service health"),
    ]
    transitions = []
    def transition(key: str, frm: str, to: str, trigger: str, guard: str, action: str, *ids: str) -> None:
        transitions.append({"id": _id(key), "from": _id(frm), "to": _id(to), "trigger": trigger,
                            "guard": guard, "action": action, "evidence": ev(*ids)})
    transition("manifest-failure", "agent-idle", "agent-manifest-blocked", "NotifyStartUp", "observed client-certificate validation failure", "returns startup result; no download in failed attempt", "agent-observed")
    transition("reinstall-observed", "agent-idle", "downloaded", "NotifyReInstall", "retained run manifest comparison", "download11 installers; missing uninstall string is skipped", "agent-observed", "installer-census")
    transition("launch-parent", "downloaded", "setup-route", "parent installer scheduled", "retained run launch", "parent /s /v\"/qn\"", "agent-observed")
    transition("route-transfer", "setup-route", "transferring", "OnShowUI", "initial/update/maintenance pre-handler completes", "OnMoveData transfers then matching after-handler", "script.OnShowUI", "script.OnMoveData")
    transition("transfer-failure", "transferring", "setup-aborted", "component transfer return<0", "or engine special abort code", "OnComponentError then abort", "script.OnMoveData", "script.Func_704")
    transition("transfer-children", "transferring", "children", "IfxOnTransferred invokes OnMoved", "not pure uninstall", "serial CHILD_ORDER; absent files skipped", "script.OnMoved")
    transition("signature-failure", "children", "setup-aborted", "VerifyTest2 returns0", "DataSync or GUI sibling present", "signature error and abort", "script.OnMoved", "native.verify")
    transition("child-failure", "children", "setup-aborted", "child return", "launch wrapper return0 AND nLaunchResult!=0", "abort; no Toyota compensation in OnAbort", "script.OnMoved", "script.OnAbort")
    transition("child-continue", "children", "children", "next child", "absent child OR launch wrapper!=0 OR child exit0", "continue optional sibling sequence", "script.OnMoved", "script.Func_629")
    transition("children-finish", "children", "setup-finish", "OnMoved returns0", "after-handler", "normal or reboot-needed finish; OnEnd starts GUIServer and prepares folders", "script.OnFirstUIAfter", "script.OnUpdateUIAfter", "script.OnEnd")
    transition("finish-reboot", "setup-finish", "os-reboot", "reboot finish", "reboot-needed and BootOption3/interactive reboot selected", "engine.Reboot", "script.Func_1216", "script.Func_1376", "prerequisites")
    transition("cancel", "transferring", "setup-aborted", "OnCanceling", "confirmation6", "close current dialog; cancelled finish; abort; decline leaves current state unchanged", "script.OnCanceling", "script.OnAbort")
    transition("uninstall-safe-end", "setup-route", "safe-end", "maintenance removal303", "SafetyShutdown directory exists", "launch persisted GTSPlusNotifyEnd", "script.OnMaintUIBefore")
    transition("safe-end-failure", "safe-end", "safe-end-failed", "helper reply/timeout", "error/still present/no reply", "exit1/2; parent aborts>0", "notify.Program.GTSPlusNotifyEndExec", "notify.ProgramReturn..cctor", "script.OnMaintUIBefore")
    transition("safe-end-success", "safe-end", "uninstall", "helper return0", "owner absent OR successful end reply and observed owner termination", "remove logged/all components; pure uninstall dispatches11 registered child uninstall strings with -s", "notify.Program.Main", "notify.Program.GTSPlusNotifyEndExec", "script.OnMaintUIBefore", "script.OnMoved", "script.Func_1834")
    transition("retry-dialog", "transferring", "transferring", "file/internet/MD5 error", "dialog result3", "repeat dialog; other engine return codes propagated", "script.OnFileError", "script.OnInternetError", "script.OnMD5Error")
    transition("pc-entry", "pc-start", "pc-check", "check selection", "mutex owned and configuration decrypted", "construct configured checker sequence", "pc.App.Main", "pc.App.OnStartup", "checker-settings", "pc.CheckPage.CreateCheckerList")
    transition("pc-next", "pc-check", "pc-check", "Next", "remaining configured checks", "next check irrespective warning; per-check exception returns false and error icon then reenables Next", "pc.<DoCheck>d__5.MoveNext", "pc.<ButtonClick>d__14.MoveNext", "pc.<<DoCheck>b__0>d.MoveNext")
    transition("pc-done", "pc-check", "pc-complete", "Next", "index>=count", "completion page; report remains memory until user saves", "pc.<ButtonClick>d__14.MoveNext", "pc.CheckCompletePage.OutputButtonClick")
    transition("pc-recovery-start", "pc-start", "process-recovery", "Reboot selection", "user initiates recovery", "find PID only under target installation path", "pc.RebootPage..ctor", "pc.RebootPage.GetPid")
    transition("pc-recovery-failed", "process-recovery", "process-recovery-failed", "recovery execution", "no PIDs OR10000ms exit wait fails OR restart PID absent OR exception", "show failure; Finish available", "pc.<ExecReboot>d__7.MoveNext", "pc.<DoReboot>d__6.MoveNext")
    transition("pc-recovery-ok", "process-recovery", "process-recovered", "restart complete", "kill waits complete; Arbitration PID>0 after10000ms delay", "show completed; Finish available", "pc.<ExecReboot>d__7.MoveNext", "pc.<DoReboot>d__6.MoveNext")
    transition("pc-exit", "pc-complete", "closed", "Finish", "user click", "close main window; OnExit; mutex finally released", "pc.CheckCompletePage.FinishButtonClick", "pc.App.OnExit", "pc.App.Main")
    transition("certificate-first-attempt", "children", "certificate-setup-attempts", "GuiServer OnFirstUIAfter", "update=false and maintenance=false", "attempt import batch -> CertInstaller empty arguments -> save remover -> service create/change/start; batch is direct CreateProcess, not cmd.exe", "certificate-script.Setup_GuiServer.exe", "certificate-sequencing", "certificate-public-identities")
    transition("certificate-partial-failure-continues", "certificate-setup-attempts", "certificate-setup-continued", "each attempted operation returns", "any launch/copy/service status or child exit including failure", "discard failure channels; later operations still attempted; no rollback or certificate-driven reboot status", "certificate-sequencing", "certificate-failure-prefixes", "firefox-policy-failure-contract")
    transition("certificate-existing-no-refresh", "children", "children", "GuiServer OnUpdateUIAfter or OnMaintUIAfter", "existing install update/repair/modify route", "finish UI only; no certificate refresh, Firefox edit, remover repair or service registration here", "certificate-script.Setup_GuiServer.exe", "certificate-sequencing")
    transition("certificate-uninstall-attempt", "uninstall", "certificate-removal-attempted", "GTSPlusGUIServer_UnInstalling", "feature selected for removal", "attempt persisted removeCerts.bat; ignore wrapper/child status; remove binding and SS store selectors only if batch actually executes; leave Firefox policy/files", "certificate-script.Setup_GuiServer.exe", "certificate-failure-prefixes", "firefox-policy-failure-contract")
    transition("certificate-pf-root-attempt", "children", "children", "GTSPlus_CA_Installed", "installed bin/ca.crt exists", "cmd.exe /C certutil -addstore Root; no launch/exit failure abort; separate DENSO root identity", "certificate-script.Setup_PF.exe", "certificate-pf-root")
    transition("certificate-pf-root-remove-attempt", "uninstall", "uninstall", "GTSPlus_CA_UnInstalling", "CA feature selected for removal", "cmd.exe /C certutil -delstore Root by GTS+ Root CA subject; ignore errors; no shared-use count", "certificate-script.Setup_PF.exe", "certificate-pf-root")
    transition("component-service-stop", "children", "children", "DataSync/GuiServer OnMoving", "service exists and not stopped", "bounded service-stop attempts separated by1000ms; stop failure does not itself abort feature transfer; DataSync also attempts bounded ProxyManager taskkill", "component.Setup_DataSync.exe", "component.Setup_GuiServer.exe")
    transition("component-trust-failure", "children", "setup-aborted", "feature certificate verification", "VerifyTest2 returns0 for installed DLL/exe or NI engine", "feature callback aborts; prior completed sibling installers are not compensated by empty OnAbort callbacks", "component.Setup_PF.exe", "component.Setup_GUI.exe", "component.Setup_DataSync.exe", "component.Setup_InfoCenter.exe", "component.Setup_GuiServer.exe", "component.CUWPlusPF.exe", "component.Setup_NativeGraphViewer.exe", "component.Setup_PCSDataViewer.exe", "component.Setup_TSEConverter.exe", "native.verify")
    transition("datasync-service-start", "children", "children", "DataSync OnMoved", "not pure uninstall", "create/change GTS+ DataSync service then start; start ProxyManager if absent; ignored command/service failures are not mapped to abort here", "component.Setup_DataSync.exe")
    transition("datasync-service-delete", "uninstall", "uninstall", "DataSync OnMoved", "pure uninstall", "delete GTS+ DataSync service", "component.Setup_DataSync.exe")
    transition("nested-launcher-install", "children", "children", "CUWPlusPF_Installed", "nested launcher payload exists", "launch CUWLauncher_Setup /clone_wait -s; no child result gate; launcher registers five extension families", "component.CUWPlusPF.exe", "component.CUWLauncher_Setup.exe")
    transition("ni-engine-install", "children", "children", "GraphViewer after-handler", "first/update or non-removal maintenance", "launch NI NativeGraph/Volume/Install.exe with spec.iss /qb- /log result.log /r; no result gate in caller", "component.Setup_NativeGraphViewer.exe")
    transition("component-registration", "children", "children", "PF/GUI feature and finish hooks", "corresponding component installed", "Arbitration startup shortcut, RegAsm registration, root-CA addstore and .gtse association; command failures are not checked by empty branches", "component.Setup_PF.exe", "component.Setup_GUI.exe")
    transition("component-deregistration", "uninstall", "uninstall", "component uninstall feature callbacks", "component selected for removal; nested launcher has its own preservation gate", "PF RegAsm /u and root-CA removal; GuiServer removeCerts.bat; CUW launcher uninstall dispatch may preserve shared launcher; NI uninst.exe; component cleanup", "component.Setup_PF.exe", "component.Setup_GuiServer.exe", "component.CUWPlusPF.exe", "component.CUWLauncher_Setup.exe", "launcher-preservation-gate", "component.Setup_NativeGraphViewer.exe", "component.Setup_PCSDataViewer.exe", "certificate-batches")
    transition("launcher-uninstall-check", "uninstall", "launcher-uninstall-check", "CUWPlusPF_UnInstalled", "nested launcher uninstall string exists", "launch nested uninstall -s without checking launch/exit result; initialization calls OnBegin", "component.CUWPlusPF.exe", "launcher-preservation-gate")
    transition("launcher-preserve-shared", "launcher-uninstall-check", "launcher-preserved", "OnBegin", "Func_2116 remove-only flag true AND existing shared-client HKLM uninstall keys>1", "abort before launcher/association removal", "launcher-preservation-gate")
    transition("launcher-removal-admitted", "launcher-uninstall-check", "uninstall", "OnBegin returns", "remove-only flag true AND existing shared-client keys<=1", "gate admits nested removal; selected launcher uninstall feature deletes extension keys", "launcher-preservation-gate", "component.CUWLauncher_Setup.exe")
    transition("launcher-abort-ignored", "launcher-preserved", "uninstall", "nested uninstall returns after abort", "outer CUWPlusPF_UnInstalled ignores wrapper/exit result", "outer component continues while shared launcher and file associations remain", "component.CUWPlusPF.exe", "launcher-preservation-gate")
    transition("create-browser-shortcuts", "children", "shortcuts-installed", "GUI engine shortcut phase", "GTSPlus GUI feature eligible", "generate Desktop/GTS+.url and Programs/GTS+/{GTS+,CUW+}.url; no startup-root browser shortcut", "declarative-shortcuts", "native.shortcut-engine", "component.Setup_GUI.exe")
    transition("activate-browser-shortcut", "shortcuts-installed", "browser-navigation-requested", "user activates desktop/menu .url", "Windows HTTPS handler configured", "Windows shell opens local GTSMain.html or CUWMain.html in default handler; this is not InfoCenter tray activation or automatic process startup", "declarative-shortcuts", "native.shortcut-engine")
    handoffs = [
        {"to_domain": "bootstrap", "caller": "parent setup.inx OnMaintUIBefore", "callee": "GTSPlusNotifyEnd -> MsgDatComm.ER_EndABAppCS -> Arbitration", "mechanism": "child process then existing application communication API", "payload": "helper exit0/1/2; parent abort on>0", "evidence": ev("script.OnMaintUIBefore", "notify.<>c.<GTSPlusNotifyEndExec>b__2_0", "notify.ProgramReturn..cctor")},
        {"to_domain": "bootstrap", "caller": "PcChecker ExecReboot", "callee": "GTSPlusArbitration.exe", "mechanism": "Process.Kill/WaitForExit/Start", "payload": "four process names; install-prefix filter;10000ms waits", "evidence": ev("pc.RebootPage..ctor", "pc.RebootPage.GetPid", "pc.<ExecReboot>d__7.MoveNext")},
        {"to_domain": "sync_upload", "caller": "InfoCenter UpdateStatus", "callee": "DataSync + shared status API", "mechanism": "ER_NotifyAppCommunicationCS and ER_GetAllRunningStatusCS", "payload": "ds_unsent_req; running-owner status; manifest version is display only", "evidence": ev("info.MainWindow.UpdateStatus", "info.MainWindow.UpdateApplicationStatus")},
        {"to_domain": "ui_ipc", "caller": "parent OnEnd", "callee": "GTS+GUIServer", "mechanism": "Windows service StartServiceW", "payload": "service name; except pure uninstall", "evidence": ev("script.OnEnd", "script.Func_2018")},
        {"to_domain": "sync_upload", "caller": "DataSync component OnMoving/OnMoved", "callee": "GTS+ DataSync and GtsPlus-ProxyManager", "mechanism": "service control and bounded process termination/relaunch", "payload": "service root from registry/config, stop waits, executable path, startup shortcut", "evidence": ev("component.Setup_DataSync.exe")},
        {"to_domain": "cuw_utility", "caller": "CUWPlusPF feature hook -> nested CUWLauncher setup", "callee": "CUWLauncher.exe", "mechanism": "nested silent installer and Windows shell file associations", "payload": ".cuw/.cuwc/.scuw/.cuwd/.usbrepro quoted file argument", "evidence": ev("component.CUWPlusPF.exe", "component.CUWLauncher_Setup.exe")},
        {"to_domain": "bootstrap", "caller": "PF OnMoved/NativeUtilityReg feature hook", "callee": "Arbitration startup and ReplaceFromLegasy COM registration", "mechanism": "startup shortcut plus RegAsm /codebase or /u", "payload": "installed executable/DLL paths", "evidence": ev("component.Setup_PF.exe")},
        {"to_domain": "ui_ipc", "caller": "GuiServer first-install after-handler", "callee": "local HTTPS binding and Firefox enterprise-root helper", "mechanism": "direct CreateProcess batch attempts then CertInstaller empty arguments; no URL ACL command in these paths", "payload": "127.0.0.1:50005, exact public chain/thumbprint/appid; update/maintenance does not refresh; failure not propagated as certificate failure", "evidence": ev("certificate-public-identities", "certificate-sequencing", "certificate-failure-prefixes", "firefox-policy-failure-contract")},
        {"to_domain": "ui_ipc", "caller": "Windows shell:GUI-installed desktop/menu InternetShortcut", "callee": "https://127.0.0.1:50005/GetResource/{gts/GTSMain.html,cuw/CUWMain.html}", "mechanism": "user activation of generated .url through default HTTPS handler", "payload": "GTS+ desktop and GTS+/CUW+ Programs labels; no automatic browser startup", "evidence": ev("declarative-shortcuts", "native.shortcut-engine")},
    ]
    persistence = [
        {"path_pattern": "GTSPlus/Ver/Manifest.json + component-name.json", "producer": "parent ComponentNA and sibling installers", "consumer": "InfoCenter status/version and AgentLite version integration", "created": "installer transfer; ten installed version files observed", "flushed": "installed JSON files", "deleted": "removal delegated component logs/registered uninstallers", "evidence": ev("versions", "installer-census", "info.MainWindow.UpdateStatus", "script.OnMoved")},
        {"path_pattern": "AgentLite/DOWNLOAD/Pc/<software-id>/<version>/*.exe", "producer": "AgentLite omitted service", "consumer": "parent/sibling InstallShield installers", "created": "retained reinstall downloads", "flushed": "DL complete observed;11 source installers retained in7z", "deleted": "cleanup attempted; one access-denied then install complete observed; current DOWNLOAD/Pc empty", "evidence": ev("agent-observed", "installer-census")},
        {"path_pattern": "AgentLite/{Manifest,SAVE,Files/setting}/*", "producer": "AgentLite omitted executable", "consumer": "AgentLite", "created": "opaque retained state files", "flushed": "persistence format and ordering not recovered", "deleted": "unknown omitted implementation", "evidence": ev("families", "agent-observed")},
        {"path_pattern": "uninstall-location/{setup.iss,SafetyShutdown/*}", "producer": "OnCustomizeUninstInfo", "consumer": "OnMaintUIBefore safe shutdown/uninstall", "created": "after component transfer", "flushed": "copy helpers/dependencies; append -f1 to uninstall string", "deleted": "runtime uninstall ownership", "evidence": ev("script.OnCustomizeUninstInfo", "script.OnMaintUIBefore")},
        {"path_pattern": "Public/Documents/GTSPlus/UserData; GTSPlus/Work", "producer": "parent OnEnd", "consumer": "GTSE File shortcut/application workspace", "created": "except pure uninstall", "flushed": "directory creation/shortcut/permission functions", "deleted": "not specified by OnEnd", "evidence": ev("script.OnEnd")},
        {"path_pattern": "<chosen-folder>/Result-yyyyMMddHHmmss.txt", "producer": "PcCheckerTool", "consumer": "user/support report", "created": "memory report at CheckPage construction; disk only folder-picker accept", "flushed": "File.WriteAllText; output error logged; cancel no write", "deleted": "no automatic deletion in inspected report path", "evidence": ev("pc.CheckPage..ctor", "pc.CheckCompletePage.OutputButtonClick")},
        {"path_pattern": "CommonDocuments/PcCheckerTool/Log", "producer": "PcCheckerTool App", "consumer": "log4net", "created": "PCT_LOG_DIR set by App constructor", "flushed": "log backend configuration", "deleted": "not recovered", "evidence": ev("pc.App..ctor", "pc.App.OnExit")},
        {"path_pattern": "startup/Arbitration shortcut; startup/GtsPlus-ProxyManager shortcut", "producer": "PF OnMoved and DataSync proxy feature", "consumer": "Windows user startup", "created": "selected first install/feature-installed callbacks", "flushed": "AddIcon installer wrapper", "deleted": "component removal ownership", "evidence": ev("component.Setup_PF.exe", "component.Setup_DataSync.exe")},
        {"path_pattern": "HKCR/.gtse + gtse_auto_file; HKCR/{.cuw,.cuwc,.scuw,.cuwd,.usbrepro} shell associations", "producer": "GUI OnEnd and nested CUWLauncher feature", "consumer": "Windows shell", "created": "component completion/feature install; launcher clears prior keys first", "flushed": "registry setup wrapper", "deleted": "CUWLauncher uninstall deletes extension keys only after OnBegin admits removal; shared-client count>1 preserves launcher/associations while outer removal continues; GUI deletion not specified by inspected OnEnd", "evidence": ev("component.Setup_GUI.exe", "component.CUWLauncher_Setup.exe", "component.CUWPlusPF.exe", "launcher-preservation-gate")},
        {"path_pattern": "PublicDocuments/GTSPlus/temp/{component-marker}.txt", "producer": "component OnEnd callbacks", "consumer": "external progress integration not recovered", "created": "except pure uninstall where guarded", "flushed": "create/close marker file; no application data payload", "deleted": "not specified by these callbacks", "evidence": ev("component.Setup_GUI.exe", "component.Setup_GuiServer.exe", "component.Setup_NativeGraphViewer.exe", "component.Setup_PCSDataViewer.exe", "component.CUWPlusPF.exe", "component.Setup_TSEConverter.exe")},
        {"path_pattern": "LocalMachine/{ROOT,CA,My}; HTTP.sys SSL binding127.0.0.1:50005", "producer": "GuiServer first-install batch launch attempt; separate PF CA feature", "consumer": "local service TLS and machine root trust", "created": "batch commands describe destructive replacement; direct batch launch is not proven interpreter execution", "flushed": "individual certutil/netsh results unobserved; no transactional/aggregate success claim", "deleted": "persisted SS remover binding/thumbprint/subject selectors; separate PF subject-based root removal; no URL ACL operation", "evidence": ev("certificate-public-identities", "certificate-failure-prefixes", "certificate-sequencing", "certificate-pf-root")},
        {"path_pattern": "Firefox/distribution/policies.json; c:/Users/{fullName,name,Default}/AppData/Roaming/Mozilla/Certificates/{rca,ica}.crt", "producer": "CertInstaller", "consumer": "Firefox trust policy", "created": "normal installer empty args only enables enterprise roots; explicit installCerts adds filenames and attempts profile copies from executable directory", "flushed": "targeted JSON merge then direct WriteAllText; caught policy errors do not fail helper; profile copies overwrite rca then ica without compensation; packaged files actually nested under certs", "deleted": "uninstall/maintenance never removes Firefox policy/profile certs in recovered paths", "evidence": ev("firefox-policy-failure-contract", "certificate-sequencing", "cert.Program.ctor", "cert.Program.CopyCerts2AppData")},
        {"path_pattern": "Desktop/GTS+.url; Programs/GTS+/{GTS+,CUW+}.url", "producer": "GUI declarative header + native ISSetup engine", "consumer": "Windows shell/default HTTPS handler", "created": "GUI-selected component shortcut phase", "flushed": "WritePrivateProfileStringW writes InternetShortcut URL/icon/working-directory properties; API result not checked here", "deleted": "GUI OnBegin deletes legacy Public/Desktop/GTSPlus.url; generated shortcut removal is InstallShield engine/log ownership", "evidence": ev("declarative-shortcuts", "native.shortcut-engine", "component.Setup_GUI.exe")},
    ]
    residuals = [
        {"question": "General AgentLite update/retry/cancel/scheduling and atomic rollback policy", "why_unclosed": "Installed tree, parent20 records/cabinet50 entries, all10 sibling SFX/cabinets and nested CUWLauncher setup contain no AgentLite/AgentLight service/host/message/edit executable body; retained run is observation only.", "next_evidence": "Original AgentLite installer or installed AgentLightHost/CommonLib/service/message/edit assemblies; decompile scheduling/version-comparison/download/install/cleanup paths."},
        {"question": "Windows setup engine transactional and third-party NI installer behavior", "why_unclosed": "All11 shipped first-party child/nested scripts are decoded and OnAbort callbacks have no custom compensation; parent abort does not compensate already completed child processes. Actual OS installer-engine rollback/reboot effects are environment-owned.", "next_evidence": "Controlled offline Windows installation snapshots and NI/InstallShield engine traces; source scripts do not establish OS transaction outcomes."},
        {"question": "Exact opaque AgentLite Manifest/SAVE configuration schema and durability", "why_unclosed": "No parser owner executable available; filenames/binary data are retained but arbitrary decryption guessing would not establish parser contracts.", "next_evidence": "AgentLite CommonLib/local persistence implementation with source-pinned payload."},
        {"question": "Native Authenticode trust result on Windows", "why_unclosed": "Static VerifyTest2 byte and decompilation evidence recovered; WinVerifyTrust was never executed and platform certificate stores/policy are environmental inputs.", "next_evidence": "Offline Windows harness with synthetic signed/unsigned files and controlled certificate store; no vendor credential/network use."},
    ]
    return {"schema": "gtsplus-lifecycle-domain-v1", "domain": DOMAIN, "sources": sources,
            "evidence": evidence,
            "states": [{"id": _id(key), "owner": owner, "meaning": meaning} for key, owner, meaning in states],
            "transitions": transitions, "handoffs": handoffs, "persistence": persistence,
            "coverage": {"components": families + ["CUWLauncher", "parent installer", "VerifyTest2", "GTSPlusNotifyEnd", "CertInstaller", "PcCheckerTool", "InfoCenter", "AgentLite retained runtime state"] + [s["installer"] for s in COMPONENTS],
                         "entrypoints": [f"{s['type']}::{s['method']}" for s in METHODS + CERT_METHODS] + [s["name"] for s in SCRIPTS] + [s["installer"] + ":" + fn["name"] for s in COMPONENTS for fn in s["functions"]] + ["CUWLauncher_Setup.exe:" + fn["name"] for fn in LAUNCHER_GATE_FUNCTIONS] + [name + ":" + fn for name, functions in CERTIFICATE_SCRIPT_PINS.items() for fn in functions],
                         "branches": [t["id"] for t in transitions]},
            "installer_child_order": CHILD_ORDER,
            "residuals": residuals,
            "tool_provenance": {"installscript_decoder": decoder_provenance,
                                "public_x509": {"dependency": "OpenSSL 3+ with legacy provider for this packaged certificate bag",
                                                "commands": ["openssl pkcs12 -legacy -nokeys -in <pinned server.pfx> -passin stdin",
                                                             "openssl x509 -outform DER",
                                                             "openssl x509 -noout -subject -issuer -serial -dates -ext subjectAltName,basicConstraints,keyUsage,extendedKeyUsage",
                                                             "openssl x509 -noout -text (selected public algorithm/key-size fields only)"],
                                                "identity": "Pinned original members and canonical DER SHA256/SHA1 calculated directly over DER bytes",
                                                "secret_handling": "Packaging password passed only through stdin to -nokeys; no argv, generated evidence, private-key output or persistent cleartext file"}},
            "analysis_projects": ["lc_install_update", "lc_install_update_verify", "lc_install_update_verify_legacy", "lc_install_update_shortcuts"],
            "safety": "Static PE/IL/InstallScript/config inspection and local package decryption only; no Windows application, installer, vehicle, authentication or network execution."}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--recovered-root", type=Path, default=DEFAULT_MAIN)
    parser.add_argument("--installscript-decoder", type=Path, default=DEFAULT_DECODER)
    parser.add_argument("--installscript-decoder-source", type=Path, default=DEFAULT_DECODER_SOURCE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    result = build(args.root, args.recovered_root, args.installscript_decoder, args.installscript_decoder_source)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(f"Wrote {args.out}: {len(result['evidence'])} evidence records, {len(result['transitions'])} transitions")


if __name__ == "__main__":
    main()
