# CacheVis-RV V3

CacheVis-RV V3 是面向计算机组成与 RISC-V Cache 教学的多实验室交互式可视化平台。

V3 已完成 M3 Policy Lab：在保持 V2 稳定行为、M1 严格 3C Miss 分类和 M2 Locality 分析的基础上，提供同步比较 LRU、FIFO 与 seeded Random 的替换策略教学页面。当前应用身份为 `CacheVis-RV V3.0`。

## 版本定位

- V1：软件著作权归档版，仅作只读参考。
- V2：稳定的 Address Visualizer 版，仅作只读参考。
- V3：采用 Sidebar、Home、Lab Registry 与 `QStackedWidget` 的多 Lab 平台版。

## 当前可用功能

- Address Explorer
- Miss Type Lab
- Locality Lab
- Policy Lab
- Single Experiment
- Compare Experiment

以下教学 Lab 仍为 Coming Soon，尚未实现：

- Performance Lab
- Write Policy Lab

Policy Lab 对同一 Cache 配置和 address trace 同步运行 LRU、FIFO 与 seeded Random。页面区分 HIT、INVALID_FILL 和 EVICTION，展示三条策略的决策证据、最新 Cache state、victim/state/outcome divergence、统计与 Timeline。历史 Timeline 选择只更新 Selected Decision Evidence，不回滚最新执行状态或 Random stream。

平台页面按需创建并缓存，切换页面不会丢失已创建 Lab 的状态。当前回归基线为 477 项 `unittest` 全部通过，无 skip；Qt smoke、真实 GUI 入口启动和用户人工视觉验收均已通过。

下一阶段为 M4 Performance Lab，继续遵循“纯逻辑 → `unittest` → GUI”的开发顺序。

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
- [项目交接上下文](docs/PROJECT_HANDOFF_CONTEXT.md)
- [V2 继承计划](docs/V2_INHERITANCE_PLAN.md)
- [路线图](docs/ROADMAP.md)
- [决策记录](docs/DECISIONS.md)

## 仓库约束

V1/V2 始终只读。不得上传 `Cache*.pdf`、环境目录、缓存或构建输出；未经明确许可不得提交、推送、创建 tag 或 PR。
