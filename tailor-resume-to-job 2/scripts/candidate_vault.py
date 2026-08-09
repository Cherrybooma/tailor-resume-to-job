#!/usr/bin/env python3
"""Manage a local, user-approved candidate evidence vault."""

import argparse
import hashlib
import json
import re
import shutil
from datetime import date
from pathlib import Path


def load_json(path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_name(name):
    cleaned = re.sub(r"[^A-Za-z0-9._\-\u4e00-\u9fff]+", "_", name).strip("._")
    return cleaned or "source"


def command_init(args):
    vault = args.vault_dir.resolve()
    for subdir in ("evidence", "derived", "applications"):
        (vault / subdir).mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    vault_meta = vault / "vault.json"
    if not vault_meta.exists():
        write_json(vault_meta, {
            "vault_version": 1,
            "candidate_id": args.candidate_id,
            "candidate_name": args.name,
            "created_at": today,
            "updated_at": today,
        })
    profile = vault / "candidate-profile.json"
    if not profile.exists():
        write_json(profile, {
            "profile_version": 1,
            "status": "draft",
            "updated_at": today,
            "candidate": {
                "name": args.name,
                "contact": {"phone": "", "email": "", "location": "", "links": []},
                "target_preferences": {"languages": [], "page_count": 1},
                "education": [], "experience": [], "case_studies": [], "projects": [],
                "skills": [], "research": [], "publications": [], "patents": [],
                "awards": [], "certifications": [], "unresolved": [],
            },
            "sources": [],
        })
    index = vault / "evidence-index.json"
    if not index.exists():
        write_json(index, {"index_version": 1, "updated_at": today, "sources": []})
    root_index_path = vault.parent / "vault-index.json"
    root_index = load_json(root_index_path, {"index_version": 1, "updated_at": today, "candidates": []})
    candidates = [item for item in root_index.get("candidates", []) if item.get("candidate_id") != args.candidate_id]
    candidates.append({
        "candidate_id": args.candidate_id,
        "candidate_name": args.name,
        "vault_dir": str(vault),
    })
    root_index["candidates"] = sorted(candidates, key=lambda item: item["candidate_id"])
    root_index["updated_at"] = today
    write_json(root_index_path, root_index)
    print(vault)


def command_add_source(args):
    vault = args.vault_dir.resolve()
    source = args.file.resolve()
    if not (vault / "vault.json").exists():
        raise SystemExit("Vault is not initialized")
    if not source.exists():
        raise SystemExit(f"Source not found: {source}")
    if args.mode == "copy" and not source.is_file():
        raise SystemExit("copy mode supports files only; use reference mode for directories")

    index_path = vault / "evidence-index.json"
    index = load_json(index_path, {"index_version": 1, "sources": []})
    digest = sha256(source) if source.is_file() else None
    for record in index["sources"]:
        if digest and record.get("sha256") == digest:
            print(json.dumps(record, ensure_ascii=False))
            return

    source_id = f"src-{len(index['sources']) + 1:04d}"
    stored_path = None
    if args.mode == "copy":
        destination = vault / "evidence" / f"{source_id}__{safe_name(source.name)}"
        shutil.copy2(source, destination)
        stored_path = str(destination)
    record = {
        "id": source_id,
        "label": args.label or source.name,
        "type": args.type,
        "mode": args.mode,
        "original_path": str(source),
        "stored_path": stored_path,
        "sha256": digest,
        "added_at": date.today().isoformat(),
        "supplied_by_user": True,
    }
    index["sources"].append(record)
    index["updated_at"] = date.today().isoformat()
    write_json(index_path, index)
    print(json.dumps(record, ensure_ascii=False))


def command_validate(args):
    vault = args.vault_dir.resolve()
    errors = []
    for required in ("vault.json", "candidate-profile.json", "evidence-index.json"):
        if not (vault / required).exists():
            errors.append(f"missing:{required}")
    index = load_json(vault / "evidence-index.json", {"sources": []})
    for record in index.get("sources", []):
        if record.get("mode") == "copy":
            stored = Path(record.get("stored_path") or "")
            if not stored.is_file():
                errors.append(f"missing_source:{record.get('id')}")
            elif record.get("sha256") != sha256(stored):
                errors.append(f"hash_mismatch:{record.get('id')}")
    result = {"valid": not errors, "errors": errors, "source_count": len(index.get("sources", []))}
    print(json.dumps(result, ensure_ascii=False))
    if errors:
        raise SystemExit(1)


def command_show(args):
    vault = args.vault_dir.resolve()
    meta = load_json(vault / "vault.json", {})
    profile = load_json(vault / "candidate-profile.json", {})
    index = load_json(vault / "evidence-index.json", {"sources": []})
    print(json.dumps({
        "vault": str(vault),
        "candidate_id": meta.get("candidate_id"),
        "candidate_name": meta.get("candidate_name"),
        "profile_status": profile.get("status"),
        "source_count": len(index.get("sources", [])),
    }, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init")
    init.add_argument("--vault-dir", type=Path, required=True)
    init.add_argument("--candidate-id", required=True)
    init.add_argument("--name", required=True)
    init.set_defaults(func=command_init)

    add = sub.add_parser("add-source")
    add.add_argument("--vault-dir", type=Path, required=True)
    add.add_argument("--file", type=Path, required=True)
    add.add_argument("--type", required=True, choices=[
        "resume", "paper", "code", "portfolio", "transcript", "certificate",
        "patent", "presentation", "report", "writing_sample", "other",
    ])
    add.add_argument("--label")
    add.add_argument("--mode", choices=["copy", "reference"], default="copy")
    add.set_defaults(func=command_add_source)

    validate = sub.add_parser("validate")
    validate.add_argument("--vault-dir", type=Path, required=True)
    validate.set_defaults(func=command_validate)

    show = sub.add_parser("show")
    show.add_argument("--vault-dir", type=Path, required=True)
    show.set_defaults(func=command_show)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
