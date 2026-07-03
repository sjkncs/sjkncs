# 07 — 同步管理 详细文档

> 对应技能：`.codebuddy/skills/07-sync-management/SKILL.md`

## 分布式同步架构

```
          ┌──────────────────┐
          │  GitHub: sjkncs  │  ← 官方源（Single Source of Truth）
          │  (main branch)   │
          └────────┬─────────┘
                   │
        ┌──────────┼──────────┐
        ▼          ▼          ▼
   ┌─────────┐ ┌─────────┐ ┌─────────┐
   │ 用户 A  │ │ 用户 B  │ │ 用户 C  │  ← 各自克隆
   │ 本地副本 │ │ 本地副本 │ │ 本地副本 │
   └────┬────┘ └────┬────┘ └────┬────┘
        │          │          │
        ▼          ▼          ▼
   ┌─────────┐ ┌─────────┐ ┌─────────┐
   │ 项目 1  │ │ 项目 2  │ │ 项目 3  │  ← 应用规则
   │ 项目 2  │ │ 项目 3  │ │         │
   └─────────┘ └─────────┘ └─────────┘
```

## 更新策略矩阵

| 变更类型 | 版本 | 自动？ | 示例 |
|----------|------|--------|------|
| 修复文档错别字 | 1.0.0 → 1.0.1 | ✅ 自动 | 改 README 描述 |
| 新增检查项 | 1.0.1 → 1.0.2 | ✅ 自动 | 代码优化新增异味检测 |
| 新增技能 | 1.0.0 → 1.1.0 | ⚠️ 询问 | 新增第 8 个维度 |
| 修改规则行为 | 1.1.0 → 1.2.0 | ⚠️ 询问 | 规则优先级调整 |
| 删除技能 | 1.2.0 → 2.0.0 | 🛑 手动 | 废弃某维度 |
| 重构目录结构 | 2.0.0 → 3.0.0 | 🛑 手动 | 完全重排 |

## 版本号规范（SemVer）

```
v1.2.3
│ │ │
│ │ └── PATCH: 向后兼容的 bug 修复、文档修正
│ └──── MINOR: 向后兼容的新功能、新技能
└────── MAJOR: 不兼容的 API 变更、技能删除
```

## 冲突处理流程

```
检测到冲突：
│
├── 本地修改 + 远程无变化 → 保留本地
│
├── 本地无修改 + 远程有变化 → 直接应用远程
│
├── 本地修改 + 远程有变化 + 修改不同部分 → 自动合并
│
└── 本地修改 + 远程有变化 + 修改同一部分 → 逐项选择：
    ├── a) 保留本地版本（我的自定义）
    ├── b) 使用远程版本（更新到最新）
    └── c) 手动合并（打开 diff 对比）
```

## 安装与维护命令

### 首次安装

```bash
# 方式 1：克隆到用户目录（推荐，所有项目共享）
git clone https://github.com/sjkncs/sjkncs.git ~/.codebuddy/sjkncs

# 方式 2：作为项目子模块
cd your-project
git submodule add https://github.com/sjkncs/sjkncs.git .codebuddy/sjkncs
```

### 日常维护

```bash
# Windows
.\sync\sync.ps1 status    # 查看版本
.\sync\sync.ps1 check     # 检查更新
.\sync\sync.ps1 pull      # 拉取更新

# Linux/macOS
./sync/sync.sh status
./sync/sync.sh check
./sync/sync.sh pull
```

## 贡献者指南

向 SJKNCS 贡献新规则或技能：

1. Fork 仓库
2. 在对应目录下创建/修改文件
3. 更新 `version.json`：
   - Bump 版本号
   - 添加 changelog 条目
4. 运行本地验证：
   ```bash
   # 确保所有 SKILL.md 有正确的 frontmatter
   find .codebuddy/skills -name "SKILL.md" | while read f; do
     echo "Checking $f..."
     head -1 "$f" | grep -q "^---$" || echo "  MISSING frontmatter!"
   done
   ```
5. 提交 PR
