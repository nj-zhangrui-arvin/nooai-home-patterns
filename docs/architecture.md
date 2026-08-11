# Architecture

```text
provider adapters -> normalized evidence -> pure policy/state machine
                                      |-> Home Assistant adapter
                                      |-> dashboard view model
                                      |-> structured diagnostics
```

公共模块不绑定家庭实体。HA YAML、厂商 API 和 UI 只是适配层；可复用核心接收结构化输入并返回可测试结果。

## 边界

- Presence：区域拓扑优先，信号只在已确认分支中辅助；
- Device commands：意图、发送、确认和失败分离；
- Commute：数据来源、时效和结论分离；
- Floorplan：模型、注册清单、渲染资产和 UI 状态分离；
- Operations：默认只读，写入走备份、检查、部署、验证和回滚。
