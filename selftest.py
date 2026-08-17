#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import tempfile
from pathlib import Path

from uploadsentinel import (
    UploadCase, Result, RuleConfig, verdict_for, cluster_results,
    append_history, load_history, load_project, parse_raw_request,
    extract_form_fields_from_multipart
)


def result(case, status, preview):
    return Result(
        case=case, category="test", filename="a.txt", content_type="text/plain",
        status_code=status, elapsed_ms=1, response_bytes=len(preview),
        response_sha256="", redirected=False, final_url="",
        similarity_to_baseline=0.0, possible_refs=[], ref_checks=[],
        verdict="UNKNOWN", score=0, notes="", response_preview=preview,
        diff_preview=""
    )


def check(name, condition):
    if not condition:
        raise AssertionError(name)
    print("[PASS]", name)


case = UploadCase("custom", "rule_test", "a.txt", "text/plain", b"x", "test")
rules = RuleConfig(
    success_regex=[r'"ok"\s*:\s*true'],
    reject_regex=[r"blocked"],
    success_status=[201],
    reject_status=[415],
)

v = verdict_for(case, 200, b'{"ok": true}', [], [], 200, .95, rules)
check("custom success regex", v[0] == "HIGH_REVIEW" and v[3])

v = verdict_for(case, 200, b'blocked {"ok": true}', [], [], 200, .95, rules)
check("reject rule has priority", v[0] == "REJECTED")

v = verdict_for(case, 415, b'x', [], [], 200, .1, rules)
check("reject status rule", v[0] == "REJECTED")

rs = cluster_results([
    result("a", 200, "same response hello"),
    result("b", 200, "same response hello!"),
    result("c", 400, "same response hello"),
], .80)
check("similar 200 responses cluster together", rs[0].cluster_id == rs[1].cluster_id)
check("different HTTP status separates cluster", rs[0].cluster_id != rs[2].cluster_id)

with tempfile.TemporaryDirectory() as td:
    hp = str(Path(td) / "history.json")
    append_history({
        "time": "now", "target": "https://example.test",
        "count": len(rs), "review": 1, "results": rs
    }, hp)
    loaded = load_history(hp)
    check("history roundtrip", len(loaded) == 1 and loaded[0]["results"][0].cluster_id > 0)

with tempfile.TemporaryDirectory() as td:
    p = Path(td) / "old.usproj"
    p.write_text(json.dumps({
        "version": 4.1,
        "config": {"url": "https://example.test"},
        "custom_cases": []
    }), encoding="utf-8")
    cfg, custom = load_project(str(p))
    check("v4 project compatibility", cfg["url"] == "https://example.test" and custom == [])

raw = (
    "POST /upload HTTP/1.1\r\n"
    "Host: example.test\r\n"
    "Content-Type: multipart/form-data; boundary=BOUND\r\n\r\n"
    "--BOUND\r\n"
    'Content-Disposition: form-data; name="bizCode"\r\n\r\n'
    "ABC-\r\n"
    "--BOUND\r\n"
    'Content-Disposition: form-data; name="file"; filename="a.png"\r\n'
    "Content-Type: image/png\r\n\r\n"
    "SAFE\r\n"
    "--BOUND--\r\n"
)
rr = parse_raw_request(raw)
fields, file_field = extract_form_fields_from_multipart(rr)
check("multipart trailing hyphen preserved", fields.get("bizCode") == "ABC-")
check("multipart file field detected", file_field == "file")

print("\nAll core self-tests passed.")
