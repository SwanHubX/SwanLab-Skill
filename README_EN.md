<div align="center">

<a href="https://swanlab.cn/">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="public/SWANLAB_LOGO_DARK.svg" />
    <source media="(prefers-color-scheme: light)" srcset="public/SWANLAB_LOGO.svg" />
    <img src="public/SWANLAB_LOGO.svg" alt="SwanLab" width="360" />
  </picture>
</a>

<h1><a href="https://swanlab.cn/">SwanLab.skill</a></h1>

> Teach agents to write SwanLab tracking code and query experiment data correctly.

[![SwanLab Website](https://img.shields.io/badge/SwanLab-Website-C21E31?labelColor=black&style=flat-square)](https://swanlab.cn/)
[![SwanLab Docs](https://img.shields.io/badge/SwanLab-Docs-c4f042?labelColor=black&style=flat-square)](https://docs.swanlab.cn)
[![ModelScope Skill](https://img.shields.io/badge/ModelScope-Skill-624aff)](https://www.modelscope.cn/skills/SwanLab/swanlab-skill)
[![Agent Skill](https://img.shields.io/badge/Agent-Skill-7c3aed)](skills/swanlab-skill/SKILL.md)
[![Skill Version](https://img.shields.io/badge/Skill-v0.3.0-7c3aed)](skills/swanlab-skill/SKILL.md)
[![SkillHub](https://img.shields.io/badge/SkillHub-Skill-1f8f4c)](https://skillhub.cn/skills/swanlab-skill)
[![License](https://img.shields.io/badge/License-MIT-d4a017)](LICENSE)

This skill covers two usage patterns: writing training tracking code with the Python SDK (`swanlab.init` / `swanlab.log` / `swanlab.finish` + multimedia logging), and querying experiment metrics, logs, summaries, and media with the `swanlab api` CLI. The agent first reads the capability reference routed by task, then generates code or runs queries — avoiding API misuse.

[中文](README.md) · [Installation](#installation) · [Contents](#contents) · [Capabilities](#capabilities) · [Run Modes](#run-modes) · [Packaging](#packaging)

</div>

---

## Installation

If you're using coding agent like Claude Code or Codex, just send it the following prompt to install automatically:

```text
Fetch the installation guide and follow it: https://raw.githubusercontent.com/SwanHubX/SwanLab-Skill/main/README.md
```

For manual installation, the recommended way is a global install:

```bash
npx skills add SwanHubX/SwanLab-Skill -g -y
```

You can also view the skill page on [ModelScope](https://www.modelscope.cn/skills/SwanLab/swanlab-skill) or [SkillHub](https://skillhub.cn/skills/swanlab-skill).

> Note: `-g` installs at user level and `-y` skips interactive confirmation. Nothing is written into the current project — the skill is downloaded to `.agents/skills` under your home directory, with symlinks created for Claude Code, Codex, and other CLIs that support Agent Skills. Multiple agent CLIs under the same user can share this single copy.

Then log in to SwanLab:

```bash
pip install swanlab
swanlab login          # paste your API key from https://swanlab.cn
swanlab ping           # (optional) check connectivity
swanlab verify         # (optional) validate credentials
```

To update the skill later:

```bash
npx skills update swanlab-skill -g -y
```

## Contents

```text
skills/
└── swanlab-skill/
    ├── SKILL.md
    ├── references/
    │   ├── SDK_QUICKSTART.md
    │   ├── CLI_REFERENCE.md
    │   └── SWANLAB_CONCEPTS.md
    └── scripts/
        ├── plot_metrics.py
        └── runs_benchmark.py
```

| File                             | Purpose                                                                                              |
| -------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `SKILL.md`                       | Lightweight entry point and task router — tells the agent whether to read the SDK or CLI reference   |
| `references/SDK_QUICKSTART.md`   | Tracking code quickstart: `swanlab.init` / `log` / `finish` and media logging (image / audio / text) |
| `references/CLI_REFERENCE.md`    | Query metrics, logs, summaries, columns, and media, and filter experiments via `swanlab api`         |
| `references/SWANLAB_CONCEPTS.md` | Data model, terminology, and path convention (`user/project/run_id`)                                 |
| `scripts/plot_metrics.py`        | Line chart of a single experiment's scalar metrics                                                   |
| `scripts/runs_benchmark.py`      | Compare the same metric across experiments (normalization + best-run ranking)                        |

## Capabilities

| Capability                                                                                     | How                              | Entry point                                                                     |
| ---------------------------------------------------------------------------------------------- | -------------------------------- | ------------------------------------------------------------------------------- |
| Log metrics & rich media (image / audio / text) during training and fine-tuning                | Python SDK                       | `references/SDK_QUICKSTART.md`                                                  |
| Inspect a run's metrics, logs, summaries, columns, and media                                   | `swanlab api run ...` CLI        | `references/CLI_REFERENCE.md`                                                   |
| List / filter experiments by config or summary conditions                                      | `swanlab api run filter` CLI     | `references/CLI_REFERENCE.md`                                                   |
| Manage projects, self-hosted users, and other resources                                        | `swanlab api project / user` CLI | `references/CLI_REFERENCE.md`                                                   |
| Understand the data model & terminology before querying                                        | —                                | `references/SWANLAB_CONCEPTS.md`                                                |
| Plot a **single** experiment's scalar metrics as a line chart                                  | Helper script                    | `scripts/plot_metrics.py user/proj/run -k loss,acc -o chart.png`                |
| **Compare** the same metric across **multiple** experiments (normalization + best-run ranking) | Helper script                    | `scripts/runs_benchmark.py user/proj/r1 user/proj/r2 -k loss --direction lower` |

Both helper scripts accept `--data file.json` to render from previously saved query output, and require `swanlab login` (or `--api-key` / `--host`).

## Run Modes

`swanlab.init(mode=...)` controls where data goes:

| Mode       | Local Storage | Cloud Upload | Use Case                                                |
| ---------- | ------------- | ------------ | ------------------------------------------------------- |
| `online`   | Yes           | Yes          | Normal cloud usage. Requires login.                     |
| `local`    | Yes           | No           | Air-gapped / no account needed.                         |
| `offline`  | Yes           | No           | Save locally, upload to cloud later via `swanlab sync`. |
| `disabled` | No            | No           | Completely disable all logging.                         |

## Packaging

Build the release archive:

```bash
make package
```

The generated `dist/swanlab-skill.zip` extracts to:

```text
SKILL.md
references/
scripts/
```

So it can be extracted directly into a skill directory such as `.claude/skills/swanlab-skill/`.

## License

[MIT License](LICENSE).

Copyright (c) 2026 Emotion Machine (Beijing) Technology Co., Ltd.
