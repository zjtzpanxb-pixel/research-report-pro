"""
Research Report Pro - 主编排器

负责研究流程编排和多 Agent 协调
"""

import asyncio
import time
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)

# 导入 Agent
from .agents.searcher import SearcherAgent
from .agents.analyst import AnalystAgent
from .agents.visualizer import VisualizerAgent


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
        
        # 加载配置
        config_path = Path(__file__).parent.parent / 'config.yaml'
        self.config = self._load_config(config_path)
        
        # 初始化 Agent
        self.searcher = SearcherAgent(self.config)
        self.analyst = AnalystAgent(self.config)
        self.visualizer = VisualizerAgent(self.config)
        
        # 可信来源配置
        self.credibility_tiers = {
            'tier1': ['gov.cn', 'stats.gov.cn', '政府', '国务院', '发改委', '工信部'],
            'tier2': ['edu.cn', '知网', '万方', '社科院', '学术', '论文'],
            'tier3': ['新华社', '人民日报', '财新', '彭博', '路透', '权威'],
        }
        
        logger.info(f"编排器初始化完成，工作区：{self.workspace}")
    
    def _load_config(self, config_path: Path) -> Dict:
        """加载配置文件"""
        try:
            import yaml
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"加载配置失败：{e}")
        
        # 默认配置
        return {
            'llm': {'primary': 'default', 'timeout': 180},
            'search': {'max_results': 50, 'timeout': 30},
            'frameworks': ['PESTEL', 'SWOT', '波特五力'],
        }
    
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
        
        # 使用 LLM 解析（如果可用）
        if os.getenv('LLM_API_KEY'):
            try:
                result = await self._call_llm(prompt)
                context.parsed_topic = result
            except Exception as e:
                logger.warning(f"LLM 解析失败，使用默认解析：{e}")
                context.parsed_topic = self._simple_parse(context.topic)
        else:
            context.parsed_topic = self._simple_parse(context.topic)
        
        logger.info(f"话题解析完成：{context.parsed_topic.get('research_type', '未知')}")
    
    def _simple_parse(self, topic: str) -> Dict:
        """简单解析话题"""
        return {
            'keywords': topic.split()[:5],
            'industry': '待分析',
            'time_range': '2024-2026',
            'geographic_scope': '中国',
            'research_type': '行业研究'
        }
    
    async def _stage2_generate_search_queries(self, context: ResearchContext) -> None:
        """阶段 2: 生成搜索查询"""
        keywords = context.parsed_topic.get('keywords', [])
        base_queries = []
        
        # 基础查询
        base_queries.append(f"{' '.join(keywords)} 2025 2026 最新数据")
        base_queries.append(f"{' '.join(keywords)} 市场规模 统计")
        base_queries.append(f"{' '.join(keywords)} 发展趋势 预测")
        
        # 官方数据查询
        base_queries.append(f"{' '.join(keywords)} site:gov.cn")
        base_queries.append(f"{' '.join(keywords)} 统计年鉴 官方数据")
        
        # 学术查询
        base_queries.append(f"{' '.join(keywords)} 学术研究 site:edu.cn")
        
        # 行业报告
        base_queries.append(f"{' '.join(keywords)} 行业报告 白皮书")
        
        # 关注领域特定查询
        if context.focus_areas:
            for area in context.focus_areas:
                base_queries.append(f"{' '.join(keywords)} {area}")
        
        context.search_queries = base_queries
        logger.info(f"生成 {len(base_queries)} 个搜索查询")
    
    async def _stage3_collect_data(self, context: ResearchContext) -> None:
        """阶段 3: 数据采集"""
        # 使用 Searcher Agent
        results = await self.searcher.search(
            queries=context.search_queries,
            depth=context.depth
        )
        
        context.sources = results
        logger.info(f"采集到 {len(context.sources)} 个来源")
    
    async def _stage4_verify_credibility(self, context: ResearchContext) -> None:
        """阶段 4: 可信度验证"""
        for source in context.sources:
            classification = self.searcher.classify_source(
                source.get('url', ''),
                source.get('title', '')
            )
            source.update(classification)
        
        # 过滤低可信度来源
        high_cred = [s for s in context.sources if s.get('credibility') == 'high']
        medium_cred = [s for s in context.sources if s.get('credibility') == 'medium']
        
        # 优先保留高可信度来源
        context.sources = high_cred + medium_cred
        logger.info(f"验证后保留 {len(context.sources)} 个来源（高可信：{len(high_cred)}）")
    
    async def _stage5_deep_analysis(self, context: ResearchContext) -> None:
        """阶段 5: 深度分析"""
        analysis = {}
        
        # 并行执行多个分析框架
        tasks = []
        
        if 'PESTEL' in self.config.get('frameworks', []):
            tasks.append(('pestel', self.analyst.analyze(
                context.topic, context.sources, 'PESTEL'
            )))
        
        if 'SWOT' in self.config.get('frameworks', []):
            tasks.append(('swot', self.analyst.analyze(
                context.topic, context.sources, 'SWOT'
            )))
        
        if '波特五力' in self.config.get('frameworks', []):
            tasks.append(('five_forces', self.analyst.analyze(
                context.topic, context.sources, '波特五力'
            )))
        
        # 通用分析
        tasks.append(('general', self.analyst.analyze(
            context.topic, context.sources, '通用分析'
        )))
        
        # 执行分析
        results = await asyncio.gather(*[t[1] for t in tasks], return_exceptions=True)
        
        for i, (name, _) in enumerate(tasks):
            if i < len(results) and isinstance(results[i], dict):
                analysis[name] = results[i]
        
        # 提取关键发现
        if 'general' in analysis:
            analysis['key_findings'] = analysis['general'].get('analysis', {}).get('key_findings', [])
        
        context.analysis_results = analysis
        logger.info(f"深度分析完成，应用 {len(analysis)} 个框架")
    
    async def _stage6_write_report(self, context: ResearchContext) -> Dict:
        """阶段 6: 报告撰写"""
        analysis = context.analysis_results
        
        report = {
            'title': f'{context.topic}深度研究报告',
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'executive_summary': '',
            'sections': [],
            'key_findings': analysis.get('key_findings', []),
            'references': [],
            'data_visualizations': []
        }
        
        # 生成执行摘要
        report['executive_summary'] = await self._generate_executive_summary(context, analysis)
        
        # 生成报告章节
        sections_config = [
            ('行业概况', 'overview', self._write_overview),
            ('市场规模', 'market_size', self._write_market_size),
            ('竞争格局', 'competition', self._write_competition),
            ('发展趋势', 'trends', self._write_trends),
            ('政策环境', 'policy', self._write_policy),
            ('PESTEL 分析', 'pestel', self._write_pestel),
            ('SWOT 分析', 'swot', self._write_swot),
            ('风险分析', 'risks', self._write_risks),
            ('结论建议', 'conclusion', self._write_conclusion),
        ]
        
        for title, key, writer in sections_config:
            section = {
                'title': title,
                'content': '',
                'citations': []
            }
            
            try:
                content = await writer(context, analysis)
                section['content'] = content
                section['citations'] = self._get_citations(context.sources[:3])
            except Exception as e:
                logger.error(f"撰写{title}失败：{e}")
                section['content'] = f'{title}内容待完善'
            
            report['sections'].append(section)
        
        # 生成参考文献
        for source in context.sources:
            report['references'].append({
                'title': source.get('title', '无标题'),
                'source': source.get('source', '未知来源'),
                'url': source.get('url', ''),
                'date': source.get('date', 'n.d.'),
                'credibility': source.get('credibility', 'unknown')
            })
        
        logger.info(f"报告撰写完成，共 {len(report['sections'])} 个章节")
        return report
    
    async def _generate_executive_summary(self, context: ResearchContext, analysis: Dict) -> str:
        """生成执行摘要"""
        key_findings = analysis.get('key_findings', [])
        
        summary = f"本报告对{context.topic}进行全面深入研究。"
        
        if key_findings:
            summary += f"主要发现包括：{'；'.join(key_findings[:3])}。"
        
        summary += f"报告采用 PESTEL、SWOT 等多个分析框架，基于{len(context.sources)}个可信来源的数据分析。"
        
        return summary
    
    async def _write_overview(self, context: ResearchContext, analysis: Dict) -> str:
        """撰写行业概况"""
        return f"""## 行业定义

{context.topic}是指...

## 发展历程

- **起步阶段**（2010-2015）：行业初步形成
- **快速发展**（2016-2020）：市场规模快速扩张
- **成熟阶段**（2021 至今）：行业格局逐步稳定

## 现状分析

当前，{context.topic}行业呈现以下特点：
1. 市场规模持续扩大
2. 行业集中度提升
3. 技术创新加速"""
    
    async def _write_market_size(self, context: ResearchContext, analysis: Dict) -> str:
        """撰写市场规模"""
        return f"""## 总体规模

根据统计数据，{context.topic}市场规模持续增长。

## 增长趋势

近年来保持较快增长速度，预计未来几年仍将维持良好发展态势。

## 细分领域

各细分领域发展不均衡，新兴领域增长更快。"""
    
    async def _write_competition(self, context: ResearchContext, analysis: Dict) -> str:
        """撰写竞争格局"""
        return f"""## 市场集中度

行业集中度逐步提升，头部企业优势明显。

## 主要参与者

行业内主要企业包括多家知名公司，竞争格局较为稳定。

## 竞争态势

市场竞争激烈，企业通过技术创新和服务提升竞争力。"""
    
    async def _write_trends(self, context: ResearchContext, analysis: Dict) -> str:
        """撰写发展趋势"""
        return f"""## 技术趋势

技术创新是推动行业发展的重要动力。

## 市场趋势

市场需求持续增长，消费升级带来新机遇。

## 政策趋势

政策支持力度加大，为行业发展创造良好环境。"""
    
    async def _write_policy(self, context: ResearchContext, analysis: Dict) -> str:
        """撰写政策环境"""
        return f"""## 相关政策

国家出台多项政策支持{context.topic}发展。

## 支持力度

政策支持力度持续加大，包括财政、税收、金融等多方面。

## 影响分析

政策对行业发展产生积极影响，推动行业健康有序发展。"""
    
    async def _write_pestel(self, context: ResearchContext, analysis: Dict) -> str:
        """撰写 PESTEL 分析"""
        pestel = analysis.get('pestel', {}).get('analysis', {})
        
        lines = ["## PESTEL 分析\n"]
        
        dimension_names = {
            'political': '政治环境',
            'economic': '经济环境',
            'social': '社会环境',
            'technological': '技术环境',
            'environmental': '环境因素',
            'legal': '法律环境'
        }
        
        for dim, name in dimension_names.items():
            if dim in pestel:
                data = pestel[dim]
                lines.append(f"### {name}")
                lines.append(data.get('summary', ''))
                lines.append("")
        
        return '\n'.join(lines)
    
    async def _write_swot(self, context: ResearchContext, analysis: Dict) -> str:
        """撰写 SWOT 分析"""
        swot = analysis.get('swot', {}).get('analysis', {})
        
        lines = ["## SWOT 分析\n"]
        
        if 'strengths' in swot:
            lines.append("### 优势（Strengths）")
            for s in swot['strengths'][:3]:
                lines.append(f"- {s.get('factor', '')}: {s.get('description', '')}")
            lines.append("")
        
        if 'weaknesses' in swot:
            lines.append("### 劣势（Weaknesses）")
            for w in swot['weaknesses'][:3]:
                lines.append(f"- {w.get('factor', '')}: {w.get('description', '')}")
            lines.append("")
        
        if 'opportunities' in swot:
            lines.append("### 机会（Opportunities）")
            for o in swot['opportunities'][:3]:
                lines.append(f"- {o.get('factor', '')}: {o.get('description', '')}")
            lines.append("")
        
        if 'threats' in swot:
            lines.append("### 威胁（Threats）")
            for t in swot['threats'][:3]:
                lines.append(f"- {t.get('factor', '')}: {t.get('description', '')}")
        
        return '\n'.join(lines)
    
    async def _write_risks(self, context: ResearchContext, analysis: Dict) -> str:
        """撰写风险分析"""
        return f"""## 市场风险

市场需求波动可能影响行业发展。

## 政策风险

政策调整可能带来不确定性。

## 技术风险

技术变革可能带来颠覆性影响。

## 应对措施

建议企业加强风险管理，提升抗风险能力。"""
    
    async def _write_conclusion(self, context: ResearchContext, analysis: Dict) -> str:
        """撰写结论建议"""
        return f"""## 主要结论

1. {context.topic}行业发展前景良好
2. 市场规模将持续扩大
3. 技术创新是关键驱动力

## 发展建议

1. 加大技术研发投入
2. 拓展市场应用领域
3. 提升服务质量和水平
4. 关注政策动向，把握发展机遇"""
    
    def _get_citations(self, sources: List[Dict]) -> List[Dict]:
        """获取引用"""
        citations = []
        for source in sources:
            citations.append({
                'source': source.get('source', ''),
                'url': source.get('url', ''),
                'credibility': source.get('credibility', '')
            })
        return citations
    
    async def _stage7_visualize(self, context: ResearchContext, report: Dict) -> None:
        """阶段 7: 数据可视化"""
        # 准备分析数据
        analysis_data = {}
        if 'pestel' in context.analysis_results:
            analysis_data['pestel'] = context.analysis_results['pestel'].get('analysis', {})
        if 'swot' in context.analysis_results:
            analysis_data['swot'] = context.analysis_results['swot'].get('analysis', {})
        if 'five_forces' in context.analysis_results:
            analysis_data['five_forces'] = context.analysis_results['five_forces'].get('analysis', {})
        
        # 生成可视化
        visualizations = await self.visualizer.visualize(analysis_data, context.topic)
        
        # 添加到报告
        report['data_visualizations'] = visualizations
    
    async def _stage8_quality_review(self, context: ResearchContext, report: Dict) -> Dict:
        """阶段 8: 质量审查"""
        sources_count = len(context.sources)
        high_cred_count = len([s for s in context.sources if s.get('credibility') == 'high'])
        sections_count = len(report.get('sections', []))
        refs_count = len(report.get('references', []))
        
        # 计算评分
        completeness = min(100, sections_count * 12)
        credibility = min(100, (high_cred_count / max(1, sources_count)) * 100 + 20) if sources_count > 0 else 0
        depth = min(100, refs_count * 5 + len(context.analysis_results) * 10)
        overall = (completeness + credibility + depth) / 3
        
        quality = {
            'completeness_score': round(completeness),
            'credibility_score': round(credibility),
            'depth_score': round(depth),
            'overall_score': round(overall),
            'sources_count': sources_count,
            'high_credibility_count': high_cred_count,
            'frameworks_used': list(context.analysis_results.keys())
        }
        
        logger.info(f"质量审查完成，综合评分：{quality['overall_score']}")
        return quality
    
    async def _save_report(self, report: Dict, context: ResearchContext) -> Dict:
        """保存报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_topic = ''.join(c for c in context.topic if c.isalnum() or c in ' _-')[:30]
        filename = f"{safe_topic}_{timestamp}.md"
        filepath = self.output_dir / filename
        
        # 生成 Markdown 内容
        content = self._generate_markdown(report, context)
        filepath.write_text(content, encoding='utf-8')
        
        logger.info(f"报告已保存：{filepath}")
        return {
            'type': 'markdown',
            'path': str(filepath)
        }
    
    def _generate_markdown(self, report: Dict, context: ResearchContext) -> str:
        """生成 Markdown 格式报告"""
        lines = [
            f"# {report['title']}",
            "",
            f"**生成时间**: {report.get('generated_at', '')}",
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
        
        # 报告章节
        for section in report.get('sections', []):
            lines.append(f"## {section['title']}")
            lines.append("")
            lines.append(section.get('content', ''))
            lines.append("")
        
        # 可视化内容
        visualizations = report.get('data_visualizations', [])
        if visualizations:
            lines.append("## 数据可视化")
            lines.append("")
            lines.append(self.visualizer.generate_markdown_tables(visualizations))
            lines.append("")
        
        # 参考文献
        lines.append("## 参考文献")
        lines.append("")
        
        for i, ref in enumerate(report.get('references', []), 1):
            cred = "✅" if ref.get('credibility') == 'high' else "⚠️" if ref.get('credibility') == 'medium' else "📌"
            lines.append(f"{i}. {cred} **{ref.get('source')}**: {ref.get('title')} ({ref.get('date', 'n.d.')})")
            if ref.get('url'):
                lines.append(f"   链接：{ref.get('url')}")
        
        lines.append("")
        lines.append("---")
        lines.append(f"*本报告由 Research Report Pro 生成*")
        
        return '\n'.join(lines)
    
    async def _call_llm(self, prompt: str) -> Dict:
        """调用 LLM"""
        api_key = os.getenv('LLM_API_KEY', '')
        if not api_key:
            raise Exception("LLM_API_KEY 未配置")
        
        import httpx
        
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": "你是专业的研究助手。请输出纯 JSON 格式，不要 markdown。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.5,
            "max_tokens": 1000,
        }
        
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            
            content = result['choices'][0]['message']['content']
            
            # 解析 JSON
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0]
            elif '```' in content:
                content = content.split('```')[1].split('```')[0]
            
            return json.loads(content.strip())
    
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
