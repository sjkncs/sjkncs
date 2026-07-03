# 04 — 回退备份 详细文档

> 对应技能：`.codebuddy/skills/04-rollback-backup/SKILL.md`

## 为什么需要专门的回退机制？

Git 提供了基础的版本控制，但 AI 辅助编程有其特殊性：

1. **AI 修改速度快** — 几分钟可以改 10 个文件，靠 `git reflog` 恢复太慢
2. **AI 不理解业务上下文** — 可能删除看似无用但实际重要的代码
3. **多步修改链** — "先改 A，再改 B，最后发现问题出在 A" 的连锁反应
4. **实验性修改** — "试一下这个方案" 的成本应该很低

## 三层保护的协同工作

```
修改请求
    │
    ▼
风险评估 ──→ 低风险（改注释、格式）→ 仅依赖 Git 历史
    │
    ├──→ 中风险（修改逻辑、重构小函数）→ Layer 1 文件备份
    │
    └──→ 高风险（改架构、删文件）→ Layer 1 + Layer 2 + Layer 3
```

## Layer 1 文件备份实战

### AI 自动备份流程

```
修改 src/components/AcademicSummary.tsx 前：

1. 检查 .codebuddy/backups/ 目录
2. 创建：.codebuddy/backups/2026-07-03/AcademicSummary.tsx.1200.bak
3. 更新 manifest.json
4. 执行修改
5. 修改完成后通知用户：
   "已备份原文件到 .codebuddy/backups/2026-07-03/，如需回滚请告知"
```

### 手动回滚

```
用户：恢复 AcademicSummary.tsx 到修改前

AI：
1. 读取 manifest.json，找到最新备份
2. 将备份复制回原路径
3. 验证文件恢复
4. 标记 manifest 中 restored: true
```

## Layer 2 Git 安全点实战

### AI 自动提交时机

```bash
# 例：修改 3 个组件文件后
git add src/components/Header.tsx src/components/Sidebar.tsx src/components/Footer.tsx
git commit -m "[AI] backup: before refactoring layout components"

# 例：删除 2 个文件前
git add -u
git commit -m "[AI] backup: before removing deprecated API routes"
```

### Git 安全点时间线

```
main:  ●──●──●──[AI] backup: init──[AI] feat: login──[AI] backup: pre-refactor──[AI] refactor: components
                    ▲                                              ▲
                    │ 安全点 1                                      │ 安全点 2
                    └── 可回滚到此处                                └── 可回滚到此处
```

## Layer 3 实验分支实战

```bash
# AI 执行高风险重构前
git checkout -b ai-experiment/refactor-auth
# ... 在分支上自由修改 ...
# 成功后合并
git checkout main
git merge --no-ff ai-experiment/refactor-auth
git branch -d ai-experiment/refactor-auth
# 如果失败
git checkout main
git branch -D ai-experiment/refactor-auth  # 丢弃实验
```

## 备份清理策略

```
自动清理规则（AI 定期执行）：
├── 文件备份：保留最近 20 个，删除更早的
├── Git 安全点：保留 30 天内的
├── 实验分支：合并后立即删除
└── manifest.json 中标记 restored: true 的备份优先清理
```
