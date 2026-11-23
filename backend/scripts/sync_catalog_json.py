"""
Daily Living Model Catalog Updater (SPEC-34).

Queries HuggingFace Hub for newly trending verified GGUF repositories,
selects the sweet-spot Q4_K_M quant (or best quantized fallback), extracts
real file sizes and LFS SHA-256 digests, and merges new entries over the
hand-curated `catalog/models.json` baseline without overwriting curated models.

Can update `catalog/models.json` in place OR generate a static GitHub Pages
bundle (`--site-dir _site`) containing `models.json`, `.nojekyll`, and `index.html`.

Usage (from repo root or backend/):
    python backend/scripts/sync_catalog_json.py
    python backend/scripts/sync_catalog_json.py --base catalog/models.json --site-dir _site --live-url https://contextuai.github.io/vesper/models.json
"""
from __future__ import annotations

import argparse
import copy
import html
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote

import httpx

REPO_ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = REPO_ROOT / "catalog" / "models.json"
DEFAULT_LIVE_URL = "https://contextuai.github.io/vesper/models.json"

VERIFIED_ORGS = (
    "qwen",
    "bartowski",
    "unsloth",
    "ggml-org",
    "lmstudio-community",
    "google",
    "mistralai",
)

ALLOWED_PIPELINES = {None, "", "text-generation", "image-text-to-text"}
DISALLOWED_TAGS = {
    "text-to-image",
    "text-to-video",
    "text-to-speech",
    "diffusers",
    "image-generation",
    "audio-to-audio",
    "automatic-speech-recognition",
    "feature-extraction",
    "sentence-similarity",
}

QUANT_PREFERENCE = (
    "Q4_K_M",
    "Q4_K_L",
    "Q4_K_S",
    "Q5_K_M",
    "Q5_K_S",
    "Q4_0",
    "IQ4_XS",
    "IQ4_NL",
    "Q6_K",
    "Q8_0",
)

_QUANT_TOKEN_RE = re.compile(
    r"(?:^|[^a-z0-9])("
    r"Q4_K_M|Q4_K_L|Q4_K_S|Q5_K_M|Q5_K_S|Q6_K|Q8_0|Q4_0|IQ4_XS|IQ4_NL|Q3_K_M|Q2_K|BF16|F16|F32"
    r")(?:[^a-z0-9]|$)",
    re.IGNORECASE,
)
_SPLIT_SHARD_RE = re.compile(r"-\d{5}-of-\d{5}\.gguf$", re.IGNORECASE)
_SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")

FAMILY_LOGOS = {
    "qwen": "https://cdn.simpleicons.org/alibabacloud/FF6A00",
    "gemma": "https://cdn.simpleicons.org/googlegemini/4285F4",
    "llama": "https://cdn.simpleicons.org/meta/0467DF",
    "deepseek": "https://cdn.simpleicons.org/deepseek/4D6BFE",
    "mistral": "https://cdn.simpleicons.org/mistralai/FA520F",
    "phi": "https://cdn.simpleicons.org/microsoft/00A4EF",
    "smollm": "https://cdn.simpleicons.org/huggingface/FFD21E",
}


def _infer_family(repo_id: str) -> str:
    low = repo_id.lower()
    for fam in ("qwen", "gemma", "llama", "deepseek", "mistral", "phi", "smollm"):
        if fam in low:
            return fam
    return "custom"


def _infer_params(name: str) -> tuple[str, float]:
    m = re.search(r"(\d+(?:\.\d+)?)\s*[bB]\b", name)
    if not m:
        return "7B", 7.0
    val = float(m.group(1))
    label = f"{int(val)}B" if val.is_integer() else f"{val}B"
    return label, val


def _slugify(repo_id: str) -> str:
    base = repo_id.split("/")[-1].lower()
    base = re.sub(r"-gguf$", "", base)
    return re.sub(r"[^a-z0-9]+", "-", base).strip("-")[:48]


def _infer_quantization(filename: str) -> Optional[str]:
    stem = filename.rsplit(".", 1)[0] if filename.lower().endswith(".gguf") else filename
    match = _QUANT_TOKEN_RE.search(stem)
    if not match:
        return None
    return match.group(1).upper()


def _extract_size_and_sha256(sibling: Dict[str, Any]) -> Tuple[int, Optional[str]]:
    if not isinstance(sibling, dict):
        return 0, None
    lfs = sibling.get("lfs") if isinstance(sibling.get("lfs"), dict) else {}
    raw_size = sibling.get("size") or lfs.get("size") or 0
    try:
        size_bytes = max(0, int(raw_size))
    except (TypeError, ValueError):
        size_bytes = 0

    raw_sha = lfs.get("sha256")
    sha256: Optional[str] = None
    if isinstance(raw_sha, str):
        cleaned = raw_sha.strip()
        if _SHA256_RE.fullmatch(cleaned):
            sha256 = cleaned.lower()
    return size_bytes, sha256


def _is_candidate_gguf(filename: str) -> bool:
    if not filename or "/" in filename or "\\" in filename:
        return False
    low = filename.lower()
    if not low.endswith(".gguf"):
        return False
    if _SPLIT_SHARD_RE.search(low):
        return False
    for blocked in ("mmproj", "imatrix", "vocab", "draft", "mtp-"):
        if blocked in low:
            return False
    return True


def _pick_q4km(siblings: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    candidates: List[Tuple[str, Dict[str, Any]]] = []
    for sib in siblings or []:
        if not isinstance(sib, dict):
            continue
        rfilename = str(sib.get("rfilename") or "")
        if not _is_candidate_gguf(rfilename):
            continue
        quant = _infer_quantization(rfilename)
        if quant in QUANT_PREFERENCE:
            candidates.append((quant, sib))

    for target_quant in QUANT_PREFERENCE:
        tier = [sib for q, sib in candidates if q == target_quant]
        if tier:
            # Prefer canonical filename over Unsloth dynamic quant if both appear
            for sib in tier:
                if "-ud-" not in str(sib.get("rfilename", "")).lower():
                    return sib
            return tier[0]
    return None


def _build_request_headers(url: str) -> Dict[str, str]:
    headers = {
        "User-Agent": "Vesper-Catalog-Sync/1.0",
        "Accept": "application/json",
    }
    if url.startswith("https://huggingface.co/"):
        token = (os.getenv("HF_TOKEN") or "").strip()
        if token:
            headers["Authorization"] = f"Bearer {token}"
    return headers


def _http_get_json(
    url: str,
    params: Optional[Dict[str, Any]] = None,
    timeout: float = 15.0,
    retries: int = 3,
) -> Any:
    headers = _build_request_headers(url)
    last_exc: Optional[Exception] = None
    for attempt in range(retries):
        try:
            resp = httpx.get(url, params=params, headers=headers, timeout=timeout)
            if resp.status_code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                time.sleep(min(2.0 ** attempt, 8.0))
                continue
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as exc:
            last_exc = exc
            if exc.response is not None and exc.response.status_code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                time.sleep(min(2.0 ** attempt, 8.0))
                continue
            raise
        except httpx.HTTPError as exc:
            last_exc = exc
            if attempt < retries - 1:
                time.sleep(min(2.0 ** attempt, 8.0))
                continue
            raise
    if last_exc is not None:
        raise last_exc
    raise RuntimeError(f"Failed to fetch JSON from {url}")


def _is_eligible_llm_repo(meta: Dict[str, Any]) -> bool:
    if not isinstance(meta, dict):
        return False
    if bool(meta.get("gated")) or bool(meta.get("private")) or bool(meta.get("disabled")):
        return False
    pipeline_tag = meta.get("pipeline_tag")
    if pipeline_tag not in ALLOWED_PIPELINES:
        return False
    raw_tags = meta.get("tags") or []
    tags = {str(t).strip().lower() for t in raw_tags if isinstance(t, str)}
    if tags & DISALLOWED_TAGS:
        return False
    return True


def _is_valid_catalog_entry(entry: Any) -> bool:
    return (
        isinstance(entry, dict)
        and bool(entry.get("id"))
        and bool(entry.get("name"))
        and bool(entry.get("hf_repo"))
        and bool(entry.get("hf_filename"))
    )


def _fetch_live_models(live_url: str) -> List[Dict[str, Any]]:
    try:
        data = _http_get_json(live_url, timeout=10.0, retries=2)
    except Exception:
        return []
    if isinstance(data, dict) and isinstance(data.get("models"), list):
        return [m for m in data["models"] if _is_valid_catalog_entry(m)]
    if isinstance(data, list):
        return [m for m in data if _is_valid_catalog_entry(m)]
    return []


def _render_site_html(payload: Dict[str, Any], baseline_ids: Optional[set[str]] = None) -> str:
    updated_at = html.escape(str(payload.get("updated_at") or ""))
    models = payload.get("models") or []
    curated = baseline_ids or set()
    rows_html: List[str] = []
    for model in models:
        mid = str(model.get("id") or "")
        name = html.escape(str(model.get("name") or mid))
        provider = html.escape(str(model.get("provider") or ""))
        params = html.escape(str(model.get("parameter_size") or ""))
        quant = html.escape(str(model.get("quantization") or "Q4_K_M"))
        size_gb = html.escape(f"{float(model.get('size_gb') or 0):.2f} GB")
        raw_sha = str(model.get("sha256") or "")
        sha_display = html.escape(raw_sha[:12] if raw_sha else "—")
        hf_repo = str(model.get("hf_repo") or "")
        hf_repo_esc = html.escape(hf_repo)
        hf_href = html.escape(f"https://huggingface.co/{quote(hf_repo, safe='/-_.')}")
        badge = "Curated" if (mid in curated or not model.get("is_new")) else "Trending"
        rows_html.append(
            "<tr>"
            f"<td><strong>{name}</strong></td>"
            f"<td>{provider}</td>"
            f"<td>{params}</td>"
            f"<td><code>{quant}</code></td>"
            f"<td>{size_gb}</td>"
            f"<td><code>{sha_display}</code></td>"
            f"<td><a href=\"{hf_href}\" rel=\"noopener noreferrer\">{hf_repo_esc}</a></td>"
            f"<td>{badge}</td>"
            "</tr>"
        )

    tbody = "\n      ".join(rows_html)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Vesper Living Model Catalog</title>
  <style>
    :root {{ color-scheme: light dark; font-family: system-ui, -apple-system, sans-serif; }}
    body {{ max-width: 1080px; margin: 2rem auto; padding: 0 1.25rem; line-height: 1.5; }}
    h1 {{ margin-bottom: 0.25rem; }}
    .meta {{ color: #6b7280; margin-bottom: 1.5rem; font-size: 0.95rem; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 0.9rem; }}
    th, td {{ text-align: left; padding: 0.6rem 0.75rem; border-bottom: 1px solid rgba(128,128,128,0.25); }}
    th {{ font-weight: 600; }}
    code {{ font-size: 0.85em; }}
  </style>
</head>
<body>
  <h1>Vesper Living Model Catalog</h1>
  <p class="meta">
    Updated: <code>{updated_at}</code> &middot;
    Models: <strong>{len(models)}</strong> &middot;
    JSON Manifest: <a href="./models.json"><code>models.json</code></a>
  </p>
  <table>
    <thead>
      <tr>
        <th>Model</th>
        <th>Provider</th>
        <th>Params</th>
        <th>Quant</th>
        <th>Size</th>
        <th>SHA-256</th>
        <th>HuggingFace Repo</th>
        <th>Tier</th>
      </tr>
    </thead>
    <tbody>
      {tbody}
    </tbody>
  </table>
</body>
</html>
"""


def sync_catalog(
    limit: int = 30,
    max_new: int = 5,
    base_path: Optional[Path] = None,
    output_path: Optional[Path] = None,
    live_url: Optional[str] = None,
    max_trending: int = 25,
    site_dir: Optional[Path] = None,
) -> int:
    baseline_file = Path(base_path) if base_path is not None else CATALOG_PATH
    payload = json.loads(baseline_file.read_text(encoding="utf-8"))
    baseline_models: List[Dict[str, Any]] = [
        copy.deepcopy(m)
        for m in (payload.get("models") or [])
        if isinstance(m, dict) and m.get("id")
    ]

    baseline_ids = {str(m["id"]) for m in baseline_models}
    seen_ids = set(baseline_ids)
    seen_repos = {
        str(m.get("hf_repo") or "").lower()
        for m in baseline_models
        if m.get("hf_repo")
    }

    trending_models: List[Dict[str, Any]] = []
    if live_url:
        for live_entry in _fetch_live_models(live_url):
            mid = str(live_entry["id"])
            repo_low = str(live_entry.get("hf_repo") or "").lower()
            if mid in seen_ids or repo_low in seen_repos:
                continue
            trending_models.append(copy.deepcopy(live_entry))
            seen_ids.add(mid)
            seen_repos.add(repo_low)

    repos = _http_get_json(
        "https://huggingface.co/api/models",
        params={"filter": "gguf", "sort": "trendingScore", "limit": limit},
        timeout=20.0,
    )

    added = 0
    for item in repos if isinstance(repos, list) else []:
        if added >= max_new:
            break
        if not isinstance(item, dict):
            continue
        repo_id = str(item.get("id") or "")
        owner = repo_id.split("/")[0].lower() if "/" in repo_id else ""
        if owner not in VERIFIED_ORGS or repo_id.lower() in seen_repos:
            continue
        if not _is_eligible_llm_repo(item):
            continue

        try:
            info = _http_get_json(
                f"https://huggingface.co/api/models/{repo_id}",
                params={"blobs": "true"},
                timeout=15.0,
            )
        except Exception:
            continue
        if not _is_eligible_llm_repo(info):
            continue

        chosen = _pick_q4km(info.get("siblings") or [])
        if not chosen:
            continue

        filename = str(chosen["rfilename"])
        quantization = _infer_quantization(filename)
        if not quantization:
            continue

        size_bytes, sha256 = _extract_size_and_sha256(chosen)
        if size_bytes <= 0:
            continue
        size_gb = round(size_bytes / (1024 ** 3), 2)
        if size_gb < 0.3 or size_gb > 48.0:
            continue

        quant_suffix = re.sub(r"[^a-z0-9]+", "", quantization.lower())
        mid = f"{_slugify(repo_id)}-{quant_suffix}"
        if mid in seen_ids:
            continue

        fam = _infer_family(repo_id)
        param_str, param_num = _infer_params(repo_id)
        ram_req = max(2, int(round(size_gb * 1.25)))
        display_name = repo_id.split("/")[-1].replace("-GGUF", "").replace("_", " ").replace("-", " ")

        entry: Dict[str, Any] = {
            "id": mid,
            "name": display_name[:52],
            "family": fam,
            "provider": repo_id.split("/")[0],
            "parameter_size": param_str,
            "parameter_count": param_num,
            "size_gb": size_gb,
            "ram_required_gb": ram_req,
            "ram_recommended_gb": ram_req + 4,
            "categories": ["general"],
            "description": f"Trending verified GGUF from {repo_id} ({param_str}).",
            "hf_repo": repo_id,
            "hf_filename": filename,
            "logo_url": FAMILY_LOGOS.get(fam, "https://cdn.simpleicons.org/huggingface/FFD21E"),
            "quantization": quantization,
            "context_window": 32768,
            "supports_vision": (
                info.get("pipeline_tag") == "image-text-to-text"
                or "vl" in repo_id.lower()
                or "vision" in repo_id.lower()
            ),
            "supports_tools": True,
            "quality_tier": "great",
            "speed_tier": "fast" if param_num <= 9 else "medium",
            "chat_template": "chatml",
            "is_new": True,
        }
        if sha256:
            entry["sha256"] = sha256

        trending_models.append(entry)
        seen_ids.add(mid)
        seen_repos.add(repo_id.lower())
        added += 1

    if max_trending == 0:
        trending_models = []
    elif max_trending > 0 and len(trending_models) > max_trending:
        trending_models = trending_models[-max_trending:]

    existing_models = baseline_models + trending_models

    resolved_output = Path(output_path) if output_path is not None else None
    resolved_site = Path(site_dir) if site_dir is not None else None
    writing_separate_target = (
        resolved_site is not None
        or (resolved_output is not None and resolved_output.resolve() != baseline_file.resolve())
    )

    if added > 0 or writing_separate_target:
        payload["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        payload["models"] = existing_models

    serialized = json.dumps(payload, indent=2) + "\n"

    if resolved_site is not None:
        resolved_site.mkdir(parents=True, exist_ok=True)
        site_json_path = resolved_site / "models.json"
        site_json_path.write_text(serialized, encoding="utf-8")
        (resolved_site / ".nojekyll").write_text("", encoding="utf-8")
        (resolved_site / "index.html").write_text(
            _render_site_html(payload, baseline_ids=baseline_ids),
            encoding="utf-8",
        )
        if resolved_output is not None and resolved_output.resolve() != site_json_path.resolve():
            resolved_output.parent.mkdir(parents=True, exist_ok=True)
            resolved_output.write_text(serialized, encoding="utf-8")
    elif resolved_output is not None:
        if added > 0 or resolved_output.resolve() != baseline_file.resolve():
            resolved_output.parent.mkdir(parents=True, exist_ok=True)
            resolved_output.write_text(serialized, encoding="utf-8")
    elif added > 0:
        baseline_file.write_text(serialized, encoding="utf-8")

    print(f"Catalog sync complete: +{added} new models (total={len(existing_models)})")
    return added


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Sync Vesper Living Model Catalog")
    parser.add_argument("--base", type=Path, default=None, help="Path to baseline models.json")
    parser.add_argument("--output", type=Path, default=None, help="Output models.json path")
    parser.add_argument("--site-dir", type=Path, default=None, help="Static site directory to populate")
    parser.add_argument("--live-url", type=str, default=None, help="Existing live models.json URL to merge")
    parser.add_argument("--limit", type=int, default=30, help="HF trending query limit")
    parser.add_argument("--max-new", type=int, default=5, help="Max newly discovered models to add per run")
    parser.add_argument("--max-trending", type=int, default=25, help="Max retained non-baseline models")
    args = parser.parse_args(argv)

    sync_catalog(
        limit=args.limit,
        max_new=args.max_new,
        base_path=args.base,
        output_path=args.output,
        live_url=args.live_url,
        max_trending=args.max_trending,
        site_dir=args.site_dir,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
