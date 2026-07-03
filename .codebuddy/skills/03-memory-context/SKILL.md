---
name: memory-context
description: >-
  记忆与上下文管理：跨会话记忆持久化、上下文窗口优化、关键信息提取与传递。
  解决 AI "失忆"问题 — /clear 之后仍然知道之前做了什么。
description_zh: >-
  基于 planning-with-files 模式增强的记忆系统。通过 task_plan.md /
  findings.md / progress.md / decisions.md 四文件实现持久化记忆，
  支持断点续传、上下文恢复、知识沉淀。
version: 1.0.0
category: 记忆上下文
skill_id: sjkncs-03
---

# 03 — 记忆上下文（Memory Context）

## 核心问题

AI 编程助手的最大痛点：**每次对话都是一张白纸**。

- `/clear` 后丢失所有上下文
- 长对话中 token 超出窗口导致信息截断
- 多个并发会话之间无法共享信息
- 关键决策被遗忘

## 解决方案：四文件记忆系统

在项目根目录创建 `.codebuddy/memory/` 目录：

```
.codebuddy/memory/
├── task_plan.md      # 任务规划（做什么、怎么做、分几步）
├── findings.md       # 发现与知识（代码结构、依赖关系、坑点）
├── progress.md       # 进度追踪（已完成、进行中、阻塞项）
└── decisions.md      # 决策记录（为什么这样设计、替代方案）
```

### task_plan.md — 任务规划

```markdown
# 任务规划

## 当前任务
- [ ] 实现用户登录功能
  - [ ] 前端登录表单
  - [ ] API 接口对接
  - [ ] Token 存储
  - [ ] 登录状态管理

## 执行顺序
1. 先建 API 接口（后端先行）
2. 再写类型定义
3. 实现前端组件
4. 集成测试

## 预估复杂度
| 子任务 | 预估文件数 | 预估行数 | 风险 |
|--------|-----------|---------|------|
| API 接口 | 2 | ~80 | 低 |
| 类型定义 | 1 | ~30 | 低 |
| 前端组件 | 3 | ~200 | 中 |
```

### findings.md — 发现与知识

```markdown
# 发现与知识

## 项目架构
- 前端：React + TypeScript + Vite
- 后端：NestJS + PostgreSQL
- 包管理器：pnpm (workspace)

## 关键文件
| 文件 | 作用 | 关键导出 |
|------|------|----------|
| `apps/web/src/App.tsx` | 根组件 | Router 配置 |
| `packages/shared/src/types.ts` | 共享类型 | User, ApiResponse |
| `apps/api/src/auth/auth.service.ts` | 认证服务 | login(), refreshToken() |

## 已知坑点
- `useAuth` 不能在 Router 外层使用
- PostgreSQL 连接需要手动配置 SSL
- pnpm workspace 的 hoisting 需要特殊配置
```

### progress.md — 进度追踪

```markdown
# 进度追踪

## 最近更新：2026-07-03 12:00

| 时间 | 会话 | 完成内容 | 状态 |
|------|------|----------|------|
| 12:00 | #3 | 实现登录表单 UI | ✅ |
| 11:30 | #2 | 创建 API 登录接口 | ✅ |
| 11:00 | #1 | 初始化项目结构 | ✅ |

## 当前状态
- **进行中**：Token 存储机制
- **阻塞项**：无
- **下一步**：集成测试
```

### decisions.md — 决策记录

```markdown
# 决策记录

## DEC-001：选择 Zustand 而非 Redux
- **日期**：2026-07-01
- **决策者**：开发团队
- **原因**：项目规模中等，不需要 Redux 的复杂度
- **替代方案**：Redux Toolkit, Jotai, Context API
- **影响**：状态管理代码减少约 40%
```

## 工作流触发条件

| 触发条件 | 操作 |
|----------|------|
| **新会话开始** | 读取 `progress.md` 和 `task_plan.md`，恢复上下文 |
| **完成任务** | 更新 `progress.md`，标记完成时间 |
| **发现新信息** | 追加到 `findings.md` |
| **做出决策** | 记录到 `decisions.md` |
| **任务阻塞** | 在 `progress.md` 记录阻塞原因 |
| **会话过长** | 主动将关键信息写入记忆文件，避免丢失 |

## 自动执行规则

AI 在以下时刻应**主动**更新记忆：

1. **每完成一个子任务** → 更新 `progress.md`
2. **发现项目中的重要文件/依赖** → 追加到 `findings.md`
3. **做出非显而易见的架构决策** → 记录 `decisions.md`
4. **计划有变** → 更新 `task_plan.md`
5. **会话即将结束** → 刷新所有记忆文件确保最新

## 主动声明

在每个编码会话开始时，AI 应该声明：
> 已从 `.codebuddy/memory/` 恢复上次会话状态：上次完成了 X，当前进度 Y，下一步 Z。
