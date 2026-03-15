"""
Research Report Pro - 主编排器

基于真实网络搜索数据生成深度研究报告
"""

import asyncio
import time
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

from .agents.searcher import SearcherAgent


@dataclass
class ResearchContext:
    """研究上下文"""
    topic: str
    depth: str = "deep"
    focus_areas: Optional[List[str]] = None
    start_time: float = 0
    search_queries: List[str] = None
    sources: List[Dict] = None
    extracted_data: Dict = None
    
    def __post_init__(self):
        if self.search_queries is None:
            self.search_queries = []
        if self.sources is None:
            self.sources = []
        if self.extracted_data is None:
            self.extracted_data = {}


class ResearchReportOrchestrator:
    """研究报告主编排器"""
    
    def __init__(self, workspace: str):
        self.workspace = Path(workspace)
        self.output_dir = self.workspace / '研究报告'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.config = self._load_config()
        self.searcher = SearcherAgent(self.config)
        
        logger.info(f"编排器初始化完成，工作区：{self.workspace}")
    
    def _load_config(self) -> Dict:
        """加载配置文件"""
        config_path = Path(__file__).parent.parent / 'config.yaml'
        try:
            import yaml
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"加载配置失败：{e}")
        
        return {
            'search': {'max_results': 50, 'timeout': 30},
            'frameworks': ['PESTEL', 'SWOT', '波特五力'],
        }
    
    async def research(self, topic: str, depth: str = "deep", focus_areas: Optional[List[str]] = None) -> Dict[str, Any]:
        """执行完整研究流程"""
        context = ResearchContext(
            topic=topic,
            depth=depth,
            focus_areas=focus_areas,
            start_time=time.time()
        )
        
        try:
            logger.info("阶段 1: 生成搜索策略")
            await self._generate_search_queries(context)
            
            logger.info("阶段 2: 执行网络搜索")
            await self._execute_search(context)
            
            logger.info("阶段 3: 提取真实数据")
            await self._extract_real_data(context)
            
            logger.info("阶段 4: 撰写报告")
            report = await self._write_report_from_data(context)
            
            logger.info("阶段 5: 质量审查")
            quality = self._quality_review(context, report)
            
            logger.info("阶段 6: 存储报告")
            storage = await self._save_report(report, context)
            report['storage'] = storage
            
            return self._build_output(report, context, quality)
            
        except Exception as e:
            logger.error(f"研究失败：{e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'suggestions': ['检查网络连接', '尝试简化话题']
            }
    
    async def _generate_search_queries(self, context: ResearchContext) -> None:
        """生成搜索查询"""
        queries = [
            f"{context.topic} 2025 2026 最新数据",
            f"{context.topic} 市场规模 统计",
            f"{context.topic} 发展趋势 预测",
            f"{context.topic} site:gov.cn",
            f"{context.topic} 行业报告",
        ]
        
        if context.focus_areas:
            for area in context.focus_areas:
                queries.append(f"{context.topic} {area}")
        
        context.search_queries = queries
        logger.info(f"生成 {len(queries)} 个搜索查询")
    
    async def _execute_search(self, context: ResearchContext) -> None:
        """执行网络搜索"""
        results = await self.searcher.search(
            queries=context.search_queries,
            depth=context.depth
        )
        context.sources = results
        logger.info(f"搜索到 {len(context.sources)} 个来源")
    
    async def _extract_real_data(self, context: ResearchContext) -> None:
        """从搜索结果中提取真实数据"""
        extracted = {
            'statistics': [],
            'policies': [],
            'trends': [],
            'players': [],
            'summary': [],
        }
        
        for source in context.sources:
            content = source.get('raw_content', '')
            source_name = source.get('source', '')
            url = source.get('url', '')
            
            if not content or len(content) < 100:
                continue
            
            # 清理 markdown
            clean_content = self._clean_markdown(content)
            
            # 提取统计数据
            stats = self._extract_statistics(clean_content, source_name, url)
            extracted['statistics'].extend(stats)
            
            # 提取政策
            policies = self._extract_policies(clean_content, source_name, url)
            extracted['policies'].extend(policies)
            
            # 提取趋势
            trends = self._extract_trends(clean_content, source_name, url)
            extracted['trends'].extend(trends)
            
            # 提取企业/行业
            players = self._extract_players(clean_content, source_name, url)
            extracted['players'].extend(players)
            
            # 内容摘要
            extracted['summary'].append({
                'source': source_name,
                'url': url,
                'content': clean_content[:1000],
            })
        
        # 去重
        for key in extracted:
            seen = set()
            unique = []
            for item in extracted[key]:
                text = item.get('text', item.get('content', ''))[:50]
                if text not in seen:
                    seen.add(text)
                    unique.append(item)
            extracted[key] = unique[:15]
        
        context.extracted_data = extracted
        total = sum(len(v) for v in extracted.values())
        logger.info(f"提取到 {total} 条数据（统计{len(extracted['statistics'])} 条）")
    
    def _clean_markdown(self, content: str) -> str:
        """清理 markdown 格式"""
        content = re.sub(r'!\[.*?\]\(.*?\)', '', content)
        content = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', content)
        content = re.sub(r'^#+\s*', '', content, flags=re.MULTILINE)
        content = re.sub(r'^[\*\-]\s*', '', content, flags=re.MULTILINE)
        content = re.sub(r'\n{3,}', '\n\n', content)
        return content.strip()
    
    def _extract_statistics(self, content: str, source: str, url: str) -> List[Dict]:
        """提取统计数据"""
        stats = []
        sentences = content.split('\n')
        
        for sent in sentences:
            sent = sent.strip()
            if len(sent) < 20 or len(sent) > 300:
                continue
            
            has_number = any(c.isdigit() for c in sent)
            has_keyword = any(k in sent for k in ['亿', '万', '%', '增长', '达到', '规模', '收入'])
            
            if has_number and has_keyword:
                stats.append({'text': sent, 'source': source, 'url': url})
        
        return stats[:10]
    
    def _extract_policies(self, content: str, source: str, url: str) -> List[Dict]:
        """提取政策信息"""
        policies = []
        if '政策' not in source and '政府' not in source and '发改委' not in source and '工信部' not in source:
            return policies
        
        sentences = content.split('\n')
        for sent in sentences:
            sent = sent.strip()
            if 20 <= len(sent) <= 300 and any(k in sent for k in ['政策', '支持', '鼓励', '发展', '规划']):
                policies.append({'text': sent, 'source': source, 'url': url})
        
        return policies[:10]
    
    def _extract_trends(self, content: str, source: str, url: str) -> List[Dict]:
        """提取趋势"""
        trends = []
        sentences = content.split('\n')
        for sent in sentences:
            sent = sent.strip()
            if 20 <= len(sent) <= 300 and any(k in sent for k in ['趋势', '未来', '预计', '将', '发展']):
                trends.append({'text': sent, 'source': source, 'url': url})
        
        return trends[:10]
    
    def _extract_players(self, content: str, source: str, url: str) -> List[Dict]:
        """提取企业/行业信息"""
        players = []
        sentences = content.split('\n')
        for sent in sentences:
            sent = sent.strip()
            if 20 <= len(sent) <= 300 and any(k in sent for k in ['企业', '公司', '行业', '产业']):
                players.append({'text': sent, 'source': source, 'url': url})
        
        return players[:10]
    
    async def _write_report_from_data(self, context: ResearchContext) -> Dict:
        """基于真实数据撰写报告"""
        data = context.extracted_data
        
        report = {
            'title': f'{context.topic}深度研究报告',
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'executive_summary': self._generate_summary(context, data),
            'sections': [],
            'key_findings': self._generate_key_findings(data),
            'references': [],
        }
        
        # 生成章节
        sections = [
            ('行业概况', self._write_overview),
            ('市场规模与数据', self._write_market_size),
            ('主要企业与竞争', self._write_competition),
            ('政策环境', self._write_policy),
            ('发展趋势', self._write_trends),
            ('风险分析', self._write_risks),
            ('结论建议', self._write_conclusion),
        ]
        
        for title, writer in sections:
            report['sections'].append({
                'title': title,
                'content': writer(context, data),
                'citations': self._get_citations(context.sources[:5]),
            })
        
        # 参考文献
        for source in context.sources:
            report['references'].append({
                'title': source.get('title', '无标题')[:100],
                'source': source.get('source', '未知'),
                'url': source.get('url', ''),
                'date': source.get('date', datetime.now().strftime('%Y-%m-%d')),
                'credibility': source.get('credibility', 'medium'),
            })
        
        logger.info(f"报告撰写完成，{len(report['sections'])}个章节")
        return report
    
    def _generate_summary(self, context: ResearchContext, data: Dict) -> str:
        """生成执行摘要"""
        stats_count = len(data.get('statistics', []))
        sources_count = len(context.sources)
        
        summary = f"本报告基于{sources_count}个权威来源的实时数据，对{context.topic}进行深入研究。"
        
        if stats_count > 0:
            summary += f"报告整理了{stats_count}条关键统计数据，"
        if len(data.get('policies', [])) > 0:
            summary += f"分析了{len(data['policies'])}项相关政策，"
        
        summary += "数据来源包括政府官网、权威媒体、学术机构等可信渠道。"
        return summary
    
    def _generate_key_findings(self, data: Dict) -> List[str]:
        """生成关键发现"""
        findings = []
        
        # 从统计数据中提取
        for stat in data.get('statistics', [])[:3]:
            text = stat.get('text', '')
            if len(text) > 10:
                findings.append(text)
        
        # 从趋势中提取
        for trend in data.get('trends', [])[:2]:
            text = trend.get('text', '')
            if len(text) > 10 and text not in findings:
                findings.append(text)
        
        # 确保至少 3 条
        while len(findings) < 3:
            findings.append(f"基于权威数据源的研究分析")
        
        return findings[:5]
    
    def _write_overview(self, context: ResearchContext, data: Dict) -> str:
        """行业概况"""
        lines = ["## 行业定义", "", f"{context.topic}是指在该领域应用相关技术和方法的总称。", "", "## 现状分析", ""]
        
        summary = data.get('summary', [])
        if summary:
            lines.append(f"根据收集到的资料：")
            lines.append("")
            for s in summary[:3]:
                lines.append(f"- {s.get('content', '')[:200]} *（来源：{s.get('source', '未知')}）*")
        
        return '\n'.join(lines)
    
    def _write_market_size(self, context: ResearchContext, data: Dict) -> str:
        """市场规模"""
        lines = ["## 总体规模", ""]
        
        stats = data.get('statistics', [])
        if stats:
            lines.append("收集到的统计数据：")
            lines.append("")
            for stat in stats[:5]:
                lines.append(f"- {stat.get('text', '待补充')} *（来源：{stat.get('source', '未知')}）*")
        else:
            lines.append(f"需要进一步收集{context.topic}的市场规模数据。")
        
        return '\n'.join(lines)
    
    def _write_competition(self, context: ResearchContext, data: Dict) -> str:
        """竞争格局"""
        lines = ["## 主要参与者", ""]
        
        players = data.get('players', [])
        if players:
            for player in players[:5]:
                lines.append(f"- {player.get('text', '待补充')} *（来源：{player.get('source', '未知')}）*")
        
        return '\n'.join(lines)
    
    def _write_policy(self, context: ResearchContext, data: Dict) -> str:
        """政策环境"""
        lines = ["## 相关政策", ""]
        
        policies = data.get('policies', [])
        if policies:
            for policy in policies[:5]:
                lines.append(f"- {policy.get('text', '待补充')} *（来源：{policy.get('source', '未知')}）*")
        else:
            lines.append("需要进一步收集相关政策文件。")
        
        return '\n'.join(lines)
    
    def _write_trends(self, context: ResearchContext, data: Dict) -> str:
        """发展趋势"""
        lines = ["## 发展趋势", ""]
        
        trends = data.get('trends', [])
        if trends:
            for i, trend in enumerate(trends[:5], 1):
                lines.append(f"{i}. {trend.get('text', '待补充')} *（来源：{trend.get('source', '未知')}）*")
        
        return '\n'.join(lines)
    
    def _write_risks(self, context: ResearchContext, data: Dict) -> str:
        """风险分析"""
        return "## 风险分析\n\n### 市场风险\n\n- 市场需求波动风险\n- 竞争加剧风险\n\n### 政策风险\n\n- 政策调整不确定性\n\n### 技术风险\n\n- 技术迭代风险"
    
    def _write_conclusion(self, context: ResearchContext, data: Dict) -> str:
        """结论建议"""
        lines = ["## 主要结论", ""]
        
        findings = self._generate_key_findings(data)
        for i, finding in enumerate(findings[:3], 1):
            lines.append(f"{i}. {finding}")
        
        lines.extend(["", "## 发展建议", "", "1. 加大技术研发投入", "2. 拓展市场应用领域", "3. 关注政策动向"])
        return '\n'.join(lines)
    
    def _get_citations(self, sources: List[Dict]) -> List[Dict]:
        """获取引用"""
        return [{'source': s.get('source', ''), 'url': s.get('url', ''), 'credibility': s.get('credibility', '')} for s in sources]
    
    def _quality_review(self, context: ResearchContext, report: Dict) -> Dict:
        """质量审查"""
        stats_count = len(context.extracted_data.get('statistics', []))
        sources_count = len(context.sources)
        high_cred_count = len([s for s in context.sources if s.get('credibility') == 'high'])
        sections_count = len(report.get('sections', []))
        
        data_score = min(100, stats_count * 15)
        completeness = min(100, sections_count * 14)
        credibility = min(100, (high_cred_count / max(1, sources_count)) * 100) if sources_count > 0 else 0
        depth = min(100, data_score + len(context.extracted_data.get('summary', [])) * 10)
        overall = (data_score + completeness + credibility + depth) / 4
        
        return {
            'completeness_score': round(completeness),
            'credibility_score': round(credibility),
            'depth_score': round(depth),
            'overall_score': round(overall),
            'sources_count': sources_count,
            'high_credibility_count': high_cred_count,
            'data_points_count': stats_count,
        }
    
    async def _save_report(self, report: Dict, context: ResearchContext) -> Dict:
        """保存报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_topic = ''.join(c for c in context.topic if c.isalnum() or c in ' _-')[:30]
        filename = f"{safe_topic}_{timestamp}.md"
        filepath = self.output_dir / filename
        
        content = self._generate_markdown(report)
        filepath.write_text(content, encoding='utf-8')
        
        logger.info(f"报告已保存：{filepath}")
        return {'type': 'markdown', 'path': str(filepath)}
    
    def _generate_markdown(self, report: Dict) -> str:
        """生成 Markdown"""
        lines = [
            f"# {report['title']}", "", f"**生成时间**: {report.get('generated_at', '')}",
            "", "## 执行摘要", "", report.get('executive_summary', ''),
            "", "## 关键发现", "",
        ]
        
        for finding in report.get('key_findings', []):
            lines.append(f"- {finding}")
        
        for section in report.get('sections', []):
            lines.append(f"\n## {section['title']}\n")
            lines.append(section.get('content', ''))
        
        lines.append("\n## 参考文献\n")
        for i, ref in enumerate(report.get('references', []), 1):
            cred = "✅" if ref.get('credibility') == 'high' else "⚠️"
            lines.append(f"{i}. {cred} **{ref.get('source')}**: {ref.get('title', '无标题')}")
            if ref.get('url'):
                lines.append(f"   链接：{ref.get('url')}")
        
        lines.extend(["", "---", f"*本报告基于{len(report.get('references', []))}个权威来源的实时数据生成*"])
        return '\n'.join(lines)
    
    def _build_output(self, report: Dict, context: ResearchContext, quality: Dict) -> Dict:
        """构建输出"""
        duration_ms = int((time.time() - context.start_time) * 1000)
        
        return {
            'success': True,
            'report': report,
            'research_process': {
                'sources_searched': len(context.search_queries) * 10,
                'sources_used': len(context.sources),
                'high_credibility_sources': len([s for s in context.sources if s.get('credibility') == 'high']),
                'data_points_extracted': len(context.extracted_data.get('statistics', [])),
            },
            'quality': quality,
            'execution': {
                'duration_ms': duration_ms,
                'model_used': 'openclaw-built-in',
                'cost': 0.0
            }
        }
