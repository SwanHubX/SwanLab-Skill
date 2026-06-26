# SwanLab-Skill

<div style="text-align: center">
  <p>
    <a href="https://skillhub.cn/skills/swanlab-skill">🐧 SkillHub</a> |
    <a href="https://www.modelscope.cn/skills/SwanLab/swanlab-skill">🤖 ModelScope</a>
  </p>
</div>

Skills to guide Claude Code, Codex, and other coding agents on using the
[SwanLab](https://swanlab.cn) AI training experiment tracking platform — both
writing tracking code and querying experiment data.

## 🚀 Getting Started

```bash
npx skills add SwanHubX/SwanLab-Skill -y -g
```



Then log in to SwanLab:

```bash
pip install swanlab
swanlab login          # paste your API key from https://swanlab.cn
swanlab ping           # (optional) check connectivity
swanlab verify         # (optional) validate credentials
```

> `npx skills` is a utility for installing skills into major coding agent CLIs.
> Use `--global` to install for all projects, or `--agent <name>` to target a
> specific agent. See the [npx skills docs](https://github.com/vercel-labs/skills)
> for more details.

## 💡 What you can do

| Capability | How | Entry point |
| --- | --- | --- |
| Log metrics & rich media (image / audio / text) during training and fine-tuning | Python SDK (`swanlab.init` / `swanlab.log` / `swanlab.finish` + media helpers) | `references/SDK_QUICKSTART.md` |
| Inspect a run's metrics, logs, summaries, columns, and media | `swanlab api run ...` CLI | `references/CLI_REFERENCE.md` |
| List / filter experiments by config or summary conditions | `swanlab api run filter` CLI | `references/CLI_REFERENCE.md` |
| Manage projects, self-hosted users, and other resources | `swanlab api project / user` CLI | `references/CLI_REFERENCE.md` |
| Understand the data model & terminology before querying | — | `references/SWANLAB_CONCEPTS.md` |
| Plot a **single** experiment's scalar metrics as a line chart | Helper script | `scripts/plot_metrics.py user/proj/run -k loss,acc -o chart.png` |
| **Compare** the same metric across **multiple** experiments (normalization + best-run ranking) | Helper script | `scripts/runs_benchmark.py user/proj/r1 user/proj/r2 -k loss --direction lower` |

Both helper scripts accept `--data file.json` to render from previously saved
query output, and require `swanlab login` (or `--api-key` / `--host`).

## 🪜 Run Modes

`swanlab.init(mode=...)` controls where data goes:

| Mode       | Local Storage | Cloud Upload | Use Case                                                      |
| ---------- | ------------- | ------------ | ------------------------------------------------------------- |
| `online`   | Yes           | Yes          | Normal cloud usage. Requires login.                           |
| `local`    | Yes           | No           | Air-gapped / no account needed.                               |
| `offline`  | Yes           | No           | Save locally, upload to cloud later via `swanlab sync`.       |
| `disabled` | No            | No           | Completely disable all logging.                               |

## 📚 License

[Apache License 2.0](LICENSE). 

Copyright 2024-2025 Emotion Machine (Beijing) Technology Co., Ltd.
