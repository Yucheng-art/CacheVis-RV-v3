# CacheVis-RV V3

CacheVis-RV V3 是面向计算机组成与 RISC-V Cache 教学的多实验室交互式可视化平台。当前应用身份为 `CacheVis-RV V3.0`，M0–M5 计划内功能里程碑已经完成。

## 版本定位

- V1：软件著作权归档版，仅作只读参考。
- V2：稳定 Address Visualizer 版，仅作只读参考。
- V3：采用 Sidebar、Home、Lab Registry 与 `QStackedWidget` 的多 Lab 平台版。

## 当前可用功能

平台共有 8 个 Available Lab，Coming Soon 为 0。

Learn：

1. Address Explorer
2. Miss Type Lab
3. Locality Lab
4. Policy Lab
5. Performance Lab
6. Write Policy Lab

Classic Tools：

7. Single Experiment
8. Compare Experiment

Write Policy Lab 同步比较 Write-Through / Write-Back 与 Write-Allocate / No-Write-Allocate 四种组合，展示 dirty line、dirty eviction，以及 block fill、immediate store、bypass 和 dirty write-back 的教学流量。页面明确区分 runtime traffic 与 final dirty drain；查看历史 evidence 不会回滚当前 Cache、统计或运行位置。

平台页面按需创建并缓存，切换页面不会丢失已创建 Lab 的状态。当前回归基线为 720 项 `unittest` 全部通过、无 skip；Qt offscreen smoke、真实 GUI 入口启动、七个 Write Policy preset GUI smoke 和用户人工视觉验收均已通过。

Write Policy Lab 不模拟 store buffer、write combining、coherence、memory consistency、实际 L2、pipeline CPI、energy model、动画或专用报告导出。当前 trace 的结果只适用于给定 Cache 配置和流量假设，不代表任一策略普遍最优。

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
- [M5 Write Policy Lab 总结](docs/V3_M5_WRITE_POLICY_LAB_SUMMARY.md)
- [M5 Write Policy Lab Smoke Checklist](docs/V3_M5_WRITE_POLICY_LAB_SMOKE_CHECKLIST.md)
- [项目交接上下文](docs/PROJECT_HANDOFF_CONTEXT.md)
- [V2 继承计划](docs/V2_INHERITANCE_PLAN.md)
- [路线图](docs/ROADMAP.md)
- [决策记录](docs/DECISIONS.md)

## 仓库约束

V1/V2 始终只读。不得上传 `Cache*.pdf`、环境目录、缓存或构建输出；未经明确许可不得提交、推送、创建 tag 或 PR。
