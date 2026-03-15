#!/bin/bash
# Research Report Pro - 快速测试脚本

echo "======================================"
echo "Research Report Pro - 功能测试"
echo "======================================"
echo ""

# 检查依赖
echo "📦 检查依赖..."
python3 -c "import httpx" 2>/dev/null && echo "✅ httpx 已安装" || echo "⚠️  httpx 未安装"
python3 -c "import yaml" 2>/dev/null && echo "✅ pyyaml 已安装" || echo "⚠️  pyyaml 未安装"
echo ""

# 检查 API 配置
echo "🔑 检查 API 配置..."
if [ -n "$BING_SEARCH_API_KEY" ]; then
    echo "✅ Bing Search API 已配置"
else
    echo "⚠️  Bing Search API 未配置（使用备用模式）"
fi

if [ -n "$LLM_API_KEY" ]; then
    echo "✅ LLM API 已配置"
else
    echo "⚠️  LLM API 未配置（使用模拟分析）"
fi
echo ""

# 运行测试
echo "🧪 运行 Agent 测试..."
python3 -c "
from src.agents.searcher import SearcherAgent
from src.agents.analyst import AnalystAgent
from src.agents.visualizer import VisualizerAgent
import asyncio

async def test_all():
    config = {'search': {'max_results': 5}, 'frameworks': ['PESTEL', 'SWOT']}
    
    # 测试搜索
    searcher = SearcherAgent(config)
    results = await searcher.search(['人工智能'], depth='standard')
    print(f'✅ 搜索测试：{len(results)} 个结果')
    
    # 测试分析
    analyst = AnalystAgent(config)
    for framework in ['PESTEL', 'SWOT']:
        analysis = await analyst.analyze('人工智能', results, framework)
        print(f'✅ {framework}分析：完成')
    
    # 测试可视化
    visualizer = VisualizerAgent(config)
    viz = await visualizer.visualize({'swot': analysis.get('analysis', {})}, '人工智能')
    print(f'✅ 可视化测试：{len(viz)} 个图表')
    
    return True

success = asyncio.run(test_all())
print('\\n✅ 所有测试通过！' if success else '❌ 测试失败')
"

echo ""
echo "======================================"
echo "测试完成！"
echo "======================================"
echo ""
echo "运行完整研究："
echo "  python main.py \"中国新能源汽车行业\""
echo ""
echo "深度研究："
echo "  python main.py \"人工智能\" deep 技术 市场 政策"
echo ""
