# V3 M2 Locality Lab 总结

## 里程碑结果

M2 已完成 Locality 分析核心、Controller/View Models、独立 PySide6 页面和平台接入。Locality Lab 已从 Coming Soon 迁移为 Available，可从 Home 与 Sidebar 打开；Registry factory 延迟创建页面，Main Window 缓存并复用页面实例。

M2 完成时共有 370 项 `unittest` 全部通过，无 skip；Qt offscreen smoke、真实 GUI 入口启动以及用户人工视觉验收均已通过。

## 教学模型

Locality Lab 使用 mutually exclusive primary evidence，方便逐步解释每次访问：

1. exact address 已访问 → `TEMPORAL`
2. address 未访问但 memory block 已访问 → `SPATIAL`
3. memory block 未访问 → `FIRST_TOUCH`

现实访问可能同时具有多种局部性特征；这里的互斥分类是教学展示选择，不是对现实局部性的唯一描述。

地址转换规则：

```text
block_address = address // block_size_bytes
offset = address % block_size_bytes
```

Locality 与 Cache HIT/MISS 相互独立：

- HIT 不自动等于 Temporal。
- MISS 不自动等于没有 locality。
- Spatial hit 可以存在。
- Temporal miss 可以存在。

## 复用证据与统计

每一步可展示：

- address reuse gap
- block reuse gap
- block reuse distance
- same-block transition
- address delta
- unique addresses / unique blocks
- Cache hit/miss
- First Touch / Spatial / Temporal counts and rates

Block reuse distance 使用 MRU→LRU distinct-block recency stack；访问发生前，目标 block 在栈中的索引就是 reuse distance。首次访问没有 reuse 样本，相关平均值显示 N/A，而不是 0.0。

持续验证三个不变量：

- `F + S + T = Accesses`
- `F + S = Unique Addresses`
- `Hits + Misses = Accesses`

## 页面与状态语义

页面包含：

- Experiment Controls
- Current Access
- Locality Evidence
- Cache State
- Block/Offset Access Map
- Locality Statistics
- Teaching Insight
- Timeline

历史 Timeline 选择只更新 selected Evidence 和 SELECTED 标记，不回滚 Current Access、Cache State、Statistics 或 Block Access Map。继续执行 Step 后，新步骤重新成为 CURRENT 和 SELECTED。

## 六个内置 Preset

| Preset | F/S/T | Hits/Misses |
|---|---:|---:|
| Sequential Spatial | 2/6/0 | 6/2 |
| Fixed Stride | 8/0/0 | 0/8 |
| Loop Temporal Reuse | 1/3/4 | 7/1 |
| Block Locality | 1/3/4 | 7/1 |
| Matrix Row-Major | 4/12/0 | 12/4 |
| Matrix Column-Major | 4/12/0 | 0/16 |

Row-major 和 Column-major 访问完全相同的 16 个地址，最终 Block Map cell 集合与 F/S 计数相同。两者访问顺序不同，因此 Cache 结果显著不同。Column-major 并非没有 spatial locality；它是在当前 direct-mapped Cache 组织下没有有效利用已有的空间局部性潜力。

## 尚未实现

- Policy Lab
- Performance Lab
- Write Policy Lab
- L2
- 历史 Cache snapshot 回滚
- 动画
- Locality 双实验同时对比引擎
- 报告导出扩展

下一阶段为 M3 Policy Lab。
