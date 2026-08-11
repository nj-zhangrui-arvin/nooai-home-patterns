# nooai-home-patterns

![Synthetic smart-home dashboard preview](assets/hero.png)

## 中文

### 目的

把公开可分享的 Home Assistant 模块、Skill、文档、示例和发布门禁收敛到一个总仓库。

### 价值

- 同时提供公开发布审计、人物定位、可靠命令、通勤策略和阶段交付模式。
- 保留完整的公开 docs/examples/tests/tools 结构，方便二次拆分或直接参考。
- 默认不带任何私有家庭配置、历史或运行数据；展示图为独立生成的虚构场景。

### 独立仓库

| 项目 | 解决的问题 |
| --- | --- |
| [public-release-audit](https://github.com/nj-zhangrui-arvin/public-release-audit) | 在公开前检查工作树、暂存区、历史、媒体与凭据泄露。 |
| [ha-reliable-command](https://github.com/nj-zhangrui-arvin/ha-reliable-command) | 为无回读或弱回读设备提供不过度声称成功的幂等状态机。 |
| [ha-presence-evidence](https://github.com/nj-zhangrui-arvin/ha-presence-evidence) | 用区域拓扑和证据链约束 RSSI，阻止不可能的房间跳变。 |
| [ha-floorplan-pipeline](https://github.com/nj-zhangrui-arvin/ha-floorplan-pipeline) | 规范合成或许可 3D 户型资产的生成、校验与隐私门禁。 |
| [codex-phase-release](https://github.com/nj-zhangrui-arvin/codex-phase-release) | 把长任务收敛为有范围、有证据、可交接的阶段交付。 |
| [ha-commute-policy](https://github.com/nj-zhangrui-arvin/ha-commute-policy) | 用 freshness 与 provenance 做 provider-neutral 通勤提醒判断。 |

### Quickstart

```bash
env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
env PYTHONDONTWRITEBYTECODE=1 python3 tools/check_public_export.py . --media-manifest media-manifest.json
```

### 效果

- 生成与 `open-source/` 对齐的公共候选仓库结构，并补上 MIT、Provenance、CI 和媒体门禁。
- 首页效果图经过元数据清理和精确哈希审核，由 `media-manifest.json` 管控。

### 限制

- 不是生产 Home Assistant 配置，也不保留原私有 Git 历史。
- 任何新增媒体或第三方资产都需要再次人工审核。

### 隐私

- 目录只来自公开白名单；显式排除 `home-assistant/`、`scripts/`、`data/`、历史和缓存。
- 公共示例全部基于合成实体名、example 配置和脱敏文档。

## English

### Purpose

Collect the publicly shareable Home Assistant modules, skills, documentation, examples, and release gates in one umbrella repository.

### Value

- Combines public release auditing, presence inference, reliable commands, commute policy, and phase release patterns.
- Keeps the full public docs/examples/tests/tools structure for direct reuse or further splitting.
- Ships with no private household configuration, history, or runtime data; its preview is fictional and independently generated.

### Standalone repositories

| Project | What it removes |
| --- | --- |
| [public-release-audit](https://github.com/nj-zhangrui-arvin/public-release-audit) | Checks trees, staged changes, history, media, and credentials before publication. |
| [ha-reliable-command](https://github.com/nj-zhangrui-arvin/ha-reliable-command) | Adds an idempotent state machine for weak-feedback devices without claiming unobserved success. |
| [ha-presence-evidence](https://github.com/nj-zhangrui-arvin/ha-presence-evidence) | Constrains RSSI with topology and evidence to prevent impossible room jumps. |
| [ha-floorplan-pipeline](https://github.com/nj-zhangrui-arvin/ha-floorplan-pipeline) | Defines generation, validation, and privacy gates for synthetic or licensed 3D floorplans. |
| [codex-phase-release](https://github.com/nj-zhangrui-arvin/codex-phase-release) | Turns long tasks into bounded, evidenced, handoff-ready phases. |
| [ha-commute-policy](https://github.com/nj-zhangrui-arvin/ha-commute-policy) | Makes provider-neutral commute decisions with freshness and provenance. |

### Quickstart

```bash
env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
env PYTHONDONTWRITEBYTECODE=1 python3 tools/check_public_export.py . --media-manifest media-manifest.json
```

### Outcomes

- Builds a public-candidate repository aligned with `open-source/` while adding MIT, provenance, CI, and media gates.
- Keeps the homepage preview under an exact digest-based media manifest.

### Limitations

- It is not a production Home Assistant configuration and does not preserve private Git history.
- Any new media or third-party assets still require manual review.

### Privacy

- The tree is built only from the public allowlist and explicitly excludes `home-assistant/`, `scripts/`, `data/`, history, and caches.
- All public examples rely on synthetic entity names, example configs, and redacted documentation.
