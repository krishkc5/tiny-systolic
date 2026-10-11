"""Fail closed on missing/violating electrical metrics from a final flow artifact.
Usage: python tools/check_physical.py <GDS_logs directory>
This supplements Tiny Tapeout precheck; it is not a fabrication waiver.
"""
import json, math, sys
from pathlib import Path

def audit(root):
    paths=list(root.glob('**/final/metrics.json'))
    if len(paths)!=1:raise ValueError('Expected exactly one final/metrics.json')
    m=json.loads(paths[0].read_text());errors=[]
    def zero(key):
        if key not in m or m[key]!=0:errors.append(f'{key}: {m.get(key,"MISSING")}')
    corners=[f'{rc}_{pvt}' for rc in ['nom','min','max'] for pvt in ['tt_025C_1v80','ss_100C_1v60','ff_n40C_1v95']]
    for corner in corners:
        for metric in ['design__max_slew_violation__count','design__max_fanout_violation__count','design__max_cap_violation__count','timing__setup_vio__count','timing__hold_vio__count','timing__unannotated_net_filtered__count']:
            zero(metric+'__corner:'+corner)
        for kind in ['setup','hold']:
            key=f'timing__{kind}__ws__corner:{corner}';value=m.get(key)
            if not isinstance(value,(int,float)) or not math.isfinite(value) or value<0:errors.append(f'{key}: {value}')
    print(json.dumps({'metrics_file':str(paths[0]),'electrical_checks_pass':not errors,'issues':errors},indent=2))
    return not errors
if __name__=='__main__':
    try:ok=audit(Path(sys.argv[1]))
    except (ValueError,KeyError,IndexError,OSError) as e:print(f'ERROR: {e}',file=sys.stderr);ok=False
    sys.exit(0 if ok else 1)
