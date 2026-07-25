# V3 M1 Miss Type Lab 总结

## 里程碑状态

M1 已完成。Miss Type Lab 已正式成为 Available Lab，并通过 Lab Registry 接入 Home、Sidebar 和 Main Window 的惰性页面缓存。

完成时质量基线：

- 270 项 `unittest` 全部通过，无 skip。
- Qt offscreen smoke 通过。
- GUI 真实入口进入事件循环至少 3 秒且无 traceback。
- 三个 preset、双 Cache、Evidence、Statistics、Timeline、滚动布局与页面状态保持已完成人工视觉验收。

## 严格 3C 模型

分类单位是 memory block，不是原始 byte address。地址的 block offset 不改变 memory block 身份。

每次访问同时执行：

1. Actual Cache 访问。
2. 同容量、同 block size 的 fully associative LRU Reference Cache 访问。
3. seen-before 判断。
4. 使用既有分类结果形成证据链。

分类规则：

- 第一次访问 memory block 且 Actual miss：Compulsory。
- 非首次访问，Actual miss、Reference hit：Conflict。
- 非首次访问，Actual miss、Reference miss：Capacity。
- Actual hit：不进行 miss 分类。

Actual Cache 在本 Lab 中固定使用 LRU，避免引入 policy miss。该限制不改变通用 Cache core 对其他 replacement policy 的既有支持。

## 页面结构

- Experiment Controls：preset、trace、Cache size、block size、ways、固定 LRU，以及 Reset、Step、Run All。
- Current Access：最新执行步骤、地址、memory block、Actual/Reference 结果、分类和 set/way 证据。
- Actual Cache：真实 sets/ways 与 Cache line 状态。
- Fully Associative Reference Cache：同容量参考 Cache 的单 set/all-lines 状态。
- Classification Evidence：seen-before、双方 hit/miss、分类原因和 rule path。
- 3C Statistics：Accesses、Hits、Misses、C/F/A、Hit Rate、Miss Rate 和统计不变量。
- Timeline：横向可滚动的 H/C/F/A chip，以及独立 CURRENT/SELECTED 状态。

历史 Timeline 选择只更新 Evidence。Current Access、双 Cache 和累计 Statistics 保持最新执行状态；本阶段不实现历史 Cache snapshot 回滚。

## 内置 preset

| Preset | 稳定结果 |
| --- | --- |
| Compulsory demo | C C C C |
| Conflict demo | C C F F |
| Capacity demo | C C C A |

地址输入支持十进制、`0x` 十六进制，以及逗号、空格和换行混合分隔。共享 parser 位于 `cachevis_rv.experiments`，Address Explorer 保留兼容 facade。

## 尚未实现

- Locality Lab
- Policy Lab
- Performance Lab
- Write Policy Lab
- L2
- 完整 write-back 行为
- 历史 Cache snapshot 回滚
- 动画

下一阶段为 M2 Locality Lab。
