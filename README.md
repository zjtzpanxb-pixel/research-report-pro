# Research Report Pro - 标杆级研究报告生成

> 对话题进行全面深入研究和分析，生成标杆级报告，所有数据引用均来自可信官方来源

## 🚀 快速开始

### 1. 安装依赖

```bash
cd /Users/pxb/.openclaw/workspace/skills/research-report-pro
pip install -r requirements.txt
```

### 2. 配置 API Keys（可选但推荐）

```bash
# 复制环境配置示例
cp .env.example .env

# 编辑 .env 文件，填入你的 API Keys
```

**推荐配置的 API：**

| API | 用途 | 获取地址 |
|-----|------|----------|
| **Bing Search** | 网络搜索 | [Microsoft Azure](https://www.microsoft.com/en-us/bing/apis/bing-web-search-api) |
| **Google Custom Search** | 网络搜索 | [Google Cloud](https://console.cloud.google.com/apis/credentials) |
| **OpenAI API** | 深度分析 | [OpenAI](https://platform.openai.com/api-keys) |

**不配置也能用**：系统会自动使用备用数据源（模拟模式）。

### 3. 使用

**对话触发：**
```
研究一下中国新能源汽车行业
分析十四五规划对数字经济的影响
```

**命令行：**
```bash
# 标准研究
python main.py "中国新能源汽车行业"

# 深度研究（指定关注领域）
python main.py "人工智能发展" deep 技术 市场 政策
```

---

## 📋 功能特性

### 核心能力

| 能力 | 说明 | 状态 |
|------|------|------|
| **多源数据采集** | 官方统计/行业报告/学术论文/权威媒体 | ✅ |
| **可信度验证** | 来源三级分级（政府/学术/媒体） | ✅ |
| **深度分析** | PESTEL/SWOT/波特五力/价值链分析 | ✅ |
| **LLM 智能分析** | 使用大模型进行深度分析 | ⚠️ 需 API |
| **数据可视化** | 图表/趋势/对比分析 | ✅ |
| **引用管理** | 完整的参考文献和数据来源标注 | ✅ |

### 研究流程

```
1. 话题解析 → 2. 搜索策略 → 3. 数据采集 → 4. 可信度验证
                                           ↓
8. 质量审查 ← 7. 引用标注 ← 6. 报告撰写 ← 5. 深度分析
```

---

## 🎯 使用示例

### 示例 1：行业研究

```bash
python main.py "中国新能源汽车行业"
```

**输出：**
```
✅ 研究报告生成成功！

📄 标题：中国新能源汽车行业深度研究报告

📊 关键发现:
   1. 2025 年渗透率达 42%，同比增长 18%
   2. 比亚迪市场份额 35%，领跑行业
   3. 出口量突破 120 万辆，成为全球第一

🔍 研究过程:
   搜索来源：50 个
   采用来源：15 个
   高可信度：8 个 ✅

📈 质量评分:
   完整性：95/100
   可信度：92/100
   深度：90/100
   综合评分：92/100

📚 引用来源：15 个
📁 报告路径：/研究报告/新能源汽车行业_20260315.md
```

### 示例 2：政策分析

```bash
python main.py "十四五规划对数字经济的影响" deep
```

### 示例 3：指定关注领域

```bash
python main.py "人工智能发展" deep 技术 市场 政策 投资
```

---

## 📁 输出结构

生成的报告包含以下章节：

```markdown
# [话题] 深度研究报告

## 执行摘要
- 核心发现概述

## 关键发现
- 发现 1
- 发现 2
- ...

## 行业概况
- 定义与分类
- 发展历程
- 现状分析

## 市场规模
- 总体规模
- 增长趋势
- 细分领域

## 竞争格局
- 主要参与者
- 市场份额
- 竞争态势

## 发展趋势
- 技术趋势
- 市场趋势
- 政策趋势

## 政策环境
- 相关政策
- 支持力度
- 影响分析

## PESTEL 分析
- 政治环境
- 经济环境
- 社会环境
- 技术环境
- 环境因素
- 法律环境

## SWOT 分析
- 优势
- 劣势
- 机会
- 威胁

## 风险分析
- 市场风险
- 政策风险
- 技术风险

## 结论建议
- 主要结论
- 发展建议

## 数据可视化
- 关键数据表格
- 趋势图
- 竞争格局图

## 参考文献
- [1] ✅ 官方来源：标题
- [2] ✅ 学术来源：标题
- ...
```

---

## ⚙️ 配置说明

### 可信来源分级

| 分级 | 来源类型 | 示例 | 可信度 |
|------|----------|------|--------|
| **Tier 1** | 政府/官方统计 | gov.cn, stats.gov.cn, 国务院 | ✅ 高 |
| **Tier 2** | 学术/研究机构 | edu.cn, 知网，社科院 | ✅ 高 |
| **Tier 3** | 权威媒体 | 新华社，人民日报，财新 | ⚠️ 中 |

### 分析框架

- **PESTEL** - 政治/经济/社会/技术/环境/法律
- **SWOT** - 优势/劣势/机会/威胁
- **波特五力** - 行业竞争分析
- **价值链分析** - 产业价值分布

### 环境变量

```bash
# 搜索 API（至少配置一个）
BING_SEARCH_API_KEY=xxx
GOOGLE_SEARCH_API_KEY=xxx
GOOGLE_CSE_ID=xxx

# LLM API（推荐）
LLM_API_KEY=xxx

# 其他
OPENCLAW_WORKSPACE=/Users/pxb/.openclaw/workspace
LOG_LEVEL=INFO
```

---

## 📊 质量指标

| 指标 | 目标 | 说明 |
|------|------|------|
| 成功率 | >90% | 报告生成成功率 |
| P95 延迟 | <5 分钟 | 95% 报告完成时间 |
| 单次成本 | <¥10 | 深度报告成本（使用 API 时） |
| 可信来源占比 | >70% | 高可信度来源比例 |
| 引用完整率 | 100% | 所有数据均有引用 |

---

## 🔧 故障排除

### 问题 1：搜索失败

**症状**：提示"搜索来源不足"

**解决**：
1. 检查网络连接
2. 配置 Bing/Google Search API
3. 或接受使用备用数据源（模拟模式）

### 问题 2：LLM 分析失败

**症状**：分析报告使用模拟数据

**解决**：
1. 配置 `LLM_API_KEY` 环境变量
2. 检查 API Key 是否有效
3. 检查网络连接

### 问题 3：依赖缺失

```bash
# 安装依赖
pip install -r requirements.txt

# 如果 httpx 安装失败
pip install httpx --upgrade
```

### 问题 4：报告质量低

**解决**：
1. 使用 `deep` 深度模式
2. 指定更多关注领域
3. 配置搜索 API 获取更多真实数据

---

## 📂 文件结构

```
research-report-pro/
├── SKILL.md                 # Skill 描述
├── README.md                # 使用说明
├── config.yaml              # 配置文件
├── main.py                  # 主入口
├── requirements.txt         # Python 依赖
├── .env.example             # 环境配置示例
├── src/
│   ├── orchestrator.py      # 主编排器
│   └── agents/
│       ├── searcher.py      # 搜索专家
│       ├── analyst.py       # 分析专家
│       └── visualizer.py    # 可视化专家
├── templates/               # 报告模板
└── tests/                   # 测试用例
```

---

## 🚀 高级用法

### 自定义分析框架

编辑 `config.yaml`：

```yaml
frameworks:
  - PESTEL
  - SWOT
  - 波特五力
  - 价值链分析
  - 自定义框架
```

### 批量生成报告

```bash
# 创建批量脚本
cat > batch_research.sh << 'EOF'
#!/bin/bash
topics=("新能源汽车" "人工智能" "数字经济")
for topic in "${topics[@]}"; do
  python main.py "$topic" deep
done
EOF

chmod +x batch_research.sh
./batch_research.sh
```

### 集成到工作流

```python
from src.orchestrator import ResearchReportOrchestrator

orchestrator = ResearchReportOrchestrator(workspace='/path/to/workspace')
result = await orchestrator.research(
    topic='人工智能行业',
    depth='deep',
    focus_areas=['技术', '市场', '投资']
)

# 访问报告内容
report = result['report']
print(report['title'])
print(report['executive_summary'])
```

---

## 📚 API 获取指南

### Bing Search API

1. 访问 [Microsoft Azure](https://www.microsoft.com/en-us/bing/apis/bing-web-search-api)
2. 注册/登录 Microsoft 账号
3. 创建 Bing Search API 资源
4. 获取 API Key

**免费额度**：每月 1000 次调用

### Google Custom Search API

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目
3. 启用 Custom Search API
4. 创建 API Key
5. 创建 Custom Search Engine，获取 CSE ID

**免费额度**：每天 100 次调用

### OpenAI API

1. 访问 [OpenAI Platform](https://platform.openai.com/)
2. 注册/登录账号
3. 创建 API Key
4. 充值账户

**建议**：使用 GPT-4o 或 GPT-3.5-turbo

---

## 📝 版本历史

### v1.1 (2026-03-15)
- ✅ 集成真实搜索 API（Bing/Google）
- ✅ 集成 LLM 深度分析
- ✅ 多 Agent 协作架构
- ✅ 数据可视化增强
- ✅ 完善错误处理

### v1.0 (2026-03-15)
- ✅ 初始版本
- ✅ 基础框架实现

---

## 📄 许可证

MIT License

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**仓库**: https://github.com/zjtzpanxb-pixel/research-report-pro  
**作者**: Skill Creator Pro Framework  
**最后更新**: 2026-03-15
