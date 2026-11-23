"""Unit tests for backend/scripts/sync_catalog_json.py (Living Model Catalog sync & GitHub Pages export)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import httpx
import pytest

from scripts import sync_catalog_json as sc


class _FakeResponse:
    def __init__(self, status_code: int, payload: Any):
        self.status_code = status_code
        self._payload = payload
        self.request = httpx.Request("GET", "https://example.test")

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                f"HTTP {self.status_code}",
                request=self.request,
                response=httpx.Response(self.status_code, request=self.request),
            )

    def json(self) -> Any:
        return self._payload


def test_extract_size_and_sha256():
    valid_sha = "A" * 64
    size, sha = sc._extract_size_and_sha256(
        {"rfilename": "model-Q4_K_M.gguf", "size": 5_000_000_000, "lfs": {"sha256": valid_sha, "size": 5_000_000_000}}
    )
    assert size == 5_000_000_000
    assert sha == "a" * 64

    # Fallback to lfs.size when top-level size is absent, reject invalid sha256
    size2, sha2 = sc._extract_size_and_sha256(
        {"rfilename": "model-Q4_K_M.gguf", "lfs": {"size": 2_500_000_000, "sha256": "not-a-sha"}}
    )
    assert size2 == 2_500_000_000
    assert sha2 is None

    # Missing size -> 0
    size3, sha3 = sc._extract_size_and_sha256({"rfilename": "model-Q4_K_M.gguf"})
    assert size3 == 0
    assert sha3 is None


def test_pick_q4km_and_infer_quantization():
    assert sc._infer_quantization("Qwen3-8B-Q4_K_M.gguf") == "Q4_K_M"
    assert sc._infer_quantization("google_gemma-3-12b-it-Q5_K_M.gguf") == "Q5_K_M"
    assert sc._infer_quantization("Model-BF16.gguf") == "BF16"

    # Ignores mmproj, MTP/ subdirectories, and split shards; prefers Q4_K_M
    siblings = [
        {"rfilename": "mmproj-model-f16.gguf", "size": 800_000_000},
        {"rfilename": "MTP/mtp-model-Q4_K_M.gguf", "size": 2_000_000_000},
        {"rfilename": "Model-Q4_K_M-00001-of-00003.gguf", "size": 4_000_000_000},
        {"rfilename": "Model-Q5_K_M.gguf", "size": 6_000_000_000},
        {"rfilename": "Model-Q4_K_M.gguf", "size": 5_000_000_000},
    ]
    picked = sc._pick_q4km(siblings)
    assert picked is not None
    assert picked["rfilename"] == "Model-Q4_K_M.gguf"

    # Falls back to Q5_K_M with accurate quant label when Q4_K_* not present
    fallback_siblings = [
        {"rfilename": "MTP/mtp-Model-Q4_K_M.gguf", "size": 2_000_000_000},
        {"rfilename": "Model-BF16.gguf", "size": 16_000_000_000},
        {"rfilename": "Model-Q5_K_M.gguf", "size": 6_500_000_000},
    ]
    fallback = sc._pick_q4km(fallback_siblings)
    assert fallback is not None
    assert fallback["rfilename"] == "Model-Q5_K_M.gguf"
    assert sc._infer_quantization(fallback["rfilename"]) == "Q5_K_M"

    # Returns None for BF16-only / unquantized repos
    bf16_only = [
        {"rfilename": "Model-BF16.gguf", "size": 16_000_000_000},
        {"rfilename": "Model-F16.gguf", "size": 16_000_000_000},
        {"rfilename": "mmproj-Q4_K_M.gguf", "size": 500_000_000},
    ]
    assert sc._pick_q4km(bf16_only) is None


def test_sync_catalog_merges_live_filters_non_llm_and_renders_site(tmp_path: Path, monkeypatch):
    baseline_path = tmp_path / "models.json"
    baseline_models: List[Dict[str, Any]] = [
        {
            "id": "curated-qwen3-8b-q4km",
            "name": "Curated Qwen3 8B",
            "family": "qwen",
            "provider": "Alibaba Qwen",
            "parameter_size": "8B",
            "parameter_count": 8.0,
            "size_gb": 5.0,
            "ram_required_gb": 7,
            "ram_recommended_gb": 10,
            "categories": ["general", "coding"],
            "description": "Hand-curated entry",
            "hf_repo": "Qwen/Qwen3-8B-GGUF",
            "hf_filename": "Qwen3-8B-Q4_K_M.gguf",
            "quantization": "Q4_K_M",
            "is_new": False,
        }
    ]
    baseline_path.write_text(
        json.dumps({"schema_version": 1, "updated_at": "2026-11-15T00:00:00Z", "models": baseline_models}),
        encoding="utf-8",
    )

    live_url = "https://contextuai.github.io/vesper/models.json"
    site_dir = tmp_path / "_site"

    valid_sha_qwen = "b" * 64
    valid_sha_gemma = "c" * 64
    size_15gb = int(15.5 * (1024 ** 3))
    size_8gb = int(8.25 * (1024 ** 3))

    def fake_get(url: str, params=None, headers=None, timeout=None):
        if url == live_url:
            return _FakeResponse(
                200,
                {
                    "schema_version": 1,
                    "models": [
                        # Baseline duplicate should be skipped cleanly
                        baseline_models[0],
                        # Old live trending entries (cap test: keep newest)
                        {
                            "id": "older-live-1",
                            "name": "Older Live 1",
                            "hf_repo": "bartowski/Older-1-GGUF",
                            "hf_filename": "Older-1-Q4_K_M.gguf",
                            "size_gb": 4.2,
                            "quantization": "Q4_K_M",
                            "is_new": True,
                        },
                        {
                            "id": "recent-live-2",
                            "name": "Recent Live <script>alert(1)</script>",
                            "hf_repo": "bartowski/Recent-2-GGUF",
                            "hf_filename": "Recent-2-Q4_K_M.gguf",
                            "size_gb": 6.1,
                            "quantization": "Q4_K_M",
                            "is_new": True,
                        },
                    ],
                },
            )
        if url == "https://huggingface.co/api/models":
            return _FakeResponse(
                200,
                [
                    {"id": "unverified/Random-Model-GGUF"},
                    {"id": "unsloth/Gated-Model-7B-GGUF"},
                    {"id": "unsloth/MiniMax-H3-Image-GGUF", "pipeline_tag": "text-to-image"},
                    {"id": "unsloth/Mtp-Only-Model-GGUF"},
                    {"id": "unsloth/Qwen3.8-27B-GGUF", "pipeline_tag": "text-generation"},
                    {"id": "bartowski/gemma-3-12b-vl-GGUF", "pipeline_tag": "image-text-to-text"},
                ],
            )
        if url == "https://huggingface.co/api/models/unsloth/Gated-Model-7B-GGUF":
            assert params == {"blobs": "true"}
            return _FakeResponse(
                200,
                {
                    "gated": "manual",
                    "pipeline_tag": "text-generation",
                    "siblings": [{"rfilename": "Gated-Q4_K_M.gguf", "size": size_8gb}],
                },
            )
        if url == "https://huggingface.co/api/models/unsloth/Mtp-Only-Model-GGUF":
            return _FakeResponse(
                200,
                {
                    "gated": False,
                    "pipeline_tag": "text-generation",
                    "siblings": [
                        {"rfilename": "MTP/mtp-Model-Q4_K_M.gguf", "size": size_8gb},
                        {"rfilename": "Model-BF16.gguf", "size": size_15gb},
                    ],
                },
            )
        if url == "https://huggingface.co/api/models/unsloth/Qwen3.8-27B-GGUF":
            assert params == {"blobs": "true"}
            return _FakeResponse(
                200,
                {
                    "gated": False,
                    "pipeline_tag": "text-generation",
                    "tags": ["gguf", "qwen3"],
                    "siblings": [
                        {"rfilename": "MTP/mtp-Qwen3.8-27B-Q4_K_M.gguf", "size": 2_000_000_000},
                        {
                            "rfilename": "Qwen3.8-27B-UD-Q4_K_M.gguf",
                            "size": size_15gb,
                            "lfs": {"size": size_15gb, "sha256": valid_sha_qwen},
                        },
                    ],
                },
            )
        if url == "https://huggingface.co/api/models/bartowski/gemma-3-12b-vl-GGUF":
            assert params == {"blobs": "true"}
            return _FakeResponse(
                200,
                {
                    "gated": False,
                    "pipeline_tag": "image-text-to-text",
                    "tags": ["gguf"],
                    "siblings": [
                        {"rfilename": "mmproj-model-f16.gguf", "size": 900_000_000},
                        {
                            "rfilename": "gemma-3-12b-vl-Q5_K_M.gguf",
                            "lfs": {"size": size_8gb, "sha256": valid_sha_gemma},
                        },
                    ],
                },
            )
        raise AssertionError(f"Unexpected HTTP GET: {url}")

    monkeypatch.setattr(httpx, "get", fake_get)

    added = sc.sync_catalog(
        limit=25,
        max_new=5,
        base_path=baseline_path,
        live_url=live_url,
        max_trending=3,
        site_dir=site_dir,
    )
    assert added == 2

    # Curated baseline file stays untouched on disk
    orig_baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    assert len(orig_baseline["models"]) == 1

    # Generated static bundle exists
    manifest_file = site_dir / "models.json"
    nojekyll_file = site_dir / ".nojekyll"
    index_file = site_dir / "index.html"
    assert manifest_file.is_file()
    assert nojekyll_file.is_file()
    assert index_file.is_file()

    out = json.loads(manifest_file.read_text(encoding="utf-8"))
    # 1 baseline + capped 3 trending (recent-live-2, Qwen3.8-27B, gemma-3-12b-vl)
    out_ids = [m["id"] for m in out["models"]]
    assert out_ids[0] == "curated-qwen3-8b-q4km"
    assert "older-live-1" not in out_ids
    assert "recent-live-2" in out_ids
    assert len(out["models"]) == 4

    by_id = {m["id"]: m for m in out["models"]}
    qwen_entry = by_id["qwen3-8-27b-q4km"]
    assert qwen_entry["size_gb"] == 15.5
    assert qwen_entry["quantization"] == "Q4_K_M"
    assert qwen_entry["sha256"] == valid_sha_qwen
    assert qwen_entry["supports_vision"] is False

    gemma_entry = by_id["gemma-3-12b-vl-q5km"]
    assert gemma_entry["size_gb"] == 8.25
    assert gemma_entry["quantization"] == "Q5_K_M"
    assert gemma_entry["sha256"] == valid_sha_gemma
    assert gemma_entry["supports_vision"] is True

    # Ensure index.html escapes HTML from model names/metadata and distinguishes tiers
    html_text = index_file.read_text(encoding="utf-8")
    assert "<script>alert(1)</script>" not in html_text
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html_text
    assert "<td>Curated</td>" in html_text
    assert "<td>Trending</td>" in html_text
    assert "./models.json" in html_text
