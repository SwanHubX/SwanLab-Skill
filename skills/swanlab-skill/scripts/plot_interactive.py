#!/usr/bin/env python3
"""
SwanLab interactive HTML chart generator.

Fetch scalar metrics via the SwanLab OOP Api (or load pre-fetched JSON),
then render a single self-contained HTML file with ECharts line charts —
one chart per metric key, all experiments overlaid. The output can be
opened in any browser or embedded wherever raw HTML is accepted.

No third-party Python packages are needed in --data mode (pure stdlib);
ECharts is downloaded once from CDN and cached locally, then inlined into
every generated HTML file.

Usage:
    # Basic (requires `swanlab login` first)
    python plot_interactive.py username/project_name/run_id --keys loss,acc

    # Compare multiple experiments
    python plot_interactive.py user/proj/run1 user/proj/run2 -k loss

    # From pre-fetched JSON (skip API calls entirely, zero dependencies)
    python plot_interactive.py --data metrics.json -k loss,acc -o chart.html
    # Multi-experiment JSON: {"experiments": [{"name": ..., "metrics": {...}}, ...]}
    # (same format as runs_benchmark.py --data)

    # Self-hosted server
    python plot_interactive.py user/proj/run1 -k loss --host https://your-swanserver
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
#  ECharts runtime — download once, cache, inline into output
# ---------------------------------------------------------------------------

ECHARTS_URL = "https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"
ECHARTS_CACHE = Path.home() / ".cache" / "swanlab-skill" / "echarts.min.js"


def load_echarts_js() -> str:
    """Return the ECharts library source, using a local cache when available."""
    if ECHARTS_CACHE.exists():
        return ECHARTS_CACHE.read_text(encoding="utf-8")
    print(f"Downloading ECharts from {ECHARTS_URL} (one-time, cached afterwards) ...")
    try:
        with urllib.request.urlopen(ECHARTS_URL, timeout=30) as resp:
            source = resp.read().decode("utf-8")
    except OSError as e:
        raise RuntimeError(
            f"Failed to download ECharts and no cache found at {ECHARTS_CACHE}. "
            "Check network access, or place echarts.min.js at that path manually."
        ) from e
    ECHARTS_CACHE.parent.mkdir(parents=True, exist_ok=True)
    ECHARTS_CACHE.write_text(source, encoding="utf-8")
    return source


# ---------------------------------------------------------------------------
#  Data fetching (API mode) — swanlab imported lazily so --data needs no deps
# ---------------------------------------------------------------------------


def fetch_experiment(
    path: str,
    keys: List[str],
    sample: int,
    api_key: Optional[str],
    host: Optional[str],
) -> Dict[str, Any]:
    """Fetch one experiment's metrics via the SwanLab Api."""
    from swanlab.api import Api

    api = Api(api_key=api_key, host=host)
    experiment = api.run(path)
    if not experiment.run_id:
        raise ValueError(f"Failed to fetch experiment at path '{path}'. Please verify the path and credentials.")
    return {
        "name": experiment.name,
        "path": path,
        "metrics": experiment.metrics(keys=keys, sample=sample, ignore_timestamp=True),
    }


# ---------------------------------------------------------------------------
#  Data extraction — pull (steps, values) pairs from the raw API dict
#  (same shapes as plot_metrics.py / runs_benchmark.py)
# ---------------------------------------------------------------------------


def _unwrap_envelope(data: Any) -> Any:
    """Unwrap the ``{"ok": ..., "errmsg": ..., "data": ...}`` envelope written by CLI ``--save``."""
    if (
        isinstance(data, dict)
        and "list" not in data
        and "keys" not in data
        and isinstance(data.get("ok"), bool)
        and "data" in data
    ):
        return data.get("data") or {}
    return data


def _extract(metric_data: Dict[str, Any], key: str) -> Tuple[List[int], List[float]]:
    """
    Pull (steps, values) for one metric key.

    Handles three response shapes:
    - Current SDK format (``Experiment.metrics()`` / ``Metrics.json()``)::
        ``{"keys": [...], "list": [{"key": k, "metrics": [{"index": i, "data": v}, ...], ...}]}``
    - CLI ``--save`` output — the same structure wrapped in an
      ``{"ok": ..., "errmsg": ..., "data": ...}`` envelope
    - Legacy format (pre-0.9.0)::
        ``{key: [{"step": s, "value": v}, ...]}`` (flat list or nested under "data")
    """
    data = _unwrap_envelope(metric_data)
    if not isinstance(data, dict):
        return [], []

    points: Any = None
    entries = data.get("list")
    if isinstance(entries, list):
        for entry in entries:
            if isinstance(entry, dict) and entry.get("key") == key:
                points = entry.get("metrics") or []
                break
    elif key in data:
        entry = data[key]
        if isinstance(entry, dict) and "data" in entry:
            points = entry["data"]
        elif isinstance(entry, list):
            points = entry

    steps: List[int] = []
    values: List[float] = []
    for pt in points or []:
        if not isinstance(pt, dict):
            continue
        step = pt.get("step")
        if step is None:
            step = pt.get("index")
        value = pt.get("value")
        if value is None:
            value = pt.get("data")
        if step is None or value is None:
            continue
        try:
            steps.append(int(step))
            values.append(float(value))
        except (TypeError, ValueError):
            continue
    return steps, values


# ---------------------------------------------------------------------------
#  HTML rendering
# ---------------------------------------------------------------------------

# Same palette as runs_benchmark.py
_COLORS = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
]

_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  body {{ margin: 0; padding: 16px; font-family: -apple-system, "Segoe UI", Roboto, sans-serif; background: #fff; }}
  h1 {{ font-size: 18px; margin: 0 0 12px; }}
  .chart {{ width: 100%; height: 420px; margin-bottom: 24px; }}
</style>
</head>
<body>
<h1>{title}</h1>
{chart_divs}
<script>{echarts_js}</script>
<script>
const DATA = {data_json};
const PALETTE = {colors_json};
DATA.charts.forEach((chart, ci) => {{
  const el = document.getElementById("chart-" + ci);
  const inst = echarts.init(el);
  inst.setOption({{
    color: PALETTE,
    title: {{ text: chart.key, left: "center", textStyle: {{ fontSize: 14 }} }},
    tooltip: {{ trigger: "axis" }},
    legend: {{ bottom: 0, type: "scroll" }},
    grid: {{ left: 60, right: 24, top: 40, bottom: 60 }},
    xAxis: {{ type: "value", name: chart.xName, nameLocation: "middle", nameGap: 28 }},
    yAxis: {{ type: "value", scale: true }},
    dataZoom: [{{ type: "inside" }}, {{ type: "slider", height: 18, bottom: 30 }}],
    series: chart.series.map(s => ({{
      name: s.name,
      type: "line",
      showSymbol: false,
      sampling: "lttb",
      data: s.points
    }}))
  }});
  window.addEventListener("resize", () => inst.resize());
}});
</script>
</body>
</html>
"""


def normalize_steps(steps: List[int]) -> List[float]:
    """Map steps to [0, 100] percentage scale."""
    if not steps:
        return []
    total = max(steps) if max(steps) != 0 else 1
    return [s / total * 100.0 for s in steps]


def build_html(
    experiments: List[Dict[str, Any]],
    keys: List[str],
    title: str,
    normalize: bool,
) -> str:
    """Render the self-contained HTML for the given experiments and keys."""
    charts = []
    for key in keys:
        series = []
        for exp in experiments:
            steps, values = _extract(exp.get("metrics", exp), key)
            if not steps:
                continue
            x = normalize_steps(steps) if normalize else steps
            points = [[float(xi), float(vi)] for xi, vi in zip(x, values)]
            series.append({"name": exp.get("name") or exp.get("path") or "unknown", "points": points})
        charts.append({"key": key, "xName": "progress (%)" if normalize else "step", "series": series})

    chart_divs = "\n".join(f'<div id="chart-{i}" class="chart"></div>' for i in range(len(charts)))
    return _HTML_TEMPLATE.format(
        title=title,
        chart_divs=chart_divs,
        echarts_js=load_echarts_js(),
        data_json=json.dumps({"charts": charts}, ensure_ascii=False),
        colors_json=json.dumps(_COLORS),
    )


# ---------------------------------------------------------------------------
#  CLI entry point
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render SwanLab metrics as a self-contained interactive HTML file (ECharts).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Experiment paths (username/project/run_id). Optional when --data is used.",
    )
    parser.add_argument(
        "--data",
        default=None,
        help="Path to pre-fetched JSON: single-experiment metrics (SDK output / CLI --save file) "
        'or multi-experiment {"experiments": [...]} (runs_benchmark.py --data format). Skips API calls.',
    )
    parser.add_argument("--keys", "-k", required=True, help="Comma-separated metric keys, e.g. 'loss,acc'")
    parser.add_argument("--labels", default=None, help="Comma-separated display names (matched to paths by order).")
    parser.add_argument("--sample", "-s", type=int, default=1500, help="Sample size per metric (default: 1500)")
    parser.add_argument(
        "--normalize", action="store_true", help="Normalize x-axis to 0-100%% for unequal-length experiments."
    )
    parser.add_argument(
        "--output", "-o", default="metrics_chart.html", help="Output HTML path (default: metrics_chart.html)"
    )
    parser.add_argument("--title", "-t", default=None, help="Page title (default: auto)")
    parser.add_argument("--api-key", default=None, help="SwanLab API key (or use swanlab login)")
    parser.add_argument("--host", default=None, help="SwanLab API host URL (for self-hosted)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    keys = [k.strip() for k in args.keys.split(",") if k.strip()]

    if not keys:
        print("Error: --keys must contain at least one key.", file=sys.stderr)
        return 1

    if not args.paths and not args.data:
        print("Error: provide either PATH arguments or --data <json_file>.", file=sys.stderr)
        return 1

    experiments: List[Dict[str, Any]] = []

    if args.data:
        with open(args.data, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
        # Multi-experiment: {"experiments": [{name, path, metrics}, ...]}
        # Single experiment: raw metrics dict (any of the shapes _extract accepts)
        items = raw_data.get("experiments", [raw_data]) if isinstance(raw_data, dict) else raw_data
        for item in items:
            experiments.append(
                {
                    "name": item.get("name", "") if isinstance(item, dict) else "",
                    "path": item.get("path", "") if isinstance(item, dict) else "",
                    "metrics": item.get("metrics", item) if isinstance(item, dict) else {},
                }
            )
        print(f"Loaded metric data from: {args.data} ({len(experiments)} experiment(s))")
    else:
        custom_labels: List[str] = []
        if args.labels:
            custom_labels = [lbl.strip() for lbl in args.labels.split(",")]
            if len(custom_labels) != len(args.paths):
                print(
                    f"Error: --labels has {len(custom_labels)} items but {len(args.paths)} paths given.",
                    file=sys.stderr,
                )
                return 1
        for i, path in enumerate(args.paths):
            print(f"Fetching [{i + 1}/{len(args.paths)}] {path} ...")
            try:
                exp = fetch_experiment(path, keys, args.sample, args.api_key, args.host)
            except ValueError as e:
                print(f"Error: {e}", file=sys.stderr)
                return 1
            if custom_labels:
                exp["name"] = custom_labels[i]
            experiments.append(exp)

    title = args.title or (f"Metrics: {', '.join(args.paths)}" if args.paths else "SwanLab Metrics")
    html = build_html(experiments, keys, title, args.normalize)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Chart saved to: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
