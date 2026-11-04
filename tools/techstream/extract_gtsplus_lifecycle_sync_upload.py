#!/usr/bin/env python3
"""Extract pinned DataSync queue recovery, crash ordering, proxy and ActionTool evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import dnfile
from dncil.clr.token import Token

from tools import REPO_ROOT
from tools.techstream.extract_gtsplus_tse_managed_semantics import (
    _body, _method_pin, _open, _recovery_proof, sha256_file,
)
from tools.techstream.inspect_dotnet_il import format_operand, resolve_token, type_name
from tools.techstream.gtsplus_local_crypto import decrypt_file

DEFAULT_ROOT = REPO_ROOT / 'software/Techstream/gtsplus/unpacked/gtsplus'
DEFAULT_RECOVERED = REPO_ROOT / 'build/out/gts-lifecycle-aux'
DEFAULT_OUT = REPO_ROOT / 'data/generated/gtsplus_2026/lifecycle_sync_upload.json'
DOMAIN = 'sync_upload'
COMPONENTS = {
    'sync': ('GTSPlus DataSync/GTSPlusDataSync.exe', '057da3b0f92e070418225d498c29c68b4d845a0f6720863ce1934cdf62972021', '2e3fb514e8b22b64d4a811be30013bf15c4b6d64cf166065df24c8dd2dc3afae', 'cc7fe52f26c93837899e917024e665ab2cfe568bf4a6f5908e6ce931db265f33'),
    'proxy': ('GTSPlus DataSync/GtsPlus-ProxyManager.exe', 'c07002eb0c008ecd07f395b5009af4d61afb487d24ac7fee7949735860a70a51', '2b4ed71dee1bdbac69c6115e488d351ae69a3f01eac0e815388d2979ca599821', 'e310d1daae22b139f1683744b991118406075537a249e82bc30ea6ef5894947a'),
    'action': ('DiagMessageInput/ActionTool.exe', '3e82c1bb4014c7df4d54a1ec7822da1e45bd98663e54f32d47e379daa8f5ea5d', 'c20d5d2c729306786494e3ef178ae518de2d88f0a6ada777bc79640f24492216', '4fc7fc2a27f6c848fb54ede602715801c6d852b7bfd0c69bf115f0aaaa90b654'),
    'common': ('DiagMessageInput/CommonLibrary.dll', 'fcceab0815336f8242ecea4fb8bbbef8cd2985169537c3b00a001e807e466151', '', ''),
}
# Each tuple pins a decoded method by RVA and checks decisive resolved IL operands.
# The assembly hashes above guard every branch byte, including unprinted instructions.
METHODS = [
    ('service_main', 'sync', 0x2689, ['ServiceBase::Run'], 'SCM service entry; no console/GUI main loop.'),
    ('service_start', 'sync', 0x231c, ['CoInitializeSecurity', 'StartAliveMonitorRunningEvent', 'StartWaitingForApiEvent', 'Timer::set_AutoReset'], 'OnStart installs inter-process callbacks and a non-repeating initialization timer.'),
    ('service_timer', 'sync', 0x23c8, ['Execute', 'ServiceController::Stop', 'WaitForStatus'], 'Controller construction/uncaught execution failure stops the Windows service; finally logs monitoring completion.'),
    ('controller_init', 'sync', 0x2a44, ['InitializeDatabase', 'InitializeAuthentication', "'DSP.pp'", 'ReadEncryptedExternalProperty', 'migrationInfoQueue', 'transmissionTaskInfoQueue'], 'Controller creates shared cancellation/semaphore and two in-memory queues after database and encrypted policy initialization.'),
    ('database_init', 'sync', 0x2f90, ['get_DatabaseDirectryPath', 'DatabaseFacade::EnsureCreated', 'GetUserVersion', 'Invalid database file.'], 'System folder drive prefix + GTSPlusDataSyncDb contains SQLite DB; new DB is EnsureCreated, newer user_version throws. Older-version branch exits this method; it does not call DoMigration here.'),
    ('task_order', 'sync', 0x2df8, ['transmissionTask', 'migrationTask', 'monitoringTask', 'disposalTask', 'cleaningTask', 'launchLoggingTask'], 'Start transmission, migration, monitoring, disposal, cleaning, then optional logging.'),
    ('heartbeat', 'sync', 0x2ee8, ['taskStatus', 'Initialize'], 'Controller heartbeat reinitializes taskStatus=0 tasks; optional logging only when launchLoggingTask is true.'),
    ('watch_start', 'sync', 0x6248, ['SetWatcherInfoList', 'OperateExistingFiles', 'StartWatching', 'StopWatching'], 'Initial scan precedes enabling created-file watchers; startup failure stops/clears watchers.'),
    ('watch_create', 'sync', 0x64f8, ['Directory::CreateDirectory', 'FileSystemWatcher::set_Path', 'FileSystemWatcher::set_NotifyFilter', 'FileSystemWatcher::add_Created'], 'One configured destination directory watcher uses NotifyFilter 0x11 (FileName|LastWrite), Created event; no recursive watcher setting.'),
    ('watch_enqueue', 'sync', 0x6368, ['CreateMigrationInfo', '::Add', 'Unexpected exception'], 'Created files become FileInfo+Destination migration records in memory; enqueue exceptions are logged.'),
    ('migration_worker', 'sync', 0x6104, ['get_IsCancellationRequested', '::TryTake', 'ReleasableWait', 'InsertProcessInfo', 'DoMigration', 'CalculateHashMd5', 'UpdateProcessInfo', '::TryAdd'], 'Under shared semaphore: commit process_info first, move file second, store MD5(MD5(file)+LOCAL salt), then best-effort timed transmission enqueue. Exceptions are logged and loop continues; cancellation is checked at loop head.'),
    ('migration_move', 'sync', 0x5f18, ['get_WorkDirectory', 'get_Path', 'Path::Combine', 'FileInfo::MoveTo'], 'Move original into configured transmission work directory under decimal process_info.id (not its original extension).'),
    ('migration_commit', 'sync', 0x5f74, ['set_Destination', 'set_UnitId', 'set_OriginalFileName', 'set_OriginalExtension', 'DbContext::SaveChanges'], 'Persistent row records destination/unit/original name/extension plus audit timestamps before file movement.'),
    ('transmission_start', 'sync', 0x66dc, ['StartAppCommunicationEvent', 'OperateAccumulatedFiles', 'SetTransmissionSchedule', 'add_OnConnectivityChanged', 'DoProcessAsync'], 'Startup scans accumulated files, enables timer/connectivity notification and live queue worker; setup catch disposes network/rest clients.'),
    ('transmission_timer', 'sync', 0x6a18, ['Timer::Stop', 'CheckNetworkAvailability', 'OperateAccumulatedFiles', 'Timer::Start'], 'Periodic backlog scan runs only online; timer stops around scan and restarts.'),
    ('connectivity', 'sync', 0x68f0, ['0x40', '0x400', 'System.Enum::HasFlag', 'OperateAccumulatedFiles'], 'IPv4/IPv6 Internet connectivity flags trigger backlog scan; disconnection logs a warning.'),
    ('backlog', 'sync', 0x6a70, ['ReleasableWait', 'EnumerateFiles', 'SelectProcessInfo', 'ExtractAccumulatedDataList', 'OrderByDescending', 'get_IsCancellationRequested', 'OperateFile'], 'Reconcile work files with DB under semaphore, process destinations by descending monitoring priority, abort iteration on cancellation, continue after per-destination exceptions.'),
    ('backlog_due', 'sync', 0x9f54, ['get_RetrySchedule', 'DateTimeOffset::CompareTo', '::Add', 'FileSystemInfo::Delete'], 'A matching original-id file is eligible when retry_schedule absent or due; unreferenced work files are deleted unless referenced as compressed artifacts.'),
    ('backlog_missing', 'sync', 0xa00c, ['Enumerable::All', 'DeleteProcessInfo'], 'Rows with no decimal-id original file are removed during reconciliation.'),
    ('operate', 'sync', 0x6d60, ['get_StopExecute', 'get_MskStatus', 'DoValidation', 'DoProperCompression', 'GetProxy', 'CalculateHashSha256', 'DoTransmission', 'AddHashValue', 'get_MaxAttempts', 'mskexpired', 'mskrevoked'], 'StopExecute or nonzero MSK status suppresses upload. Validate original/compressed payload, persist validation, refresh proxy then request; success records duplicate digest then deletes files/row; retry schedules delay, max attempts disposes, special MSK results suspend uploads and notify PF.'),
    ('validation_steps', 'sync', 0x705c, ['ldc.i4.s 0x63', 'ldc.i4.s 0x62', 'ldc.i4.5'], 'Fresh original checks extension/size/duplicate/JSON header; previously validated original rechecks duplicate+tampering; compressed checks size on first validation or tampering on reuse.'),
    ('validation', 'sync', 0x79d0, ['ValidateTampering', 'ValidateExtension', 'ValidateFileSize', 'ValidateDoubleTransmission', 'ValidateJsonHeader', 'Enumerable::All'], 'Enabled destination validators all must pass; no unconditional file-type inference from filename alone.'),
    ('compression', 'sync', 0x7c98, ['zstandardClient', 'gZipClient', 'Compress'], 'CompressionMethod 1=Zstandard, 2=GZip; method 0 uses original through CheckCompressionStatus. Reuse existing compressed artifact if recorded and present.'),
    ('request_body', 'sync', 0x7168, ['set_FileName', 'set_Version', 'set_DataType', 'set_CompressionMethod', 'set_Checksum', "'SHA256'", 'set_FileSize'], 'Request metadata fields FileName,Version,DataType,CompressionMethod,Checksum,HashAlgorithm,FileSize. Checksum is SHA256(SHA256(transmitted bytes)+GLOBAL salt), not plain file SHA256.'),
    ('multipart_args', 'sync', 0xa0c0, ["'application/json'", "'logInfo'", "'application/octet-stream'", "'logFile'", 'DoMultipartPostAsync'], 'Multipart logInfo JSON and logFile binary; binary alias restores original name plus compression suffix.'),
    ('http_client', 'sync', 0x8b50, ["'Basic'", 'get_ServerAccessId', 'get_ServerAccessPassword', 'ToBase64String', 'set_Proxy', 'set_UseProxy', 'HttpClient::.ctor', "'X-GUID'"], 'Each destination gets Basic authorization and X-GUID; timeout uses config. Empty proxy uses parameterless HttpClient at IL0065. Proxy branch constructs HttpClient(HttpMessageHandler) at IL00ED from configured handler; overload signatures are retained.'),
    ('http_response', 'sync', 0x8cd0, ["'X-MSK'", 'PostAsync', 'ReadAsStringAsync', 'Deserialize', '0xc8', 'IsRetryTargetStatusCode', 'MIR4030001', 'MIR4000000', 'TaskCanceledException', 'HttpRequestException', 'get_RequestCountThreshold'], 'MSK loaded locally if missing and added as X-MSK when nonempty. Deserialize response before HTTP check. HTTP200 => result1; configured retry status =>2; HTTP403/MIR4030001=>4(expired); HTTP400/MIR4000000=>5(revoked); other=>3. Exceptions produce retry2 with timeout/communication/unexpected delay. Inner request loop count is config-bounded.'),
    ('retry_status', 'sync', 0x49f0, ['get_StatusErrors', '<IsRetryTargetStatusCode>b__0', 'Enumerable::Where'], 'HTTP retry eligibility/delay comes from configured status list; not hardcoded broad 5xx retry.'),
    ('retry_commit', 'sync', 0x7710, ['set_RetrySchedule', 'set_IsRetryable', 'get_RequestAttempts', 'set_RequestAttempts', 'DbContext::SaveChanges'], 'Retry update always sets is_retryable=true; its boolean argument controls incrementing attempts, not retryability. OperateFile passes false for HTTP401, so 401 does not consume attempts.'),
    ('success_cleanup', 'sync', 0x7800, ['get_CompressedFilePath', 'DeleteFile', 'DeleteProcessInfo'], 'Acknowledged success deletes compressed/original files before removing DB row.'),
    ('error_cleanup', 'sync', 0x7838, ['TransmissionErrorEntity', 'ValidationErrorEntity', 'DisposeFileImmediately', 'DeleteProcessInfo'], 'Validation and terminal transmission errors apply distinct destination disposal policies then delete queue row.'),
    ('immediate_disposal', 'sync', 0x78cb, ['ldc.i4.2', 'EvacuateFile', 'DeleteFile'], 'DisposalType=2 evacuates; other values delete immediately.'),
    ('evacuate', 'sync', 0x7918, ['get_Id', 'get_OriginalFileName', 'FileInfo::MoveTo', 'FileSystemInfo::Delete'], 'Evacuation deletes compression artifact and moves original to configured evacuation/id/original_filename, replacing existing destination.'),
    ('expiration', 'sync', 0x9694, ['get_IsRetryable', 'get_CreatedAt', 'get_Expiration', 'AddDays', 'AddHours', 'AddMinutes', 'AddSeconds', 'DateTimeOffset::CompareTo', 'DeleteProcessInfo'], 'Disposal skips is_retryable=true. Nonretryable rows expire at CreatedAt+configured duration; then delete or evacuate and remove row. Missing originals also remove compression/row.'),
    ('clean_policy', 'sync', 0x9510, ['get_ValidationError', 'get_TransmissionError', 'get_AllowCleaning', 'DoCleaningCore'], 'Clean evacuation directories only when disposal type2 and AllowCleaning; validation/transmission evacuation paths are handled separately.'),
    ('clean_age', 'sync', 0x95b0, ['get_LastWriteTime', 'get_Cleaning', 'get_Expiration', 'DateTimeOffset::CompareTo'], 'Evacuation subdirectory LastWriteTime+common retention duration must be earlier than now; in-use IOException skips directory.'),
    ('log_package', 'sync', 0x99cc, ['CreateUnmergedFilePath', 'CreateMergedFilePath', 'MergeFileContents', 'get_MonitoringRule', 'FileInfo::MoveTo', 'UpdateLoggingHistory'], 'DataSync logs are copied, randomized delay applied, single log renamed or multiple logs merged once-header, moved into configured logging destination watch root; history updated then copied/source logs deleted.'),
    ('log_constants', 'sync', 0x5d7c, ['GTSPlusDataSync'], 'Logging filename pattern GTSPlusDataSync*.log; export names GUID_firstdate_lastdate.log or GUID_date.log.'),
    ('logging_selector', 'sync', 0x84ca, ['DSY-D01', 'get_Id', 'System.String::op_Equality'], 'LoggingTask is enabled only when DSY-D01 destination exists; deployed C02/E02/M02 policy has no DSY-D01, so optional log packaging is inactive.'),
    ('auth_init', 'sync', 0x3afc, ['CreateChallengeCode', 'CheckAuthenticationCode', 'throw'], 'Native local crypto authentication must return challenge and accept authentication code or controller initialization throws.'),
    ('policy_read', 'sync', 0x3b50, ['Decryption', 'ParseDataSyncProperties', 'DeserializeWithValidation', 'throw'], 'Native config decryption nonzero result or property parser failure throws; YAML is deserialized with validation after header skip.'),
    ('msk_read', 'sync', 0x4a44, ['get_MskFileDirectryPath', 'get_MskFileName', 'get_PfPasswordFilePath', 'ReadEncryptedExternalMsk'], 'Read encrypted local LIC/msk using configured PF Env pairing; failures are handled by multipart method and may leave X-MSK absent.'),
    ('ipc_register', 'sync', 0x7d44, ['get_SenderApplicationName', 'AppCommunicationCallback', 'ER_StartAppCommunicationCS'], 'Service registers JSON application communication callback as GTS+ DataSync.'),
    ('ipc_messages', 'sync', 0x7d90, ['mskupdated', 'ds_unsent_req', 'ds_send', 'get_Unit_id_list', 'SelectProcessInfoUnitAll', 'CheckUnitId', 'set_Unsent_num', 'OperateAccumulatedFiles'], 'mskupdated clears cached MSK/status; ds_unsent_req returns result+unit_list counts (empty requested list means all units); ds_send scans backlog. Bad JSON/unknown id returns empty; malformed request result1, invalid unit2, exception9.'),
    ('ipc_notify', 'sync', 0x81c0, ['get_DestinationApplicationName', 'get_SenderApplicationName', 'ER_NotifyAppCommunicationCS'], 'MSK-expired/revoked notices go to configured GTS+ PF; callback return is not an upload acknowledgment.'),
    ('confirm_end', 'sync', 0x25b3, ['ldc.i4.1', 'SetStopExecute'], 'PF ending-confirmation pauses new file upload work without cancelling the controller.'),
    ('execute_end', 'sync', 0x25d7, ['brfalse.s', 'ServiceBase::Stop', 'ldc.i4.0', 'SetStopExecute'], 'Ending decision true stops service; false cancels shutdown and clears upload pause.'),
    ('service_stop', 'sync', 0x238e, ['Abort', 'EndAliveMonitorRunningEvent', 'EndWaitingForApiEvent', 'set_ExitCode'], 'OnStop aborts controller if present, unregisters liveness/ending callbacks, and sets exit code0.'),
    ('controller_abort', 'sync', 0x2d08, ['CancellationTokenSource::Cancel', 'controlMode', 'get_ControllerAbortTimeout', 'Task::Wait', 'Dispose'], 'Cancel shared token and clear controlMode; bounded wait for shutdown task, then dispose token/semaphore.'),
    ('stop_order', 'sync', 0x2e80, ['loggingTask', 'cleaningTask', 'disposalTask', 'monitoringTask', 'migrationTask', 'transmissionTask'], 'Task shutdown reverses startup order.'),
    ('transmission_stop', 'sync', 0x67b8, ['Task::WaitAll', 'get_CurrentCount', 'remove_OnConnectivityChanged', 'Timer::Stop', 'EndAppCommunicationEvent', 'taskStatus'], 'Await queue worker and semaphore availability; then stop/dispose timer, network/rest resources, unregister application IPC, clear status.'),
    ('proxy_main', 'proxy', 0x22ec, ['GTSPlusProxyManager', 'Mutex::.ctor', 'Application::Run', 'ReleaseMutex'], 'One global mutex owner starts hidden WinForms message loop; duplicate closes handle and returns; finally releases/ closes mutex.'),
    ('proxy_init', 'proxy', 0x20b8, ['0xea60', 'set_ShowInTaskbar', 'InitializeAuthentication', 'ReadEncryptedExternalProperty', 'MainTask', 'Run'], 'Hidden process decrypts server URI policy, samples system proxy immediately, then installs 60000ms timer; policy exceptions rethrow.'),
    ('proxy_lookup', 'proxy', 0x2962, ['GetSystemWebProxy', 'IWebProxy::GetProxy'], 'Proxy discovery asks current-user system WebProxy for configured destination URI; not a network upload.'),
    ('proxy_persist', 'proxy', 0x2974, ['Uri::get_AbsoluteUri', 'Uri::get_Host', 'Uri::get_Port', 'Host,', 'Port,', 'EncryptionProxyFile', 'File::Delete'], 'Changed proxy host/port writes encrypted Host/Port CSV via DSP.pp; direct destination (proxy URI equals server URI) deletes proxy file.'),
    ('proxy_path', 'proxy', 0x2a74, ['ProxyInformation.csv'], 'ProxyInformation.csv is on SystemDrive; despite .csv suffix its persisted contents are encrypted.'),
    ('proxy_consume', 'sync', 0x45fc, ['File::Exists', 'Decryption', 'Host,', 'Port,'], 'Missing proxy file returns empty host/port; encrypted file is decoded then Host/Port parsed.'),
    ('proxy_refresh', 'sync', 0x46b0, ['GetProxyFile', 'op_Inequality', 'Dispose', 'createHttpClient'], 'Before each upload, changed proxy host/port disposes/rebuilds all destination clients.'),
    ('action_entry', 'action', 0x2054, ['GetParentProcessId', 'GetExecutablePath', 'GTSPlus.exe', 'GTSPLUS-2-FIXEDMSGINPUT', 'FixedMessage_ActionToolMutex', 'Shutdown'], 'ActionTool rejects unidentified/wrong parent, absent/wrong first argument, or existing mutex; accepted launch is WPF wizard.'),
    ('action_exit', 'action', 0x219f, ['_createdNew', 'ReleaseMutex', 'WaitHandle::Dispose'], 'ActionTool releases owned mutex on WPF exit.'),
    ('action_input', 'action', 0x3940, ['CryptoFileUtil::Decrypt', 'XMLUtility::DeserializeXml', 'IsValidSendData', 'set_IsFileOpenFaildVisible'], 'Selected encrypted command file decrypts to ECUSendData XML; invalid XML/commands clears SendData and displays failure, cancelled file dialog leaves state unchanged.'),
    ('action_run', 'action', 0x333c, ['CancellationTokenSource::.ctor', 'get_SendData', 'get_VIN', 'ReadVINString', 'Send', 'Receive', 'CompelteAction'], 'Worker checks VIN when requested and sends validated command list through local communicator; finally collects received frames and invokes completion action even on cancellation/error.'),
    ('action_cancel', 'action', 0x314e, ['get_IsCancellationRequested', 'CancellationTokenSource::Cancel'], 'Cancel requests cooperative cancellation once; no uploaded-server cancellation protocol.'),
    ('action_output', 'action', 0x31e0, ['set_Error', 'XMLUtility::SerializeXml', 'get_ResultFilePath', 'CryptoFileUtil::Encrypt', 'pop'], 'Result/error serializes ECUResultData XML and encrypts to output; encryption return boolean is popped and exceptions swallowed, then next-page returns true.'),
    ('action_filename', 'action', 0x3b40, ['yyyyMMddHHmmss', '.rlog', 'File::Exists'], 'Default result beside input: inputstem_timestamp.rlog, collision suffix (n); user can override output. This is a local encrypted action log, not DataSync queue format.'),
    ('action_envelope', 'common', 0x3184, ['set_Mode', 'set_Padding', 'GenerateIV', 'BitConverter::GetBytes', 'Stream::Write', 'CryptoStream::.ctor'], 'Envelope: native-endian Int16 wrapped-key length (little-endian on target Windows), RSA-wrapped random AES key, AES IV, AES-CBC PKCS7 ciphertext; output false on caught exception.'),
    ('action_hybrid', 'common', 0x32c8, ['GetPublicKey', 'CreateRandomByte', 'EncryptFile'], 'Action result uses generated 16-byte random AES key encrypted by RSA public key, never an account credential.'),
    ('command_schema_init', 'common', 0x2647, ['1.0.0', '<VIN>', '<Commands>'], 'ECUSendData defaults Version to1.0.0 and initializes VIN/Commands collections.'),
    ('result_schema_init', 'common', 0x2407, ['1.0.0', '<VIN>', '<Data>'], 'ECUResultData defaults Version to1.0.0 and initializes VIN/Data collections.'),
    ('json_serialize', 'sync', 0x36e4, ['set_NullValueHandling', 'SerializeObject'], 'Newtonsoft JSON serialization is indented and omits null values; wire property names are explicit metadata annotations.'),
    ('action_transport', 'action', 0x3dbc, ['IsProhibitionFunctional', 'IsProhibitionSID', 'ldc.i4.0', 'DiagCommunication::Command', 'AddMessage'], 'ECUCommunicator.Send converts XML command to message, silently returns success0 for prohibited functional/SID requests without transport call; otherwise passes device/message to J2534 Command and records request/result frames.'),
    ('action_functional_filter', 'common', 0x3968, ['0x720', '0x740', '0x760', '0xfe'], 'Prohibited functional identifiers:0x720, or0x740/0x760 with N_TA0xFE.'),
    ('action_sid_filter', 'common', 0x39dd, ['0x27', 'bne.un.s'], 'SID0x27 is prohibited by ActionTool message inspection.'),
    ('action_error_class', 'action', 0x3623, ['ldc.i4.1', 'ldc.i4.5', 'ceq'], 'Communication results1..5 classify as cancellation errors; other values do not through this classifier.'),
    ('action_error_map', 'action', 0x363c, ['switch', '0x100', '0x900', 'ldc.i4.8'], 'Communication results0..5 map to result-error0,3,4,5,6,7; remaining listed/unknown statuses map to8.'),
]

# Keep complete instruction streams for queue ordering, including compiler closures.
# RVAs are authenticated by COMPONENTS; no business-logic transcription is executed.
QUEUE_METHODS = {
    'queue_model': 0x3f98, 'queue_configure': 0x3f40,
    'queue_database_init': 0x2f90, 'queue_controller_init': 0x2a44,
    'queue_migration_sql': 0x312f, 'queue_user_version_get': 0x4b08,
    'queue_user_version_set': 0x4b15, 'queue_sql_execute': 0x4b74,
    'queue_migrate': 0x6104, 'queue_move': 0x5f18,
    'queue_insert': 0x5f74, 'queue_original_hash': 0x6030,
    'queue_compress': 0x7c98, 'queue_gzip': 0x4448,
    'queue_zstd': 0x4bcc, 'queue_compression_status': 0x70cd,
    'queue_gzip_path': 0x44c0, 'queue_zstd_path': 0x4cb8,
    'queue_validate_steps': 0x705c, 'queue_validate': 0x79d0,
    'queue_validated_commit': 0x7610, 'queue_retry_commit': 0x7710,
    'queue_operate': 0x6d60, 'queue_receipt': 0x71b8,
    'queue_receipt_insert': 0x732c, 'queue_receipt_delete': 0x73b0,
    'queue_receipt_select': 0x721c, 'queue_receipt_match': 0x72a0,
    'queue_receipt_order': 0x9f13, 'queue_destination_order': 0x9f01,
    'queue_receipt_predicate': 0xa15c, 'queue_receipt_trim': 0x8330,
    'queue_duplicate': 0x7c24, 'queue_tampering': 0x7b40,
    'queue_md5_file': 0x35cc, 'queue_md5_text': 0x3668,
    'queue_ack_cleanup': 0x7800, 'queue_error_cleanup': 0x7838,
    'queue_delete_files': 0x78ed, 'queue_evacuate': 0x7918,
    'queue_delete_row': 0x75cc, 'queue_backlog': 0x6a70,
    'queue_extract': 0x6c84, 'queue_missing': 0xa00c,
    'queue_remove_missing': 0x9f43, 'queue_due_or_orphan': 0x9f54,
    'queue_original_missing_predicate': 0xa06b,
    'queue_original_match_predicate': 0xa088,
    'queue_compressed_match_predicate': 0xa0a5,
    'queue_live': 0x821c, 'queue_start': 0x66dc,
    'queue_disposal_lock': 0x55b8, 'queue_disposal': 0x9694,
    'queue_wait': 0x32b4, 'queue_wait_cancel': 0x3310,
    'queue_release': 0x84f2, 'queue_heartbeat': 0x2ee8,
    'queue_task_initialize': 0x516a,
    'queue_history_insert': 0x5c38, 'queue_history_update': 0x5cc0,
}

EF_RECEIPT_METHODS = {
    'ef_dbset_add': 0x4c745, 'ef_context_add': 0x3f59,
    'ef_context_entry_state': 0x4050, 'ef_context_set_state': 0x3ece,
    'ef_graph_attach': 0x57109, 'ef_graph_paint': 0x5716c,
    'ef_entry_set_state': 0x57c60, 'ef_entry_track_state': 0x57dd4,
    'ef_start_tracking': 0x62778, 'ef_identity_map_lookup': 0x625d4,
    'ef_identity_key_type': 0x57bc5, 'ef_identity_factory': 0x57b68,
    'ef_nullable_factory': 0x7759d, 'ef_is_nullable_type': 0x25f8,
    'ef_key_factory': 0x59f30, 'ef_composite_factory': 0x5a030,
    'ef_composite_current': 0x56741, 'ef_composite_entry': 0x567f0,
    'ef_composite_values': 0x566c7, 'ef_composite_null_predicate': 0x76d57,
    'ef_nullable_add': 0x5b5ec, 'ef_find_null_property': 0x5676c,
}


def _id(value: str) -> str:
    return f'{DOMAIN}.{value}'


def _operand(pe: Any, value: Any, base: int, opcode: str) -> str:
    if isinstance(value, Token):
        row = resolve_token(pe, value)
        if isinstance(row, dnfile.mdtable.MethodSpecRow):
            row = row.Method.row
        if isinstance(row, dnfile.mdtable.MemberRefRow):
            owner = row.Class.row
            if isinstance(owner, dnfile.mdtable.TypeSpecRow):
                return f'TypeSpec({owner.Signature.value.hex()})::{row.Name}'
        if isinstance(row, dnfile.mdtable.TypeSpecRow):
            return f'TypeSpec({row.Signature.value.hex()})'
        return format_operand(pe, row)
    if opcode == 'switch':
        return ','.join(f'IL_{target-base:04x}' for target in value)
    if isinstance(value, int) and opcode.startswith(('br', 'beq', 'bne', 'bgt', 'blt', 'bge', 'ble', 'leave')):
        return f'IL_{value-base:04x}'
    return format_operand(pe, value)


def _redacted_policy(data: bytes) -> list[str]:
    """Whitelist nonsecret policy keys; never emit arbitrary YAML scalar values."""
    scalars = {'id', 'unitid', 'path', 'priority', 'compressionmethod', 'compressionlevel', 'maxattempts', 'dovalidation', 'maxbytesize', 'hashvaluequantitylimit', 'tokenpath', 'disposaltype', 'expirationtimeindays', 'expirationtimeinhours', 'expirationtimeinminutes', 'expirationtimeinseconds', 'allowcleaning', 'delayseconds', 'httpstatuscode', 'disposaltask', 'transmissiontask', 'loggingtask', 'cleaningtask', 'isminoutputmode', 'perioddays', 'max', 'min'}
    containers = {'applicationsetting', 'destinations', 'monitoringrule', 'transmissionrule', 'validationrule', 'disposalrule', 'extensions', 'fileextensionvalidation', 'originalsizevalidation', 'doubletransmissionvalidation', 'jsonheadervalidation', 'compressedsizevalidation', 'validationerror', 'transmissionerror', 'expiration', 'evacuate', 'common', 'initialization', 'executioninterval', 'transmission', 'retry', 'timeouterror', 'communicationerror', 'unexpectederror', 'statuserrors', 'workdirectory', 'logging', 'cleaning'}
    result = []
    previous = ''
    for line in data.decode('utf-8-sig').splitlines():
        match = re.match(r'^\s*(?:-\s*)?([A-Za-z_-]+):\s*(.*?)\s*$', line)
        if match:
            key, value = match.groups()
            previous = key.replace('_', '').replace('-', '').lower()
            if previous in scalars or (not value and previous in containers):
                result.append(line.rstrip())
        elif previous == 'extensions' and re.fullmatch(r'\s*-\s+[.A-Za-z0-9*_-]+\s*', line):
            result.append(line.rstrip())
    return result


def _queue_contract() -> dict[str, Any]:
    """Source-order contract; prefixes assume completed calls survived the interruption."""
    def item(prefix: str, remaining: str, recovery: str, *refs: str) -> dict[str, Any]:
        return {'prefix': prefix, 'remaining_state': remaining,
                'restart_or_next_scan': recovery, 'evidence': [_id(r) for r in refs]}

    return {
        'identity': {
            'queue_key': 'process_info.id INTEGER PRIMARY KEY AUTOINCREMENT; original is work_directory/decimal(id). Filename, destination, content and unit_id are not queue uniqueness constraints.',
            'migration_input': 'FileInfo plus configured destination from initial scan/Created event. No persistent discovery record or enqueue deduplication; a repeated stale discovery can insert a row before MoveTo fails.',
            'receipt_key': '(original_hash_value,destination), both NOT NULL, primary key; no unit_id, original filename, compression format or request identifier in duplicate identity.',
            'null_receipt_failure': 'Bundled EF Core 2.2.4.0 rejects NULL OriginalHashValue during DbSet.Add tracking, before SaveChanges/SQLite: composite key factory returns null when any component is null; NullableKeyIdentityMap.Add throws InvalidOperationException using InvalidKeyValue. SQLite NOT NULL is an additional independent constraint, not the first application failure.',
            'null_receipt_evidence': [_id(x) for x in ('queue_model', 'queue_receipt_insert', 'ef_dbset_add', 'ef_context_add', 'ef_context_entry_state', 'ef_context_set_state', 'ef_graph_attach', 'ef_graph_paint', 'ef_entry_set_state', 'ef_entry_track_state', 'ef_start_tracking', 'ef_identity_map_lookup', 'ef_identity_key_type', 'ef_identity_factory', 'ef_nullable_factory', 'ef_is_nullable_type', 'ef_key_factory', 'ef_composite_factory', 'ef_composite_current', 'ef_composite_entry', 'ef_nullable_add', 'ef_find_null_property')],
            'hash_input': 'lowercase hex MD5(UTF8(lowercase hex MD5(original bytes) + LOCAL salt)); salts are not exported. Compressed integrity uses the same construction over compressed bytes; receipt uses original_hash_value.',
            'receipt_window': 'SelectHashInfo orders UpdatedAt ascending then filters destination. AddHashValue deletes the oldest only when count == limit, commits that deletion separately, then inserts receipt separately. Startup trims while count > limit. Equal UpdatedAt has no secondary ordering. Captured policy limit=100 per destination.',
            'duplicate_path': 'Duplicate validation reads persisted original_hash_value, not newly computed content hash. A receipt hit enters validation-error disposal, without another upload. Receipt tracking is conditional on DoubleTransmissionValidation.DoValidation.',
            'derivative_identity': 'Decimal-id originals have no extension: gzip appends .gz, Zstandard appends .zst. Recorded compressed_file_path owns a derivative only by exact full-path string; orphan matching does not infer ownership from an id prefix.',
            'evidence': [_id(x) for x in ('database_schema', 'queue_migrate', 'queue_receipt', 'queue_receipt_trim', 'queue_receipt_order', 'queue_receipt_predicate', 'queue_duplicate', 'queue_md5_file', 'queue_md5_text', 'queue_validate', 'queue_gzip_path', 'queue_zstd_path', 'queue_compressed_match_predicate')],
        },
        'transactions': {
            'unit': 'Each helper creates/disposes its own DatabaseContext and calls SaveChanges. Insert metadata, original hash, validation/compressed metadata, retry, receipt eviction, receipt insertion and process deletion are separate calls/contexts. No enclosing explicit application transaction joins them to files or HTTP.',
            'files': 'MoveTo/Create/Delete and compression are outside SQLite SaveChanges. Gzip opens original Open/Read/FileShare.Read and destination FileMode.Create, CopyTo then disposes gzip/destination/original streams. Zstd also creates/truncates destination before compression and disposes streams. Neither uses temp+rename or explicit Flush(true).',
            'schema_upgrade': 'Embedded USER_VERSION_1 = ALTER TABLE process_info ADD COLUMN retry_schedule datetimeoffset. InitializeDatabase calls EnsureCreated first. Existing lower user_version exits without DoMigration; equal accepted, greater throws. New file gets latest version1 via separate PRAGMA. DoMigration closure executes SQL then version PRAGMA separately; InitializeDatabase never invokes it.',
            'durability_limit': 'Completed-call ordering only. EF provider commit/rollback, filesystem rename semantics, disk caches, torn writes and power-loss durability are external. Captured SQLite PRAGMAs describe the opened snapshot, not service connection settings.',
            'evidence': [_id(x) for x in ('queue_insert', 'queue_original_hash', 'queue_validated_commit', 'queue_retry_commit', 'queue_receipt_delete', 'queue_receipt_insert', 'queue_delete_row', 'queue_gzip', 'queue_zstd', 'queue_database_init', 'queue_migration_sql', 'embedded_migration_sql')],
        },
        'persisted_vs_memory': {
            'persisted': ['id/destination/unit_id/original name+extension', 'original/compressed hashes and compressed path', 'is_validated', 'is_retryable', 'retry_schedule', 'request_attempts', 'audit timestamps', 'bounded receipt window', 'logging_history System row'],
            'memory_only': ['migration/transmission BlockingCollection queues', 'shared cancellation token', 'StopExecute', 'MSK cached string/status', 'taskStatus', 'timer/connectivity registrations', 'active request and its returned result'],
            'restart': 'Controller constructs fresh queues/token/semaphore. Transmission backlog reconciliation runs before monitoring initial discovery. Original hash is set only by migration worker; backlog does not reconstruct a missing hash. Retryable rows bypass age disposal indefinitely; retry_schedule remains the due gate after restart. Live queued items reselect id under semaphore and skip deleted rows, but do not recheck retry_schedule before OperateFile.',
            'retry_limit_prefix': 'Retry schedule/is_retryable/attempt count are saved before testing MaxAttempts and terminal cleanup. If interruption follows that save at the limit, restart still selects the due row and can issue another request: there is no pre-request attempt-limit gate. HTTP401 does not increment attempts.',
            'live_backlog_overlap': 'A live queue hint can wait while backlog processes the same row first. If backlog saves a future retry_schedule, the later live worker reselects that row but ignores the due time and can send immediately. Semaphore prevents simultaneous normal requests, not this sequential retry-schedule bypass.',
            'evidence': [_id(x) for x in ('queue_controller_init', 'queue_start', 'queue_live', 'queue_retry_commit', 'queue_operate', 'queue_disposal', 'queue_due_or_orphan')],
        },
        'coordination': {
            'normal': 'Controller passes one SemaphoreSlimWrapper(1,1) to migration, transmission and disposal. Migration holds it across insert/move/hash/enqueue; live transmission across fresh-row selection and all OperateFile work; backlog across reconciliation and every destination/request; disposal across the entire selected batch. Thus slow synchronous HTTP blocks all these normal holders.',
            'triggers': 'Timer and connectivity callback and manual ds_send call the same blocking OperateAccumulatedFiles. Timer Stop/Start reduces its own overlap, not other callbacks. Backlog waits without CancellationToken; cancellation checked per eligible item after reconciliation. Watcher discovery only enqueues, without semaphore, and initial scan precedes enabling Created notifications. Heartbeat checks taskStatus without queue recovery transaction.',
            'exceptional_wait': 'Both ReleasableWait overloads swallow OperationCanceledException/ObjectDisposedException and return a wrapper with isReleasable=false. Callers do not test acquisition and continue into their critical section. Mutual exclusion therefore is not guaranteed after cancelled/disposed Wait; Dispose only releases when isReleasable=true.',
            'heartbeat_limit': 'AbstractBaseTask.Initialize only calls StartProcess and logs. Transmission.StartProcess stores taskStatus=1 before IPC registration/backlog/timer/connectivity/worker setup; its catch disposes rest/network clients without resetting status. A setup failure after that store is not repaired by the heartbeat status==0 test.',
            'limits': 'No file readiness/close handshake from Created notification, no atomic initial-scan/watch handoff, no cross-process filesystem/DB lock in this queue protocol. Actual callback scheduling, writer readiness and OS cross-volume MoveTo behavior remain external. StopExecute/MSK reset and unsent-count queries are not protected by the queue semaphore in AppCommunicationCallback.',
            'evidence': [_id(x) for x in ('queue_controller_init', 'queue_migrate', 'queue_live', 'queue_backlog', 'queue_disposal_lock', 'queue_wait', 'queue_wait_cancel', 'queue_release', 'queue_heartbeat', 'watch_start', 'watch_enqueue', 'ipc_messages')],
            'order_evidence': [_id(x) for x in ('queue_destination_order', 'queue_task_initialize', 'queue_start', 'queue_heartbeat')],
        },
        'crash_prefix_matrix': [
            item('EnsureCreated succeeded for a new database, before version PRAGMA', 'Schema may exist with default user_version0.', 'Next startup sees an existing lower-version file and exits InitializeDatabase without migration or version repair. Existing lower-version schema is likewise not upgraded by this method.', 'queue_database_init', 'queue_user_version_set', 'embedded_migration_sql'),
            item('Discovered/enqueued only', 'Source remains in watch root; in-memory work can vanish.', 'Next monitoring initial scan rediscovers source. Scan-to-enable gap can miss a newly created file until a later monitor restart.', 'watch_start', 'watch_enqueue'),
            item('InsertProcessInfo SaveChanges, before successful MoveTo', 'Row without work/id, source may remain; move failure leaves row.', 'Backlog deletes missing-original row; monitoring rescans source and allocates another id. A partial external move outcome is outside managed ordering.', 'queue_insert', 'queue_move', 'queue_missing'),
            item('MoveTo succeeded, before original-hash SaveChanges', 'work/id + row with NULL original_hash_value.', 'Backlog accepts original by decimal name, does not rehash row. Fresh validation has no tampering check; duplicate query for NULL misses receipts. After successful request, EF Core NullableKeyIdentityMap.Add rejects the null receipt primary-key component with InvalidOperationException during DbSet.Add, before SaveChanges or SQL; cleanup is skipped. Subsequent validated-original tampering check compares computed hash to NULL and disposes. These are source-derived branches, not an observed service outcome.', 'queue_move', 'queue_original_hash', 'queue_validate_steps', 'queue_validate', 'queue_receipt_insert', 'queue_model', 'ef_nullable_add', 'ef_composite_entry', 'queue_tampering', 'queue_operate'),
            item('Original hash saved, before/during timed TryAdd', 'Durable original+row, queue hint absent; TryAdd boolean discarded.', 'Startup/timer/connectivity/manual backlog recovers by work/id, independent of lost queue hint.', 'queue_migrate', 'queue_due_or_orphan'),
            item('Compression created/truncated output, before validation metadata SaveChanges', 'Original+row and unrecorded complete/partial suffix file.', 'Reconciliation deletes unreferenced suffix; if operated before orphan pass, FileMode.Create truncates it and compresses anew. No persisted compressed path means no reuse.', 'queue_gzip', 'queue_zstd', 'queue_compression_status', 'queue_due_or_orphan', 'queue_validated_commit'),
            item('Validation/compressed metadata SaveChanges', 'is_validated flag plus compressed path/hash (nonzero compression); no upload outcome.', 'Reuse recorded existing compression, validate original duplicate+tampering and compressed tampering; missing compressed file recompresses. Missing original deletes row then unreferenced derivative.', 'queue_validated_commit', 'queue_compression_status', 'queue_validate_steps', 'queue_missing', 'queue_due_or_orphan'),
            item('Request issued or server accepted, before client receipt SaveChanges', 'Files+row remain, remote outcome may be ambiguous; retry metadata may be unchanged.', 'Due backlog can resend: request metadata has no persisted idempotency token, and remote deduplication is unspecified.', 'queue_operate', 'request_body', 'queue_receipt_insert'),
            item('Oldest receipt DeleteHashInfo SaveChanges, before new receipt insertion', 'Window temporarily shortened, new acknowledged digest absent; payload retained.', 'Oldest forgotten content can pass duplicate validation; current work can resend until a receipt is committed.', 'queue_receipt', 'queue_receipt_delete', 'queue_receipt_insert'),
            item('New receipt SaveChanges, before any ack file cleanup', 'Receipt+original+optional compressed+row.', 'Next duplicate check invokes validation-error policy rather than HTTP; already-acknowledged original can be evacuated. Receipt primary-key failure also aborts cleanup, because insertion is not upsert.', 'queue_operate', 'queue_receipt_insert', 'queue_duplicate', 'queue_error_cleanup'),
            item('Ack cleanup deletes compressed, before original delete', 'Receipt+original+row; compressed metadata points to missing file.', 'Duplicate validation precedes compression and disposes the original; disabled duplicate tracking permits recompress/resend.', 'queue_delete_files', 'queue_operate'),
            item('Ack cleanup deletes original, before process Delete SaveChanges', 'Receipt+row, no original.', 'Backlog deletes row without upload. If row commit fails, next scan repeats reconciliation.', 'queue_ack_cleanup', 'queue_delete_files', 'queue_missing'),
            item('Retry SaveChanges, before terminal-limit disposal', 'Persisted is_retryable=true/schedule/attempt count, original remains.', 'Age disposal skips row; when due, request can exceed configured maximum because limit checked only after another retry response. Cancel/restart does not clear schedule.', 'queue_retry_commit', 'queue_operate', 'queue_disposal'),
            item('Live hint remains while backlog commits retry state for same row', 'Future retry_schedule persists, stale in-memory hint still holds row id.', 'Live worker reselects id but bypasses schedule check and may send again immediately; process restart loses hint and returns to due-time backlog gating.', 'queue_live', 'queue_backlog', 'queue_retry_commit'),
            item('Immediate error evacuation creates id directory/deletes compressed/deletes preexisting target, before original MoveTo', 'Original+row remain; compressed and prior evacuated target may be gone.', 'Reprocess row; replacement has a delete-before-move loss window. Error deletion instead deletes compressed then original before row removal.', 'queue_evacuate', 'queue_delete_files', 'queue_error_cleanup'),
            item('Immediate error original moved/deleted, before row removal', 'Evacuated original or no original; stale row.', 'Missing-original reconciliation removes row, deletes leftover unreferenced work files; evacuation remains for cleaning.', 'queue_evacuate', 'queue_error_cleanup', 'queue_missing', 'queue_due_or_orphan'),
            item('Age disposal original moved/deleted, before compressed delete', 'Unlike immediate error path: original handled FIRST, compressed+row remain.', 'Backlog removes row then derivative becomes orphan and is deleted. Direct disposal retry after expiry also deletes compression/row when original missing.', 'queue_disposal', 'queue_missing', 'queue_due_or_orphan'),
            item('Reconciliation missing-original DeleteProcessInfo SaveChanges, before in-memory list removal/orphan sweep', 'Unreferenced derivative can remain; deleted row absent from database.', 'Next scan deletes work file if no current row owns exact compressed FullName; exception aborts extraction and returns partial eligible list.', 'queue_missing', 'queue_remove_missing', 'queue_due_or_orphan', 'queue_extract'),
            item('Optional logging work-root MoveTo, before logging_history update/source deletion', 'Watched export exists, old history/source logs can remain.', 'Repeat logging can create duplicate work; optional DSY-D01 absent in deployed policy. logging_history is not a queue receipt.', 'log_package', 'queue_history_update', 'logging_selector'),
        ],
        'external_limits': [
            'Crash prefixes are source-derived reachable states assuming preceding operations completed; they are not crash-injection observations or guarantees of power-loss durability.',
            'SQLite permits varchar length overflow and arbitrary boolean/integer values absent CHECK constraints; recorded type names are affinity declarations. No foreign keys, extra unique constraints or queue content-dedup index exist in captured schema.',
            'Remote acceptance, exactly-once semantics and remote hash/idempotency policy require service implementation or authorized fixtures. Client receipt is a local finite history, not remote transaction evidence.',
            'Actual-IL smoke uses original decoded method instructions with inert logger/config and SQLite/filesystem hooks. Hooks do not prove EF provider behavior or Windows event scheduling.',
        ],
    }


def build(root: Path = DEFAULT_ROOT, recovered_root: Path = DEFAULT_RECOVERED) -> dict[str, Any]:
    root, recovered_root = root.resolve(), recovered_root.resolve()
    diagnostics = root / 'Toyota Diagnostics'
    sources: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []
    assemblies: dict[str, Any] = {}
    methods: dict[str, dict[int, tuple[str, Any]]] = {}

    def source(key: str, path: Path, representation: str, expected: str = '') -> str:
        digest = sha256_file(path)
        if expected and digest != expected:
            raise ValueError(f'source byte drift: {key}')
        sid = _id(key)
        sources.append({'id': sid, 'path': path.relative_to(REPO_ROOT).as_posix(), 'sha256': digest, 'size': path.stat().st_size, 'representation': representation})
        return sid

    manifest_path = recovered_root / 'manifest.json'
    source('recovery_manifest', manifest_path, 'CP recovery manifest linking original stubs/sidecars to recovered representations')
    recovery = {entry['relative_path']: entry for entry in json.loads(manifest_path.read_text())['entries']}
    for key, (rel, decoded_hash, stub_hash, sidecar_hash) in COMPONENTS.items():
        path = (diagnostics if key == 'common' else recovered_root) / rel
        source(key, path, 'installed managed plaintext' if key == 'common' else 'CP recovered managed PE', decoded_hash)
        if key != 'common':
            source(key + '_stub', diagnostics / rel, 'installed CP protected stub', stub_hash)
            source(key + '_sidecar', Path(str(diagnostics / rel) + '._'), 'installed CP encrypted body', sidecar_hash)
            entry = recovery[rel]
            if (entry['output_sha256'], entry['stub_sha256'], entry['sidecar_sha256']) != (decoded_hash, stub_hash, sidecar_hash):
                raise ValueError(f'recovery provenance drift: {rel}')
        proof = _recovery_proof(path)
        assemblies[key] = pe = _open(path)
        methods[key] = {int(m.row.Rva): (type_name(td) + '::' + str(m.row.Name), m.row) for td in pe.net.mdtables.TypeDef for m in td.MethodList if m.row.Rva}
        evidence.append({'id': _id(key + '_materialized'), 'source': _id(key), 'kind': 'managed-body-materialization', 'locator': 'MethodDef table', **proof})

    for eid, key, rva, required, finding in METHODS:
        name, row = methods[key][rva]
        pe = assemblies[key]
        body = _body(pe, row)
        base = body.instructions[0].offset
        lines = [{'offset': ins.offset-base, 'opcode': str(ins.opcode), 'operand': _operand(pe, ins.operand, base, str(ins.opcode))} for ins in body.instructions]
        text = [f"{line['opcode']} {line['operand']}" for line in lines]
        selected: set[int] = set()
        for needle in required:
            matches = [i for i, line in enumerate(text) if needle in line]
            if not matches:
                raise ValueError(f'IL anchor drift: {name} {rva:#x}: {needle}')
            # At most one matching site per required anchor, with neighboring dataflow.
            for i in matches[:1]:
                selected.update(range(max(0, i-1), min(len(lines), i+2)))
        signatures = []
        if eid in ('http_client', 'http_response', 'action_envelope'):
            for ins, line in zip(body.instructions, lines):
                if isinstance(ins.operand, Token) and str(ins.opcode) in ('newobj', 'call', 'callvirt'):
                    target = resolve_token(pe, ins.operand)
                    if isinstance(target, dnfile.mdtable.MethodSpecRow):
                        target = target.Method.row
                    signature = getattr(target, 'Signature', None)
                    if signature:
                        signatures.append({**line, 'signature_hex': signature.value.hex(), 'token': hex(ins.operand.value)})
            if eid == 'http_client':
                constructors = {s['offset']: s['signature_hex'] for s in signatures if s['operand'] == 'System.Net.Http.HttpClient::.ctor'}
                if constructors != {0x65: '200001', 0xed: '200101128479'}:
                    raise ValueError('HttpClient constructor overload drift')
        # Retain branch instructions and their targets, not merely calls/strings.
        selected.update(i for i, ins in enumerate(body.instructions) if str(ins.opcode) == 'switch')
        branches = [line for line in lines if line['opcode'].startswith(('br', 'beq', 'bne', 'bgt', 'blt', 'bge', 'ble', 'leave')) or line['opcode'] == 'switch']
        evidence.append({'id': _id(eid), 'source': _id(key), 'kind': 'managed-il', 'locator': name, **_method_pin(row, body), 'il_offset_origin': 'first instruction = IL_0000', 'anchors': [lines[i] for i in sorted(selected)], 'branches': branches, 'exception_regions': [{'kind': h.exception_type, 'try': [h.try_start, h.try_end], 'handler': [h.handler_start, h.handler_end]} for h in body.exception_handlers], 'finding': finding})
        if signatures:
            evidence[-1]['call_signatures'] = signatures
        if eid == 'http_response':
            post_calls = [item for item in signatures if item['operand'] == 'System.Net.Http.HttpClient::PostAsync']
            if len(post_calls) != 1 or not post_calls[0]['signature_hex'].startswith('2002'):
                raise ValueError('PostAsync overload/cancellation contract drift')
            evidence[-1]['cancellation_contract'] = 'Two-argument PostAsync(uri,content) carries no CancellationToken. Controller cancellation stops queue/backlog iteration, not this in-flight request; request timeout is30000ms, controller abort wait15000ms.'

    ef_path = diagnostics / 'GTSPlus DataSync/Microsoft.EntityFrameworkCore.dll'
    ef_source = source('ef_core', ef_path, 'installed managed EF Core dependency',
                       '290e1c3d36f8c5ea61b627206a07bcc109f16852cd57af85e9e66199a3311e29')
    ef = _open(ef_path)
    version = ef.net.mdtables.Assembly.rows[0]
    if (version.MajorVersion, version.MinorVersion, version.BuildNumber, version.RevisionNumber) != (2, 2, 4, 0):
        raise ValueError('bundled EF Core version drift')
    assemblies['ef_core'] = ef
    methods['ef_core'] = {int(m.row.Rva): (type_name(td) + '::' + str(m.row.Name), m.row)
                          for td in ef.net.mdtables.TypeDef for m in td.MethodList if m.row.Rva}
    for eid, rva in EF_RECEIPT_METHODS.items():
        name, row = methods['ef_core'][rva]
        body = _body(ef, row)
        base = body.instructions[0].offset
        evidence.append({'id': _id(eid), 'source': ef_source, 'kind': 'managed-il-complete',
                         'locator': name, **_method_pin(row, body), 'assembly_version': '2.2.4.0',
                         'il_offset_origin': 'first instruction = IL_0000',
                         'instructions': [{'offset': ins.offset - base, 'opcode': str(ins.opcode),
                                           'operand': _operand(ef, ins.operand, base, str(ins.opcode))}
                                          for ins in body.instructions],
                         'exception_regions': [{'kind': h.exception_type,
                                                'try': [h.try_start, h.try_end],
                                                'handler': [h.handler_start, h.handler_end]}
                                               for h in body.exception_handlers]})

    # Complete streams make file/SQL prefixes auditable, not selected-call summaries.
    pe = assemblies['sync']
    for eid, rva in QUEUE_METHODS.items():
        name, row = methods['sync'][rva]
        body = _body(pe, row)
        base = body.instructions[0].offset
        instructions = []
        for ins in body.instructions:
            record = {'offset': ins.offset - base, 'opcode': str(ins.opcode),
                      'operand': _operand(pe, ins.operand, base, str(ins.opcode))}
            if isinstance(ins.operand, Token):
                record['token'] = hex(ins.operand.value)
                target = resolve_token(pe, ins.operand)
                if isinstance(target, dnfile.mdtable.MethodSpecRow):
                    target = target.Method.row
                signature = getattr(target, 'Signature', None)
                if signature:
                    record['signature_hex'] = signature.value.hex()
            instructions.append(record)
        evidence.append({'id': _id(eid), 'source': _id('sync'), 'kind': 'managed-il-complete',
                         'locator': name, **_method_pin(row, body),
                         'il_offset_origin': 'first instruction = IL_0000',
                         'instructions': instructions,
                         'exception_regions': [{'kind': h.exception_type,
                                                'try': [h.try_start, h.try_end],
                                                'handler': [h.handler_start, h.handler_end]}
                                               for h in body.exception_handlers]})
    migration_resources = [r for r in pe.net.resources
                           if str(r.name) == 'GTSPlusDataSync.Resource.MigrationSql.resources']
    migration_sql = [{'name': e.name, 'sql': e.value} for e in migration_resources[0].data.entries]
    if migration_sql != [{'name': 'USER_VERSION_1',
                          'sql': 'ALTER TABLE process_info ADD COLUMN retry_schedule datetimeoffset'}]:
        raise ValueError('embedded migration SQL drift')
    evidence.append({'id': _id('embedded_migration_sql'), 'source': _id('sync'),
                     'kind': 'managed-resource-sql',
                     'locator': 'ManifestResource GTSPlusDataSync.Resource.MigrationSql.resources',
                     'definitions': migration_sql})
    model_properties = []
    for mapping in pe.net.mdtables.PropertyMap:
        owner = type_name(mapping.Parent.row)
        if not owner.startswith('GTSPlusDataSync.Common.Database.Model.'):
            continue
        for prop in mapping.PropertyList:
            annotations = []
            for attr in pe.net.mdtables.CustomAttribute:
                if attr.Parent.row is not prop.row:
                    continue
                constructor = attr.Type.row
                annotation_type = type_name(constructor.Class.row)
                if annotation_type.startswith('System.ComponentModel.DataAnnotations.'):
                    entry = {'type': annotation_type, 'blob_hex': attr.Value.value.hex()}
                    if annotation_type.endswith('.ColumnAttribute'):
                        blob = attr.Value.value
                        if blob[:2] != b'\x01\x00' or blob[2] >= 0x80:
                            raise ValueError('model ColumnAttribute encoding drift')
                        entry['column_name'] = blob[3:3 + blob[2]].decode('utf-8')
                    annotations.append(entry)
            model_properties.append({'owner': owner, 'property': str(prop.row.Name),
                                     'signature_hex': prop.row.Type.value.hex(),
                                     'annotations': annotations})
    evidence.append({'id': _id('queue_model_attributes'), 'source': _id('sync'),
                     'kind': 'managed-model-metadata',
                     'locator': 'Database.Model PropertyMap/CustomAttribute tables',
                     'properties': model_properties,
                     'finding': 'Source Column(TypeName,Order) and Required attributes; fluent keys/defaults are pinned in queue_model and actual SQL in database_schema.'})

    schema_types = {'ECUSendData', 'ECUSendObject', 'ECUResultData', 'ECUResultObject', 'ECUResponseObject', 'VINData', 'RequestBodyEntity', 'ResponseBodyEntity', 'CommonResult'}
    for key in ('common', 'sync'):
        pe = assemblies[key]
        for mapping in pe.net.mdtables.PropertyMap:
            name = type_name(mapping.Parent.row)
            if name.rsplit('.', 1)[-1] not in schema_types:
                continue
            properties = []
            for prop in mapping.PropertyList:
                attributes = []
                for attr in pe.net.mdtables.CustomAttribute:
                    if attr.Parent.row is not prop.row:
                        continue
                    constructor = attr.Type.row
                    owner = getattr(constructor, 'Class', None)
                    attribute_type = type_name(owner.row) if owner else str(constructor.Name)
                    if attribute_type.startswith(('System.Xml.Serialization.', 'Newtonsoft.Json.JsonProperty')):
                        blob = attr.Value.value
                        if blob[:2] != b'\x01\x00' or blob[2] >= 0x80:
                            raise ValueError('schema attribute encoding drift')
                        attributes.append({'type': attribute_type, 'wire_name': blob[3:3+blob[2]].decode('utf-8'), 'blob_hex': blob.hex()})
                properties.append({'clr_name': str(prop.row.Name), 'wire_annotations': attributes})
            evidence.append({'id': _id('schema_' + name.rsplit('.', 1)[-1]), 'source': _id(key), 'kind': 'managed-schema-metadata', 'locator': name + ' PropertyMap/CustomAttribute tables', 'properties': properties, 'finding': 'Exact XML/JSON wire member names from serialization attributes; associated serializers and constructor bodies are pinned separately.'})

    config_path = diagnostics / 'GTSPlus DataSync/GTSPlusDataSync.exe.config'
    config_id = source('config', config_path, 'installed XML application configuration')
    settings = {s.attrib['name']: s.findtext('value') for s in ET.parse(config_path).findall('.//setting')}
    expected = {'TimerEventInterval': '1000', 'ControllerHeartbeatInterval': '1000', 'RequestCountThreshold': '1', 'RequestIntervalAdditionValue': '2000', 'RequestConnectionTimeout': '30000', 'ControllerAbortTimeout': '15000', 'MigrationTaskTakeTimeout': '10000', 'MigrationTaskAddTimeout': '3000', 'ServiceName': 'GTS+ DataSync', 'DatabaseDirectryPath': 'GTSPlusDataSyncDb', 'DestinationApplicationName': 'GTS+ PF', 'SenderApplicationName': 'GTS+ DataSync'}
    if any(settings.get(k) != v for k, v in expected.items()):
        raise ValueError('service config contract drift')
    evidence.append({'id': _id('settings'), 'source': config_id, 'kind': 'xml-config', 'locator': 'applicationSettings/GTSPlusDataSync.Properties.Settings', 'values': settings, 'finding': '1-second service/heartbeat timer, 30-second HTTP timeout, one inner HTTP attempt, 15-second controller abort wait; outer retries persist in SQLite.'})
    source('encrypted_policy', diagnostics / 'GTSPlus DataSync/GTSPlusDataSync.yml', 'installed encrypted policy; no credential values exported')
    source('policy_pair', diagnostics / 'GTSPlus DataSync/DSP.pp', 'installed local configuration decryption pairing; contents omitted')
    cm_path = recovered_root / 'ContentServer/GtsPlus-CM.dll'
    source('crypto_cm', cm_path, 'recovered native configuration cryptography')
    source('crypto_cm_stub', diagnostics / 'ContentServer/GtsPlus-CM.dll', 'installed CP native stub')
    source('crypto_cm_sidecar', diagnostics / 'ContentServer/GtsPlus-CM.dll._', 'installed CP native encrypted body')
    plain_policy = decrypt_file(diagnostics / 'GTSPlus DataSync/GTSPlusDataSync.yml', diagnostics / 'GTSPlus DataSync/DSP.pp', cm_path, key_type=1)
    policy_lines = _redacted_policy(plain_policy)
    policy_text = '\n'.join(policy_lines)
    for anchor in ('GTS-C02', 'GTS-E02', 'GTS-M02', 'http-status-code: 401', 'http-status-code: 500', 'http-status-code: 503', 'delay-seconds: 86400', 'max-attempts:  5', 'max-byte-size:  20971520', 'max-byte-size:  15728640'):
        if anchor not in policy_text:
            raise ValueError(f'decoded nonsecret policy drift: {anchor}')
    evidence.append({'id': _id('deployment_policy'), 'source': _id('encrypted_policy'), 'kind': 'offline-decrypted-whitelist-policy', 'locator': 'GTSPlusDataSync.yml; native DoFileDecryption key_type1 with DSP.pp', 'related_sources': [_id('policy_pair'), _id('crypto_cm')], 'plaintext_sha256': hashlib.sha256(plain_policy).hexdigest(), 'redacted_yaml_lines': policy_lines, 'finding': 'GTS-C02(priority2) and GTS-M02(priority1), unit GTS+, watch public LOGS/BDC roots; GTS-E02(priority0), unit ErrorReport, watches DataSync/Logs. All use gzip2/level2/max5, extension validation, 20MiB original/15MiB compressed limits, duplicate window100, JSON header validation off, evacuation type2,14-day nonretryable expiration/cleaning. Retry401 waits86400s without attempt increment;500/503 and exception delays0. Backlog/disposal1800s, logging/cleaning3600s; logs package every7days. Account/endpoint values excluded.'})
    evidence[-1]['artifact_eligibility'] = {'GTS-C02': '.json in public LOGS/BDC/GTS-C02', 'GTS-M02': '.json in public LOGS/BDC/GTS-M02', 'GTS-E02': '.gtsr in public DataSync/Logs/GTS-E02', 'ActionTool': '.rlog is not an accepted configured upload extension; independent local result', 'DataSync_service_logs': 'DSY-D01 destination absent, so optional log packaging task disabled'}
    destination_ids = re.findall(r'^\s*-\s+id:\s*(\S+)', policy_text, re.MULTILINE)
    if destination_ids != ['GTS-C02', 'GTS-E02', 'GTS-M02'] or '- .json' not in policy_text or '- .gtsr' not in policy_text:
        raise ValueError('destination eligibility/deactivated logging policy drift')
    db_path = root / 'GTSPlusDataSyncDb/GTSPlusDataSync.db'
    db_id = source('captured_db', db_path, 'captured SQLite state, opened read-only')
    with sqlite3.connect(db_path.as_uri() + '?mode=ro', uri=True) as db:
        tables = []
        for name, sql in db.execute("SELECT name,sql FROM sqlite_master WHERE type='table' ORDER BY name"):
            tables.append({
                'table': name, 'sql': sql,
                'row_count': db.execute(f'SELECT count(*) FROM "{name}"').fetchone()[0],
                'columns': [list(r) for r in db.execute(f'PRAGMA table_info("{name}")')],
                'indexes': [list(r) for r in db.execute(f'PRAGMA index_list("{name}")')],
                'foreign_keys': [list(r) for r in db.execute(f'PRAGMA foreign_key_list("{name}")')],
            })
        schema_objects = [{'type': kind, 'name': name, 'table': table, 'sql': sql}
                          for kind, name, table, sql in db.execute(
                              'SELECT type,name,tbl_name,sql FROM sqlite_master ORDER BY type,name')]
        captured_pragmas = {name: db.execute(f'PRAGMA {name}').fetchone()[0]
                            for name in ('user_version', 'schema_version', 'page_size', 'journal_mode')}
        sequence = [list(r) for r in db.execute('SELECT name,seq FROM sqlite_sequence')]
    if [t['table'] for t in tables] != ['hash_info', 'logging_history', 'process_info', 'sqlite_sequence']:
        raise ValueError('queue schema drift')
    evidence.append({'id': _id('database_schema'), 'source': db_id, 'kind': 'sqlite-schema',
                     'locator': 'sqlite_master; table_info/index_list/foreign_key_list; read-only snapshot',
                     'tables': tables, 'schema_objects': schema_objects,
                     'captured_pragmas': captured_pragmas, 'sqlite_sequence': sequence,
                     'finding': 'Complete captured schema including AUTOINCREMENT state and implicit primary-key indexes; varchar lengths are not CHECK constraints. No foreign keys, triggers, views or extra queue dedup index.'})

    states = [{'id': _id(key), 'owner': owner, 'meaning': meaning} for key, owner, meaning in [
        ('stopped', 'Windows SCM', 'service not executing'), ('initializing', 'GTSPlusDataSync.exe', 'timer/controller/database/local-policy initialization'), ('watching', 'MonitoringTask', 'destination watchers and initial scans active'), ('discovered', 'MonitoringTask', 'FileInfo+Destination queued in memory'), ('staged', 'MigrationTask/SQLite', 'persistent row with decimal-id original file'), ('eligible', 'TransmissionTask', 'due file and unpaused MSK-valid work'), ('uploading', 'RestClient', 'multipart request outstanding'), ('retry_wait', 'SQLite process_info', 'retry_schedule persisted, is_retryable true'), ('msk_blocked', 'TransmissionTask', 'MSK expired/revoked suspends upload'), ('paused', 'TransmissionTask', 'ending confirmation pauses next work'), ('disposed', 'DataSync tasks', 'original deleted/evacuated, compression removed, row removed'), ('proxy_running', 'GtsPlus-ProxyManager.exe', 'hidden current-user proxy sampler'), ('action_ready', 'ActionTool.exe', 'accepted GTSPlus parent/token and valid encrypted command XML'), ('action_running', 'ActionTool.exe', 'local diagnostic command worker'), ('action_result', 'ActionTool.exe', 'encrypted ECUResultData .rlog output attempted'),
    ]]
    states.append({'id': _id('stopping'), 'owner': 'GTSPlusDataSync.exe/Windows SCM', 'meaning': 'OnStop cancels controller work and performs bounded shutdown; an already-issued HTTP request has no cancellation token.'})
    transitions: list[dict[str, Any]] = []
    def transition(key: str, start: str, end: str, trigger: str, guard: str, action: str, refs: list[str]) -> None:
        transitions.append({'id': _id(key), 'from': _id(start), 'to': _id(end), 'trigger': trigger, 'guard': guard, 'action': action, 'evidence': [_id(r) for r in refs]})
    transition('start', 'stopped', 'initializing', 'SCM OnStart then one-shot timer', 'native local config authentication succeeds', 'initialize DB, parse encrypted validated YAML and shared queues', ['service_main', 'service_start', 'controller_init', 'database_init', 'auth_init', 'policy_read'])
    transition('init_failure', 'initializing', 'stopped', 'uncaught controller initialization exception', 'OnTimer catch', 'ServiceController.Stop and WaitForStatus(Stopped)', ['service_timer'])
    transition('tasks', 'initializing', 'watching', 'controller startup', 'not cancelled', 'start task graph; heartbeat reinitializes inactive tasks', ['task_order', 'heartbeat'])
    transition('discovery', 'watching', 'discovered', 'initial directory scan or Created event', 'configured destination root', 'enqueue migration entity; log enqueue exception', ['watch_start', 'watch_create', 'watch_enqueue'])
    transition('stage', 'discovered', 'staged', 'migration worker dequeues', 'shared semaphore and not cancelled', 'commit metadata, MoveTo work/id, commit salted original MD5, TryAdd transmission entity', ['migration_worker', 'migration_move', 'migration_commit'])
    transition('recover', 'staged', 'eligible', 'startup/timer/connectivity/ds_send backlog scan', 'matching original id file and absent/due retry_schedule', 'reconcile orphan files/rows and process destinations in descending priority', ['backlog', 'backlog_due', 'backlog_missing', 'transmission_timer', 'connectivity', 'ipc_messages'])
    transition('transmit', 'eligible', 'uploading', 'OperateFile', 'StopExecute=false; MskStatus=0; original/compressed validation passes; online', 'compress/reuse payload, persist validation, refresh proxy, issue multipart request', ['operate', 'validation_steps', 'validation', 'compression', 'request_body', 'multipart_args', 'http_response'])
    transition('validation_failure', 'eligible', 'disposed', 'original/compressed validation false', 'destination validation disposal policy', 'delete or evacuate original; remove compressed artifact and queue row', ['operate', 'error_cleanup', 'immediate_disposal', 'evacuate'])
    transition('ack', 'uploading', 'disposed', 'HTTP200 after response deserialization', 'result1', 'record duplicate hash when enabled, delete compression/original, delete row', ['http_response', 'operate', 'success_cleanup'])
    transition('retry', 'uploading', 'retry_wait', 'configured retry status or timeout/communication/unexpected exception', 'attempt limit not reached', 'persist now+delay; always is_retryable=true; increment attempts except HTTP401', ['http_response', 'retry_status', 'operate', 'retry_commit'])
    transition('retry_due', 'retry_wait', 'eligible', 'backlog scan', 'retry_schedule<=now and file present', 'revalidate duplicate/tampering and retry', ['backlog_due', 'validation_steps'])
    transition('terminal_error', 'uploading', 'disposed', 'result3 or retry attempts reach MaxAttempts', 'destination transmission-error policy', 'delete/evacuate original, remove compressed file and queue row', ['http_response', 'operate', 'error_cleanup'])
    transition('msk_expired_revoked', 'uploading', 'msk_blocked', '403/MIR4030001 or 400/MIR4000000', 'retry status list checked first', 'clear cached MSK; set status1 or2; notify PF; keep queued file', ['http_response', 'operate', 'ipc_notify'])
    transition('msk_updated', 'msk_blocked', 'eligible', 'PF mskupdated', 'valid JSON id', 'clear cached key/status, permit subsequent work; callback does not itself scan', ['ipc_messages'])
    transition('expire', 'staged', 'disposed', 'disposal timer', 'is_retryable=false and CreatedAt+expiration<now', 'evacuate or delete and remove row', ['expiration'])
    transition('pause', 'eligible', 'paused', 'external OnConfirmEnding callback delivered', 'conditional registered ending hook; not assumed during normal GTS arbitration exit', 'SetStopExecute(true)', ['confirm_end'])
    transition('cancel_end', 'paused', 'eligible', 'external OnExecuteEnding(false) callback delivered', 'conditional ending decision cancels shutdown', 'SetStopExecute(false)', ['execute_end'])
    transition('shutdown', 'paused', 'stopping', 'external OnExecuteEnding(true) callback delivered', 'conditional ending hook actually invoked; not a prerequisite for SCM stop', 'ServiceBase.Stop enters the same OnStop cancellation path as independent SCM stop', ['execute_end', 'service_stop', 'controller_abort'])
    for start in ('initializing', 'watching', 'discovered', 'staged', 'eligible', 'retry_wait', 'msk_blocked', 'paused', 'uploading'):
        action = 'Enter OnStop without ending confirmation; Abort controller if present, cancel shared token and clear controlMode; pending durable queue state is not discarded by cancellation.'
        if start == 'uploading':
            action += ' The outstanding two-argument PostAsync remains uncancelled: HTTP timeout30000ms exceeds controller abort wait15000ms; SCM stop does not imply upload acknowledgement or file deletion.'
        transition('scm_stop_' + start, start, 'stopping', 'independent SCM stop invokes OnStop', 'no PF pause/MSK/network/queue-state prerequisite; controller may be absent during initialization', action, ['service_stop', 'controller_abort', 'transmission_stop', 'http_response', 'settings'])
    transition('stop_return', 'stopping', 'stopped', 'OnStop returns after controller Abort wait', 'controller wait completes or its15000ms bound expires', 'Unregister liveness/ending callbacks and set service exit code0. Worker teardown reverses task order; bounded wait is not proof that an outstanding30000ms HTTP request has already completed.', ['service_stop', 'controller_abort', 'stop_order', 'transmission_stop', 'http_response', 'settings'])
    transition('proxy_start', 'stopped', 'proxy_running', 'proxy executable Main', 'global mutex newly created; local config decrypt succeeds', 'sample current-user system proxy immediately and every60seconds; direct path deletes file', ['proxy_main', 'proxy_init', 'proxy_lookup', 'proxy_persist'])
    transition('proxy_exit', 'proxy_running', 'stopped', 'WinForms loop exit/exception', 'finally entered', 'release mutex and close handle; no custom service-stop protocol in this executable', ['proxy_main'])
    transition('action_launch', 'stopped', 'action_ready', 'GTSPlus starts ActionTool', 'exact parent path, first argument, unique mutex; command XML validates', 'start WPF wizard; choose input/result path and device', ['action_entry', 'action_input'])
    transition('action_execute', 'action_ready', 'action_running', 'wizard confirms sending', 'valid input plus selected device', 'execute local command worker; cancellation is cooperative', ['action_run', 'action_cancel'])
    transition('action_finish', 'action_running', 'action_result', 'normal or cancelled/error worker completion', 'next-page flow', 'collect responses/error, serialize and encrypt .rlog; encryption boolean ignored', ['action_run', 'action_output', 'action_filename', 'action_envelope', 'action_hybrid'])

    handoffs = [
        {'to_domain': 'ui_ipc', 'caller': 'GTSPlusDataSync.exe', 'callee': 'GTS+ PF', 'mechanism': 'MsgDatComm.CExternalMethod ER_* CS IPC', 'payload': 'liveness/ending callbacks; outbound mskexpired/mskrevoked JSON; inbound mskupdated,ds_send,ds_unsent_req notification.unit_id_list; result/unit_list/unit_id/unsent_num response', 'evidence': [_id(x) for x in ['ipc_register', 'ipc_messages', 'ipc_notify', 'confirm_end', 'execute_end', 'settings']]},
        {'to_domain': 'sync_upload', 'caller': 'GtsPlus-ProxyManager.exe', 'callee': 'DataSync RestClient', 'mechanism': 'encrypted file IPC on SystemDrive', 'payload': 'GTSPlusDataSyncDb/ProxyInformation.csv: Host/Port; deletion means no explicit proxy', 'evidence': [_id(x) for x in ['proxy_lookup', 'proxy_persist', 'proxy_path', 'proxy_consume', 'proxy_refresh', 'http_client']]},
        {'to_domain': 'bootstrap', 'caller': 'GTSPlus.exe', 'callee': 'ActionTool.exe', 'mechanism': 'child process with parent validation and first argument', 'payload': 'GTSPLUS-2-FIXEDMSGINPUT; encrypted command package selected in wizard, encrypted .rlog stays in selected local directory', 'evidence': [_id(x) for x in ['action_entry', 'action_input', 'action_output', 'action_filename']]},
        {'to_domain': 'sync_upload', 'caller': 'DataSync RestClient', 'callee': 'external destination ServerUri', 'mechanism': 'HTTP multipart POST external boundary', 'payload': 'Basic auth (values omitted), X-GUID, optional X-MSK, logInfo JSON + logFile binary; response CommonResult.StatusCode', 'evidence': [_id(x) for x in ['http_client', 'http_response', 'multipart_args', 'request_body']]},
        {'to_domain': 'auth_settings', 'caller': 'DataSync PropertyManager/RestClient', 'callee': 'local GtsPlus-CM and PF-produced MSK state', 'mechanism': 'native local configuration decryption plus PF IPC', 'payload': 'DSP.pp pairs with encrypted policy (mode1); PF Env pairs with LIC/msk (mode2); mskupdated refreshes cache; Basic/X-MSK values omitted', 'evidence': [_id(x) for x in ['auth_init', 'policy_read', 'msk_read', 'http_client', 'http_response', 'ipc_messages', 'deployment_policy']]},
        {'to_domain': 'vci_transport', 'caller': 'ActionTool.Models.ECUCommunicator', 'callee': 'CommonLibrary.Communication.J2534.DiagCommunication', 'mechanism': 'managed in-process ReadVIN/Command transport calls', 'payload': 'selected device; protocol/CAN_ID/optional N_TA and message bytes; result frame collection; filtered requests return0 without a command call', 'evidence': [_id(x) for x in ['action_run', 'action_transport', 'action_functional_filter', 'action_sid_filter']]},
    ]
    persistence = [
        {'path_pattern': '%SystemDrive%/GTSPlusDataSyncDb/GTSPlusDataSync.db', 'producer': 'EF Core DataSync tasks', 'consumer': 'DataSync restart/backlog/disposal; PF unsent inquiry', 'created': 'controller EnsureCreated', 'flushed': 'per-row SaveChanges after insert/hash/validation/retry/receipt/history operations', 'deleted': 'queue rows after ack/error cleanup or missing-file reconciliation; database file retained', 'evidence': [_id(x) for x in ['database_init', 'migration_commit', 'retry_commit', 'database_schema', 'success_cleanup', 'backlog_missing']]},
        {'path_pattern': '<Transmission.WorkDirectory.Path>/<process_info.id>[compression suffix]', 'producer': 'MigrationTask; TransmissionTask compression', 'consumer': 'TransmissionTask; DisposalTask', 'created': 'original moved after DB insert, optional compression follows validation', 'flushed': 'file streams disposed by compression; metadata saved independently (not an atomic file+DB transaction)', 'deleted': 'HTTP200 cleanup; validation/terminal error policy; expiration; orphan reconciliation', 'evidence': [_id(x) for x in ['migration_worker', 'migration_move', 'compression', 'success_cleanup', 'error_cleanup', 'expiration', 'backlog_due']]},
        {'path_pattern': '<destination disposal Evacuate.Path>/<id>/<original_filename>', 'producer': 'TransmissionTask or DisposalTask', 'consumer': 'CleaningTask', 'created': 'DisposalType2 on validation/terminal upload error or age expiration', 'flushed': 'FileInfo.MoveTo after deleting compressed artifact', 'deleted': 'AllowCleaning=true, configured common expiration from directory LastWriteTime', 'evidence': [_id(x) for x in ['evacuate', 'expiration', 'clean_policy', 'clean_age']]},
        {'path_pattern': '%PUBLIC%/Documents/GTSPlus/DataSyncTmp/Log/GTSPlusDataSync_yyyyMMdd.log -> DSY-D01 watch root when configured', 'producer': 'log4net; optional LoggingTask', 'consumer': 'MonitoringTask -> normal upload queue only with DSY-D01 destination', 'created': 'daily service log; optional copy/merge path inactive in captured deployment (no DSY-D01)', 'flushed': 'if enabled, merged file moved to destination root and logging_history SaveChanges', 'deleted': 'if enabled, source/copied logs after staging; normal queue lifecycle follows', 'evidence': [_id(x) for x in ['settings', 'log_package', 'log_constants', 'logging_selector', 'deployment_policy']]},
        {'path_pattern': '%SystemDrive%/GTSPlusDataSyncDb/ProxyInformation.csv', 'producer': 'current-user ProxyManager', 'consumer': 'service RestClient', 'created': 'changed system proxy host/port', 'flushed': 'native EncryptionProxyFile with DSP.pp pairing', 'deleted': 'system proxy URI equals destination URI (direct)', 'evidence': [_id(x) for x in ['proxy_persist', 'proxy_path', 'proxy_consume']]},
        {'path_pattern': '<selected inputstem>_<yyyyMMddHHmmss>[(n)].rlog or selected override', 'producer': 'ActionTool RunningPageViewModel', 'consumer': 'local user/export consumer, not established as DataSync input', 'created': 'normal/cancel/error result XML encryption attempted', 'flushed': 'CryptoStream and FileStream disposed; Encrypt false is ignored by caller', 'deleted': 'no result deletion in inspected ActionTool flow', 'evidence': [_id(x) for x in ['action_output', 'action_filename', 'action_envelope']]},
    ]
    return {'schema': 'gtsplus-lifecycle-domain-v1', 'domain': DOMAIN, 'sources': sources, 'evidence': evidence, 'states': states, 'transitions': transitions, 'handoffs': handoffs, 'persistence': persistence,
        'queue_recovery_contract': _queue_contract(),
        'coverage': {'components': ['GTSPlusDataSync.exe service/controller/Monitoring/Migration/Transmission/Disposal/Cleaning/Logging/RestClient', 'GtsPlus-ProxyManager.exe', 'DiagMessageInput/ActionTool.exe', 'DiagMessageInput/CommonLibrary.dll package envelope', 'offline-decrypted DataSync deployment policy'], 'entrypoints': ['SCM Program.Main/OnStart/OnStop', 'OnTimer', 'Created watcher and initial scan', 'connectivity/timer/live queue workers', 'PF ending/application callbacks', 'ProxyManager Program.Main/timer', 'ActionTool WPF App.OnStartup/OnExit'], 'branches': ['fatal initialization; heartbeat task restart; migration cancellation/error; offline backlog retention; validation/tampering/duplicate; compression reuse; HTTP200/configured retry/status-specific MSK failure/terminal failure; retry delay/attempt count (401 exception); ack cleanup/evacuation/expiry/cleaning; pause/confirm/cancel shutdown; proxy singleton/direct/change; ActionTool parent/token/singleton/input validation/cancel/result-write failure']},
        'artifact_classes': {'queue_metadata': 'SQLite process_info', 'duplicate_receipts': 'SQLite hash_info', 'log_export_history': 'SQLite logging_history', 'upload_originals': 'configured watch roots -> decimal-id work files', 'transport_derivatives': 'Zstandard/GZip', 'local_policy': 'encrypted GTSPlusDataSync.yml + DSP.pp', 'authorization_material': 'LIC/msk paired with PF Env; values never exported', 'cross_user_proxy_handoff': 'encrypted ProxyInformation.csv', 'action_command_package': 'encrypted ECUSendData XML', 'action_result_package': 'encrypted ECUResultData .rlog'},
        'residuals': [{'question': 'Remote receipt durability and server-side MSK/account decisions', 'why_unclosed': 'Offline corpus includes client branch contract, not deployed server implementation or responses; no network/authentication requests made.', 'next_evidence': 'Authorized redacted response fixture/service implementation; offline feed into pinned client classifier.'}, {'question': 'Windows runtime ordering of service/watch/IPC callbacks', 'why_unclosed': 'No Windows CLR/SCM/WinForms runtime in this environment; source/IL checks and offline package decryption do not exercise OS callbacks.', 'next_evidence': 'Bounded offline Windows harness with fixture files and IPC stubs, no real endpoint/device.'}]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=DEFAULT_ROOT)
    parser.add_argument('--recovered-root', type=Path, default=DEFAULT_RECOVERED)
    parser.add_argument('--output', type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    artifact = build(args.root, args.recovered_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2, ensure_ascii=False, sort_keys=True) + '\n', encoding='utf-8')
    print(f'wrote {args.output}: {len(artifact["evidence"])} evidence, {len(artifact["transitions"])} transitions')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
