"""Create or publish the Zenodo version for the merged amine manuscript."""

import argparse
from hashlib import file_digest, sha256
import json
import os
from pathlib import Path
import re
from tempfile import TemporaryDirectory
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener, urlopen
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
SUBMISSION = ROOT / "docs/scientific/latex/submission_metadata.yml"
RECORD_ID = 23323107
CONCEPT_ID = "23323106"
ORIGIN = "https://zenodo.org"
LATEST = f"{ORIGIN}/api/records/{RECORD_ID}/versions/latest"
DEPOSITIONS = f"{ORIGIN}/api/deposit/depositions"
ARCHIVE_NAME = "amine-thermodynamics-fpe.zip"


def field(text, name, indent=0):
    """Read a single-line scalar from the repository's metadata files."""
    prefix = " " * indent
    match = re.search(rf"^{prefix}{name}: (.+)$", text, re.MULTILINE)
    if match is None:
        raise ValueError(f"Missing metadata field {name}")
    return match[1].strip().strip('"')


def submission_metadata(text, commit):
    # These fields use folded text, single-line scalars and a block list.
    title = re.search(r"^title: >\n((?:  [^\n]+\n)+)", text, re.MULTILINE)[1].split()
    keywords = re.search(r"^keywords:\n((?:  - [^\n]+\n)+)", text, re.MULTILINE)[1]
    author = (ROOT / "CITATION.cff").read_text()
    family = re.search(r"^  - family-names: (.+)$", author, re.MULTILINE)[1]
    given = field(author, "given-names", 4)
    orcid = field(author, "orcid", 4).removeprefix("https://orcid.org/")
    affiliation = field(author, "affiliation", 4)
    if (f"{given} {family}" != field(text, "name", 2) or orcid != field(text, "orcid", 2)
            or affiliation != field(text, "organization", 4)):
        raise ValueError("Author details differ between CITATION.cff and submission metadata")
    if field(text, "repository_license") != "MIT" or field(author, "license") != "MIT":
        raise ValueError("License differs from the MIT license on the published Zenodo version")
    repository = field(text, "repository")
    return {"metadata": {
        "title": " ".join(title),
        "description": (
            "<p>Data and code for the Fluid Phase Equilibria article on CO₂ solubility in aqueous "
            "MEA, DEA, MDEA and AMP with ePC-SAFT. The archive includes processed observations, "
            "model inputs, fitted parameter values, retained numerical results, the analysis and "
            "figure code, the Engine wheels, and commands to regenerate the article and supplement "
            "tables and figures.</p><p>The project code is MIT-licensed. Third-party measurements "
            "remain under the terms of their sources.</p>"
        ),
        "upload_type": "software",
        "access_right": "open",
        "creators": [{"name": f"{family}, {given}", "orcid": orcid, "affiliation": affiliation}],
        "keywords": [line.removeprefix("  - ") for line in keywords.splitlines()],
        "license": "mit-license",
        "related_identifiers": [{"identifier": f"{repository}/tree/{commit}",
                                 "relation": "isDerivedFrom", "scheme": "url"}],
        "prereserve_doi": True,
    }}


def pack(destination):
    manifest = destination / "SHA256SUMS"
    entries = {}
    for line in manifest.read_text().splitlines():
        digest, name = line.split("  ", 1)
        path = destination / name
        if (name in entries or name == manifest.name or not path.resolve().is_relative_to(destination)
                or Path(name).as_posix() != name or ".." in Path(name).parts):
            raise ValueError(f"Invalid manifest entry: {name}")
        entries[name] = digest
    if not {"README.md", "provenance/source.json", "provenance/rebuild-check.json"} <= entries.keys():
        raise ValueError("Seal the rebuilt deposit before uploading")
    checks = json.loads((destination / "provenance/rebuild-check.json").read_text())
    if not all(checks[name]["layout_text_matches"] and not checks[name]["undefined_references_or_citations"]
               for name in ("main", "supplement")):
        raise ValueError("Deposit PDF rebuild did not pass")
    archive = destination.parent / ARCHIVE_NAME
    with TemporaryDirectory(dir=archive.parent) as directory:
        candidate = Path(directory) / archive.name
        with ZipFile(candidate, "w", compression=ZIP_DEFLATED) as output:
            for name, digest in entries.items():
                content = (destination / name).read_bytes()
                if sha256(content).hexdigest() != digest:
                    raise ValueError(f"Seal checksum mismatch: {name}")
                output.writestr(name, content)
            output.writestr(manifest.name, manifest.read_bytes())
        candidate.replace(archive)
    return archive


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def request(method, url, *, token=None, payload=None, archive=None):
    target = urlsplit(url)
    if (target.scheme, target.netloc) != ("https", "zenodo.org") or target.query:
        raise ValueError("Unexpected Zenodo endpoint")
    headers = {"User-Agent": "Amine-Thermodynamics/429", "Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    send = build_opener(NoRedirect()).open if token else urlopen
    try:
        if archive:
            headers.update({"Content-Type": "application/octet-stream",
                            "Content-Length": str(archive.stat().st_size)})
            with archive.open("rb") as stream:
                with send(Request(url, data=stream, method=method, headers=headers), timeout=120) as response:
                    return json.load(response)
        body = None
        if payload is not None:
            headers["Content-Type"] = "application/json"
            body = json.dumps(payload).encode()
        with send(Request(url, data=body, method=method, headers=headers), timeout=120) as response:
            return None if response.status == 204 else json.load(response)
    except HTTPError as error:
        raise SystemExit(f"Zenodo {method} {target.path} returned HTTP {error.code}") from None
    except (URLError, OSError, ValueError):
        raise SystemExit(f"Zenodo {method} {target.path} failed") from None


def check_draft(record, draft_id):
    if str(record["id"]) != str(draft_id) or str(record["conceptrecid"]) != CONCEPT_ID or record["submitted"]:
        raise ValueError("Expected an unpublished draft of the amine manuscript concept")


def draft(destination, text, *, token=None, dry_run=False):
    commit = json.loads((destination / "provenance/source.json").read_text())["commit"]
    if not re.fullmatch(r"[a-f0-9]{40}", commit):
        raise ValueError("Invalid deposit commit")
    payload = submission_metadata(text, commit)
    archive = pack(destination)
    with archive.open("rb") as stream:
        digest = file_digest(stream, "sha256").hexdigest()
    print(f"{archive}: {archive.stat().st_size} bytes, sha256:{digest}", flush=True)
    if dry_run:
        print(f"GET {LATEST}")
        print(f"POST {DEPOSITIONS}/{RECORD_ID}/actions/newversion (using the latest version ID from GET)")
        print(f"GET {DEPOSITIONS}/<draft-id>")
        print(f"DELETE {DEPOSITIONS}/<draft-id>/files/<file-id> (for each inherited or superseded file)")
        print(f"PUT {ORIGIN}/api/files/<bucket-id>/{archive.name} (if the matching archive is absent)")
        print(f"PUT {DEPOSITIONS}/<draft-id>")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    latest = request("GET", LATEST)
    if str(latest["conceptrecid"]) != CONCEPT_ID:
        raise ValueError("Latest record is outside the expected Zenodo concept")
    inherited = {entry["key"] for entry in latest["files"]}
    version = request("POST", f"{DEPOSITIONS}/{int(latest['id'])}/actions/newversion", token=token)
    draft_id = int(urlsplit(version["links"]["latest_draft"]).path.rstrip("/").rsplit("/", 1)[-1])
    endpoint = f"{DEPOSITIONS}/{draft_id}"
    record = request("GET", endpoint, token=token)
    check_draft(record, draft_id)
    unexpected = {entry["filename"] for entry in record["files"]} - inherited - {archive.name}
    if unexpected:
        raise ValueError(f"Existing draft {draft_id} contains files outside this deposit: {sorted(unexpected)}")
    with archive.open("rb") as stream:
        md5 = file_digest(stream, "md5").hexdigest()
    uploaded = None
    for entry in record["files"]:
        if entry["filename"] == archive.name and entry["checksum"].removeprefix("md5:") == md5:
            uploaded = entry
        else:
            request("DELETE", f"{endpoint}/files/{quote(str(entry['id']), safe='')}", token=token)
    if uploaded is None:
        bucket = record["links"]["bucket"].rstrip("/")
        uploaded = request("PUT", f"{bucket}/{quote(archive.name)}", token=token, archive=archive)
    if uploaded["checksum"].removeprefix("md5:") != md5:
        raise ValueError("Zenodo's upload checksum differs from the archive MD5")
    updated = request("PUT", endpoint, token=token, payload=payload)
    print(f"Draft URL {updated['links']['html']}")
    print(f"Reserved DOI {updated['metadata']['prereserve_doi']['doi']}")
    print(f"{archive.name} {uploaded['checksum']}")


def publish(draft_id, token):
    endpoint = f"{DEPOSITIONS}/{draft_id}"
    record = request("GET", endpoint, token=token)
    check_draft(record, draft_id)
    if [entry["filename"] for entry in record["files"]] != [ARCHIVE_NAME]:
        raise ValueError(f"Expected the draft to contain only {ARCHIVE_NAME}")
    if not record["metadata"].get("prereserve_doi", {}).get("doi"):
        raise ValueError("Expected a reserved DOI on the draft")
    result = request("POST", f"{endpoint}/actions/publish", token=token)
    print(f"Record URL {result['links']['html']}")
    print(f"DOI {result['doi']}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--token-file", type=Path, default=os.environ.get("ZENODO_TOKEN_FILE"),
                        help="file containing the Zenodo token (or set ZENODO_TOKEN_FILE)")
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("draft", help="stage the archive in a new Zenodo version draft")
    create.add_argument("--deposit", type=Path, help="sealed directory (defaults to local_data_release)")
    create.add_argument("--dry-run", action="store_true", help="show requests without contacting Zenodo")
    commands.add_parser("publish", help="publish the specified draft").add_argument("draft_id", type=int)
    args = parser.parse_args()
    try:
        text = SUBMISSION.read_text()
        if args.command == "draft":
            destination = args.deposit or Path(field(text, "local_data_release").split(" (", 1)[0])
            destination = destination.expanduser().resolve()
            if args.dry_run:
                draft(destination, text, dry_run=True)
                return
        if not args.token_file:
            parser.error("provide --token-file or set ZENODO_TOKEN_FILE")
        token = args.token_file.expanduser().read_text().strip()
        if not re.fullmatch(r"[!-~]+", token):
            parser.error("invalid Zenodo token file")
        if args.command == "draft":
            draft(destination, text, token=token)
        else:
            publish(args.draft_id, token)
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
