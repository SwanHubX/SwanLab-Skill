# Analysis Guide — Experiment Analysis Pipelines

Workflow recipes for turning `swanlab api` queries into analysis or reports. Command syntax: `CLI_REFERENCE.md`. Response schemas: `SWANLAB_CONCEPTS.md`.

| User says...                                               | Pipeline      |
| ---------------------------------------------------------- | ------------- |
| "analyze this run" / "why did it crash or diverge"         | Run-level     |
| "analyze this project" / "write a report" / "compare runs" | Project-level |

Pre-flight first: confirm host + credentials (`SKILL.md > Environment Connectivity`). A 404 on project-scoped queries means wrong host, not missing data.

---

## Run-Level Pipeline

```
run info → run series → branch by intent
```

1. **`run info PATH`** — what the run actually was.
   - Hyperparameters: `profile.config.<key>.value` (nested `{value, desc, sort}`, not flat).
   - Environment: `profile.metadata` (`command`, `git_info`, `gpu`, `swanlab.version`).
   - Duration = `finished_at` − `created_at`.
   - **Trust config over run name** — names are free-text and can contradict config.
2. **`run series PATH`** — discover metric keys (`--class system` for hardware, `--type media` for media).
3. **Branch by intent**:

| Intent                                | Next step                                                   |
| ------------------------------------- | ----------------------------------------------------------- |
| Quick conclusion / final numbers      | `run summary` (latest + min/max/avg per key, one call)      |
| Curve shape, convergence, overfitting | `run metrics --keys k1,k2 --save` → plot (see below)        |
| State `CRASHED` / suspicious          | `run logs --level ERROR` first; bulk-read via `export-logs` |
| A step range or tail                  | `run metrics` with `--range-start/--range-end/--range-tail` |
| Logged images/audio/text              | `run medias --keys KEY --step N`                            |

---

## Project-Level Pipeline

```
run list → (optional) run filter → per-run info + summary → synthesize
```

1. **`run list PROJECT_PATH`** — inventory. Items embed the full `profile`; extract only `run_id` / `name` / `state` / `description` / timestamps with `jq`/`python` instead of dumping raw JSON.
2. **`run filter`** (optional) — narrow the set first: by `state`, config dimension, metric threshold, or time range (`SWANLAB_CONCEPTS.md > Filter Query`).
3. **Per-run `run info` + `run summary`** — loop over shortlisted `run_id`s into a table. Check exit codes and retry transient failures before parsing stdout.
   - Summary gives only the latest value + aggregates. For per-key fine-grained analysis — trends, oscillation, when a metric peaked — also pull the time series: `run metrics PATH --keys KEY --save` per run, then compare curves or plot them (see Visualization). Don't rank runs on final values alone.
4. **Synthesize** — group by config dimensions (model, dataset, lr, ...), rank by the target metric, cite run names/ids as evidence.

### Analysis discipline

- **Config is truth, names are labels.** Names are not unique and can drift from config; group and compare by config values.
- **`description` often carries variant labels** — read it together with `name`.
- **Watch for invalidated batches.** Mid-project pipeline fixes make older runs incomparable; time clusters and description markers reveal the boundary. Flag suspect batches, don't average them in.
- **Single-run ablations are directional only.** Within-noise differences need repeated seeds before becoming conclusions.
- **Check convergence before ranking.** If val `max ≈ last`, training hadn't saturated — note it instead of ranking undertrained runs.

---

## Visualization

Charts are a pipeline step, not a separate task:

| Scenario                   | Script                        |
| -------------------------- | ----------------------------- |
| One run, several keys      | `scripts/plot_metrics.py`     |
| Same key across runs       | `scripts/runs_benchmark.py`   |
| Interactive HTML (ECharts) | `scripts/plot_interactive.py` |
| Unequal-length runs        | add `--normalize`             |
| Only final numbers needed  | no chart — use `run summary`  |

**Data bridge (no double-fetching)**: all three scripts accept `--data FILE.json` and skip API calls:

```bash
swanlab api run metrics user/proj/RUN_ID --keys val/loss --save
python scripts/plot_metrics.py --data swanlab-YYYYMMDD_HHMMSS-xxxx.json -k val/loss -o val_loss.png
```

**Benchmark path list from a project**: extract run ids from `run list` output and expand to `user/proj/<id>` paths, then pass them to `runs_benchmark.py`.

Notes:

- Scripts use the OOP `swanlab.api.Api`, which reuses the saved login state (`.netrc` / `SWANLAB_API_KEY`): no flags needed on the logged-in default instance; pass `--host` / `--api-key` only for other instances.
- `plot_metrics.py` / `runs_benchmark.py` render static matplotlib images. For interactive ECharts output, use `plot_interactive.py` — it consumes the same fetched JSON (`run metrics --save` output, or the multi-experiment `{"experiments": [...]}` format of `runs_benchmark.py --data`) and emits one self-contained HTML file. Its `--data` mode is pure stdlib; ECharts is fetched from CDN once and cached at `~/.cache/swanlab-skill/echarts.min.js`.
