#!/usr/bin/env python3
"""
Research Report Pro - OpenClaw Skill 入口

对话题进行全面深入研究和分析，生成标杆级报告
所有数据引用均来自可信官方来源
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.orchestrator import ResearchReportOrchestrator


def extract_intent(message: str) -> dict:
    """从用户消息中提取意图和参数"""
    message = message.strip()
    
    # 默认参数
    params = {
        'depth': 'deep',
        'focus_areas': None,
    }
    
    # 检测深度参数
    if '简单' in message or '快速' in message:
        params['depth'] = 'standard'
    
    # 提取关注领域（"关注 XXX" 或 "重点 XXX"）
    focus_keywords = ['关注', '重点', '侧重', '主要看']
    for keyword in focus_keywords:
        if keyword in message:
            parts = message.split(keyword)
            if len(parts) > 1:
                # 提取后面的内容作为关注领域
                focus_text = parts[1].split()[0] if parts[1].split() else ''
                if focus_text:
                    params['focus_areas'] = [focus_text]
    
    return {
        'topic': message,
        'params': params,
    }


async def generate_report(message: str) -> str:
    """
    生成研究报告
    
    Args:
        message: 用户消息
    
    Returns:
        格式化的输出文本
    """
    # 提取意图
    extracted = extract_intent(message)
    topic = extracted['topic']
    params = extracted['params']
    
    # 初始化编排器
    orchestrator = ResearchReportOrchestrator(
        workspace=os.getenv('OPENCLAW_WORKSPACE', '/Users/pxb/.openclaw/workspace')
    )
    
    try:
        # 调用研究流程
        result = await orchestrator.research(
            topic=topic,
            depth=params['depth'],
            focus_areas=params['focus_areas']
        )
        
        # 格式化输出
        output = []
        
        if result.get('success'):
            report = result.get('report', {})
            research = result.get('research_process', {})
            quality = result.get('quality', {})
            execution = result.get('execution', {})
            
            output.append("✅ **研究报告生成成功！**\n")
            output.append(f"📄 **标题**: {report.get('title', '')}\n")
            
            # 摘要（截取前 200 字）
            summary = report.get('executive_summary', '')
            if summary:
                summary_text = summary[:200] + '...' if len(summary) > 200 else summary
                output.append(f"📝 **摘要**: {summary_text}\n")
            
            # 关键发现
            findings = report.get('key_findings', [])
            if findings:
                output.append("📊 **关键发现**:")
                for i, finding in enumerate(findings[:5], 1):
                    output.append(f"   {i}. {finding}")
                output.append("")
            
            # 研究过程
            output.append("🔍 **研究过程**:")
            output.append(f"   搜索来源：{research.get('sources_searched', 0)} 个")
            output.append(f"   采用来源：{research.get('sources_used', 0)} 个")
            high_cred = research.get('high_credibility_sources', 0)
            output.append(f"   高可信度：{high_cred} 个 {'✅' if high_cred > 0 else '⚠️'}")
            output.append("")
            
            # 质量评分
            output.append("📈 **质量评分**:")
            output.append(f"   完整性：{quality.get('completeness_score', 0)}/100")
            output.append(f"   可信度：{quality.get('credibility_score', 0)}/100")
            output.append(f"   深度：{quality.get('depth_score', 0)}/100")
            output.append(f"   综合评分：{quality.get('overall_score', 0)}/100")
            output.append("")
            
            # 引用来源
            refs = report.get('references', [])
            output.append(f"📚 **引用来源**: {len(refs)} 个")
            
            # 显示部分高可信度引用
            high_cred_refs = [r for r in refs if r.get('credibility') == 'high'][:3]
            if high_cred_refs:
                output.append("\n📖 **部分引用**:")
                for ref in high_cred_refs:
                    cred = "✅" if ref.get('credibility') == 'high' else "⚠️"
                    output.append(f"   {cred} {ref.get('source')}: {ref.get('title', '无标题')[:50]}")
            
            # 执行信息
            output.append(f"\n⏱️  **执行信息**:")
            output.append(f"   耗时：{execution.get('duration_ms', 0)/1000:.1f}秒")
            output.append(f"   成本：¥{execution.get('cost', 0):.2f}")
            
            # 报告路径
            storage = report.get('storage', {})
            if storage.get('path'):
                output.append(f"\n📁 **报告路径**: {storage.get('path')}")
            
            # 分析框架
            frameworks = quality.get('frameworks_used', [])
            if frameworks:
                output.append(f"\n🔬 **分析框架**: {', '.join(frameworks)}")
        
        else:
            output.append("❌ **研究报告生成失败**\n")
            output.append(f"错误：{result.get('error', '未知错误')}")
            
            if result.get('suggestions'):
                output.append("\n💡 **建议**:")
                for suggestion in result.get('suggestions', []):
                    output.append(f"   - {suggestion}")
        
        return '\n'.join(output)
        
    except Exception as e:
        return f"❌ **生成失败**: {str(e)}\n\n请检查配置或联系管理员。"


def run(message: str) -> str:
    """
    OpenClaw 同步调用入口
    
    Args:
        message: 用户消息
    
    Returns:
        响应文本
    """
    return asyncio.run(generate_report(message))


# OpenClaw 技能元数据
SKILL_METADATA = {
    'name': 'research-report-pro',
    'description': '对话题进行全面深入研究和分析，生成标杆级报告',
    'version': '1.1.0',
    'author': 'Skill Creator Pro Framework',
    'triggers': [
        '研究一下',
        '分析',
        '研究报告',
        '深度分析',
        '帮我研究',
        '行业研究',
        '政策分析',
        '市场调研',
        '生成报告',
    ],
}


# 测试入口
if __name__ == '__main__':
    # 测试用例
    test_message = "研究一下中国新能源汽车行业"
    print(f"测试消息：{test_message}")
    print("")
    result = run(test_message)
    print(result)
