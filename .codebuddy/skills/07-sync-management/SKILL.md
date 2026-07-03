---
name: sync-management
description: >-
  更新同步与优化管理：技能/Rules 的版本追踪、远程同步、冲突合并、自动更新。
  让所有人始终使用最新的规则体系，告别"你的规则和我的不一样"。
description_zh: >-
  基于 GitHub 的分布式技能同步系统：版本检测 → 增量更新 → 冲突合并 → 回滚保护。
  支持手动/自动两种更新模式，内置兼容性检查。
version: 1.0.0
category: 更新同步和优化管理
skill_id: sjkncs-07
---

# 07 — 更新同步与优化管理（Sync & Management）

## 核心理念

> 规则和技能会持续演进。需要一个机制确保团队所有成员始终使用最新版本，同时保护本地自定义不丢失。

## 同步架构

```
┌──────────────────────┐
│   GitHub: sjkncs     │  ← 官方仓库（规则源）
│   (upstream)         │
└────────┬─────────────┘
         │ git pull / sync
         ▼
┌──────────────────────┐
│   本地 .codebuddy/   │  ← 本地副本
│   (local)            │
└────────┬─────────────┘
         │ apply / merge
         ▼
┌──────────────────────┐
│   用户项目           │  ← 实际使用
│   (project)          │
└──────────────────────┘
```

## 版本追踪系统

### version.json（仓库根目录）

```json
{
  "repo": "sjkncs",
  "version": "2.0.0",
  "release_date": "2026-07-03",
  "skills": {
    "01-code-optimization": { "version": "1.0.0", "updated": "2026-07-03" },
    "02-rule-management": { "version": "1.0.0", "updated": "2026-07-03" },
    "03-memory-context": { "version": "1.0.0", "updated": "2026-07-03" },
    "04-rollback-backup": { "version": "1.0.0", "updated": "2026-07-03" },
    "05-file-classification": { "version": "1.0.0", "updated": "2026-07-03" },
    "06-token-saving": { "version": "1.0.0", "updated": "2026-07-03" },
    "07-sync-management": { "version": "1.0.0", "updated": "2026-07-03" }
  },
  "changelog": [
    { "version": "1.0.0", "date": "2026-07-03", "changes": ["初始发布", "七维技能体系"] }
  ],
  "compatibility": {
    "min_codebuddy_version": "1.0.0",
    "max_codebuddy_version": "*"
  }
}
```

## 同步工作流

### 初始化（首次安装）

```bash
# 克隆到用户技能目录
git clone https://github.com/sjkncs/sjkncs.git ~/.codebuddy/sjkncs

# 或仅复制 .codebuddy/ 到项目
cp -r sjkncs/.codebuddy/* your-project/.codebuddy/
```

### 检查更新

```bash
# AI 自动检测（每周一次）
1. 对比本地 version.json 与远程 version.json
2. 如果远程版本更新 → 提示用户
3. 显示 changelog 中新增/变更内容
```

### 应用更新

```
更新策略：
├── 自动合并（安全）：
│   ├── 新增技能（本地不存在）
│   ├── 补丁版本更新（1.0.0 → 1.0.1）
│   └── 文档/示例更新
│
├── 提示合并（需确认）：
│   ├── 次要版本更新（1.0.0 → 1.1.0）
│   ├── 规则优先级变更
│   └── 新增依赖项
│
└── 手动合并（强制）：
    ├── 主版本更新（1.0.0 → 2.0.0）
    ├── 破坏性变更
    └── 删除/重命名技能
```

### 冲突处理

```
本地修改 vs 远程更新冲突时：
1. 备份本地文件（Layer 1 文件级备份）
2. 应用远程更新
3. 对比本地修改和远程更新
4. 逐项展示冲突，让用户选择：
   a) 保留本地版本
   b) 使用远程版本
   c) 手动合并（打开 diff）
```

## 本地覆盖机制

用户可以在项目级覆盖技能的行为：

```
.codebuddy/
├── sjkncs/                    # 官方版本（不要直接修改）
│   └── skills/...
├── overrides/                 # 本地覆盖（优先级更高）
│   ├── 01-code-optimization.override.md  # 覆盖同名技能
│   └── custom-rules.md                   # 额外规则
└── CLAUDE.md                  # 聚合文件（自动从官方+覆盖生成）
```

### 覆盖文件格式

```markdown
---
overrides: 01-code-optimization
priority: higher
reason: "项目使用 Vue 而非 React，需要调整组件分类规则"
---

## 本地调整
- React 相关规则替换为 Vue 等效规则
- 新增项目特定优化检查项
```

## 自动更新配置

### sync-config.yaml

```yaml
# 同步配置
sync:
  # 更新频率
  check_interval: weekly          # daily | weekly | monthly | manual

  # 更新策略
  auto_apply:
    patch: true                   # 补丁版本自动应用
    minor: ask                    # 次要版本询问
    major: ask                    # 主版本询问

  # 通知
  notify_on_update: true
  notify_channels:
    - claude_session              # 在 AI 会话中提示

  # 忽略
  ignore_skills: []               # 不同步的技能列表

  # 备份
  backup_before_update: true
  backup_retention: 30            # 保留天数
```

## 发布流程

```
贡献者端：
1. 修改 skill 文件
2. 更新 version.json（bump 版本号 + 添加 changelog）
3. git commit + push

用户端：
4. AI 检测到更新 → 通知用户
5. 用户确认 → 拉取 + 合并
6. 自动备份 → 应用更新 → 验证
```

## 最佳实践

| 实践 | 说明 |
|------|------|
| **语义化版本** | 严格遵循 semver：MAJOR.MINOR.PATCH |
| **变更日志** | 每次更新必须写 changelog |
| **向后兼容** | MINOR 版本必须向后兼容 |
| **迁移指南** | MAJOR 版本必须提供迁移指南 |
| **测试更新** | 发布前在沙盒环境测试更新流程 |
