---
name: file-classification
description: >-
  主动分类代码文件：自动识别文件类型、建议目录归属、检测放置错误。
  让项目目录始终整洁有序，新人也能快速定位代码。
description_zh: >-
  智能文件分类引擎：根据文件内容（imports、exports、命名规则）自动推断
  文件所属模块，检测放错位置的文件，建议标准化目录结构。
version: 1.0.0
category: 主动分类代码文件
skill_id: sjkncs-05
---

# 05 — 主动分类代码文件（File Classification）

## 核心理念

> 代码文件的位置就是文档。好的目录结构自解释，无需额外文档。

## 分类标准：四层分析模型

```
Level 1: 文件名模式匹配 ─── 根据命名约定推断（Component.tsx → components/）
Level 2: 导出类型分析 ─── 根据 export 内容推断（export function → utils/）
Level 3: 导入依赖分析 ─── 根据 imports 推断层级关系
Level 4: AI 语义理解 ─── 读取文件内容，理解业务含义
```

## 标准目录结构模板

### 前端项目（React/Vue）

```
src/
├── components/        # 可复用 UI 组件
│   ├── ui/           # 基础 UI 组件（Button, Input, Modal）
│   ├── layout/       # 布局组件（Header, Sidebar, Footer）
│   └── [feature]/    # 业务组件（UserCard, ProductList）
├── pages/            # 页面级组件（路由入口）
├── hooks/            # 自定义 Hooks
├── services/         # API 调用、外部服务
├── stores/           # 状态管理
├── utils/            # 工具函数（纯函数）
├── types/            # TypeScript 类型定义
├── constants/        # 常量、配置
├── styles/           # 全局样式
└── assets/           # 静态资源（图片、字体）
```

### 后端项目（NestJS/Express）

```
src/
├── modules/          # 业务模块
│   └── [module]/
│       ├── [module].controller.ts
│       ├── [module].service.ts
│       ├── [module].module.ts
│       ├── dto/
│       └── entities/
├── common/           # 公共模块
│   ├── guards/
│   ├── interceptors/
│   ├── filters/
│   └── decorators/
├── config/           # 配置文件
├── database/         # 数据库迁移、种子
└── utils/            # 工具函数
```

## 分类规则引擎

### 自动分类规则表

| 检测模式 | 推断类型 | 建议目录 |
|----------|----------|----------|
| `export default function Xxx()` 且包含 JSX | React 组件 | `components/` |
| `export function useXxx` | React Hook | `hooks/` |
| `export const XxxAtom` / `createSlice` | 状态 | `stores/` |
| `import axios` / `fetch(` | API 服务 | `services/` |
| `interface Xxx` / `type Xxx` 为主 | 类型定义 | `types/` |
| 仅纯函数导出，无副作用 | 工具函数 | `utils/` |
| `@Controller()` / `@Get()` | 控制器 | `modules/[name]/` |
| `@Injectable()` + 数据库操作 | 服务 | `modules/[name]/` |
| 大量 `export const` 常量 | 常量 | `constants/` |
| `.css` / `.scss` 导入为主 | 样式 | `styles/` |

### 位置检测警告

对已有项目运行分类检查，检测以下问题：

```
⚠️ 警告类型：
├── WRONG_DIR:  文件放错了目录
├── MIXED_TYPE: 一个文件包含多种类型的导出
├── TOO_DEEP:   嵌套过深（>4 层）
├── TOO_FLAT:   同目录文件过多（>15 个）
├── ORPHAN:     文件没有被任何地方导入
└── CYCLE:      检测到循环依赖
```

## 工作流程

### 新项目初始化

```
1. 分析项目类型（前端/后端/全栈）
2. 推荐目录结构模板
3. 创建目录骨架
4. 生成 .gitkeep 和初始 README
```

### 已有项目分析

```
1. 扫描所有源文件
2. 对每个文件运行四层分析
3. 生成分类报告
   - ✅ 位置正确的文件
   - ⚠️ 建议移动的文件
   - ❌ 需要重构的文件（混合类型）
4. 用户确认后执行移动/重构
```

### 持续监控

```
1. 新建文件时自动提示建议位置
2. 定期检查（或变更时触发）位置一致性
3. 更新分类报告
```

## 禁止事项

- ❌ 不经用户确认就移动文件
- ❌ 对第三方库代码进行分类
- ❌ 忽略项目已有的特殊约定
- ❌ 破坏 import 路径（移动必须同步更新引用）
