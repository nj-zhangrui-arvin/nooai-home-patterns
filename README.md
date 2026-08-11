# nooai-home-patterns

![Synthetic smart-home dashboard preview](assets/hero.png)

## 中文

### 目的

把公开可分享的 Home Assistant 模块、Skill、文档、示例和发布门禁收敛到一个总仓库。

### 价值

- 同时提供公开发布审计、人物定位、可靠命令、通勤策略和阶段交付模式。
- 保留完整的公开 docs/examples/tests/tools 结构，方便二次拆分或直接参考。
- 默认不带任何私有家庭配置、历史或运行数据；展示图为独立生成的虚构场景。

### Quickstart

```bash
env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
env PYTHONDONTWRITEBYTECODE=1 python3 tools/check_public_export.py .
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

### Quickstart

```bash
env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
env PYTHONDONTWRITEBYTECODE=1 python3 tools/check_public_export.py .
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
