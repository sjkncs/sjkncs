---
name: rollback-backup
description: >-
  自由回退与备份：Git 快照管理、安全实验区、变更追踪、一键回滚。
  让每一次修改都有"后悔药"，告别"改坏了回不去"的焦虑。
description_zh: >-
  三层保护机制：文件级备份（修改前自动备份原文件）→ Git 快照（关键节点自动 commit）
  → 安全实验区（高风险修改在分支上进行）。
  所有备份自动命名、自动过期、一键恢复。
version: 1.0.0
category: 自由回退和备份
skill_id: sjkncs-04
---

# 04 — 自由回退与备份（Rollback & Backup）

## 核心原则

> 没有回退计划的修改就是赌博。每次改动前，先确保可以安全回退。

## 三层保护机制

```
Layer 1: 文件级备份 ──────── 修改前自动保存原文件到 .codebuddy/backups/
Layer 2: Git 快照 ────────── 关键节点自动 commit（AI 提交标记）
Layer 3: 安全实验区 ──────── 高风险修改在独立分支进行
```

---

## Layer 1：文件级自动备份

### 规则
- **修改任何文件前**，先将原文件复制到 `.codebuddy/backups/{date}/{filename}.bak`
- 备份文件自动命名：`{original_name}.{timestamp}.bak`
- 保留最近 20 个备份，自动清理旧备份

### 备份目录结构

```
.codebuddy/backups/
├── 2026-07-03/
│   ├── AcademicSummary.tsx.1200.bak
│   ├── LoginForm.tsx.1130.bak
│   └── api.service.ts.1100.bak
├── 2026-07-02/
│   └── ...
└── manifest.json    # 备份清单：文件→备份→时间→原因
```

### manifest.json 格式

```json
{
  "backups": [
    {
      "id": "bak-001",
      "original": "src/components/AcademicSummary.tsx",
      "backup": ".codebuddy/backups/2026-07-03/AcademicSummary.tsx.1200.bak",
      "created": "2026-07-03T12:00:00",
      "reason": "修改学术总结组件的渲染逻辑",
      "restored": false
    }
  ]
}
```

---

## Layer 2：Git 自动快照

### AI 自动提交规范

AI 在执行重要操作后应自动创建标记性 commit：

```bash
# 提交格式
git add <changed_files>
git commit -m "[AI] <category>: <brief description>"

# 分类标签
[AI] feat:    新功能实现
[AI] fix:     Bug 修复
[AI] refactor: 代码重构
[AI] style:   格式化调整
[AI] backup:  修改前快照（安全点）
```

### 安全点策略

在以下时机自动创建安全点：

| 触发时机 | 操作 |
|----------|------|
| 修改 >3 个文件 | `git commit -m "[AI] backup: pre-refactor checkpoint"` |
| 删除文件 | `git commit -m "[AI] backup: before deleting X files"` |
| 跨模块修改 | `git commit -m "[AI] backup: cross-module change checkpoint"` |
| 用户说"先保存一下" | `git commit -m "[AI] backup: manual checkpoint"` |

### 回滚命令

```bash
# 回滚到上一个安全点
git log --oneline --grep="\[AI\] backup:" | head -1
git reset --hard <commit_hash>

# 回滚特定文件
git checkout <commit_hash> -- <file_path>

# 查看所有 AI 安全点
git log --oneline --grep="\[AI\]"
```

---

## Layer 3：安全实验区

### 分支策略

```bash
# AI 进行高风险修改前
git checkout -b ai-experiment/<feature-name>
# 完成后合并
git checkout main
git merge --no-ff ai-experiment/<feature-name>
# 如果失败，删除实验分支
git branch -D ai-experiment/<feature-name>
```

### 高风险操作定义

- 删除 >50 行代码
- 修改核心模块（auth, database, router）
- 重构目录结构
- 升级主要依赖版本
- 修改类型定义（影响 >5 个文件）

---

## AI 自动执行规则

```
在任何修改操作前：
1. 评估风险等级（低/中/高）
2. 低风险：仅依赖 Git 历史
3. 中风险：创建 Layer 1 文件备份
4. 高风险：创建 Layer 1 + Layer 2 安全点 + Layer 3 实验分支

修改完成后：
- 向用户报告创建的备份/安全点
- 提示回滚方法
```

## 清理策略

- **文件备份**：保留最近 20 个，自动清理旧的
- **Git 安全点**：保留最近 30 天，定期 squash
- **实验分支**：合并后立即删除
