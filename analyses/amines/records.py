"""Locate retained inputs using the stage catalogue."""

from functools import cache
import json
from pathlib import Path

from MEA.common.retained_results import read as read_json

from .wheel import ROOT

RESULTS = ROOT / "analyses/amines/results"


@cache
def catalog():
    return json.loads(Path(__file__).with_name("sources.json").read_text())


@cache
def archive_paths():
    return {row["archive_path"]: ROOT / path for path, row in catalog().items()
            if "archive_path" in row and row["c_disposition"] == "stage-layout"}


def input_path(path):
    path = (ROOT / path).resolve()
    if not path.is_relative_to(ROOT):
        return path
    key = path.relative_to(ROOT).as_posix()
    paths = archive_paths()
    if key in paths:
        return paths[key]
    if path.suffix == ".json" and key + ".gz" in paths:
        return paths[key + ".gz"]
    return path


def read(path):
    return read_json(input_path(path))
