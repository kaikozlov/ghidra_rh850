# Remaining Mode06 table 24/25 evidence

The exporter preserves these records but does not claim complete semantic decoding.
The current source contains 120 instances, not 120 distinct definitions: six copies
(NA/EU/JP, each PowerTrain_CARB and CAN_CARB) of six table24 and fourteen table25 rows.

Concatenated record SHA-256 (identical in every copy):
- table24: 29ae73ae47135e23ec587c18d1523efda908b7f031c4fa87a86663d92197da79
- table25: 665a54d709a6cdb744ddfcdf676062fc48dbd24dc75d28c2927dfc5c56cca11d

## Proven fields

Current KgpDataCtrl.dll table24: eight-byte records, lookup keys bytes5/4,
exception u16+0 and exception flag byte7. Bytes2..3/6 remain unnamed.
Table25: 84-byte records, lookup keys bytes77/76, name string ID u32+48,
exception u16+72 and flag byte81.
GetDataMonitorShortName1006ACF0 returns the record base as a UTF16 string
(all supplied templates have an empty prefix); the capacity of that buffer is
not established. SetRecString1006AA20 resolves only the name ID at48.
GetDatMonName1006ACA0 returns that resolved string.
DebugOutputTrace1006B680 is an empty function.

These are available in obd_monitor.py, with semantic_status=indexes_only and
all original bytes retained. Adjacent table23 suggests possible conversion
and bit-range fields, but matching layout/data patterns are not sufficient
proof of the table25 consumer contract.

## Alternatives investigated

All three installed binary trees were searched, not only the newest release:
- GTSPlus GetMonitorResultInfo_DT SHA256
  2f647d0cbddfda39950f4180c5a477c3fb35e17d6e906dcd67b5015a086173ec
- DS-4 GetMonitorResultInfo_DT SHA256
  393c8ef88721dd0691580912cf5f6c9cbdfab0478ffc771fbfa5cbfdff69ada4
- Techstream V18 GetMonitorResultInfo_DT SHA256
  c16aa9c8a6fc4aad3036c40f8ab93508070ab4714988dd62ddfe21242441bdfb
- V18 KgpDataMonitorCtrl SHA256
  62a083b22693e60c94665644cf1bd5cda64376f0b1d388cc76d9c4fafef2e71f

V18 GetMonitorResultInfo Execute10001010 routes through10001D40(table28),
100028D0(table27),10003440(aliases143/144). Current DS-4 Execute10002820
routes through100016A0/10001C10/100021A0, likewise the newer result families.
Current GetMonitoringTestCARB10001060 uses frame requests and Mode06 response
analyzers rather than table24/25 records.

Class-name/import searches find these record classes only in KgpDataCtrl and
KgpDataMonitorCtrl. The latter's references inspected in V18 and current GTS
are copy/destruction infrastructure, not data-field consumers. This alone
does not establish absence, because generic query factories can hide classes.

Therefore executable-section immediate scans for query IDs0x218/0x219 were
also performed across the current GTS, DS-4, and V18 DLLs. Inspected hits
were logging line numbers, not record queries. Examples proven by decompilation:
current DataListIF10029EE5 (CheckRcvFrame error line536),100417B5
(SaveRcvTimeLog CloseFile line536); V18 GetMultiFrzFrmDatP4
10001631/1000164B (log lines536/537). Other scan hits were checked against
ErrReportf import calls. This is evidence of no located consumer, not a proof
covering every possible dynamically formed query ID.

No relevant debug-symbol/type-header/schema files were found locally. The
available full historical release is V18; the other installer copies are the
same release, not an older implementation.

## Actual current response-buffer and factory paths

Current GetMonitoringTestCARB10001780 obtains frame0x8E, patches requestbyte1,
and passes response list CCommFrameData+0x58 to AnalyzeSupportTid/Mid.
It uses the response-derived support list, not table24's enumerated templates.
GetMonitoringTestCARB10001DF0 obtains frame0x8F, patches requestbyte1 with each
supported ID, and passes CCommFrameDataMultiReceive+0x80 response lists to
AnalyzeTestResultTid/Mid. CommandCommon10004210 decodes one header byte followed
by six-byte tuples: TID, CID/limit flag, value16BE, limit16BE. CID is low7bits;
highbit chooses minimum (set) or maximum (clear). It merges equal(TID,CID),
keeping first value and first supplied limit of each kind. The exporter has an
offline implementation and duplicate/malformed-input regression tests.

GetMonitoringTestCARB10001310 projects these native result objects directly
into CCmdMonitoringTest: identity multiplier/divisor1/1, offset0, empty unit,
width16, and response-derived minimum/maximum support flags. This path does
not apply table25's apparent physical references or bit positions.

The generic table factory is real: KgpDataCtrl100845D0 cases0x18/0x19 construct
CDb06TidTable/CDb06TidMonitorTable with kind2, table24/25. Caller is
MakeTable10081C4F. GetTableKindInfo10064F10 rejects low-only IDs0x18/0x19;
CDiagToolDb queries require a valid kind in the highbyte. GetDbRecord10065F00
selects the file's table-pointer array by lowbyte and dispatches virtual
GetQuery at +0x18 (kind2), or +0x14 otherwise. This demonstrates support for
generic access, not an application consumer of these particular records.

KgpDataMonitorCtrl imports table25 GetQuery at IAT100409DC/100409E0 through
thunks10037A3C/10037A42. Their references are vtable100441AC; references to that
vtable found are exported table move/copy constructors1000F010/1000F060.
Import names alone hid these class names, so earlier import-only absence
was not sufficient evidence. Native category routing was also traced: categories900/916 select role0x54
GetMonitoringTestCARB and common role0x5B GetMonitorResultInfo. Data-list roles
0x5/0xAD select GetDatMonListDk, whose10001000/100012A0/10001460 paths query
tables0x20D/0x20F/0x20A only. CARBModeInit query sites use0x105/0x110/0x12C/
0x131/0x132. StartDiagCARB10001010 performs bus/phase diagnostic setup.
KgpDataMonitorCtrl100364C0 routes phase7 to DataMonitorDKIso9141 and10035F90
loads its Run export. Its examined decompilation has no24/25 query; the0x219
at1000C610 is a logging line, not a query ID.

## Recovered protected-body cross-check

A separate scan covered 249 PE artifacts under build/out/gts-all-unprotected,
including Auxiliary and CUWPlus, not just the installed GTSPlus bin directory.
No recovered body contains a 06Tid symbol. Imported generic database readers
were enumerated in mode06-deep-trace/recovered-imports.json. Of 114 raw
push/mov immediate candidates for 0x218/0x219, seven occur in binaries importing
KgpDataCtrl's GetDbRecord. All seven are error-report source line numbers,
not database query arguments: DS-4 CommandCommon10083F04; current
CommandCommon1003AC77/10040A15/100A3976; GetPCSReadTime10003931;
GetPVMImageFFDP5 10006D44; GetDMCImageFFDP5 1000740A. Their call or branch target
resolves to CommonDll::ErrReportf through the actual PE import table.
The disassembly and candidate list are saved under build/out/mode06-deep-trace.
This excludes these immediate candidates; it does not prove that an arbitrary
dynamically constructed query can never reach the generic table factory.

## What remains necessary

A historical implementation that actually consumes table24/25 fields, a
record-format specification, or runtime evidence of such a consumer is needed
to assign the remaining field roles safely. The current evidence does not
justify calling these records fully decoded, removing them, or inventing
request/response behavior.

Regression: uv run python -m tests.techstream.verify_obd_monitor verifies all
120 instances retain exact bytes/source identities and records this boundary.
