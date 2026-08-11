# Reference modules

这些模块是纯逻辑参考实现，不连接真实 Home Assistant 或厂商 API。

- `presence_inference.py`：区域拓扑优先，信号只在已确认分支中分类；
- `reliable_device_command.py`：无回读设备的幂等命令状态机；
- `commute_alert.py`：带 freshness、provenance 和人工复核的提示策略。

生产集成应把实体状态转换为这些模块的输入，再把结果映射回 HA；模块本身不调用设备服务。

所有时间戳在适配器边界应转换为带时区的 UTC `datetime`。为兼容合成 fixture，模块会把 naive `datetime` 解释为 UTC；不要把本地墙上时间以 naive 值传入。
