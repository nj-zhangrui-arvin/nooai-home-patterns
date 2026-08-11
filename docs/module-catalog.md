# Module catalog

| 模块 | 形式 | 复用边界 |
| --- | --- | --- |
| Presence inference | Python 纯逻辑 + Skill | 拓扑事件、TTL、分支内信号候选 |
| Reliable command | Python 状态机 | 无回读/弱回读设备的意图与确认 |
| Commute alert | Python 策略 | provider-neutral 时效与人工复核 |
| Floorplan 3D | Skill | 备份、生成、注册、视觉和 staged 门禁 |
| Phase release | Skill | 分阶段执行、证据、提交和交接 |
| Public release audit | Skill + Python 门禁 | 工作树、暂存区、提交信息、历史和私密元数据 |
| SSH/Windows | 依赖既有 Skills | `ssh-inspect` 与 `ssh-windows-utf8`，不重复实现 |

天气安全可以复用 Commute 的 freshness/provenance 模式。洗衣、晾衣架、窗帘和红外设备可以复用 Reliable command 状态机。

生态边界：3D 输出可对接 SVG/GLB Lovelace 卡；BLE/MQTT 定位由 Bermuda、ESPresense 等 provider 采集，本项目只负责证据归一化与拓扑推断。第三方来源和许可证见 `../THIRD_PARTY_NOTICES.md`。
