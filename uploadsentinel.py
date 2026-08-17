#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
import argparse
import csv
import difflib
import hashlib
import html
import json
import re
import sys
import time
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import urljoin, urlparse

try:
    import requests
except ImportError:
    requests = None


PNG_1X1 = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR"
    b"\x00\x00\x00\x01"
    b"\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00"
    b"\x1f\x15\xc4\x89"
    b"\x00\x00\x00\rIDAT"
    b"\x08\xd7c\xf8\xcf\xc0\xf0\x1f\x00\x05\x00\x01\xff"
    b"\x89\x99=\x1d"
    b"\x00\x00\x00\x00IEND\xaeB`\x82"
)
GIF_MINIMAL = (
    b"GIF89a\x01\x00\x01\x00\x80\x00\x00"
    b"\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,"
    b"\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
)
TEXT_PAYLOAD = b"UPLOAD_SENTINEL_SAFE_TEST\nNo executable content is present.\n"
JSON_PAYLOAD = b'{"uploadSentinel":"safe-test","executable":false}\n'
CSV_PAYLOAD = b"name,value\nupload_sentinel,safe_test\n"
SVG_SAFE = (
    b'<svg xmlns="http://www.w3.org/2000/svg" width="1" height="1">'
    b'<rect width="1" height="1"/></svg>'
)
PDF_MINIMAL = b"%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF\n"

SUCCESS_MARKERS = [
    "upload success", "uploaded successfully", "successfully uploaded",
    '"success":true', '"success": true', '"code":0', '"code": 0',
    "上传成功", "上传完成", "上传成功！"
]
REJECT_MARKERS = [
    "unsupported file", "invalid file", "not allowed", "forbidden extension",
    "invalid extension", "invalid mime", "file type is not allowed",
    "上传失败", "文件类型不支持", "非法文件", "格式不支持", "不允许上传"
]

URL_RE = re.compile(r'(?i)(https?://[^\s"\'<>\\]+|/[A-Za-z0-9_\-./%?=&]+)')


@dataclass
class UploadCase:
    category: str
    name: str
    filename: str
    content_type: str
    content: bytes
    description: str
    enabled: bool = True


@dataclass
class RawRequest:
    method: str
    target: str
    http_version: str
    headers: Dict[str, str]
    body: bytes

    @property
    def host(self) -> str:
        for k, v in self.headers.items():
            if k.lower() == "host":
                return v.strip()
        return ""

    def infer_url(self, scheme="https") -> str:
        if self.target.startswith(("http://", "https://")):
            return self.target
        if not self.host:
            raise ValueError("Raw request has no Host header and no absolute URL")
        return f"{scheme}://{self.host}{self.target}"


@dataclass
class Result:
    case: str
    category: str
    filename: str
    content_type: str
    status_code: int
    elapsed_ms: int
    response_bytes: int
    response_sha256: str
    redirected: bool
    final_url: str
    similarity_to_baseline: float
    possible_refs: List[str]
    ref_checks: List[dict]
    verdict: str
    score: int
    notes: str
    response_preview: str
    diff_preview: str
    cluster_id: int = 0
    matched_rules: List[str] = field(default_factory=list)
    manual_state: str = "UNREVIEWED"



@dataclass
class RuleConfig:
    """User-defined, non-payload verdict hints."""
    success_regex: List[str] = field(default_factory=list)
    reject_regex: List[str] = field(default_factory=list)
    success_status: List[int] = field(default_factory=list)
    reject_status: List[int] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]):
        data = data or {}
        return cls(
            success_regex=[str(x) for x in data.get("success_regex", []) if str(x).strip()],
            reject_regex=[str(x) for x in data.get("reject_regex", []) if str(x).strip()],
            success_status=[int(x) for x in data.get("success_status", []) if str(x).strip()],
            reject_status=[int(x) for x in data.get("reject_status", []) if str(x).strip()],
        )

    def to_dict(self):
        return asdict(self)


def _regex_matches(patterns: List[str], text: str) -> List[str]:
    matched = []
    for pattern in patterns:
        try:
            if re.search(pattern, text, re.I | re.M):
                matched.append(pattern)
        except re.error:
            # Invalid patterns are ignored by the engine and should be validated by the UI.
            continue
    return matched


def cluster_results(results: List[Result], threshold: float = 0.92) -> List[Result]:
    """
    Lightweight response clustering for triage.
    Uses status + normalized response-preview similarity; no external ML dependency.
    """
    representatives = []
    next_id = 1

    for result in results:
        if result.status_code == 0:
            result.cluster_id = 0
            continue

        current = normalize_body(result.response_preview.encode("utf-8", "replace"))
        assigned = False
        for cluster_id, status, rep in representatives:
            if status != result.status_code:
                continue
            if text_similarity(current, rep) >= threshold:
                result.cluster_id = cluster_id
                assigned = True
                break

        if not assigned:
            result.cluster_id = next_id
            representatives.append((next_id, result.status_code, current))
            next_id += 1

    return results


def result_from_dict(data: Dict[str, Any]) -> Result:
    """Backward-compatible Result deserialization for old history/project exports."""
    defaults = {
        "case": "", "category": "", "filename": "", "content_type": "",
        "status_code": 0, "elapsed_ms": 0, "response_bytes": 0,
        "response_sha256": "", "redirected": False, "final_url": "",
        "similarity_to_baseline": 0.0, "possible_refs": [], "ref_checks": [],
        "verdict": "UNKNOWN", "score": 0, "notes": "",
        "response_preview": "", "diff_preview": "", "cluster_id": 0,
        "matched_rules": [], "manual_state": "UNREVIEWED"
    }
    defaults.update(data or {})
    return Result(**defaults)

def ensure_requests():
    if requests is None:
        raise RuntimeError("Missing dependency: requests. Install with: pip install requests")


def build_safe_cases() -> List[UploadCase]:
    return [
        UploadCase("baseline","png_baseline","sentinel.png","image/png",PNG_1X1,"Normal PNG baseline"),
        UploadCase("baseline","gif_baseline","sentinel.gif","image/gif",GIF_MINIMAL,"Normal GIF baseline"),
        UploadCase("baseline","txt_baseline","sentinel.txt","text/plain",TEXT_PAYLOAD,"Normal text baseline"),
        UploadCase("filename","upper_extension","sentinel.PNG","image/png",PNG_1X1,"Uppercase extension"),
        UploadCase("filename","mixed_extension","sentinel.PnG","image/png",PNG_1X1,"Mixed-case extension"),
        UploadCase("filename","double_extension","sentinel.txt.png","image/png",PNG_1X1,"Double extension"),
        UploadCase("filename","triple_extension","sentinel.safe.txt.png","image/png",PNG_1X1,"Triple extension"),
        UploadCase("filename","spaces","safe upload test.png","image/png",PNG_1X1,"Spaces in filename"),
        UploadCase("filename","unicode","安全上传测试.png","image/png",PNG_1X1,"Unicode filename"),
        UploadCase("filename","long_name",("a"*140)+".png","image/png",PNG_1X1,"Long filename"),
        UploadCase("filename","leading_dot",".sentinel.png","image/png",PNG_1X1,"Leading dot filename"),
        UploadCase("filename","many_dots","safe...test...png.png","image/png",PNG_1X1,"Many dots in filename"),
        UploadCase("mime","png_octet_stream","sentinel.png","application/octet-stream",PNG_1X1,"Valid PNG, generic MIME"),
        UploadCase("mime","png_text_plain","sentinel.png","text/plain",PNG_1X1,"Valid PNG, text/plain MIME"),
        UploadCase("mime","txt_claim_png","sentinel.png","image/png",TEXT_PAYLOAD,"Text body claiming image/png"),
        UploadCase("mime","png_claim_txt","sentinel.txt","text/plain",PNG_1X1,"PNG body claiming text/plain"),
        UploadCase("mime","gif_claim_png","sentinel.png","image/png",GIF_MINIMAL,"GIF body claiming PNG"),
        UploadCase("type","json_file","sentinel.json","application/json",JSON_PAYLOAD,"JSON handling"),
        UploadCase("type","csv_file","sentinel.csv","text/csv",CSV_PAYLOAD,"CSV handling"),
        UploadCase("type","svg_safe","sentinel.svg","image/svg+xml",SVG_SAFE,"Static SVG with no script"),
        UploadCase("type","pdf_safe","sentinel.pdf","application/pdf",PDF_MINIMAL,"Minimal benign PDF"),
        UploadCase("type","unknown_ext","sentinel.unknown","application/octet-stream",TEXT_PAYLOAD,"Unknown extension"),
        UploadCase("type","no_extension","sentinel","application/octet-stream",TEXT_PAYLOAD,"No extension"),
        UploadCase("content","empty_png","sentinel.png","image/png",b"","Empty file claiming PNG"),
        UploadCase("content","tiny_text","sentinel.txt","text/plain",b"A","One-byte text file"),
        UploadCase("content","png_trailing_text","sentinel.png","image/png",PNG_1X1+b"\nSAFE_TRAILER\n","PNG with harmless trailing bytes"),
    ]


def custom_case_from_text(name: str, category: str, filename: str, content_type: str, content: str) -> UploadCase:
    return UploadCase(category or "custom", name, filename, content_type, content.encode("utf-8"), "Custom benign text payload")


def parse_raw_request(text: str) -> RawRequest:
    normalized = text.replace("\r\n", "\n")
    head, _, body = normalized.partition("\n\n")
    lines = head.split("\n")
    if not lines or len(lines[0].split()) < 2:
        raise ValueError("Invalid raw HTTP request line")
    parts = lines[0].split()
    method, target = parts[0], parts[1]
    version = parts[2] if len(parts) > 2 else "HTTP/1.1"
    headers = {}
    current = None
    for line in lines[1:]:
        if not line:
            continue
        if line[:1] in (" ", "\t") and current:
            headers[current] += " " + line.strip()
            continue
        if ":" in line:
            k, v = line.split(":", 1)
            current = k.strip()
            headers[current] = v.strip()
    return RawRequest(method, target, version, headers, body.encode("utf-8", "replace"))


def parse_cookie_header(cookie: str) -> Dict[str, str]:
    out = {}
    for part in cookie.split(";"):
        if "=" in part:
            k, v = part.strip().split("=", 1)
            out[k] = v
    return out


def headers_without_transport(headers: Dict[str, str]) -> Dict[str, str]:
    banned = {"content-length","host","connection","transfer-encoding"}
    return {k:v for k,v in headers.items() if k.lower() not in banned}


def extract_form_fields_from_multipart(raw: RawRequest, file_field_hint="file") -> Tuple[Dict[str,str],str]:
    ctype = next((v for k,v in raw.headers.items() if k.lower()=="content-type"), "")
    m = re.search(r'boundary="?([^";]+)', ctype, re.I)
    if not m:
        return {}, file_field_hint
    boundary = m.group(1).encode()
    fields, file_field = {}, file_field_hint
    for part in raw.body.split(b"--"+boundary):
        if b"\r\n\r\n" in part:
            ph,pb = part.split(b"\r\n\r\n",1)
        elif b"\n\n" in part:
            ph,pb = part.split(b"\n\n",1)
        else:
            continue
        hs = ph.decode("utf-8","replace")
        n = re.search(r'name="([^"]+)"', hs, re.I)
        if not n:
            continue
        name = n.group(1)
        if re.search(r'filename="[^"]*"', hs, re.I):
            file_field = name
        else:
            fields[name] = pb.rstrip(b"\r\n").decode("utf-8","replace")
    return fields, file_field


def normalize_body(body: bytes) -> bytes:
    s = body[:300000]
    s = re.sub(rb'\b[0-9a-f]{32,64}\b', b'<HEX>', s, flags=re.I)
    s = re.sub(rb'\b\d{10,13}\b', b'<TS>', s)
    s = re.sub(rb'(?i)(requestId|traceId|timestamp)["\':=\s]+[A-Za-z0-9_.:-]+', b'<DYNAMIC>', s)
    return s


def text_similarity(a: bytes, b: bytes) -> float:
    if a == b:
        return 1.0
    ta = set(re.findall(rb'[A-Za-z0-9_\-]{3,}', a[:200000].lower()))
    tb = set(re.findall(rb'[A-Za-z0-9_\-]{3,}', b[:200000].lower()))
    union = ta | tb
    jac = len(ta & tb)/len(union) if union else 0.0
    lr = min(len(a),len(b))/max(len(a),len(b),1)
    return round(jac*0.75 + lr*0.25, 4)


def make_diff(base: bytes, current: bytes, max_lines=80) -> str:
    a = normalize_body(base).decode("utf-8","replace").splitlines()
    b = normalize_body(current).decode("utf-8","replace").splitlines()
    d = list(difflib.unified_diff(a,b,fromfile="baseline",tofile="current",lineterm=""))
    if len(d) > max_lines:
        d = d[:max_lines] + [f"... truncated, {len(d)-max_lines} more lines ..."]
    return "\n".join(d)


def _same_origin(a: str, b: str) -> bool:
    pa, pb = urlparse(a), urlparse(b)
    def port(p):
        if p.port:
            return p.port
        return 443 if p.scheme == "https" else 80
    return (
        pa.scheme.lower() == pb.scheme.lower()
        and (pa.hostname or "").lower() == (pb.hostname or "").lower()
        and port(pa) == port(pb)
    )


def _looks_like_upload_ref(value: str) -> bool:
    low = value.lower()
    if low.startswith(("javascript:", "data:", "mailto:", "#")):
        return False
    parsed = urlparse(value)
    path = parsed.path.lower()
    useful_tokens = (
        "upload", "download", "attachment", "file", "media", "resource",
        "document", "image", "avatar", "oss", "object", "storage"
    )
    useful_exts = (
        ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".pdf",
        ".txt", ".csv", ".json", ".xml", ".bin", ".dat"
    )
    return path.endswith(useful_exts) or any(tok in path for tok in useful_tokens)


def extract_refs(resp, base_url: str) -> List[str]:
    """Extract likely uploaded-file references while reducing generic HTML-path noise."""
    refs = []

    # JSON values are higher-confidence because upload APIs commonly return path/url fields.
    try:
        data = resp.json()
        def walk(x, key_hint=""):
            if isinstance(x, dict):
                for k, v in x.items():
                    walk(v, str(k).lower())
            elif isinstance(x, list):
                for v in x:
                    walk(v, key_hint)
            elif isinstance(x, str) and x.startswith(("http://", "https://", "/")):
                if (
                    _looks_like_upload_ref(x)
                    or any(t in key_hint for t in ("url", "path", "file", "download", "upload", "uri", "location"))
                ):
                    refs.append(urljoin(base_url, x))
        walk(data)
    except Exception:
        pass

    # Free text/HTML is much noisier, so only keep file/upload-looking references.
    try:
        for x in URL_RE.findall(resp.text[:200000]):
            if _looks_like_upload_ref(x):
                refs.append(urljoin(base_url, x))
    except Exception:
        pass

    out, seen = [], set()
    for x in refs:
        if x not in seen and urlparse(x).scheme in ("http", "https"):
            seen.add(x)
            out.append(x)
    return out[:30]


def verify_refs(session, refs: List[str], base_url: str, timeout=8,
                verify_tls=True, max_refs=3, allow_cross_origin=False) -> List[dict]:
    """
    Verify returned references conservatively.
    - Only same-origin references are requested by default.
    - Redirects are NOT automatically followed, preventing an in-scope URL from
      redirecting the scanner to an unrelated third-party host.
    """
    checks = []
    for ref in refs[:max_refs]:
        item = {
            "url": ref, "method": "", "status": 0, "content_type": "",
            "bytes": 0, "error": "", "skipped": False, "location": ""
        }

        if not allow_cross_origin and not _same_origin(base_url, ref):
            item["skipped"] = True
            item["error"] = "cross-origin reference skipped"
            checks.append(item)
            continue

        try:
            r = session.head(
                ref, timeout=timeout, verify=verify_tls,
                allow_redirects=False
            )
            item.update(
                method="HEAD",
                status=r.status_code,
                content_type=r.headers.get("Content-Type", ""),
                bytes=int(r.headers.get("Content-Length", "0") or 0),
                location=r.headers.get("Location", "")
            )

            if r.status_code in (405, 501) or r.status_code >= 500:
                r = session.get(
                    ref, timeout=timeout, verify=verify_tls,
                    allow_redirects=False, stream=True
                )
                chunk = next(r.iter_content(4096), b"")
                item.update(
                    method="GET",
                    status=r.status_code,
                    content_type=r.headers.get("Content-Type", ""),
                    bytes=len(chunk),
                    location=r.headers.get("Location", "")
                )
        except Exception as e:
            item["error"] = str(e)
        checks.append(item)
    return checks

def response_preview(resp, body: bytes, limit=4000) -> str:
    ctype = (resp.headers.get("Content-Type", "") or "").lower()
    textual = (
        ctype.startswith("text/")
        or "json" in ctype
        or "xml" in ctype
        or "javascript" in ctype
        or "html" in ctype
    )
    if textual:
        return body[:limit].decode(resp.encoding or "utf-8", "replace")
    sample = body[:256]
    return (
        f"[binary response]\\nContent-Type: {ctype or 'unknown'}\\n"
        f"Length: {len(body)} bytes\\nSHA256: {hashlib.sha256(body).hexdigest()}\\n\\n"
        f"First {len(sample)} bytes (hex):\\n{sample.hex(' ')}"
    )

def verdict_for(case, status, body, refs, ref_checks, baseline_status, similarity,
                rules: Optional[RuleConfig] = None):
    low = body[:100000].decode("utf-8","ignore").lower()
    rules = rules or RuleConfig()
    matched_rules = []

    # User reject rules are intentionally evaluated before built-in acceptance hints.
    reject_regex_hits = _regex_matches(rules.reject_regex, low)
    if status in rules.reject_status:
        matched_rules.append(f"reject_status:{status}")
    matched_rules += [f"reject_regex:{x}" for x in reject_regex_hits]
    if matched_rules:
        return "REJECTED", 20, "Matched custom reject rule", matched_rules

    if status >= 500:
        return "ERROR",5,"Server error", matched_rules
    if status in (401,403,429):
        return "BLOCKED",10,"Authentication/WAF/rate-limit response", matched_rules
    if status >= 400:
        return "REJECTED",15,f"HTTP {status}", matched_rules
    if any(m.lower() in low for m in REJECT_MARKERS):
        return "REJECTED",20,"Application rejection marker", matched_rules

    success_regex_hits = _regex_matches(rules.success_regex, low)
    if status in rules.success_status:
        matched_rules.append(f"success_status:{status}")
    matched_rules += [f"success_regex:{x}" for x in success_regex_hits]

    explicit_success = any(m.lower() in low for m in SUCCESS_MARKERS)
    if case.category == "baseline":
        return "BASELINE",0,"Baseline request completed", matched_rules

    score, reasons = 20, []
    if explicit_success:
        score += 25; reasons.append("success marker")
    if matched_rules:
        score += 25; reasons.append("custom success rule")
    if refs:
        score += 15; reasons.append("returned path/URL")
    if any(x.get("status") in (200,206,301,302,303,307,308) for x in ref_checks if not x.get("skipped")):
        score += 15; reasons.append("returned reference responded")
    if baseline_status is not None and status == baseline_status:
        score += 10; reasons.append("same status as baseline")
    if similarity >= .90:
        score += 20; reasons.append(f"high baseline similarity {similarity:.2f}")
    elif similarity >= .70:
        score += 10; reasons.append(f"moderate similarity {similarity:.2f}")

    if score >= 70:
        return "HIGH_REVIEW",min(score,100),", ".join(reasons), matched_rules
    if score >= 50:
        return "REVIEW",min(score,100),", ".join(reasons), matched_rules
    return "UNKNOWN",min(score,100),", ".join(reasons) or "No reliable indicator", matched_rules


class Scanner:
    def __init__(self,url,field_name="file",method="POST",data=None,headers=None,cookies=None,
                 proxy=None,timeout=15,verify_tls=True,allow_redirects=True,delay=.25,
                 verify_returned_refs=True,rules=None,cluster_threshold=.92):
        ensure_requests()
        self.url=url; self.field_name=field_name; self.method=method.upper()
        self.data=data or {}; self.headers=headers or {}; self.cookies=cookies or {}
        self.proxy=proxy; self.timeout=timeout; self.verify_tls=verify_tls
        self.allow_redirects=allow_redirects; self.delay=max(0,delay)
        self.verify_returned_refs=verify_returned_refs
        self.rules = rules if isinstance(rules, RuleConfig) else RuleConfig.from_dict(rules)
        self.cluster_threshold = min(max(float(cluster_threshold), .50), 1.0)
        self.session=requests.Session()
        self.session.cookies.update(self.cookies)
        if proxy:
            self.session.proxies.update({"http":proxy,"https":proxy})

    @classmethod
    def from_raw_request(cls,raw_text,scheme="https",file_field_hint="file",proxy=None,timeout=15,
                         verify_tls=True,delay=.25,verify_returned_refs=True,rules=None,
                         cluster_threshold=.92):
        raw=parse_raw_request(raw_text)
        fields,file_field=extract_form_fields_from_multipart(raw,file_field_hint)
        headers=headers_without_transport(raw.headers)
        cookie=next((v for k,v in raw.headers.items() if k.lower()=="cookie"),"")
        cookies=parse_cookie_header(cookie)
        headers={k:v for k,v in headers.items() if k.lower() not in ("content-type","cookie")}
        return cls(raw.infer_url(scheme),file_field,raw.method,fields,headers,cookies,proxy,timeout,
                   verify_tls,True,delay,verify_returned_refs,rules,cluster_threshold)

    def run(self,cases=None,progress=None):
        cases=[c for c in (cases or build_safe_cases()) if c.enabled]
        ordered=sorted(cases,key=lambda x:0 if x.name=="png_baseline" else 1)
        results=[]; baseline_status=None; baseline_body=None
        for idx,case in enumerate(ordered,1):
            files={self.field_name:(case.filename,case.content,case.content_type)}
            started=time.perf_counter()
            try:
                resp=self.session.request(self.method,self.url,data=self.data,files=files,headers=self.headers,
                                          timeout=self.timeout,verify=self.verify_tls,allow_redirects=self.allow_redirects)
                elapsed=int((time.perf_counter()-started)*1000)
                body=resp.content
                refs=extract_refs(resp,resp.url)
                if case.category=="baseline" and baseline_body is None:
                    baseline_status=resp.status_code; baseline_body=body
                sim=text_similarity(normalize_body(body),normalize_body(baseline_body)) if baseline_body is not None else 0.0
                ref_checks=verify_refs(self.session,refs,self.url,self.timeout,self.verify_tls) if (self.verify_returned_refs and refs) else []
                verdict,score,notes,matched_rules=verdict_for(
                    case,resp.status_code,body,refs,ref_checks,baseline_status,sim,self.rules
                )
                preview=response_preview(resp,body)
                diff=make_diff(baseline_body,body) if baseline_body is not None and case.name!="png_baseline" else ""
                r=Result(case.name,case.category,case.filename,case.content_type,resp.status_code,elapsed,len(body),
                         hashlib.sha256(body).hexdigest(),bool(resp.history),resp.url,sim,refs,ref_checks,
                         verdict,score,notes,preview,diff,0,matched_rules,"UNREVIEWED")
            except Exception as e:
                r=Result(case.name,case.category,case.filename,case.content_type,0,0,0,"",False,"",0.0,[],[],
                         "ERROR",0,str(e),"","",0,[],"UNREVIEWED")
            results.append(r)
            if progress: progress(idx,len(ordered),case,r)
            if idx != len(ordered): time.sleep(self.delay)
        return cluster_results(results, self.cluster_threshold)


def save_project(path, config, custom_cases):
    obj={"version":5,"config":config,"custom_cases":[
        {"category":c.category,"name":c.name,"filename":c.filename,"content_type":c.content_type,
         "content":c.content.decode("utf-8","replace"),"description":c.description,"enabled":c.enabled}
        for c in custom_cases
    ]}
    Path(path).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding="utf-8")


def load_project(path):
    obj=json.loads(Path(path).read_text(encoding="utf-8"))
    custom=[]
    for x in obj.get("custom_cases",[]):
        custom.append(UploadCase(x.get("category","custom"),x["name"],x["filename"],x["content_type"],
                                 x.get("content","").encode("utf-8"),x.get("description","Custom"),x.get("enabled",True)))
    return obj.get("config",{}), custom



def default_history_path() -> Path:
    return Path.home() / ".uploadsentinel" / "history.json"


def load_history(path: Optional[str] = None, limit=30) -> List[dict]:
    p = Path(path) if path else default_history_path()
    if not p.exists():
        return []
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            return []
        out = []
        for item in raw[-limit:]:
            if not isinstance(item, dict):
                continue
            results = [result_from_dict(x) for x in item.get("results", []) if isinstance(x, dict)]
            out.append({
                "time": item.get("time", ""),
                "target": item.get("target", ""),
                "count": int(item.get("count", len(results))),
                "review": int(item.get("review", 0)),
                "results": results
            })
        return out
    except Exception:
        return []


def save_history(entries: List[dict], path: Optional[str] = None, limit=30):
    p = Path(path) if path else default_history_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    serializable = []
    for item in (entries or [])[-limit:]:
        serializable.append({
            "time": item.get("time",""),
            "target": item.get("target",""),
            "count": item.get("count",0),
            "review": item.get("review",0),
            "results": [asdict(r) if isinstance(r, Result) else r for r in item.get("results",[])]
        })
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(serializable, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(p)


def append_history(entry: dict, path: Optional[str] = None, limit=30):
    p = Path(path) if path else default_history_path()
    existing = load_history(str(p), limit=limit)
    existing.append(entry)
    save_history(existing, str(p), limit=limit)


def clear_history(path: Optional[str] = None):
    p = Path(path) if path else default_history_path()
    if p.exists():
        p.unlink()

def save_json(results,path):
    Path(path).write_text(json.dumps([asdict(x) for x in results],ensure_ascii=False,indent=2),encoding="utf-8")

def save_csv(results,path):
    with open(path,"w",encoding="utf-8-sig",newline="") as f:
        w=csv.writer(f)
        w.writerow(["case","category","filename","content_type","status_code","elapsed_ms","response_bytes",
                    "similarity_to_baseline","cluster_id","verdict","score","manual_state","matched_rules",
                    "final_url","possible_refs","ref_checks","notes","response_sha256"])
        for r in results:
            w.writerow([r.case,r.category,r.filename,r.content_type,r.status_code,r.elapsed_ms,r.response_bytes,
                        r.similarity_to_baseline,r.cluster_id,r.verdict,r.score,r.manual_state,
                        " | ".join(r.matched_rules),r.final_url," | ".join(r.possible_refs),
                        json.dumps(r.ref_checks,ensure_ascii=False),r.notes,r.response_sha256])

def save_html(results,path,target):
    rows=[]
    for r in sorted(results,key=lambda x:(x.manual_state=="CONFIRMED",x.score),reverse=True):
        refs="<br>".join(html.escape(x) for x in r.possible_refs[:5])
        rules="<br>".join(html.escape(x) for x in r.matched_rules[:8])
        rows.append(
            "<tr>"
            f"<td>{html.escape(r.verdict)}</td>"
            f"<td>{r.score}</td>"
            f"<td>{r.cluster_id}</td>"
            f"<td>{html.escape(r.manual_state)}</td>"
            f"<td>{html.escape(r.category)}</td>"
            f"<td>{html.escape(r.case)}</td>"
            f"<td>{html.escape(r.filename)}</td>"
            f"<td>{html.escape(r.content_type)}</td>"
            f"<td>{r.status_code}</td>"
            f"<td>{r.elapsed_ms}</td>"
            f"<td>{r.response_bytes}</td>"
            f"<td>{r.similarity_to_baseline:.2f}</td>"
            f"<td>{refs}</td>"
            f"<td>{rules}</td>"
            f"<td>{html.escape(r.notes)}</td>"
            "</tr>"
        )
    doc=f"""<!doctype html><html><head><meta charset="utf-8"><title>UploadSentinel v1.0 Report</title>
<style>
body{{font-family:Arial;margin:26px;background:#f6f7f9;color:#222}}
table{{border-collapse:collapse;width:100%;background:white}}
th,td{{border:1px solid #ddd;padding:7px;font-size:13px;vertical-align:top}}
th{{background:#eee;position:sticky;top:0}}
</style></head><body>
<h1>UploadSentinel v1.0 Report</h1><p>Target: {html.escape(target)}</p>
<p><b>REVIEW/HIGH_REVIEW means manual verification is recommended; it is not a confirmed vulnerability.</b></p>
<table><thead><tr>
<th>Verdict</th><th>Score</th><th>Cluster</th><th>Manual</th><th>Category</th><th>Case</th>
<th>Filename</th><th>MIME</th><th>HTTP</th><th>ms</th><th>Bytes</th><th>Similarity</th>
<th>Refs</th><th>Matched rules</th><th>Notes</th>
</tr></thead><tbody>{''.join(rows)}</tbody></table></body></html>"""
    Path(path).write_text(doc,encoding="utf-8")


def parse_kv(items):
    out={}
    for item in items or []:
        if "=" not in item: raise ValueError(f"Expected KEY=VALUE: {item}")
        k,v=item.split("=",1); out[k]=v
    return out


def cli():
    ap=argparse.ArgumentParser(description="UploadSentinel v1.0")
    src=ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--url"); src.add_argument("--raw-request")
    ap.add_argument("--scheme",default="https",choices=["http","https"])
    ap.add_argument("-f","--field",default="file")
    ap.add_argument("-X","--method",default="POST",choices=["POST","PUT","PATCH"])
    ap.add_argument("-d","--data",action="append"); ap.add_argument("-H","--header",action="append")
    ap.add_argument("--cookie",action="append"); ap.add_argument("--proxy")
    ap.add_argument("--timeout",type=int,default=15); ap.add_argument("--delay",type=float,default=.25)
    ap.add_argument("-k","--insecure",action="store_true")
    ap.add_argument("--no-ref-check",action="store_true")
    ap.add_argument("--category",action="append")
    ap.add_argument("-o","--output",default="uploadsentinel-v5-results")
    args=ap.parse_args()

    if args.raw_request:
        raw=Path(args.raw_request).read_text(encoding="utf-8",errors="replace")
        scanner=Scanner.from_raw_request(raw,args.scheme,args.field,args.proxy,args.timeout,not args.insecure,args.delay,not args.no_ref_check)
    else:
        scanner=Scanner(args.url,args.field,args.method,parse_kv(args.data),parse_kv(args.header),parse_kv(args.cookie),
                        args.proxy,args.timeout,not args.insecure,True,args.delay,not args.no_ref_check)
    cases=build_safe_cases()
    if args.category:
        wanted=set(args.category); cases=[x for x in cases if x.category in wanted]
    def prog(i,n,c,r):
        print(f"[{i:02}/{n:02}] {r.verdict:11} score={r.score:3} HTTP={r.status_code:<3} sim={r.similarity_to_baseline:.2f} {c.name}")
    results=scanner.run(cases,prog)
    save_json(results,args.output+".json"); save_csv(results,args.output+".csv"); save_html(results,args.output+".html",scanner.url)
    print(f"Saved: {args.output}.json / .csv / .html")

if __name__=="__main__":
    cli()
