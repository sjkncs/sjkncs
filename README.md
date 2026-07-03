# 🧠 SJKNCS — AI 编程七维治理体系

> **S**ystematic **J**udicious **K**nowledge-based **N**avigation for **C**ode **S**tandards
>
> 一套为 AI 编程助手（Claude Code / CodeBuddy / Cursor）设计的系统化规则与技能治理框架。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](version.json)

---

## 🎯 解决什么问题？

AI 编程助手强大但存在七个核心痛点：

| 痛点 | 表现 | 对应维度 |
|------|------|----------|
| 代码质量不稳定 | AI 生成的代码能跑但难维护 | 📐 代码优化 |
| 规则混乱 | 每个人教 AI 不同的习惯，行为不一致 | 📋 规则管理 |
| 对话失忆 | /clear 后忘掉前面做的所有事情 | 🧠 记忆上下文 |
| 改坏回不去 | 重构后发现问题但无法回退 | 🔄 回退备份 |
| 目录混乱 | 文件随意放置，项目越来越乱 | 📁 文件分类 |
| Token 浪费 | 一次对话读几百个文件，消耗昂贵 | 💰 Token 节约 |
| 版本分裂 | 团队成员的规则版本不一致 | 🔄 同步管理 |

---

## 📐 七维体系

```
                    ┌──────────────┐
                    │  规则管理     │ ← 统一行为契约
                    │  Rule Mgmt   │
                    └──────┬───────┘
                           │ 驱动
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  代码优化     │  │  记忆上下文   │  │  Token节约   │
│  Code Opt    │  │  Memory      │  │  Token Save  │
└──────────────┘  └──────────────┘  └──────────────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │ 底层支撑
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  回退备份     │  │  文件分类     │  │  同步管理     │
│  Rollback    │  │  File Class  │  │  Sync Mgmt   │
└──────────────┘  └──────────────┘  └──────────────┘
```

---

## 🚀 快速开始

### 方式一：一键克隆（推荐）

```bash
# 克隆到项目
git clone https://github.com/sjkncs/sjkncs.git
cp -r sjkncs/.codebuddy/* your-project/.codebuddy/

# 或直接作为子模块
cd your-project
git submodule add https://github.com/sjkncs/sjkncs.git .codebuddy/sjkncs
```

### 方式二：按需安装

只安装你需要的维度：

```bash
# 例如只需要代码优化 + 记忆上下文
cp -r sjkncs/.codebuddy/skills/01-code-optimization your-project/.codebuddy/skills/
cp -r sjkncs/.codebuddy/skills/03-memory-context your-project/.codebuddy/skills/
```

### 方式三：CodeBuddy 市场安装

在 CodeBuddy 中搜索 `sjkncs` 一键安装。

---

## 📖 各维度详解

### 01 — 代码优化 (`01-code-optimization`)

**四阶段工作流**：理解 → 计划 → 执行 → 验证

| 特性 | 说明 |
|------|------|
| 代码异味检测 | 9 种常见异味自动识别 |
| 最小化修改 | Karpathy 原则：只改必要部分 |
| 性能优化清单 | 基准测试 → 瓶颈定位 → 优化验证 |
| 禁止事项 | 不理解的代码不重构、不过度设计 |

📖 [详细文档](docs/01-code-optimization.md)

---

### 02 — 规则管理 (`02-rule-management`)

**三层规则体系**：团队级 → 项目级 → 用户级

| 特性 | 说明 |
|------|------|
| 规则模板 | 标准化规则创建格式 |
| 优先级仲裁 | scope > priority > version |
| 冲突检测 | 自动发现冲突规则对 |
| 生命周期 | 创建 → 审查 → 发布 → 废弃 |

📖 [详细文档](docs/02-rule-management.md)

---

### 03 — 记忆上下文 (`03-memory-context`)

**四文件记忆系统**：task_plan / findings / progress / decisions

| 特性 | 说明 |
|------|------|
| 跨会话持久化 | /clear 后自动恢复上下文 |
| 断点续传 | 从上次中断处继续 |
| 自动更新 | AI 主动维护记忆文件 |
| 知识沉淀 | 关键发现永不丢失 |

📖 [详细文档](docs/03-memory-context.md)

---

### 04 — 回退备份 (`04-rollback-backup`)

**三层保护机制**：文件备份 → Git 快照 → 实验分支

| 特性 | 说明 |
|------|------|
| 自动备份 | 修改前自动备份原文件 |
| AI 安全点 | 关键操作自动 commit |
| 实验分支 | 高风险修改隔离执行 |
| 一键回滚 | 随时恢复到任意安全点 |

📖 [详细文档](docs/04-rollback-backup.md)

---

### 05 — 文件分类 (`05-file-classification`)

**四层分析模型**：文件名 → 导出类型 → 导入依赖 → AI 语义

| 特性 | 说明 |
|------|------|
| 自动分类 | 10+ 种文件类型自动识别 |
| 位置检测 | 发现放错位置的文件 |
| 目录模板 | React/Vue/NestJS 标准结构 |
| 持续监控 | 新建文件即时推荐位置 |

📖 [详细文档](docs/05-file-classification.md)

---

### 06 — Token 节约 (`06-token-saving`)

**六大节约策略**：懒加载 → 选择性阅读 → 摘要 → 多Agent → 缓存 → 压缩

| 策略 | 效果 |
|------|------|
| 信息懒加载 | 节省 60% 初始 Token |
| 选择性阅读 | 节省 40% 文件读取 Token |
| 多 Agent 委托 | 探索不占主会话预算 |
| 记忆缓存 | 跨会话复用，节省 80% 重复探索 |

📖 [详细文档](docs/06-token-saving.md)

---

### 07 — 同步管理 (`07-sync-management`)

**GitHub 分布式同步**：版本检测 → 增量更新 → 冲突合并 → 回滚保护

| 特性 | 说明 |
|------|------|
| 自动检测 | 每周检查远程更新 |
| 智能合并 | 补丁自动、小版本提示、大版本手动 |
| 冲突处理 | 本地覆盖 vs 远程更新三选一 |
| 备份保护 | 更新前自动备份 |

📖 [详细文档](docs/07-sync-management.md)

---

## 🏗️ 目录结构

```
sjkncs/
├── README.md                          # 本文件
├── version.json                       # 版本追踪
├── LICENSE                            # MIT
├── .codebuddy/
│   ├── CLAUDE.md                      # 聚合行为准则
│   └── skills/
│       ├── 01-code-optimization/      # 代码优化
│       ├── 02-rule-management/        # 规则管理
│       ├── 03-memory-context/         # 记忆上下文
│       ├── 04-rollback-backup/        # 回退备份
│       ├── 05-file-classification/    # 文件分类
│       ├── 06-token-saving/           # Token 节约
│       └── 07-sync-management/        # 同步管理
├── docs/                              # 详细文档
├── extras/                            # 附加资源
│   ├── karpathy-claude.md             # Karpathy 原始指南
│   └── templates/                     # 模板文件
├── sync/                              # 同步工具
│   ├── sync-config.yaml               # 同步配置
│   ├── sync.ps1                       # Windows 同步脚本
│   └── sync.sh                        # Linux/macOS 同步脚本
└── .github/                           # GitHub Actions
    └── workflows/
        └── version-check.yml          # 版本一致性检查
```

---

## 🔧 与现有技能的兼容性

SJKNCS 设计为**元技能层**，不替代现有的 211 个技能，而是提供治理框架：

```
┌─────────────────────────────────────┐
│         SJKNCS 七维治理层           │  ← 元规则/元技能
│   (规则管理 + 同步 + Token 预算)    │
├─────────────────────────────────────┤
│         现有技能生态                 │  ← 200+ 现有技能
│    (karpathy-guidelines,            │
│     planning-with-files,            │
│     生物信息学, 科学计算, ...)       │
└─────────────────────────────────────┘
```

---

## 📄 许可证

MIT License — 自由使用、修改、分发。

---

## 🤝 贡献

欢迎提交 PR！请确保：

1. 更新 `version.json` 版本号和 changelog
2. 所有变更向后兼容（MINOR 版本）
3. 破坏性变更需要迁移指南（MAJOR 版本）
4. 通过 `version-check.yml` 检查

---

## ⭐ Star 历史

如果这套体系对你有帮助，请给个 Star ⭐ 支持一下！
