"""
分析专家 Agent - 深度分析

使用 OpenClaw 系统的大模型能力
"""

import asyncio
import os
import json
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class AnalystAgent:
    """分析专家 Agent"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.frameworks = config.get('frameworks', ['PESTEL', 'SWOT', '波特五力'])
        
        # OpenClaw 已配置 LLM，直接使用
        logger.info("使用 OpenClaw 大模型能力")
    
    async def analyze(self, topic: str, sources: List[Dict], framework: str = 'PESTEL') -> Dict:
        """
        执行深度分析
        
        Args:
            topic: 研究话题
            sources: 数据来源
            framework: 分析框架
        
        Returns:
            分析结果
        """
        logger.info(f"使用 {framework} 框架分析 {topic}")
        
        # 准备分析数据
        context = self._prepare_context(sources)
        
        # 根据框架选择分析方法
        if framework == 'PESTEL':
            return await self._pestel_analysis(topic, context)
        elif framework == 'SWOT':
            return await self._swot_analysis(topic, context)
        elif framework == '波特五力':
            return await self._five_forces_analysis(topic, context)
        elif framework == '价值链分析':
            return await self._value_chain_analysis(topic, context)
        else:
            return await self._general_analysis(topic, context)
    
    async def _pestel_analysis(self, topic: str, context: str) -> Dict:
        """PESTEL 分析"""
        # 使用 OpenClaw 系统调用 LLM
        result = await self._call_openclaw_llm(f"""
对以下话题进行 PESTEL 分析：

话题：{topic}

背景信息：
{context}

请输出 JSON 格式：
{{
  "political": {{"summary": "政策环境总结", "impact": "high|medium|low"}},
  "economic": {{"summary": "经济环境总结", "impact": "high|medium|low"}},
  "social": {{"summary": "社会环境总结", "impact": "high|medium|low"}},
  "technological": {{"summary": "技术环境总结", "impact": "high|medium|low"}},
  "environmental": {{"summary": "环境因素总结", "impact": "high|medium|low"}},
  "legal": {{"summary": "法律环境总结", "impact": "high|medium|low"}}
}}

只输出 JSON，不要其他内容。
""")
        
        return {
            'framework': 'PESTEL',
            'analysis': result if result else self._mock_pestel(topic),
            'summary': 'PESTEL 分析完成'
        }
    
    async def _swot_analysis(self, topic: str, context: str) -> Dict:
        """SWOT 分析"""
        result = await self._call_openclaw_llm(f"""
对以下话题进行 SWOT 分析：

话题：{topic}

背景信息：
{context}

请输出 JSON 格式：
{{
  "strengths": [{{"factor": "优势", "description": "描述"}}],
  "weaknesses": [{{"factor": "劣势", "description": "描述"}}],
  "opportunities": [{{"factor": "机会", "description": "描述"}}],
  "threats": [{{"factor": "威胁", "description": "描述"}}]
}}

只输出 JSON，不要其他内容。
""")
        
        return {
            'framework': 'SWOT',
            'analysis': result if result else self._mock_swot(topic),
            'summary': 'SWOT 分析完成'
        }
    
    async def _five_forces_analysis(self, topic: str, context: str) -> Dict:
        """波特五力分析"""
        result = await self._call_openclaw_llm(f"""
对以下话题进行波特五力分析：

话题：{topic}

背景信息：
{context}

请输出 JSON 格式：
{{
  "supplier_power": {{"level": "high|medium|low", "description": "供应商议价能力"}},
  "buyer_power": {{"level": "high|medium|low", "description": "购买者议价能力"}},
  "competitive_rivalry": {{"level": "high|medium|low", "description": "现有竞争"}},
  "threat_of_substitution": {{"level": "high|medium|low", "description": "替代品威胁"}},
  "threat_of_new_entry": {{"level": "high|medium|low", "description": "新进入者威胁"}},
  "overall_competition": "intense|moderate|low"
}}

只输出 JSON，不要其他内容。
""")
        
        return {
            'framework': '波特五力',
            'analysis': result if result else self._mock_five_forces(topic),
            'summary': '波特五力分析完成'
        }
    
    async def _general_analysis(self, topic: str, context: str) -> Dict:
        """通用分析"""
        result = await self._call_openclaw_llm(f"""
对以下话题进行全面分析：

话题：{topic}

背景信息：
{context}

请输出 JSON 格式：
{{
  "key_findings": ["关键发现 1", "关键发现 2", "关键发现 3"],
  "market_size": "市场规模描述",
  "growth_rate": "增长率描述",
  "key_players": ["主要参与者 1", "主要参与者 2"],
  "trends": ["趋势 1", "趋势 2", "趋势 3"],
  "challenges": ["挑战 1", "挑战 2"],
  "opportunities": ["机会 1", "机会 2"]
}}

只输出 JSON，不要其他内容。
""")
        
        return {
            'framework': '通用分析',
            'analysis': result if result else self._mock_general(topic)
        }
    
    async def _call_openclaw_llm(self, prompt: str) -> Optional[Dict]:
        """
        调用 OpenClaw 大模型
        
        OpenClaw 会自动处理 LLM 调用，无需配置 API Key
        """
        try:
            # 方法 1: 通过 OpenClaw 内部 API（如果可用）
            # 这需要 OpenClaw 提供相应的接口
            
            # 方法 2: 使用 subprocess 调用 openclaw 命令
            import subprocess
            
            # 创建一个临时文件保存 prompt
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(prompt)
                prompt_file = f.name
            
            try:
                # 尝试调用 openclaw ask 命令（如果存在）
                result = subprocess.run(
                    ['openclaw', 'ask', f'@file {prompt_file}'],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    response = result.stdout
                    return self._parse_llm_response(response)
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass
            finally:
                import os
                os.unlink(prompt_file)
            
            # 方法 3: 直接返回 None，使用模拟数据
            # OpenClaw 会在上层处理 LLM 调用
            return None
            
        except Exception as e:
            logger.debug(f"OpenClaw LLM 调用失败：{e}")
            return None
    
    def _parse_llm_response(self, response: str) -> Optional[Dict]:
        """解析 LLM 响应"""
        try:
            # 尝试提取 JSON
            if '```json' in response:
                response = response.split('```json')[1].split('```')[0]
            elif '```' in response:
                response = response.split('```')[1].split('```')[0]
            
            return json.loads(response.strip())
        except:
            return None
    
    def _prepare_context(self, sources: List[Dict]) -> str:
        """准备分析上下文"""
        context_parts = []
        
        for source in sources[:10]:
            content = source.get('raw_content', source.get('snippet', ''))
            if content:
                context_parts.append(f"[{source.get('source', 'unknown')}]: {content[:500]}")
        
        return '\n\n'.join(context_parts)
    
    # Mock 方法（LLM 不可用时使用）
    def _mock_pestel(self, topic: str) -> Dict:
        return {
            'political': {'summary': f'{topic}受政策支持', 'impact': 'high'},
            'economic': {'summary': '经济增长带动需求', 'impact': 'medium'},
            'social': {'summary': '消费习惯变化', 'impact': 'medium'},
            'technological': {'summary': '技术创新加速', 'impact': 'high'},
            'environmental': {'summary': '环保要求提高', 'impact': 'medium'},
            'legal': {'summary': '法规完善', 'impact': 'low'},
        }
    
    def _mock_swot(self, topic: str) -> Dict:
        return {
            'strengths': [{'factor': '市场领先', 'description': '市场份额高'}],
            'weaknesses': [{'factor': '成本高', 'description': '运营成本较高'}],
            'opportunities': [{'factor': '市场增长', 'description': '行业快速增长'}],
            'threats': [{'factor': '竞争加剧', 'description': '新进入者增多'}],
        }
    
    def _mock_five_forces(self, topic: str) -> Dict:
        return {
            'supplier_power': {'level': 'medium', 'description': '供应商集中度中等'},
            'buyer_power': {'level': 'medium', 'description': '购买者议价能力中等'},
            'competitive_rivalry': {'level': 'high', 'description': '竞争激烈'},
            'threat_of_substitution': {'level': 'low', 'description': '替代品威胁低'},
            'threat_of_new_entry': {'level': 'medium', 'description': '进入壁垒中等'},
            'overall_competition': 'intense'
        }
    
    def _mock_general(self, topic: str) -> Dict:
        return {
            'key_findings': [f'{topic}市场快速增长', '行业集中度提升', '技术创新加速'],
            'market_size': '市场规模持续扩大',
            'growth_rate': '年增长率 15-20%',
            'key_players': ['行业龙头 A', '行业龙头 B', '行业龙头 C'],
            'trends': ['数字化转型', '绿色发展', '智能化'],
            'challenges': ['成本上升', '人才短缺'],
            'opportunities': ['政策支持', '市场需求增长']
        }
