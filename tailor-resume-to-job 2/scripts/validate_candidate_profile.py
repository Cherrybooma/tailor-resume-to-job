#!/usr/bin/env python3
"""校验个人事实库的最小结构和证据完整性。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


VALID_STATES = {"confirmed", "ambiguous", "conflicting", "unsupported"}


def load_profile(path: Path) -> dict:
    if path.suffix.lower() != ".json":
        raise ValueError("个人事实库必须使用 .json 格式")
    return json.loads(path.read_text(encoding="utf-8"))


def iter_fact_groups(candidate: dict):
    for section in ("experience", "case_studies", "projects", "research"):
        for item in candidate.get(section, []) or []:
            yield section, item


def validate(profile: dict) -> list[str]:
    errors: list[str] = []
    if not isinstance(profile, dict):
        return ["事实库根节点必须是对象。"]
    if profile.get("profile_version") != 1:
        errors.append("profile_version 必须为 1。")
    if profile.get("status") not in {"draft", "confirmed"}:
        errors.append("status 必须为 draft 或 confirmed。")
    candidate = profile.get("candidate")
    if not isinstance(candidate, dict):
        return errors + ["candidate 必须是对象。"]
    if not candidate.get("name"):
        errors.append("candidate.name 为必填字段。")

    fact_ids: set[str] = set()
    for section, item in iter_fact_groups(candidate):
        item_id = item.get("id")
        if not item_id:
            errors.append(f"{section} 条目缺少 id。")
        for fact in item.get("facts", []) or []:
            fact_id = fact.get("id")
            if not fact_id:
                errors.append(f"{section}/{item_id or '?'} 的事实缺少 id。")
            elif fact_id in fact_ids:
                errors.append(f"事实 id 重复：{fact_id}。")
            else:
                fact_ids.add(fact_id)
            state = fact.get("state")
            if state not in VALID_STATES:
                errors.append(f"{fact_id or '?'} 的 state 无效：{state!r}。")
            if state == "confirmed" and not fact.get("evidence"):
                errors.append(f"{fact_id or '?'} 已标为 confirmed，但没有 evidence。")
            if not fact.get("statement"):
                errors.append(f"{fact_id or '?'} 缺少 statement。")

    for skill in candidate.get("skills", []) or []:
        if skill.get("state") == "confirmed" and not (skill.get("evidence_fact_ids") or skill.get("evidence")):
            errors.append(f"已确认技能 {skill.get('name', '?')} 没有 evidence_fact_ids 或直接 evidence。")
        for fact_id in skill.get("evidence_fact_ids", []) or []:
            if fact_id not in fact_ids:
                errors.append(f"技能 {skill.get('name', '?')} 引用了不存在的事实 {fact_id}。")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("profile", type=Path)
    args = parser.parse_args()
    try:
        profile = load_profile(args.profile)
        errors = validate(profile)
    except Exception as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(f"错误：{error}")
        return 1
    print("个人事实库校验通过。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
