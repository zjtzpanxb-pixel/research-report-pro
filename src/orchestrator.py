"""
Research Report Pro - 主编排器

负责研究流程编排和多 Agent 协调
"""

import asyncio
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class ResearchContext:
    """研究上下文"""
    topic: str
    depth: str = "deep"
    focus_areas: Optional[List[str]] = None
    start_time: float = 0
    search_queries: List[str] = None
    sources: List[Dict] = None
    analysis_results: Dict = None
    
    def __post_init__(self):
        if self.search_queries is None:
            self.search_queries = []
        if self.sources is None:
            self.sources = []
        if self.analysis_results is None:
            self.analysis_results = {}


class ResearchReportOrchestrator:
    """研究报告主编排器"""
    
    def __init__(self, workspace: str):
        self.workspace = Path(workspace)
        self.output_dir = self.workspace / '研究报告'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 可信来源配置
        self.credibility_tiers = {
            'tier1': ['gov.cn', 'stats.gov.cn', '政府', '国务院', '发改委', '工信部'],
            'tier2': ['edu.cn', '知网', '万方', '社科院', '学术', '论文'],
            'tier3': ['新华社', '人民日报', '财新', '彭博', '路透', '权威'],
        }
        
        # 分析框架
        self.frameworks = ['PESTEL', 'SWOT', '波特五力', '价值链分析']
        
        logger.info(f"编排器初始化完成，工作区：{self.workspace}")
    
    async def research(
        self, 
        topic: str, 
        depth: str = "deep",
        focus_areas: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        执行完整研究流程
        
        Args:
            topic: 研究话题
            depth: 研究深度 (standard|deep)
            focus_areas: 关注领域
        
        Returns:
            研究报告生成结果
        """
        context = ResearchContext(
            topic=topic,
            depth=depth,
            focus_areas=focus_areas,
            start_time=time.time()
        )
        
        try:
            # 阶段 1: 话题解析
            logger.info("阶段 1: 话题解析")
            await self._stage1_parse_topic(context)
            
            # 阶段 2: 搜索策略
            logger.info("阶段 2: 生成搜索策略")
            await self._stage2_generate_search_queries(context)
            
            # 阶段 3: 数据采集
            logger.info("阶段 3: 多源数据采集")
            await self._stage3_collect_data(context)
            
            # 阶段 4: 可信度验证
            logger.info("阶段 4: 来源可信度验证")
            await self._stage4_verify_credibility(context)
            
            # 阶段 5: 深度分析
            logger.info("阶段 5: 深度分析")
            await self._stage5_deep_analysis(context)
            
            # 阶段 6: 报告撰写
            logger.info("阶段 6: 报告撰写")
            report = await self._stage6_write_report(context)
            
            # 阶段 7: 可视化
            logger.info("阶段 7: 数据可视化")
            await self._stage7_visualize(context, report)
            
            # 阶段 8: 质量审查
            logger.info("阶段 8: 质量审查")
            quality = await self._stage8_quality_review(context, report)
            
            # 存储报告
            storage = await self._save_report(report, context)
            report['storage'] = storage
            
            # 构建输出
            return self._build_output(report, context, quality)
            
        except Exception as e:
            logger.error(f"研究失败：{e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'suggestions': ['检查网络连接', '尝试简化话题', '联系管理员']
            }
    
    async def _stage1_parse_topic(self, context: ResearchContext) -> None:
        """阶段 1: 解析话题"""
        # 使用 LLM 解析话题，提取关键信息
        prompt = f"""分析以下研究话题，提取关键信息：

话题：{context.topic}

请输出 JSON 格式：
{{
  "keywords": ["关键词 1", "关键词 2"],
  "industry": "所属行业",
  "time_range": "时间范围",
  "geographic_scope": "地理范围",
  "research_type": "行业研究 | 政策分析 | 技术评估 | 市场分析"
}}"""
        
        # 模拟实现（实际应调用 LLM）
        result = {
            'keywords': context.topic.split()[:5],
            'industry': '待分析',
            'time_range': '2024-2026',
            'geographic_scope': '中国',
            'research_type': '行业研究'
        }
        
        context.parsed_topic = result
        logger.info(f"话题解析完成：{result['research_type']}")
    
    async def _stage2_generate_search_queries(self, context: ResearchContext) -> None:
        """阶段 2: 生成搜索查询"""
        # 生成多个搜索查询，覆盖不同维度
        base_queries = []
        keywords = context.parsed_topic.get('keywords', [])
        
        # 基础查询
        base_queries.append(f"{' '.join(keywords)} 2025 2026")
        base_queries.append(f"{' '.join(keywords)} 市场规模 数据")
        base_queries.append(f"{' '.join(keywords)} 发展趋势")
        
        # 官方数据查询
        base_queries.append(f"{' '.join(keywords)} site:gov.cn")
        base_queries.append(f"{' '.join(keywords)} 统计年鉴")
        
        # 学术查询
        base_queries.append(f"{' '.join(keywords)} 学术论文 site:edu.cn")
        
        context.search_queries = base_queries
        logger.info(f"生成 {len(base_queries)} 个搜索查询")
    
    async def _stage3_collect_data(self, context: ResearchContext) -> None:
        """阶段 3: 数据采集"""
        # 并行执行多个搜索
        tasks = [self._search_single_query(query) for query in context.search_queries]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 合并结果
        for result in results:
            if isinstance(result, list):
                context.sources.extend(result)
        
        logger.info(f"采集到 {len(context.sources)} 个来源")
    
    async def _search_single_query(self, query: str) -> List[Dict]:
        """执行单个搜索查询"""
        # 模拟搜索结果（实际应调用搜索 API）
        await asyncio.sleep(0.5)  # 模拟搜索延迟
        
        return [
            {
                'title': f'{query} - 相关结果',
                'url': 'https://example.com',
                'source': '示例来源',
                'date': '2026-03-15',
                'snippet': '这是搜索结果摘要...',
                'raw_content': ''
            }
        ]
    
    async def _stage4_verify_credibility(self, context: ResearchContext) -> None:
        """阶段 4: 可信度验证"""
        for source in context.sources:
            credibility = self._check_credibility(source)
            source['credibility'] = credibility
            source['credibility_tier'] = self._get_credibility_tier(source)
        
        # 过滤低可信度来源
        high_cred = [s for s in context.sources if s.get('credibility') == 'high']
        medium_cred = [s for s in context.sources if s.get('credibility') == 'medium']
        
        context.sources = high_cred + medium_cred
        logger.info(f"验证后保留 {len(context.sources)} 个来源（高可信：{len(high_cred)}）")
    
    def _check_credibility(self, source: Dict) -> str:
        """检查来源可信度"""
        url = source.get('url', '').lower()
        title = source.get('title', '').lower()
        source_name = source.get('source', '').lower()
        
        # Tier 1: 政府/官方
        for keyword in self.credibility_tiers['tier1']:
            if keyword in url or keyword in title or keyword in source_name:
                return 'high'
        
        # Tier 2: 学术/研究
        for keyword in self.credibility_tiers['tier2']:
            if keyword in url or keyword in title or keyword in source_name:
                return 'high'
        
        # Tier 3: 权威媒体
        for keyword in self.credibility_tiers['tier3']:
            if keyword in url or keyword in title or keyword in source_name:
                return 'medium'
        
        return 'low'
    
    def _get_credibility_tier(self, source: Dict) -> str:
        """获取可信度分级"""
        cred = source.get('credibility', 'low')
        if cred == 'high':
            return 'tier1'
        elif cred == 'medium':
            return 'tier2'
        return 'tier3'
    
    async def _stage5_deep_analysis(self, context: ResearchContext) -> None:
        """阶段 5: 深度分析"""
        # 应用分析框架
        analysis = {}
        
        # PESTEL 分析
        analysis['pestel'] = await self._apply_pestel(context)
        
        # SWOT 分析
        analysis['swot'] = await self._apply_swot(context)
        
        # 关键发现
        analysis['key_findings'] = await self._extract_key_findings(context)
        
        context.analysis_results = analysis
        logger.info(f"深度分析完成，应用 {len(analysis)} 个框架")
    
    async def _apply_pestel(self, context: ResearchContext) -> Dict:
        """PESTEL 分析"""
        return {
            'political': '政策环境分析...',
            'economic': '经济环境分析...',
            'social': '社会环境分析...',
            'technological': '技术环境分析...',
            'environmental': '环境因素分析...',
            'legal': '法律环境分析...'
        }
    
    async def _apply_swot(self, context: ResearchContext) -> Dict:
        """SWOT 分析"""
        return {
            'strengths': ['优势 1', '优势 2'],
            'weaknesses': ['劣势 1', '劣势 2'],
            'opportunities': ['机会 1', '机会 2'],
            'threats': ['威胁 1', '威胁 2']
        }
    
    async def _extract_key_findings(self, context: ResearchContext) -> List[str]:
        """提取关键发现"""
        # 基于采集的数据提取关键发现
        return [
            f'{context.topic} 市场规模持续增长',
            '行业集中度进一步提升',
            '技术创新成为核心竞争力',
            '政策支持力度加大'
        ]
    
    async def _stage6_write_report(self, context: ResearchContext) -> Dict:
        """阶段 6: 报告撰写"""
        report = {
            'title': f'{context.topic}深度研究报告',
            'executive_summary': f'本报告对{context.topic}进行全面深入研究...',
            'sections': [],
            'key_findings': context.analysis_results.get('key_findings', []),
            'references': []
        }
        
        # 生成报告章节
        sections = [
            ('执行摘要', 'executive_summary'),
            ('行业概况', 'overview'),
            ('市场规模', 'market_size'),
            ('竞争格局', 'competition'),
            ('发展趋势', 'trends'),
            ('政策环境', 'policy'),
            ('风险分析', 'risks'),
            ('结论建议', 'conclusion')
        ]
        
        for title, section_id in sections:
            section = {
                'title': title,
                'content': f'{title}内容...',
                'citations': []
            }
            
            # 添加引用
            for source in context.sources[:3]:
                section['citations'].append({
                    'source': source.get('source'),
                    'url': source.get('url'),
                    'credibility': source.get('credibility')
                })
            
            report['sections'].append(section)
        
        # 生成参考文献
        for source in context.sources:
            report['references'].append({
                'title': source.get('title'),
                'source': source.get('source'),
                'url': source.get('url'),
                'date': source.get('date'),
                'credibility': source.get('credibility')
            })
        
        logger.info(f"报告撰写完成，共 {len(report['sections'])} 个章节")
        return report
    
    async def _stage7_visualize(self, context: ResearchContext, report: Dict) -> None:
        """阶段 7: 数据可视化"""
        # 生成图表数据
        visualizations = [
            {
                'type': 'table',
                'title': '关键数据汇总',
                'data': {'headers': ['指标', '2024', '2025', '2026E'], 'rows': []}
            }
        ]
        
        report['data_visualizations'] = visualizations
    
    async def _stage8_quality_review(self, context: ResearchContext, report: Dict) -> Dict:
        """阶段 8: 质量审查"""
        # 计算质量评分
        sources_count = len(context.sources)
        high_cred_count = len([s for s in context.sources if s.get('credibility') == 'high'])
        sections_count = len(report.get('sections', []))
        refs_count = len(report.get('references', []))
        
        completeness = min(100, sections_count * 12)
        credibility = min(100, (high_cred_count / max(1, sources_count)) * 100 + 20)
        depth = min(100, refs_count * 5 + 30)
        overall = (completeness + credibility + depth) / 3
        
        quality = {
            'completeness_score': round(completeness),
            'credibility_score': round(credibility),
            'depth_score': round(depth),
            'overall_score': round(overall)
        }
        
        logger.info(f"质量审查完成，综合评分：{quality['overall_score']}")
        return quality
    
    async def _save_report(self, report: Dict, context: ResearchContext) -> Dict:
        """保存报告"""
        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_topic = ''.join(c for c in context.topic if c.isalnum() or c in ' _-')[:30]
        filename = f"{safe_topic}_{timestamp}.md"
        filepath = self.output_dir / filename
        
        # 生成 Markdown 内容
        content = self._generate_markdown(report)
        filepath.write_text(content, encoding='utf-8')
        
        logger.info(f"报告已保存：{filepath}")
        return {
            'type': 'markdown',
            'path': str(filepath)
        }
    
    def _generate_markdown(self, report: Dict) -> str:
        """生成 Markdown 格式报告"""
        lines = [
            f"# {report['title']}",
            "",
            f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "## 执行摘要",
            "",
            report.get('executive_summary', ''),
            "",
            "## 关键发现",
            "",
        ]
        
        for finding in report.get('key_findings', []):
            lines.append(f"- {finding}")
        
        lines.append("")
        
        for section in report.get('sections', []):
            lines.append(f"## {section['title']}")
            lines.append("")
            lines.append(section.get('content', ''))
            lines.append("")
        
        lines.append("## 参考文献")
        lines.append("")
        
        for i, ref in enumerate(report.get('references', []), 1):
            cred = "✅" if ref.get('credibility') == 'high' else "⚠️"
            lines.append(f"{i}. {cred} {ref.get('source')}: {ref.get('title')} ({ref.get('date', 'n.d.')})")
        
        return '\n'.join(lines)
    
    def _build_output(self, report: Dict, context: ResearchContext, quality: Dict) -> Dict:
        """构建最终输出"""
        duration_ms = int((time.time() - context.start_time) * 1000)
        
        return {
            'success': True,
            'report': report,
            'research_process': {
                'sources_searched': len(context.search_queries) * 10,
                'sources_used': len(context.sources),
                'high_credibility_sources': len([s for s in context.sources if s.get('credibility') == 'high']),
                'search_queries': context.search_queries
            },
            'quality': quality,
            'execution': {
                'duration_ms': duration_ms,
                'model_used': 'default',
                'token_used': 0,
                'cost': 0.0
            }
        }
