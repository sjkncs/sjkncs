---
name: token-saving
description: >-
  Token 节约策略：上下文预算管理、信息懒加载、选择性文件读取、多 Agent 委托。
  用最少的 Token 完成最多的任务，让每次对话都物超所值。
description_zh: >-
  六大 Token 节约策略：信息懒加载 → 选择性阅读 → 即时摘要 → 多 Agent 委托 →
  缓存复用 → 上下文压缩。内置 Token 预算计算器，实时监控消耗。
version: 1.0.0
category: Token节约
skill_id: sjkncs-06
---

# 06 — Token 节约（Token Saving）

## 核心理念

> Token 是稀缺资源。200K 上下文窗口不等于要填满 200K。精打细算，用最少的 Token 完成最多的任务。

## 六大节约策略

### 策略 1：信息懒加载（Lazy Loading）

```
❌ 错误：一开始就把所有相关文件都读取到上下文
✅ 正确：先获取概览，需要深入时再读取具体文件

操作步骤：
1. 搜索文件（search_file / list_dir）→ ~50 tokens
2. 扫描关键行（search_content with contextBefore/After=2）→ ~200 tokens
3. 只有确认需要时才 read_file → ~1000-5000 tokens
```

### 策略 2：选择性阅读（Selective Reading）

```
❌ 错误：read_file 读整个 500 行的文件
✅ 正确：read_file 加 offset/limit 只读需要的部分

read_file("src/large-file.ts", offset=100, limit=50)

使用场景：
- 只关心某个函数的实现 → 搜索函数名，读那一部分
- 只关心 import → search_content("^import")
- 只关心类型定义 → search_content("interface|type")
```

### 策略 3：即时摘要（On-the-fly Summarization）

```
每处理完一个子任务：
1. 用 1-2 句话总结做了什么
2. 将总结写入 progress.md（持久化）
3. 后续会话只需读取摘要，不需要重新分析

摘要格式：
"✅ 修改了 AcademicSummary.tsx (L45-L80)，提取 renderChart() 函数，
   消除了重复代码。测试通过。"
```

### 策略 4：多 Agent 委托（Multi-Agent Delegation）

```
使用 code-explorer 子 Agent 进行大规模代码探索：
- 子 Agent 的结果不会计入主会话 Token
- 适合：搜索整个代码库、分析目录结构、收集信息

Task("code-explorer", "在 src/ 下找到所有使用 useAuth 的文件")
→ 子 Agent 独立运行，只返回结论
```

### 策略 5：缓存复用（Cache Reuse）

```
利用 .codebuddy/memory/ 的持久化记忆：
- task_plan.md → 不用重复分析任务
- findings.md → 不用重新扫描项目结构
- decisions.md → 不用重新讨论已定的架构

每次会话前三件事：
1. 读 progress.md（我现在在哪？）
2. 读 task_plan.md（我要做什么？）
3. 读 findings.md（我已经知道什么？）
```

### 策略 6：上下文压缩（Context Compression）

```
当对话超过 10 轮时：
1. 主动压缩历史信息
2. 将已完成的内容总结为一句话
3. 将关键发现写入记忆文件

压缩模板：
"已完成：[子任务1,2,3]。当前进度：60%。下一步：[子任务4]。
 关键决策：使用 A 而非 B。已知坑点：[列表]。"
```

## Token 预算计算器

### 估算规则

| 操作 | 估算 Token |
|------|-----------|
| 列出目录 (list_dir) | ~50-200 |
| 搜索代码 (search_content) | ~100-500 |
| 读取短文件 (<100行) | ~500-1500 |
| 读取长文件 (>300行) | ~2000-8000 |
| 修改文件 (replace_in_file) | ~200-1000 |
| Task 子 Agent | ~500（仅结论） |
| 生成图片 (image_gen) | ~0（不计入对话） |

### 预算建议

| 任务复杂度 | 推荐 Token 预算 | 策略 |
|-----------|----------------|------|
| 简单（1-3 步） | <5,000 | 直接操作 |
| 中等（4-8 步） | 5,000-15,000 | 懒加载 + 摘要 |
| 复杂（8+ 步） | 15,000-40,000 | 多 Agent + 缓存 |
| 超大（跨多会话）| >40,000 | 持久化记忆 + 断点续传 |

## AI 自动执行规则

```
每次选择工具时评估 Token 成本：
1. search_content 够用 → 不用 read_file
2. 子 Agent 能完成 → 不用主会话执行
3. 已有缓存信息 → 不重新扫描
4. 临近预算上限 → 主动压缩并保存状态

会话开始时声明 Token 预算：
"本次任务预估 Token 预算：~8000。当前已用：0。"
```

## 禁止事项

- ❌ 一次读取超过 3 个长文件（>500 行）而不先做针对性搜索
- ❌ 在已有缓存的情况下重新扫描项目结构
- ❌ 不压缩直接让对话超过 20 轮
- ❌ 对简单任务使用 read_file 读取整个大文件
