from pathlib import Path
import hashlib, zipfile
ROOT=Path(__file__).resolve().parents[3]
base=ROOT/'reports/technical'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def compact():
 return sorted(p for p in base.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.zip' and p.name!='SHA256SUMS')
files=compact()
(base/'SHA256SUMS').write_text(''.join(f'{digest(p)}  {p.relative_to(base)}\n' for p in files))
payload=[(p,'report/'+str(p.relative_to(base))) for p in files+[base/'SHA256SUMS']]
for tree in ['baseline-physical','optimized-physical','optimized-gate-tests']:
 folder=ROOT/'build'/tree
 assert folder.is_dir(),folder
 payload.extend((p,'raw/'+tree+'/'+str(p.relative_to(folder))) for p in sorted(folder.rglob('*')) if p.is_file())
out=base/'deliverables/TinySystolic_Evidence.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 manifest=[]
 for p,name in payload:
  z.write(p,name);manifest.append(f'{digest(p)}  {name}\n')
 z.writestr('MANIFEST.sha256',''.join(manifest))
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
 for line in z.read('MANIFEST.sha256').decode().splitlines():
  expected,name=line.split('  ',1)
  assert hashlib.sha256(z.read(name)).hexdigest()==expected,name
print(f'Verified {len(payload)} files; ZIP {out.stat().st_size/1e6:.1f} MB')
