#!/usr/bin/env python3
"""
Performance benchmark for LexSearch /api/search.

Usage:
    python scripts/benchmark_search.py
    python scripts/benchmark_search.py --max-p95-ms 3000 --rounds 3

Fails (exit 1) if p95 latency exceeds --max-p95-ms.
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
DEFAULT_OUTPUT = PROJECT_ROOT / "reports" / "search_benchmark.json"

# Subset for faster perf runs (10 representative queries)
BENCHMARK_QUERIES = [
    "What are the grounds for bail in murder cases?",
    "Right to privacy Supreme Court",
    "Bail conditions NDPS Act",
    "RTI Act scope of information",
    "IPC 498A dowry harassment ingredients",
    "Article 21 life and personal liberty",
    "Section 138 cheque bounce presumption",
    "Anticipatory bail when granted",
    "Environmental clearance EIA requirements",
    "Public interest litigation locus standi",
]


def load_queries(path: Path, limit: int | None) -> list[str]:
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        queries = [str(q).strip() for q in data if str(q).strip()]
        return queries[:limit] if limit else queries
    return BENCHMARK_QUERIES


def benchmark(api_url: str, queries: list[str], rounds: int, timeout: float) -> dict:
    latencies: list[float] = []
    per_query: list[dict] = []
    errors: list[dict] = []

    with httpx.Client(base_url=api_url.rstrip("/"), timeout=timeout) as client:
        for round_num in range(1, rounds + 1):
            print(f"Round {round_num}/{rounds}")
            for query in queries:
                start = time.perf_counter()
                try:
                    response = client.post(
                        "/api/search",
                        json={"query": query, "preferred_provider": "auto", "filters": {}, "page": 1},
                    )
                    elapsed_ms = (time.perf_counter() - start) * 1000
                    response.raise_for_status()
                    latencies.append(elapsed_ms)
                    per_query.append({"query": query, "round": round_num, "latency_ms": round(elapsed_ms, 1)})
                    print(f"  {elapsed_ms:.0f}ms — {query[:50]}")
                except Exception as exc:
                    elapsed_ms = (time.perf_counter() - start) * 1000
                    errors.append({"query": query, "round": round_num, "error": str(exc), "latency_ms": round(elapsed_ms, 1)})
                    print(f"  ERROR — {query[:50]}: {exc}")

    sorted_lat = sorted(latencies)
    p95_index = max(0, int(len(sorted_lat) * 0.95) - 1)

    stats = {
        "count": len(latencies),
        "errors": len(errors),
        "mean_ms": round(statistics.mean(latencies), 1) if latencies else None,
        "p50_ms": round(statistics.median(latencies), 1) if latencies else None,
        "p95_ms": round(sorted_lat[p95_index], 1) if sorted_lat else None,
        "max_ms": round(max(latencies), 1) if latencies else None,
        "min_ms": round(min(latencies), 1) if latencies else None,
    }

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "api_url": api_url,
        "rounds": rounds,
        "queries_per_round": len(queries),
        "stats": stats,
        "samples": per_query,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="LexSearch search performance benchmark")
    parser.add_argument("--api-url", default="http://localhost:8000")
    parser.add_argument("--queries", type=Path, default=DEFAULT_QUERIES)
    parser.add_argument("--query-limit", type=int, default=10, help="Number of queries per round")
    parser.add_argument("--rounds", type=int, default=2)
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--max-p95-ms", type=float, default=3000.0)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    queries = load_queries(args.queries, args.query_limit)
    print(f"Benchmark: {len(queries)} queries x {args.rounds} rounds -> {args.api_url}\n")

    try:
        with httpx.Client(base_url=args.api_url.rstrip("/"), timeout=5.0) as client:
            client.get("/api/health").raise_for_status()
    except httpx.ConnectError:
        print(
            f"ERROR: Backend not reachable at {args.api_url}. Start uvicorn first.",
            file=sys.stderr,
        )
        return 1

    report = benchmark(args.api_url, queries, args.rounds, args.timeout)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")

    stats = report["stats"]
    print("\n=== Benchmark Results ===")
    print(f"Samples:  {stats['count']}  Errors: {stats['errors']}")
    print(f"p50:      {stats['p50_ms']}ms")
    print(f"p95:      {stats['p95_ms']}ms  (limit: {args.max_p95_ms}ms)")
    print(f"max:      {stats['max_ms']}ms")
    print(f"Report:   {args.output}")

    if stats["p95_ms"] is None:
        print("\nFAIL: no successful requests", file=sys.stderr)
        return 1
    if stats["p95_ms"] > args.max_p95_ms:
        print(f"\nFAIL: p95 {stats['p95_ms']}ms exceeds {args.max_p95_ms}ms", file=sys.stderr)
        return 1
    print("\nPASS: p95 within limit")
    return 0


if __name__ == "__main__":
    sys.exit(main())
