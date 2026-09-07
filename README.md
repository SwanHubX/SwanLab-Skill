<div align="center">

<a href="https://swanlab.cn/">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="public/SWANLAB_LOGO_DARK.svg" />
    <source media="(prefers-color-scheme: light)" srcset="public/SWANLAB_LOGO.svg" />
    <img src="public/SWANLAB_LOGO.svg" alt="SwanLab" width="360" />
  </picture>
</a>

<h1><a href="https://swanlab.cn/">SwanLab.skill</a></h1>

> 让 Agent 正确使用 SwanLab 写实验跟踪代码、查询与分析实验数据。

[![SwanLab 官网](https://img.shields.io/badge/SwanLab-官网-C21E31?labelColor=black&style=flat-square)](https://swanlab.cn/)
[![SwanLab Docs](https://img.shields.io/badge/SwanLab-官方文档-c4f042?labelColor=black&style=flat-square)](https://docs.swanlab.cn)
[![ModelScope Skill](https://img.shields.io/badge/ModelScope-Skill-624aff)](https://www.modelscope.cn/skills/SwanLab/swanlab-skill)
[![Agent Skill](https://img.shields.io/badge/Agent-Skill-7c3aed)](skills/swanlab-skill/SKILL.md)
[![Skill Version](https://img.shields.io/badge/Skill-v0.2.6-7c3aed)](skills/swanlab-skill/SKILL.md)
[![SkillHub](https://img.shields.io/badge/SkillHub-Skill-1f8f4c)](https://skillhub.cn/skills/swanlab-skill)
[![License](https://img.shields.io/badge/License-MIT-d4a017)](LICENSE)

这个 Skill 覆盖两类用法：用 Python SDK（`swanlab.init` / `swanlab.log` / `swanlab.finish` + 多媒体记录）写训练跟踪代码；用 `swanlab api` CLI 查询实验指标、日志、摘要与媒体。Agent 会先按任务路由读取对应的能力说明，再生成代码或执行查询，避免误用接口。

[English](README_EN.md) · [安装](#安装) · [内容](#内容) · [能力](#能力) · [运行模式](#运行模式) · [打包](#打包)

</div>

---

## 安装

如果你正在使用 Claude Code、Codex 等 coding agent，直接将下面这段话发给它即可自动完成安装：

```text
Fetch the installation guide and follow it: https://raw.githubusercontent.com/SwanHubX/SwanLab-Skill/main/README.md
```

手动安装推荐使用全局安装方式：

```bash
npx skills add SwanHubX/SwanLab-Skill -g -y
```

也可以在 [ModelScope](https://www.modelscope.cn/skills/SwanLab/swanlab-skill) 或 [SkillHub](https://skillhub.cn/skills/swanlab-skill) 查看 skill 页面。

> 注：`-g` 表示安装到当前用户级别，`-y` 表示跳过交互确认。这个方式不会把 skill 写进当前项目目录；它只会把 skill 下载到用户目录下的 `.agents/skills`，再为 Claude Code、Codex 等支持 Agent Skills 的 CLI 创建软链接。同一个用户下的多个 Agent CLI 可以复用这一份 skill。

然后登录 SwanLab：

```bash
pip install swanlab
swanlab login          # paste your API key from https://swanlab.cn
swanlab ping           # (optional) check connectivity
swanlab verify         # (optional) validate credentials
```

后续如果 SwanLab Skill 有更新，执行：

```bash
npx skills update swanlab-skill -g -y
```

## 内容

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

| 文件                             | 作用                                                                       |
| -------------------------------- | -------------------------------------------------------------------------- |
| `SKILL.md`                       | 轻量入口和任务路由，告诉 Agent 应该读 SDK 文档还是 CLI 文档                |
| `references/SDK_QUICKSTART.md`   | `swanlab.init` / `log` / `finish` 与 image / audio / text 等多媒体记录写法 |
| `references/CLI_REFERENCE.md`    | `swanlab api` 查询指标、日志、摘要、列、媒体与筛选实验                     |
| `references/SWANLAB_CONCEPTS.md` | 数据模型、术语与路径约定（`user/project/run_id`）                          |
| `scripts/plot_metrics.py`        | 单个实验标量指标折线图                                                     |
| `scripts/runs_benchmark.py`      | 跨实验对比同一指标（归一化 + 最优 run 排名）                               |

## 能力

| 能力                                                              | 方式                             | 入口                                                                            |
| ----------------------------------------------------------------- | -------------------------------- | ------------------------------------------------------------------------------- |
| 训练 / 微调中记录指标与媒体等对象资源文件（image / audio / text） | Python SDK                       | `references/SDK_QUICKSTART.md`                                                  |
| 查看某个 run 的指标、日志、摘要、列与媒体                         | `swanlab api run ...` CLI        | `references/CLI_REFERENCE.md`                                                   |
| 按 config 或 summary 条件筛选实验                                 | `swanlab api run filter` CLI     | `references/CLI_REFERENCE.md`                                                   |
| 管理项目、私有化用户等资源                                        | `swanlab api project / user` CLI | `references/CLI_REFERENCE.md`                                                   |
| 查询前理解数据模型与术语                                          | —                                | `references/SWANLAB_CONCEPTS.md`                                                |
| 画**单个**实验的标量指标折线图                                    | 辅助脚本                         | `scripts/plot_metrics.py user/proj/run -k loss,acc -o chart.png`                |
| **对比**多个实验的同一指标（归一化 + 排名）                       | 辅助脚本                         | `scripts/runs_benchmark.py user/proj/r1 user/proj/r2 -k loss --direction lower` |

两个辅助脚本都支持 `--data file.json` 从已保存的查询结果渲染，并要求先 `swanlab login`（或传 `--api-key` / `--host`）。

## 运行模式

`swanlab.init(mode=...)` 控制数据去向：

| Mode       | 本地存储 | 云端上传 | 适用场景                             |
| ---------- | -------- | -------- | ------------------------------------ |
| `online`   | Yes      | Yes      | 正常云端使用，需要登录               |
| `local`    | Yes      | No       | 离线环境，无需账号                   |
| `offline`  | Yes      | No       | 先存本地，之后用 `swanlab sync` 上传 |
| `disabled` | No       | No       | 完全关闭记录                         |

## 打包

生成发布包：

```bash
make package
```

生成的 `dist/swanlab-skill.zip` 会解压成：

```text
SKILL.md
references/
scripts/
```

因此可以直接解压到 `.claude/skills/swanlab-skill/` 等 skill 目录使用。

## 许可证

[MIT License](LICENSE).

Copyright (c) 2026 Emotion Machine (Beijing) Technology Co., Ltd.
