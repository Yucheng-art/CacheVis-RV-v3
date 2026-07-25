# V3 M1 Miss Type Lab Smoke Checklist

## 自动验证

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
```

预期：

- `Ran 270 tests`
- `OK`
- 无 skip

Qt smoke 应确认：

- `MissTypeLabWidget` 可创建。
- 三个 preset 分别产生 C C C C、C C F F、C C C A。
- Reset、Step、Run All 正常。
- 历史 Timeline step 可选择。
- 选择历史步骤后 Evidence 更新，但双 Cache 与 Statistics 不回滚。
- Home 与 Sidebar 均可进入 Miss Type Lab。
- 首次导航延迟创建页面，重复导航复用同一实例。
- 切换到其他 Lab 后返回，Miss Type Lab 状态保持。
- GUI 真实入口进入 Qt event loop 至少 3 秒且无 traceback。

## 人工视觉验收

- [ ] Home 的 Miss Type Lab 卡片显示 Available，按钮为 Open Lab。
- [ ] Sidebar Learn 分组包含 Address Explorer 和 Miss Type Lab。
- [ ] 页面整体可滚动，小窗口下内容不溢出。
- [ ] Experiment Controls、Current Access、双 Cache、Evidence、Statistics 和 Timeline 布局清晰。
- [ ] 三个 preset 切换只填充参数，不自动运行。
- [ ] Reset、Step、Run All 的状态变化与提示正确。
- [ ] Actual Cache 与 Reference Cache 卡片字段完整且可对照。
- [ ] Reference Cache 明确标注同容量、fully associative、LRU。
- [ ] Compulsory、Conflict、Capacity 的证据链与语义颜色清晰。
- [ ] 浅色语义背景使用高对比度深色文字。
- [ ] Timeline chip 可横向滚动，CURRENT 与 SELECTED 易于区分。
- [ ] 选择历史步骤只更新 Evidence，不回滚双 Cache 或 Statistics。
- [ ] 页面切换后实例和实验状态保持。
- [ ] 关闭并再次启动应用后，页面可正常重新进入。

## 当前明确边界

本里程碑不包含 Locality、Policy、Performance、Write Policy、L2、完整 write-back、历史 Cache snapshot 回滚或动画。
