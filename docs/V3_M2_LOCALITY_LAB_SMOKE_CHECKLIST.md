# V3 M2 Locality Lab Smoke Checklist

## 自动验证

- [x] 370 项 `unittest` 全部通过，无 skip。
- [x] `LocalityLabWidget` 可在 Qt offscreen 环境创建。
- [x] 六个 preset 参数、F/S/T 和 Hit/Miss 结果符合稳定预期。
- [x] Reset、Step、Run All 正常。
- [x] 历史选择只更新 Evidence 与 Timeline SELECTED。
- [x] Cache、Statistics 与 Block Map 不因历史选择回滚。
- [x] 继续 Step 后新步骤恢复为 CURRENT/SELECTED。
- [x] Block Map 正确生成访问 cells 与重复访问计数。
- [x] 无 reuse 样本时平均值显示 N/A。
- [x] Home 与 Sidebar 可以进入 Locality Lab。
- [x] Registry factory 延迟创建页面。
- [x] 页面切换后复用同一实例并保持状态。
- [x] Policy、Performance、Write Policy 不创建页面。
- [x] 真实 GUI 入口进入事件循环至少 3 秒，无 traceback。

## 用户人工视觉验收

用户已确认以下项目通过：

- [x] Home 与 Sidebar 导航。
- [x] 页面整体布局和滚动。
- [x] 六个 preset。
- [x] Reset、Step、Run All。
- [x] Current Access 与历史 Evidence 的区分。
- [x] First Touch / Spatial / Temporal 与 HIT/MISS 的视觉分离。
- [x] Reuse Gap / Reuse Distance。
- [x] Cache State。
- [x] Block/Offset Access Map 与重复访问计数。
- [x] Timeline CURRENT / SELECTED。
- [x] 历史选择不回滚 Cache、Statistics 或 Block Map。
- [x] Row-major / Column-major 教学对比。
- [x] 页面切换后的状态保持。
- [x] 文字对比度、滚动和布局未发现明显问题。

## 稳定结果

| Preset | F/S/T | Hits/Misses |
|---|---:|---:|
| Sequential Spatial | 2/6/0 | 6/2 |
| Fixed Stride | 8/0/0 | 0/8 |
| Loop Temporal Reuse | 1/3/4 | 7/1 |
| Block Locality | 1/3/4 | 7/1 |
| Matrix Row-Major | 4/12/0 | 12/4 |
| Matrix Column-Major | 4/12/0 | 0/16 |

本清单记录 M2 已验证状态，不表示 Policy、Performance、Write Policy、L2、动画、历史 Cache snapshot 回滚、双实验比较或报告扩展已经实现。
