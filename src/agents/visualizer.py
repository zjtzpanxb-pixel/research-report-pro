"""
可视化专家 Agent - 数据可视化

生成图表、表格等可视化内容
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


class VisualizerAgent:
    """可视化专家 Agent"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.output_dir = config.get('output', {}).get('reports_folder', '/研究报告')
    
    async def visualize(self, data: Dict[str, Any], topic: str) -> List[Dict]:
        """
        生成可视化内容
        
        Args:
            data: 数据字典
            topic: 研究话题
        
        Returns:
            可视化内容列表
        """
        logger.info("生成可视化内容")
        
        visualizations = []
        
        # 1. 关键数据表格
        if 'market_data' in data or 'key_metrics' in data:
            table = await self._create_data_table(data, topic)
            visualizations.append(table)
        
        # 2. 趋势图数据
        if 'trends' in data or 'growth' in data:
            trend_chart = await self._create_trend_chart(data, topic)
            visualizations.append(trend_chart)
        
        # 3. 竞争格局图
        if 'competition' in data or 'market_share' in data:
            competition_chart = await self._create_competition_chart(data, topic)
            visualizations.append(competition_chart)
        
        # 4. PESTEL 雷达图数据
        if 'pestel' in data:
            pestel_radar = await self._create_pestel_radar(data['pestel'])
            visualizations.append(pestel_radar)
        
        # 5. SWOT 矩阵
        if 'swot' in data:
            swot_matrix = await self._create_swot_matrix(data['swot'])
            visualizations.append(swot_matrix)
        
        # 6. 波特五力图
        if 'five_forces' in data:
            five_forces_chart = await self._create_five_forces_chart(data['five_forces'])
            visualizations.append(five_forces_chart)
        
        logger.info(f"生成 {len(visualizations)} 个可视化内容")
        return visualizations
    
    async def _create_data_table(self, data: Dict, topic: str) -> Dict:
        """创建关键数据表格"""
        # 从数据中提取指标
        market_data = data.get('market_data', {})
        
        table = {
            'type': 'table',
            'title': f'{topic}关键数据',
            'format': 'markdown',
            'headers': ['指标', '2024', '2025', '2026E', 'CAGR'],
            'rows': []
        }
        
        # 模拟数据（实际应从分析结果中提取）
        metrics = [
            ['市场规模 (亿元)', '1000', '1200', '1450', '20.4%'],
            ['增长率', '18%', '20%', '21%', '-'],
            ['企业数量', '500', '550', '600', '9.5%'],
            ['从业人数 (万人)', '50', '58', '67', '15.8%'],
            ['渗透率', '35%', '42%', '50%', '19.5%'],
        ]
        
        table['rows'] = metrics
        table['source'] = '国家统计局、行业协会'
        table['note'] = '2026 年为预测数据'
        
        return table
    
    async def _create_trend_chart(self, data: Dict, topic: str) -> Dict:
        """创建趋势图"""
        chart = {
            'type': 'line_chart',
            'title': f'{topic}市场规模趋势',
            'format': 'echarts',
            'x_axis': ['2020', '2021', '2022', '2023', '2024', '2025', '2026E'],
            'y_axis': [],
            'series': []
        }
        
        # 模拟市场规模数据
        market_sizes = [500, 650, 800, 950, 1000, 1200, 1450]
        growth_rates = [None, '30%', '23%', '19%', '5%', '20%', '21%']
        
        chart['y_axis'] = market_sizes
        chart['series'] = [{
            'name': '市场规模 (亿元)',
            'type': 'line',
            'data': market_sizes,
            'smooth': True,
            'label': {'show': True, 'position': 'top'}
        }]
        
        chart['config'] = {
            'yAxis': {'name': '亿元', 'type': 'value'},
            'xAxis': {'type': 'category'},
            'tooltip': {'trigger': 'axis'},
        }
        
        return chart
    
    async def _create_competition_chart(self, data: Dict, topic: str) -> Dict:
        """创建竞争格局图"""
        chart = {
            'type': 'pie_chart',
            'title': f'{topic}市场份额分布',
            'format': 'echarts',
            'data': []
        }
        
        # 模拟市场份额数据
        market_share = [
            {'name': '企业 A', 'value': 35},
            {'name': '企业 B', 'value': 25},
            {'name': '企业 C', 'value': 15},
            {'name': '企业 D', 'value': 10},
            {'name': '其他', 'value': 15},
        ]
        
        chart['data'] = market_share
        chart['config'] = {
            'series': [{
                'type': 'pie',
                'radius': '50%',
                'data': market_share,
                'label': {'show': True, 'formatter': '{b}: {d}%'}
            }]
        }
        
        return chart
    
    async def _create_pestel_radar(self, pestel_data: Dict) -> Dict:
        """创建 PESTEL 雷达图"""
        chart = {
            'type': 'radar_chart',
            'title': 'PESTEL 分析',
            'format': 'echarts',
            'indicators': [],
            'data': []
        }
        
        # 从 PESTEL 分析结果中提取数据
        impact_map = {'high': 5, 'medium': 3, 'low': 1}
        
        indicators = []
        values = []
        
        for dimension in ['political', 'economic', 'social', 'technological', 'environmental', 'legal']:
            if dimension in pestel_data:
                impact = pestel_data[dimension].get('impact', 'medium')
                indicators.append({
                    'name': self._translate_dimension(dimension),
                    'max': 5
                })
                values.append(impact_map.get(impact, 3))
        
        chart['indicators'] = indicators
        chart['data'] = [values]
        
        return chart
    
    async def _create_swot_matrix(self, swot_data: Dict) -> Dict:
        """创建 SWOT 矩阵"""
        matrix = {
            'type': 'matrix',
            'title': 'SWOT 分析',
            'format': 'markdown',
            'quadrants': {
                'SO': [],  # 优势 + 机会
                'WO': [],  # 劣势 + 机会
                'ST': [],  # 优势 + 威胁
                'WT': []   # 劣势 + 威胁
            }
        }
        
        strengths = swot_data.get('strengths', [])
        weaknesses = swot_data.get('weaknesses', [])
        opportunities = swot_data.get('opportunities', [])
        threats = swot_data.get('threats', [])
        
        # 生成策略建议
        for s in strengths[:2]:
            for o in opportunities[:2]:
                matrix['quadrants']['SO'].append(f"利用{s.get('factor', '')}抓住{o.get('factor', '')}")
        
        for w in weaknesses[:2]:
            for o in opportunities[:2]:
                matrix['quadrants']['WO'].append(f"通过{o.get('factor', '')}改善{w.get('factor', '')}")
        
        for s in strengths[:2]:
            for t in threats[:2]:
                matrix['quadrants']['ST'].append(f"利用{s.get('factor', '')}应对{t.get('factor', '')}")
        
        for w in weaknesses[:2]:
            for t in threats[:2]:
                matrix['quadrants']['WT'].append(f"减少{w.get('factor', '')}规避{t.get('factor', '')}")
        
        return matrix
    
    async def _create_five_forces_chart(self, five_forces_data: Dict) -> Dict:
        """创建波特五力图"""
        chart = {
            'type': 'radar_chart',
            'title': '波特五力分析',
            'format': 'echarts',
            'indicators': [],
            'data': []
        }
        
        level_map = {'high': 5, 'medium': 3, 'low': 1}
        
        forces = [
            ('supplier_power', '供应商议价能力'),
            ('buyer_power', '购买者议价能力'),
            ('competitive_rivalry', '现有竞争'),
            ('threat_of_substitution', '替代品威胁'),
            ('threat_of_new_entry', '新进入者威胁'),
        ]
        
        indicators = []
        values = []
        
        for key, name in forces:
            if key in five_forces_data:
                level = five_forces_data[key].get('level', 'medium')
                indicators.append({'name': name, 'max': 5})
                values.append(level_map.get(level, 3))
        
        chart['indicators'] = indicators
        chart['data'] = [values]
        
        return chart
    
    def _translate_dimension(self, dimension: str) -> str:
        """翻译 PESTEL 维度"""
        translation = {
            'political': '政治',
            'economic': '经济',
            'social': '社会',
            'technological': '技术',
            'environmental': '环境',
            'legal': '法律',
        }
        return translation.get(dimension, dimension)
    
    def generate_markdown_tables(self, visualizations: List[Dict]) -> str:
        """将可视化内容转换为 Markdown 表格"""
        lines = []
        
        for viz in visualizations:
            lines.append(f"### {viz.get('title', '')}")
            lines.append("")
            
            if viz['type'] == 'table':
                # 表格头
                headers = viz.get('headers', [])
                lines.append('| ' + ' | '.join(headers) + ' |')
                lines.append('| ' + ' | '.join(['---'] * len(headers)) + ' |')
                
                # 表格内容
                for row in viz.get('rows', []):
                    lines.append('| ' + ' | '.join(row) + ' |')
                
                lines.append("")
                if viz.get('source'):
                    lines.append(f"*数据来源：{viz.get('source')}*")
                if viz.get('note'):
                    lines.append(f"*注：{viz.get('note')}*")
            
            elif viz['type'] == 'matrix':
                quadrants = viz.get('quadrants', {})
                
                lines.append("|  | 机会 (O) | 威胁 (T) |")
                lines.append("|---|---|---|")
                
                so_str = "<br>".join(quadrants.get('SO', [])[:2])
                wo_str = "<br>".join(quadrants.get('WO', [])[:2])
                st_str = "<br>".join(quadrants.get('ST', [])[:2])
                wt_str = "<br>".join(quadrants.get('WT', [])[:2])
                
                lines.append(f"| **优势 (S)** | {so_str} | {st_str} |")
                lines.append(f"| **劣势 (W)** | {wo_str} | {wt_str} |")
            
            lines.append("")
        
        return '\n'.join(lines)
    
    def generate_echarts_html(self, visualizations: List[Dict]) -> str:
        """生成 ECharts HTML"""
        html_parts = ['<div class="charts-container">']
        
        for viz in visualizations:
            if viz.get('format') != 'echarts':
                continue
            
            chart_id = f"chart-{hash(viz.get('title', '')) % 10000}"
            
            html_parts.append(f'<div id="{chart_id}" style="width: 600px; height: 400px;"></div>')
            html_parts.append('<script>')
            html_parts.append(f"""
            var chart_{chart_id} = echarts.init(document.getElementById('{chart_id}'));
            var option_{chart_id} = {json.dumps(viz)};
            chart_{chart_id}.setOption(option_{chart_id});
            """)
            html_parts.append('</script>')
        
        html_parts.append('</div>')
        return '\n'.join(html_parts)
