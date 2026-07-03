# 05 — 文件分类 详细文档

> 对应技能：`.codebuddy/skills/05-file-classification/SKILL.md`

## 设计理念

> 好的项目目录结构是自我解释的。一个新人应该能通过目录名和文件名快速定位代码，而不需要查阅文档。

## 分类算法详解

### Level 1：文件名模式匹配

通过文件命名约定快速分类：

```
源文件名          → 匹配模式                    → 推断类型
─────────────────────────────────────────────────────────
useAuth.ts       → use[A-Z]*                    → Hook
Button.tsx       → [A-Z][a-z]*.tsx              → 组件 (PascalCase)
types.ts         → types, interfaces, schema    → 类型定义
api.ts           → api, service, client         → API 服务
constants.ts     → const, constant, config      → 常量
index.ts         → index (桶文件)               → 模块入口
*.test.ts        → *.test.*, *.spec.*          → 测试文件
```

### Level 2：导出类型分析

扫描文件的 export 语句：

```typescript
// 被分析文件的内容
export default function Button() { ... }     // → 组件（默认导出函数 + JSX）
export function useAuth() { ... }           // → Hook（命名导出 useXxx）
export interface User { ... }               // → 类型（interface/type 为主）
export const API_URL = "..."                // → 常量（const 为主）
export class AuthService { ... }            // → 服务（class + 业务逻辑）
```

### Level 3：导入依赖分析

通过文件的 imports 推断它在项目中的角色：

```typescript
// 如果文件主要导入这些...
import { useState, useEffect } from 'react'     // → 可能是 Hook
import axios from 'axios'                        // → 可能是 API 服务
import { Button, Input } from '@/components/ui'  // → 可能是页面或业务组件
import { createStore } from 'zustand'            // → 状态管理
```

### Level 4：AI 语义理解

前三级无法确定时，由 AI 读取文件内容做语义分析。

## 常见问题诊断

### WRONG_DIR — 文件放错目录

```
⚠️  src/pages/api-client.ts
    建议移至：src/services/api-client.ts
    原因：文件主要导出 fetch 封装函数，属于服务层
```

### MIXED_TYPE — 一个文件多种类型

```
⚠️  src/utils/helpers.ts (180 行)
    包含：工具函数 (60%) + React 组件 (30%) + 类型定义 (10%)
    建议：拆分为 utils/helpers.ts + components/HelperWidget.tsx + types/helper.ts
```

### TOO_DEEP — 嵌套过深

```
⚠️  src/components/ui/forms/inputs/text/custom/AdvancedInput.tsx
    嵌套 6 层，超过推荐的 4 层
    建议：src/components/inputs/AdvancedInput.tsx
```

### TOO_FLAT — 同级文件过多

```
⚠️  src/components/ 包含 32 个文件
    建议：按功能分组
    src/components/ui/     (基础组件)
    src/components/layout/ (布局组件)
    src/components/forms/  (表单组件)
```

### ORPHAN — 孤儿文件

```
⚠️  src/utils/old-parser.ts
    没有任何文件 import 它
    建议：确认是否仍需要，或标记为 deprecated
```
