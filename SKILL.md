# Research Report Pro - 标杆级研究报告生成

> 对话题进行全面深入研究和分析，生成标杆级报告，所有数据引用均来自可信官方来源

## 触发条件

**对话**：
- "研究一下 XXX 话题"
- "分析 XXX 行业"
- "生成 XXX 研究报告"
- "深度分析 XXX"
- "帮我研究 XXX"

**命令行**：
```bash
openclaw research-pro --topic "<研究话题>" [--depth standard|deep]
```

## 功能描述

基于多 Agent 协作和严格的研究方法论，对话题进行全面深入的研究分析：

### 核心能力
1. **多源数据采集** - 官方统计/行业报告/学术论文/权威媒体
2. **可信度验证** - 来源分级（政府/学术/媒体/其他）
3. **深度分析** - PESTEL/SWOT/波特五力等成熟框架
4. **数据可视化** - 图表/趋势/对比分析
5. **引用管理** - 完整的参考文献和数据来源标注

### 研究流程
```
1. 话题解析 → 2. 搜索策略 → 3. 数据采集 → 4. 可信度验证
                                           ↓
8. 质量审查 ← 7. 引用标注 ← 6. 报告撰写 ← 5. 深度分析
```

## 输入

```json
{
  "topic": "string (研究话题，10-200 字)",
  "context": {
    "depth": "standard|deep (可选，默认 deep)",
    "focus_areas": ["string] (可选，关注领域)",
    "output_format": "markdown|pdf (可选，默认 markdown)"
  }
}
```

## 输出

```json
{
  "report": {
    "title": "string",
    "executive_summary": "string",
    "sections": [
      {
        "title": "string",
        "content": "string",
        "citations": [{"source": "string", "url": "string", "credibility": "high|medium|low"}]
      }
    ],
    "key_findings": ["string"],
    "data_visualizations": [{"type": "chart|table", "data": "object"}],
    "references": [{"title": "string", "source": "string", "url": "string", "date": "string"}]
  },
  "research_process": {
    "sources_searched": number,
    "sources_used": number,
    "high_credibility_sources": number,
    "search_queries": ["string"]
  },
  "quality": {
    "completeness_score": 0-100,
    "credibility_score": 0-100,
    "depth_score": 0-100,
    "overall_score": 0-100
  },
  "execution": {
    "duration_ms": number,
    "model_used": "string",
    "token_used": number,
    "cost": number
  }
}
```

## 配置

```yaml
# LLM 配置
llm:
  primary: default
  fallback: fallback
  timeout: 180
  max_retries: 3

# 搜索配置
search:
  max_results: 50
  credibility_filter: true
  min_credibility: medium  # high|medium|low

# 来源可信度分级
credibility_tiers:
  tier1:  # 政府/官方统计
    - gov.cn
    - stats.gov.cn
    - 政府官网
  tier2:  # 学术/研究机构
    - edu.cn
    - 知网
    - 万方
    - 社科院
  tier3:  # 权威媒体/行业报告
    - 新华社
    - 人民日报
    - 财新
    - 彭博
    - 路透

# 分析框架
frameworks:
  - PESTEL
  - SWOT
  - 波特五力
  - 价值链分析
```

## 多 Agent 架构

```
┌─────────────────────────────────────────┐
│      Research Orchestrator (主编排)      │
└─────────────────┬───────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    ▼             ▼             ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│搜索专家  │ │分析专家  │ │写作专家  │
│Searcher │ │Analyst  │ │Writer   │
└─────────┘ └─────────┘ └─────────┘
      │           │           │
      ▼           ▼           ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│验证专家  │ │可视化   │ │审查专家  │
│Verifier │ │Visualizer│ │Reviewer │
└─────────┘ └─────────┘ └─────────┘
```

### Agent 职责

| Agent | 职责 | 输出 |
|-------|------|------|
| **Searcher** | 多源搜索、数据采集 | 原始数据集合 |
| **Verifier** | 来源可信度验证、事实核查 | 验证报告 |
| **Analyst** | 深度分析、框架应用 | 分析结论 |
| **Writer** | 报告撰写、结构化输出 | 报告草稿 |
| **Visualizer** | 数据可视化、图表生成 | 图表数据 |
| **Reviewer** | 质量审查、引用检查 | 质量评分 |

## 工作流程

```
1. 接收话题 → 解析研究范围和目标
         ↓
2. 搜索策略 → 生成搜索查询（多查询并行）
         ↓
3. 数据采集 → 多源搜索（官方/学术/媒体）
         ↓
4. 可信度验证 → 来源分级 + 事实核查
         ↓
5. 深度分析 → 应用分析框架（PESTEL/SWOT 等）
         ↓
6. 报告撰写 → 结构化撰写 + 引用标注
         ↓
7. 可视化 → 生成图表和数据表格
         ↓
8. 质量审查 → 完整性/可信度/深度评分
```

## 降级策略

| 故障 | 应对 |
|------|------|
| 搜索失败 | 切换搜索引擎 → 使用缓存数据 |
| 来源不足 | 扩大搜索范围 → 降低可信度要求 |
| LLM 超时 | 重试 3 次（指数退避）→ 降级 fallback 模型 |
| 数据冲突 | 优先官方来源 → 标注争议点 |
| 成本超支 | 建议精简版 → 用户拒绝则中止 |

## 错误码

| 错误码 | 说明 |
|--------|------|
| RRP-101 | 话题过于模糊 |
| RRP-201 | 搜索超时 |
| RRP-202 | 可信来源不足 |
| RRP-301 | 数据验证失败 |
| RRP-401 | 分析框架应用失败 |
| RRP-501 | 报告生成失败 |
| RRP-601 | 成本超支 |

## 监控指标

- **成功率**：>90%
- **P95 延迟**：<5 分钟
- **单次成本**：<¥10
- **可信来源占比**：>70%
- **引用完整率**：100%
- **用户满意度**：>4.5/5

## 示例

### 示例 1：行业研究

```
用户：研究一下中国新能源汽车行业

输出：
✅ **研究报告生成成功**

📄 **标题**: 中国新能源汽车行业深度研究报告 (2026)

📊 **关键发现**:
   - 2025 年渗透率达 42%，同比增长 18%
   - 比亚迪市场份额 35%，领跑行业
   - 出口量突破 120 万辆，成为全球第一

📈 **分析框架**: PESTEL + 波特五力

📚 **引用来源**: 15 个（官方 8 个，学术 4 个，媒体 3 个）

📁 **报告路径**: /研究报告/新能源汽车行业_20260315.md
```

### 示例 2：政策分析

```
用户：分析十四五规划对数字经济的影响

输出：
✅ 深度分析报告（含 12 个官方数据来源）
```

## 相关文件

- `SKILL.md` - Skill 定义
- `src/orchestrator.py` - 主编排器
- `src/agents/` - 多 Agent 实现
- `templates/report.md.j2` - 报告模板
- `references/` - 可信来源列表

## 版本

- v1.0 (2026-03-15) - 初始版本

## 许可证

MIT
