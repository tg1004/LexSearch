#!/usr/bin/env python3
"""
Run 50-query search quality evaluation against a live LexSearch backend.

Usage:
    python scripts/eval_search_quality.py
    python scripts/eval_search_quality.py --api-url http://localhost:8000 --output reports/quality.json

Scores each result on automated rubric (0-5):
  - Has results (result_count > 0)
  - Has AI answer (non-empty, not error template)
  - Has citations
  - Answer mentions legal content (heuristic keywords)
  - Latency under 3 seconds
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import httpx

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_QUERIES = PROJECT_ROOT / "scripts" / "eval_queries.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "reports" / "search_quality_report.json"

LEGAL_KEYWORDS = (
    "court",
    "section",
    "article",
    "judgement",
    "judgment",
    "held",
    "petition",
    "accused",
    "plaintiff",
    "defendant",
    "bail",
    "rights",
    "act",
    "ipc",
    "crpc",
    "constitution",
)

ERROR_ANSWERS = (
    "Service temporarily unavailable",
    "No results found for this query",
)


def load_queries(path: Path) -> list[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list) or len(data) < 1:
        raise ValueError(f"Expected a JSON array of queries in {path}")
    return [str(q).strip() for q in data if str(q).strip()]


def score_result(query: str, data: dict, latency_ms: float) -> dict:
    answer = (data.get("answer") or "").strip()
    result_count = int(data.get("result_count") or 0)
    citations = data.get("citations") or []
    provider = data.get("provider_used")

    checks = {
        "has_results": result_count > 0,
        "has_answer": bool(answer) and not any(err in answer for err in ERROR_ANSWERS),
        "has_citations": len(citations) > 0,
        "legal_content": any(kw in answer.lower() for kw in LEGAL_KEYWORDS),
        "fast_enough": latency_ms < 3000,
    }
    score = sum(1 for ok in checks.values() if ok)

    return {
        "query": query,
        "latency_ms": round(latency_ms, 1),
        "result_count": result_count,
        "citation_count": len(citations),
        "provider_used": provider,
        "answer_preview": answer[:200] + ("..." if len(answer) > 200 else ""),
        "checks": checks,
        "score": score,
        "max_score": 5,
    }


def check_api_reachable(api_url: str, timeout: float = 5.0) -> None:
    """Fail fast with a clear message if the backend is not running."""
    try:
        with httpx.Client(base_url=api_url.rstrip("/"), timeout=timeout) as client:
            response = client.get("/api/health")
            response.raise_for_status()
    except httpx.ConnectError as exc:
        raise SystemExit(
            f"\nERROR: Cannot reach LexSearch backend at {api_url}\n"
            f"  ({exc})\n\n"
            "Start the backend first:\n"
            "  docker compose up postgres redis elasticsearch qdrant -d\n"
            "  cd backend && .\\venv\\Scripts\\activate && uvicorn app.main:app --reload --port 8000\n"
        ) from exc
    except httpx.HTTPStatusError as exc:
        raise SystemExit(f"\nERROR: Backend at {api_url} returned {exc.response.status_code}") from exc


def run_eval(api_url: str, queries: list[str], timeout: float) -> dict:
    results: list[dict] = []
    errors: list[dict] = []

    with httpx.Client(base_url=api_url.rstrip("/"), timeout=timeout) as client:
        for index, query in enumerate(queries, start=1):
            print(f"[{index}/{len(queries)}] {query[:70]}...")
            start = time.perf_counter()
            try:
                response = client.post(
                    "/api/search",
                    json={"query": query, "preferred_provider": "auto", "filters": {}, "page": 1},
                )
                latency_ms = (time.perf_counter() - start) * 1000
                response.raise_for_status()
                row = score_result(query, response.json(), latency_ms)
                results.append(row)
            except Exception as exc:
                latency_ms = (time.perf_counter() - start) * 1000
                errors.append({"query": query, "error": str(exc), "latency_ms": round(latency_ms, 1)})

    latencies = [row["latency_ms"] for row in results]
    scores = [row["score"] for row in results]

    summary = {
        "total_queries": len(queries),
        "successful": len(results),
        "failed": len(errors),
        "avg_score": round(statistics.mean(scores), 2) if scores else 0,
        "median_score": statistics.median(scores) if scores else 0,
        "pass_rate_4plus": round(sum(1 for s in scores if s >= 4) / len(scores) * 100, 1) if scores else 0,
        "latency_ms": {
            "mean": round(statistics.mean(latencies), 1) if latencies else None,
            "p50": round(statistics.median(latencies), 1) if latencies else None,
            "p95": round(sorted(latencies)[int(len(latencies) * 0.95) - 1], 1) if len(latencies) >= 2 else (latencies[0] if latencies else None),
            "max": round(max(latencies), 1) if latencies else None,
        },
        "under_3s_pct": round(sum(1 for ms in latencies if ms < 3000) / len(latencies) * 100, 1) if latencies else 0,
    }

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "api_url": api_url,
        "summary": summary,
        "results": results,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="LexSearch 50-query quality evaluation")
    parser.add_argument("--api-url", default="http://localhost:8000", help="Backend base URL")
    parser.add_argument("--queries", type=Path, default=DEFAULT_QUERIES, help="JSON file with query list")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Report output path")
    parser.add_argument("--timeout", type=float, default=120.0, help="Per-request timeout (seconds)")
    parser.add_argument("--limit", type=int, default=None, help="Run only first N queries (for quick tests)")
    parser.add_argument("--min-pass-rate", type=float, default=70.0, help="Min %% of queries scoring >= 4")
    args = parser.parse_args()

    queries = load_queries(args.queries)
    if args.limit:
        queries = queries[: args.limit]

    print(f"Running quality eval: {len(queries)} queries -> {args.api_url}\n")

    check_api_reachable(args.api_url)

    report = run_eval(args.api_url, queries, args.timeout)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary = report["summary"]
    print("\n=== Quality Summary ===")
    print(f"Successful: {summary['successful']}/{summary['total_queries']}")
    print(f"Avg score:  {summary['avg_score']}/5")
    print(f"Score >= 4: {summary['pass_rate_4plus']}%")
    print(f"Latency p50: {summary['latency_ms']['p50']}ms  p95: {summary['latency_ms']['p95']}ms")
    print(f"Under 3s:   {summary['under_3s_pct']}%")
    print(f"Report:     {args.output}")

    if summary["pass_rate_4plus"] < args.min_pass_rate:
        print(f"\nFAIL: pass rate {summary['pass_rate_4plus']}% < {args.min_pass_rate}%", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
