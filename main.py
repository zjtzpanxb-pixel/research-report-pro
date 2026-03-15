#!/usr/bin/env python3
"""
Research Report Pro - 标杆级研究报告生成

对话题进行全面深入研究和分析，生成标杆级报告
所有数据引用均来自可信官方来源
"""

import sys
import os
import json
import logging
import asyncio
from datetime import datetime
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('research-report-pro')

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent))

# 使用绝对导入
from src.orchestrator import ResearchReportOrchestrator


def run(topic: str, depth: str = "deep", focus_areas: list = None):
    """
    Research Report Pro 主入口
    
    Args:
        topic: 研究话题
        depth: 研究深度 (standard|deep)
        focus_areas: 关注领域列表
    
    Returns:
        dict: 研究报告生成结果
    """
    logger.info(f"🔍 Research Report Pro 启动")
    logger.info(f"📝 话题：{topic}")
    logger.info(f"📊 深度：{depth}")
    logger.info(f"🎯 关注领域：{focus_areas or '自动检测'}")
    
    # 初始化编排器
    orchestrator = ResearchReportOrchestrator(
        workspace=os.getenv('OPENCLAW_WORKSPACE', '/Users/pxb/.openclaw/workspace')
    )
    
    # 执行研究流程
    result = asyncio.run(orchestrator.research(
        topic=topic,
        depth=depth,
        focus_areas=focus_areas
    ))
    
    # 输出结果
    print_result(result)
    
    return result


def print_result(result: dict):
    """打印研究报告结果"""
    print("\n" + "="*70)
    
    if result.get('success'):
        print("✅ **研究报告生成成功！**\n")
        
        report = result.get('report', {})
        print(f"📄 **标题**: {report.get('title')}")
        print(f"📝 **摘要**: {report.get('executive_summary', '')[:200]}...\n")
        
        print(f"📊 **关键发现**:")
        for i, finding in enumerate(report.get('key_findings', [])[:5], 1):
            print(f"   {i}. {finding}")
        
        research = result.get('research_process', {})
        print(f"\n🔍 **研究过程**:")
        print(f"   搜索来源：{research.get('sources_searched', 0)} 个")
        print(f"   采用来源：{research.get('sources_used', 0)} 个")
        print(f"   高可信度：{research.get('high_credibility_sources', 0)} 个")
        
        quality = result.get('quality', {})
        print(f"\n📈 **质量评分**:")
        print(f"   完整性：{quality.get('completeness_score', 0)}/100")
        print(f"   可信度：{quality.get('credibility_score', 0)}/100")
        print(f"   深度：{quality.get('depth_score', 0)}/100")
        print(f"   综合评分：{quality.get('overall_score', 0)}/100")
        
        print(f"\n📚 **引用来源**: {len(report.get('references', []))} 个")
        
        # 显示高可信度来源
        refs = report.get('references', [])[:5]
        if refs:
            print(f"\n📖 **部分引用**:")
            for ref in refs:
                cred = "✅" if ref.get('credibility') == 'high' else "⚠️"
                print(f"   {cred} {ref.get('source')}: {ref.get('title')}")
        
        execution = result.get('execution', {})
        print(f"\n⏱️  **执行信息**:")
        print(f"   耗时：{execution.get('duration_ms', 0)/1000:.1f}秒")
        print(f"   成本：¥{execution.get('cost', 0):.2f}")
        
        # 报告路径
        storage = report.get('storage', {})
        if storage.get('path'):
            print(f"\n📁 **报告路径**: {storage.get('path')}")
        
    else:
        print("❌ **研究报告生成失败**\n")
        print(f"错误：{result.get('error', '未知错误')}")
        
        if result.get('suggestions'):
            print(f"\n💡 **建议**:")
            for suggestion in result.get('suggestions', []):
                print(f"   - {suggestion}")
    
    print("="*70 + "\n")


if __name__ == '__main__':
    # 命令行调用示例
    if len(sys.argv) < 2:
        print("用法：python main.py <研究话题> [深度] [关注领域...]")
        print("\n示例:")
        print("  python main.py '中国新能源汽车行业'")
        print("  python main.py '十四五规划数字经济影响' deep")
        print("  python main.py '人工智能发展' deep 技术 市场 政策")
        sys.exit(1)
    
    topic = sys.argv[1]
    depth = sys.argv[2] if len(sys.argv) > 2 else "deep"
    focus_areas = sys.argv[3:] if len(sys.argv) > 3 else None
    
    result = run(topic, depth, focus_areas)
    
    sys.exit(0 if result.get('success') else 1)
