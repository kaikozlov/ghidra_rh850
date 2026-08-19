#!/usr/bin/env python3
"""Build canonical direct-call seed provenance closure from the clean H call graph."""
from __future__ import annotations
import argparse,csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EVID=ROOT/'data/generated/corolla_8965H1202000_direct_call_surface_evidence.json'
LEDGER=ROOT/'data/semantic_coverage_ledger.csv'
OUT=ROOT/'data/generated/corolla_8965H1202000_direct_call_surface.json'
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=OUT);a=ap.parse_args();e=json.loads(EVID.read_text())
 if not e['summary']['closed'] or e['summary']['missing_in_image_literal_call_targets']:raise ValueError('target direct-call graph is not closed')
 rows=list(csv.DictReader(LEDGER.open()))
 seeds=[r for r in rows if r['name'].startswith('direct_call_target_') and r['discovery_source']=='direct-call seed' and r['discovery_provenance']=='SeedDirectCallTargets.java']
 if len(seeds)!=153:raise ValueError(f'canonical direct-call seed cohort drift: {len(seeds)}')
 rec=[{'reference_entry':r['entry_addr'],'reference_name':r['name'],'reason':'canonical name records only literal direct-call discovery provenance; H clean literal-call graph is completely re-enumerated'} for r in seeds]
 p={'schema':'corolla-h-direct-call-surface-v1','software_id':'8965H1202000','evidence':{'call_surface':str(EVID.relative_to(ROOT)),'call_surface_sha256':sha(EVID.read_bytes()),'canonical_ledger':str(LEDGER.relative_to(ROOT)),'canonical_ledger_sha256':sha(LEDGER.read_bytes())},'h_surface_summary':e['summary'],'canonical_direct_call_seed_count':len(seeds),'surface_recensus':rec,'surface_recensus_count':len(rec),'static_conclusion':{'target_literal_call_graph_closed':True,'boundary':'direct_call_target_* is discovery provenance, not semantic identity. Complete H literal-call recensus closes that naming/provenance class only; exact-body and target-native semantic role evidence remain higher-precedence, and no one-to-one behavior is inferred from this recensus.'}}
 a.out.write_text(json.dumps(p,indent=2,sort_keys=True)+'\n');print('wrote',a.out)
if __name__=='__main__':main()
