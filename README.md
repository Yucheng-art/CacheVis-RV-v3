# CacheVis-RV V3

CacheVis-RV V3 是面向计算机组成与 RISC-V Cache 教学的多实验室交互式可视化平台。

V3 已完成 M4 Performance Lab：在保持 V2 稳定行为以及 Miss Type、Locality、Policy 教学能力的基础上，提供显式时序假设下的 AMAT sweep、traffic、cycle decomposition 与 analytical L1/L2 教学页面。当前应用身份为 `CacheVis-RV V3.0`。

## 版本定位

- V1：软件著作权归档版，仅作只读参考。
- V2：稳定的 Address Visualizer 版，仅作只读参考。
- V3：采用 Sidebar、Home、Lab Registry 与 `QStackedWidget` 的多 Lab 平台版。

## 当前可用功能

- Address Explorer
- Miss Type Lab
- Locality Lab
- Policy Lab
- Performance Lab
- Single Experiment
- Compare Experiment

以下教学 Lab 仍为 Coming Soon，尚未实现：

- Write Policy Lab

Performance Lab 使用教学用显式 cycle 模型，而不是宿主机 Python wall-clock benchmark。页面提供六个单级 Cache sweep、可编辑 point、七种指标图表、selected point 细节、Hit Rate/AMAT reversal，以及独立的 analytical L1/L2 AMAT 分解。当前没有实际 L2 CacheSimulator、write-back traffic 或硬件自动推导的 hit-time 模型。

平台页面按需创建并缓存，切换页面不会丢失已创建 Lab 的状态。当前回归基线为 620 项 `unittest` 全部通过，无 skip；Qt smoke、真实 GUI 入口启动和用户人工视觉验收均已通过。

下一阶段为 M5 Write Policy Lab，继续遵循“纯逻辑 → `unittest` → GUI”的开发顺序。

## 文档

- [产品与技术架构](docs/V3_PRODUCT_AND_TECH_ARCHITECTURE.md)
- [M0 平台外壳总结](docs/V3_M0_PLATFORM_SHELL_SUMMARY.md)
- [M0 Smoke Checklist](docs/V3_M0_SMOKE_CHECKLIST.md)
- [M1 Miss Type Lab 总结](docs/V3_M1_MISS_TYPE_LAB_SUMMARY.md)
- [M1 Miss Type Lab Smoke Checklist](docs/V3_M1_MISS_TYPE_LAB_SMOKE_CHECKLIST.md)
- [M2 Locality Lab 总结](docs/V3_M2_LOCALITY_LAB_SUMMARY.md)
- [M2 Locality Lab Smoke Checklist](docs/V3_M2_LOCALITY_LAB_SMOKE_CHECKLIST.md)
- [M3 Policy Lab 总结](docs/V3_M3_POLICY_LAB_SUMMARY.md)
- [M3 Policy Lab Smoke Checklist](docs/V3_M3_POLICY_LAB_SMOKE_CHECKLIST.md)
- [M4 Performance Lab 总结](docs/V3_M4_PERFORMANCE_LAB_SUMMARY.md)
- [M4 Performance Lab Smoke Checklist](docs/V3_M4_PERFORMANCE_LAB_SMOKE_CHECKLIST.md)
- [项目交接上下文](docs/PROJECT_HANDOFF_CONTEXT.md)
- [V2 继承计划](docs/V2_INHERITANCE_PLAN.md)
- [路线图](docs/ROADMAP.md)
- [决策记录](docs/DECISIONS.md)

## 仓库约束

V1/V2 始终只读。不得上传 `Cache*.pdf`、环境目录、缓存或构建输出；未经明确许可不得提交、推送、创建 tag 或 PR。
