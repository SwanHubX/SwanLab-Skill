---
name: swanlab-skill
metadata:
  version: "0.3.0"
description: >
  Interact with SwanLab — both writing tracking code (init/log/finish/multimedia) and querying
  experiment data via CLI (`swanlab api`). Use this skill when the user wants to write training
  tracking code, log metrics or media, manage experiments, inspect metrics/logs/keys, list
  projects/runs, filter experiments, manage self-hosted users, automate queries via CLI, or
  mentions "swanlab", "experiment tracking", "log metrics", "swanlab api", "swanlab cli".
---

# SwanLab Skill

SwanLab is an AI training experiment tracking platform. This skill covers two usage patterns:

- **Writing tracking code** — use the Python SDK (`swanlab.init`, `swanlab.log`, `swanlab.finish`, media helpers)
- **Reading experiment data** — use the `swanlab api` CLI to query metrics, logs, summaries, media, etc.

---

## Reference Routing

| If the user wants to...                                                | Read this reference              |
| ---------------------------------------------------------------------- | -------------------------------- |
| Write tracking code (init/log/finish/media)                            | `references/SDK_QUICKSTART.md`   |
| Query data via CLI (metrics/summary/logs/filter/etc.)                  | `references/CLI_REFERENCE.md`    |
| Understand data model / terminology / filter syntax                    | `references/SWANLAB_CONCEPTS.md` |
| Analyze runs/projects, compare experiments, write an experiment report | `references/ANALYSIS_GUIDE.md`   |
| Plot metrics or compare experiments visually                           | See **Scripts** below            |

> **Version note (SDK ≥ 0.9.0)**: use `swanlab api run series` to discover an experiment's metric keys. `run column` / `run columns` are deprecated since `0.9.0` and do not apply to multi-view experiments — only fall back to them when the installed SDK is `< 0.9.0`. See `CLI_REFERENCE.md > Version Applicability`.

---

## Run Modes

`swanlab.init(mode=...)` controls where data goes:

| Mode       | Local Storage  | Cloud Upload                           | Use Case                             |
| ---------- | -------------- | -------------------------------------- | ------------------------------------ |
| `online`   | Yes (protobuf) | Yes (Transport → HTTP)                 | Normal cloud usage. Requires login.  |
| `local`    | Yes (protobuf) | No                                     | Air-gapped / no account needed.      |
| `offline`  | Yes (protobuf) | No (syncable later via `swanlab sync`) | Save locally, upload to cloud later. |
| `disabled` | No             | No                                     | Completely disable all logging.      |

Default is `online` if logged in; otherwise an interactive prompt offers login, registration, or `offline`. In non-interactive environments without an API key, init raises an error instead of falling back.

---

## Scripts

Two helper scripts are available for visualizing experiment data:

### `scripts/plot_metrics.py` — Single Experiment Line Chart

Trigger when the user wants to **visualize scalar metrics from one experiment** (e.g. "plot my loss curve", "show training metrics chart").

```bash
python scripts/plot_metrics.py username/project_name/run_id --keys loss,acc
python scripts/plot_metrics.py user/proj/run1 -k loss -o loss_chart.png -s 500
python scripts/plot_metrics.py --data metrics.json -k loss,acc -o chart.png   # from saved JSON
```

### `scripts/runs_benchmark.py` — Cross-Experiment Comparison

Trigger when the user wants to **compare the same metric across multiple experiments** (e.g. "compare loss across runs", "benchmark these experiments").

```bash
python scripts/runs_benchmark.py user/proj/run1 user/proj/run2 user/proj/run3 -k loss
python scripts/runs_benchmark.py user/proj/run1 user/proj/run2 -k loss --direction lower
python scripts/runs_benchmark.py user/proj/run1 user/proj/run2 -k loss,acc --normalize
python scripts/runs_benchmark.py --data benchmark_data.json -k loss              # from saved JSON
```

### `scripts/plot_interactive.py` — Interactive HTML Chart (ECharts)

Trigger when the user wants an **interactive chart** (zoom, hover tooltips) or an HTML artifact instead of a static image. Renders one chart per key with all experiments overlaid, as a single self-contained HTML file (ECharts is downloaded once and cached; `--data` mode needs no third-party packages).

```bash
python scripts/plot_interactive.py user/proj/run1 --keys loss,acc -o chart.html
python scripts/plot_interactive.py user/proj/run1 user/proj/run2 -k loss        # multi-run overlay
python scripts/plot_interactive.py --data metrics.json -k loss,acc -o chart.html  # from saved JSON
```

Fetching from the API requires `swanlab login` (or `--api-key` / `--host` flags); `--data` mode works offline — `plot_interactive.py --data` even runs on bare Python (no third-party packages).

---

## Path Convention

CLI commands use `username/project_name` (project) or `username/project_name/run_id` (experiment). See `SWANLAB_CONCEPTS.md > Path Convention` for details.

---

## Quick Disambiguation

| User says...                                     | They probably mean...    | Route                                     |
| ------------------------------------------------ | ------------------------ | ----------------------------------------- |
| "track my training" / "log metrics"              | Write tracking code      | `SDK_QUICKSTART.md`                       |
| "log images/audio/text"                          | Log media data           | `SDK_QUICKSTART.md`                       |
| "my loss curve" / "experiment metrics"           | Query scalar data        | `CLI_REFERENCE.md > run metrics`          |
| "filter experiments"                             | Query by conditions      | `CLI_REFERENCE.md > run filter`           |
| "my experiments" / "list runs"                   | List experiments         | `CLI_REFERENCE.md > run list`             |
| "compare runs visually"                          | Cross-experiment chart   | `scripts/runs_benchmark.py`               |
| "plot metric chart"                              | Single-experiment chart  | `scripts/plot_metrics.py`                 |
| "experiment config"                              | Hyperparameters          | `CLI_REFERENCE.md > run info`             |
| "console output"                                 | Captured logs            | `CLI_REFERENCE.md > run logs`             |
| "what metrics are tracked"                       | Metric keys              | `CLI_REFERENCE.md > run series`           |
| "check connectivity" / "can I reach swanlab"     | Environment check        | `swanlab ping`                            |
| "check login status" / "am I logged in"          | Verify credentials       | `swanlab verify`                          |
| "project not found" / a query returns 404        | Wrong host (most likely) | `CLI_REFERENCE.md > Troubleshooting`      |
| run fields / run list or run info response       | Run object schema        | `SWANLAB_CONCEPTS.md > Run Object Schema` |
| "analyze this project/run" / "experiment report" | Analysis pipeline        | `ANALYSIS_GUIDE.md`                       |

---

## Environment Connectivity

Before writing tracking code or running CLI queries, especially in `online` mode, run these two checks to confirm the environment is ready:

### 1. `swanlab ping` — Test network reachability

The fastest way to diagnose connectivity issues. Run it first when a user reports upload failures, login problems, or unknown mode fallbacks.

```bash
swanlab ping
# Reports: API host, web host, latency, and login status.
# If ping fails, check SWANLAB_API_HOST / network proxy / firewall settings.
```

### 2. `swanlab verify` — Validate login credentials

After confirming the server is reachable, use `swanlab verify` to check that stored credentials are valid and have not expired. This reads the API key and host from the local `.netrc` file (created by `swanlab login`).

```bash
swanlab verify
# Validates stored API key against the server.
# Reports: which host (default https://swanlab.cn) and the logged-in username.
# Fails if: not logged in, API key is invalid, or key has expired.

swanlab verify --local
# Check local login status (.swanlab in current directory) instead of the global one.
```

**Recommended pre-flight sequence**:

1. `swanlab ping` → confirm the server is reachable
2. `swanlab verify` → confirm credentials are valid, and **note which host you are logged into**
3. **Confirm the target project lives on that host.** SwanLab has multiple independent instances (public `swanlab.cn` + self-hosted deployments) and credentials are per-instance — see `SWANLAB_CONCEPTS.md > Instances, Hosts & Credentials`. If the project is on another instance, pass `--host` / `--api-key` on every command (or export `SWANLAB_API_HOST` / `SWANLAB_API_KEY`). A `404 Not_Found` from `project info` / `run list` means **wrong host, not a missing project** — see `CLI_REFERENCE.md > Troubleshooting`.
4. Proceed with `swanlab api` queries or SDK code

---

## Behavioral Constraints

See `CLI_REFERENCE.md > Behavioral Constraints` for the full list. Key rules:

- **Use `--all` only when the user explicitly asks for it** (e.g. "fetch all", "get everything", "complete list"). For paginated list commands, always use default pagination (`--page_num` / `--page_size`).
- **Always ask for specific metric keys before running `run metrics` or `run medias`.** If the user doesn't know the key names, first run `run series PATH` to discover them (`run columns PATH` only as a fallback on SDK `< 0.9.0`).
- **Always persist large metric data to file via `--save`**, then visualize with `scripts/plot_metrics.py --data file.json` or use `run summary` for aggregate stats.

---

## Further Reading

This skill covers the most common SwanLab workflows for AI coding agents. For
details that are out of scope here (full SDK surface, advanced CLI flags,
self-hosted deployment, integrations, etc.), consult the official SwanLab
documentation:

- **Cloud guide (what is SwanLab, concepts, usage)**: https://docs.swanlab.cn/guide_cloud/general/what-is-swanlab.md
- **Python SDK & OpenAPI reference**: https://docs.swanlab.cn/api/api-index.md
