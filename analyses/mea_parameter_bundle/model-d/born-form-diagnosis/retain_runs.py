"""Move retained solve and derivative records, checking every moved byte hash."""
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    before={str(p.relative_to(HERE)):sha(p) for p in HERE.rglob('*') if p.is_file() and not p.name.startswith('assessment-p5a-')}
    moves={}
    for path in sorted(HERE.iterdir()):
        if not path.is_file() or path.name.startswith('assessment-p5a-'):continue
        category=None
        if path.suffix=='.jsonl':category='states'
        elif path.name.startswith(('fd-','p4-fd-','scan-A-','scan-B-','scan-C-','scan-D-')) and path.suffix=='.json':category='evaluations'
        elif path.name.endswith('-fit.json'):category='native-fits'
        elif path.name.endswith('-jacobian.json') or path.name.startswith(('column-','p4-column-')):category='jacobians'
        elif path.suffix=='.json':
            rec=json.loads(path.read_text())
            if isinstance(rec,dict) and ('weighted_residuals' in rec or 'optimizer_jacobian' in rec):category='evaluations'
        elif path.name in ('p1-native-born-potentials.csv','p1-reaction-activities.csv','p1-water-and-ion-activities.csv',
                            'objective-species-costs-and-signed-residuals.csv','p4refit-all-complete-evaluation-species.csv'):
            category='tables'
        if category:
            dest=HERE/'runs'/category/path.name;dest.parent.mkdir(parents=True,exist_ok=True)
            assert not dest.exists(),dest
            old=str(path.relative_to(HERE));path.rename(dest)
            new=str(dest.relative_to(HERE));assert sha(dest)==before[old]
            moves[old]=dict(path=new,sha256=before[old])
    for name in ('cache','matplotlib-cache'):
        path=HERE/name
        if path.exists():
            dest=HERE/'runs'/name;assert not dest.exists();path.rename(dest)
            for old,expected in before.items():
                if old.startswith(name+'/'):
                    new='runs/'+old;assert sha(HERE/new)==expected;moves[old]=dict(path=new,sha256=expected)
    for old,expected in before.items():
        new=moves.get(old,{}).get('path',old)
        assert (HERE/new).is_file() and sha(HERE/new)==expected,(old,new)
    (HERE/'relocation-map.json').write_text(json.dumps(dict(original_files=len(before),moved_files=len(moves),
        all_original_bytes_preserved=True,moves=moves,excluded_owner='assessment-p5a-* belongs to the assessment worker'),indent=2)+'\n')
    print(json.dumps(dict(original_files=len(before),moved_files=len(moves),root_files=sum(p.is_file() for p in HERE.iterdir()))))

if __name__=='__main__':main()
