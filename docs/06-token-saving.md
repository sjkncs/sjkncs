# 06 — Token 节约 详细文档

> 对应技能：`.codebuddy/skills/06-token-saving/SKILL.md`

## Token 经济学

AI 编程助手的 Token 消耗规律：

```
单个编码会话的 Token 分布（典型）：
├── 系统提示词 + 规则加载：      ~3,000 tokens  (5%)
├── 项目探索（读文件、搜索）：     ~8,000 tokens  (15%)
├── 代码理解（读关键文件）：      ~12,000 tokens (22%)
├── 对话交互（问与答）：          ~20,000 tokens (37%)
├── 代码生成与修改：             ~8,000 tokens  (15%)
└── 错误修复与迭代：             ~3,000 tokens  (6%)
                                  ─────────
                          总计：  ~54,000 tokens
```

**优化重点**：项目探索 + 代码理解 + 对话交互 = 占总消耗的 74%

## 策略详解

### 策略 1：信息懒加载

```
传统方式：
  理解需求 → 读全部相关文件 → 分析 → 修改
  成本：一次性加载 10+ 文件，~15,000 tokens

懒加载方式：
  理解需求 → search_content 精准定位 → 按需 read_file → 修改
  成本：初始搜索 ~500 tokens，按需读取 ~3,000 tokens
  节省：~75%
```

### 策略 2：选择性阅读

```
反例：
  read_file("src/pages/Dashboard.tsx")      # 读入 500 行 → ~8,000 tokens
  → 实际只需要看第 200-250 行的 renderChart 函数

正例：
  search_content("renderChart", path="Dashboard.tsx")  # 定位到 L200
  read_file("src/pages/Dashboard.tsx", offset=195, limit=60)  # 只读需要的 ~60 行
  → 节省：~93%
```

### 策略 3：即时摘要

```
对话中每完成一个子任务，主动总结：

"✅ 已完成：提取 renderChart() 函数 (L200→L250 提取为独立组件)
 关键变更：ChartRenderer.tsx
 测试：通过 ✓"

这个 3 行的摘要可以替代后续 500+ tokens 的上文回顾。
```

### 策略 4：多 Agent 委托

```
需要探索 "整个项目中所有使用 useAuth 的地方"：

❌ 主会话中逐个搜索：10+ 次 search_content + read_file → ~15,000 tokens
✅ 委派给 code-explorer：
   Task("code-explorer", "在 src/ 下找到所有使用 useAuth 的文件并说明上下文")
   → 子 Agent 独立运行，返回 500 tokens 结论
   节省：~97%
```

### 策略 5：缓存复用

```
会话 #1：花了 8,000 tokens 探索项目结构
→ 写入 findings.md（500 tokens）

会话 #2：直接读 findings.md → 省下 ~7,500 tokens
会话 #3：复用 findings.md → 又省下 ~7,500 tokens
...
```

### 策略 6：上下文压缩

```
当对话超过 15 轮时：

压缩前（最近 5 轮对话）：
  "我应该把这个函数放在 utils/ 还是 services/？"
  "utils/ 用于纯函数，services/ 用于有副作用的调用"
  "那 fetchUser 放在 services/ 然后 useAuth 调用它？"
  "对，这样可以保持 hooks 的纯净"
  "好的，完成了。接下来做什么？"
  → ~200 tokens

压缩后（摘要）：
  "DEC: fetchUser → services/, useAuth 调用它。进度: 60%，下一步: 错误处理"
  → ~30 tokens
  → 节省 85%
```

## Token 预算仪表盘（AI 内部分析用）

| 场景 | 预算 | 策略组合 |
|------|------|----------|
| 快速修复（改 1 行） | <2,000 | 直接定位 + 直接改 |
| 小功能（1-2 文件） | 2,000-5,000 | LazyLoad + 选择性阅读 |
| 中功能（3-5 文件） | 5,000-15,000 | + 即时摘要 |
| 大功能（6+ 文件） | 15,000-30,000 | + 多 Agent 委托 |
| 重构（跨模块） | 30,000-50,000 | + 记忆缓存 + 上下文压缩 |
