"""#410: selected #398 endpoint on the pinned wheel, bound through the Part II route."""
import json, sys
from pathlib import Path
AN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AN.parent))
from part_ii import Route, ROOT  # verifies the pinned wheel and shared values on construction
import epcsaft

REF = ROOT/'data/reference/DEA'


def route(out):
    return Route(AN/'inputs/part-ii-346/route-current.json', out)


def endpoint(out):
    route(out)  # wheel and shared-record identity checks
    return json.loads((AN/'results/retransfer-398/selection.json').read_text())['chosen']['parameters']


def mixture(doc):
    return epcsaft.Mixture(epcsaft.Parameters.from_mapping(doc))


def save(path, value):
    (AN/path).write_text(json.dumps(value, indent=1, default=float)+'\n')
