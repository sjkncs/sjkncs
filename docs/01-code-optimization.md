# 01 — 代码优化 详细文档

> 对应技能：`.codebuddy/skills/01-code-optimization/SKILL.md`

## 设计理念

代码优化不是越改越多，而是越改越少。核心哲学来自 Andrej Karpathy 的观察：

> LLM 倾向于过度设计、过度抽象、过度修改。真正好的代码是最少的代码。

## 优化决策树

```
发现代码问题
    │
    ├── 是否理解全部上下文？ ──→ 否 ──→ 先阅读，不修改
    │
    ├── 修改影响范围 > 3 个文件？ ──→ 是 ──→ 分为多次修改
    │
    ├── 是否需要改变接口？ ──→ 是 ──→ 先确认所有调用方
    │
    └── 开始修改 ──→ 一次只改一个问题
```

## 异味检测优先级

按严重程度排序（从最需要立即处理到可以延后）：

1. 🔴 **安全漏洞** — SQL 注入、XSS、敏感信息泄露
2. 🔴 **逻辑错误** — 错误的算法、数据不一致
3. 🟡 **性能瓶颈** — N+1 查询、不必要的重渲染
4. 🟡 **可维护性** — 长函数、重复代码、深层嵌套
5. 🟢 **风格问题** — 命名不规范、注释不足

## 实战案例

### 案例 1：长函数拆分

```typescript
// ❌ 优化前：120 行的组件函数
function AcademicSummary() {
  // ... 20 行数据获取
  // ... 30 行数据处理
  // ... 40 行图表渲染
  // ... 30 行交互逻辑
}

// ✅ 优化后：提取为多个小函数
function AcademicSummary() {
  const { data, loading } = useAcademicData();
  const processed = useMemo(() => processData(data), [data]);
  return <SummaryChart data={processed} onFilter={handleFilter} />;
}
```

### 案例 2：消除重复代码

```typescript
// ❌ 重复的 API 调用模式
async function getUser(id: string) {
  const res = await fetch(`/api/users/${id}`, {
    headers: { 'Content-Type': 'application/json' }
  });
  if (!res.ok) throw new Error('Failed');
  return res.json();
}

async function getProduct(id: string) {
  const res = await fetch(`/api/products/${id}`, {
    headers: { 'Content-Type': 'application/json' }
  });
  if (!res.ok) throw new Error('Failed');
  return res.json();
}

// ✅ 提取公共 API 客户端
const api = {
  get: async <T>(path: string): Promise<T> => {
    const res = await fetch(`/api${path}`, {
      headers: { 'Content-Type': 'application/json' }
    });
    if (!res.ok) throw new Error(`API Error: ${res.status}`);
    return res.json();
  }
};

// 使用
const user = await api.get<User>(`/users/${id}`);
const product = await api.get<Product>(`/products/${id}`);
```

## 优化检查清单

每次优化完成后，逐项确认：

- [ ] 所有现有测试仍然通过
- [ ] 没有引入新的 lint 警告
- [ ] 修改的代码比原来更短（或至少不长于原来的 120%）
- [ ] 新代码可以被团队成员一眼看懂
- [ ] 没有添加新的依赖
- [ ] 接口保持向后兼容
