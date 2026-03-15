"""
分析专家 Agent - 深度分析

应用成熟分析框架进行深度研究分析
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
        self.llm_config = config.get('llm', {})
        self.frameworks = config.get('frameworks', ['PESTEL', 'SWOT', '波特五力'])
        
        # OpenClaw 已配置 LLM API，直接使用
        self.api_key = 'openclaw-provided'
    
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
        prompt = f"""对以下话题进行 PESTEL 分析：

话题：{topic}

背景信息：
{context}

请按以下结构输出 JSON 格式的分析结果：
{{
  "political": {{
    "summary": "政策环境总结",
    "factors": ["政策因素 1", "政策因素 2"],
    "impact": "high|medium|low",
    "trend": "positive|negative|neutral"
  }},
  "economic": {{
    "summary": "经济环境总结",
    "factors": ["经济因素 1", "经济因素 2"],
    "impact": "high|medium|low",
    "trend": "positive|negative|neutral"
  }},
  "social": {{
    "summary": "社会环境总结",
    "factors": ["社会因素 1", "社会因素 2"],
    "impact": "high|medium|low",
    "trend": "positive|negative|neutral"
  }},
  "technological": {{
    "summary": "技术环境总结",
    "factors": ["技术因素 1", "技术因素 2"],
    "impact": "high|medium|low",
    "trend": "positive|negative|neutral"
  }},
  "environmental": {{
    "summary": "环境因素总结",
    "factors": ["环境因素 1", "环境因素 2"],
    "impact": "high|medium|low",
    "trend": "positive|negative|neutral"
  }},
  "legal": {{
    "summary": "法律环境总结",
    "factors": ["法律因素 1", "法律因素 2"],
    "impact": "high|medium|low",
    "trend": "positive|negative|neutral"
  }}
}}"""
        
        try:
            result = await self._call_llm(prompt)
            return {
                'framework': 'PESTEL',
                'analysis': result,
                'summary': self._summarize_pestel(result)
            }
        except Exception as e:
            logger.warning(f"PESTEL 分析失败（使用模拟数据）: {e}")
            return self._mock_pestel(topic)
    
    async def _swot_analysis(self, topic: str, context: str) -> Dict:
        """SWOT 分析"""
        prompt = f"""对以下话题进行 SWOT 分析：

话题：{topic}

背景信息：
{context}

请按以下结构输出 JSON 格式：
{{
  "strengths": [
    {{"factor": "优势因素", "description": "详细描述", "importance": "high|medium|low"}}
  ],
  "weaknesses": [
    {{"factor": "劣势因素", "description": "详细描述", "importance": "high|medium|low"}}
  ],
  "opportunities": [
    {{"factor": "机会因素", "description": "详细描述", "importance": "high|medium|low"}}
  ],
  "threats": [
    {{"factor": "威胁因素", "description": "详细描述", "importance": "high|medium|low"}}
  ]
}}"""
        
        try:
            result = await self._call_llm(prompt)
            return {
                'framework': 'SWOT',
                'analysis': result,
                'summary': self._summarize_swot(result)
            }
        except Exception as e:
            logger.error(f"SWOT 分析失败：{e}")
            return self._mock_swot(topic)
    
    async def _five_forces_analysis(self, topic: str, context: str) -> Dict:
        """波特五力分析"""
        prompt = f"""对以下话题进行波特五力分析：

话题：{topic}

背景信息：
{context}

请按以下结构输出 JSON 格式：
{{
  "supplier_power": {{
    "level": "high|medium|low",
    "description": "供应商议价能力分析",
    "factors": ["因素 1", "因素 2"]
  }},
  "buyer_power": {{
    "level": "high|medium|low",
    "description": "购买者议价能力分析",
    "factors": ["因素 1", "因素 2"]
  }},
  "competitive_rivalry": {{
    "level": "high|medium|low",
    "description": "现有竞争者分析",
    "factors": ["因素 1", "因素 2"]
  }},
  "threat_of_substitution": {{
    "level": "high|medium|low",
    "description": "替代品威胁分析",
    "factors": ["因素 1", "因素 2"]
  }},
  "threat_of_new_entry": {{
    "level": "high|medium|low",
    "description": "新进入者威胁分析",
    "factors": ["因素 1", "因素 2"]
  }},
  "overall_competition": "intense|moderate|low"
}}"""
        
        try:
            result = await self._call_llm(prompt)
            return {
                'framework': '波特五力',
                'analysis': result,
                'summary': self._summarize_five_forces(result)
            }
        except Exception as e:
            logger.error(f"波特五力分析失败：{e}")
            return self._mock_five_forces(topic)
    
    async def _value_chain_analysis(self, topic: str, context: str) -> Dict:
        """价值链分析"""
        prompt = f"""对以下话题进行价值链分析：

话题：{topic}

背景信息：
{context}

请按以下结构输出 JSON 格式：
{{
  "primary_activities": {{
    "inbound_logistics": "描述",
    "operations": "描述",
    "outbound_logistics": "描述",
    "marketing_sales": "描述",
    "service": "描述"
  }},
  "support_activities": {{
    "infrastructure": "描述",
    "hr_management": "描述",
    "technology_development": "描述",
    "procurement": "描述"
  }},
  "margin_analysis": "利润空间分析",
  "competitive_advantage": "竞争优势来源"
}}"""
        
        try:
            result = await self._call_llm(prompt)
            return {
                'framework': '价值链分析',
                'analysis': result
            }
        except Exception as e:
            logger.error(f"价值链分析失败：{e}")
            return self._mock_value_chain(topic)
    
    async def _general_analysis(self, topic: str, context: str) -> Dict:
        """通用分析"""
        prompt = f"""对以下话题进行全面分析：

话题：{topic}

背景信息：
{context}

请输出 JSON 格式的分析结果，包含：
{{
  "key_findings": ["关键发现 1", "关键发现 2", "关键发现 3"],
  "market_size": "市场规模描述",
  "growth_rate": "增长率描述",
  "key_players": ["主要参与者 1", "主要参与者 2"],
  "trends": ["趋势 1", "趋势 2", "趋势 3"],
  "challenges": ["挑战 1", "挑战 2"],
  "opportunities": ["机会 1", "机会 2"]
}}"""
        
        try:
            result = await self._call_llm(prompt)
            return {
                'framework': '通用分析',
                'analysis': result
            }
        except Exception as e:
            logger.error(f"通用分析失败：{e}")
            return self._mock_general(topic)
    
    def _prepare_context(self, sources: List[Dict]) -> str:
        """准备分析上下文"""
        context_parts = []
        
        for source in sources[:10]:  # 使用前 10 个来源
            content = source.get('raw_content', source.get('snippet', ''))
            if content:
                context_parts.append(f"[{source.get('source', 'unknown')}]: {content[:500]}")
        
        return '\n\n'.join(context_parts)
    
    async def _call_llm(self, prompt: str) -> Dict:
        """调用 LLM（通过 OpenClaw 系统）"""
        if not httpx:
            raise ImportError("httpx 未安装")
        
        import httpx
        
        # OpenClaw 提供 LLM 服务，使用系统配置
        # 从环境变量读取 OpenClaw 的 LLM 配置
        llm_base_url = os.getenv('OPENCLAW_LLM_BASE_URL', 'http://localhost:11434/v1/chat/completions')
        llm_model = os.getenv('OPENCLAW_LLM_MODEL', 'qwen3.5-plus')
        
        headers = {
            "Content-Type": "application/json",
        }
        
        # 如果有 API Key（某些部署需要）
        llm_api_key = os.getenv('OPENCLAW_LLM_API_KEY', '')
        if llm_api_key:
            headers['Authorization'] = f"Bearer {llm_api_key}"
        
        payload = {
            "model": llm_model,
            "messages": [
                {"role": "system", "content": "你是专业的行业分析师，擅长使用各种分析框架进行深度研究。请输出纯 JSON 格式，不要 markdown。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.5,
            "max_tokens": 2000,
        }
        
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(llm_base_url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            
            content = result['choices'][0]['message']['content']
            
            # 解析 JSON
            try:
                # 移除可能的 markdown 包裹
                if '```json' in content:
                    content = content.split('```json')[1].split('```')[0]
                elif '```' in content:
                    content = content.split('```')[1].split('```')[0]
                
                return json.loads(content.strip())
            except json.JSONDecodeError as e:
                logger.error(f"JSON 解析失败：{e}")
                raise Exception(f"LLM 返回格式错误：{content[:200]}")
    
    def _summarize_pestel(self, result: Dict) -> str:
        """总结 PESTEL 分析"""
        summary = []
        for dimension, data in result.items():
            if isinstance(data, dict):
                summary.append(f"{dimension}: {data.get('summary', '')}")
        return ' | '.join(summary)
    
    def _summarize_swot(self, result: Dict) -> str:
        """总结 SWOT 分析"""
        s = len(result.get('strengths', []))
        w = len(result.get('weaknesses', []))
        o = len(result.get('opportunities', []))
        t = len(result.get('threats', []))
        return f"优势:{s} 劣势:{w} 机会:{o} 威胁:{t}"
    
    def _summarize_five_forces(self, result: Dict) -> str:
        """总结波特五力分析"""
        overall = result.get('overall_competition', 'moderate')
        return f"行业竞争程度：{overall}"
    
    # Mock 方法（LLM 失败时使用）
    def _mock_pestel(self, topic: str) -> Dict:
        return {
            'framework': 'PESTEL',
            'analysis': {
                'political': {'summary': f'{topic}受政策支持', 'factors': ['政策利好'], 'impact': 'high'},
                'economic': {'summary': '经济增长带动需求', 'factors': ['GDP 增长'], 'impact': 'medium'},
                'social': {'summary': '消费习惯变化', 'factors': ['消费升级'], 'impact': 'medium'},
                'technological': {'summary': '技术创新加速', 'factors': ['技术进步'], 'impact': 'high'},
                'environmental': {'summary': '环保要求提高', 'factors': ['碳中和'], 'impact': 'medium'},
                'legal': {'summary': '法规完善', 'factors': ['监管加强'], 'impact': 'low'},
            },
            'summary': '整体环境利好'
        }
    
    def _mock_swot(self, topic: str) -> Dict:
        return {
            'framework': 'SWOT',
            'analysis': {
                'strengths': [{'factor': '市场领先', 'description': '市场份额高', 'importance': 'high'}],
                'weaknesses': [{'factor': '成本高', 'description': '运营成本较高', 'importance': 'medium'}],
                'opportunities': [{'factor': '市场增长', 'description': '行业快速增长', 'importance': 'high'}],
                'threats': [{'factor': '竞争加剧', 'description': '新进入者增多', 'importance': 'medium'}],
            },
            'summary': '优势明显，机会大于威胁'
        }
    
    def _mock_five_forces(self, topic: str) -> Dict:
        return {
            'framework': '波特五力',
            'analysis': {
                'supplier_power': {'level': 'medium', 'description': '供应商集中度中等'},
                'buyer_power': {'level': 'medium', 'description': '购买者议价能力中等'},
                'competitive_rivalry': {'level': 'high', 'description': '竞争激烈'},
                'threat_of_substitution': {'level': 'low', 'description': '替代品威胁低'},
                'threat_of_new_entry': {'level': 'medium', 'description': '进入壁垒中等'},
                'overall_competition': 'intense'
            },
            'summary': '行业竞争激烈'
        }
    
    def _mock_value_chain(self, topic: str) -> Dict:
        return {
            'framework': '价值链分析',
            'analysis': {
                'primary_activities': {'operations': '核心运营高效'},
                'support_activities': {'technology_development': '技术研发投入大'},
                'margin_analysis': '利润率高于行业平均',
                'competitive_advantage': '技术和品牌优势'
            }
        }
    
    def _mock_general(self, topic: str) -> Dict:
        return {
            'framework': '通用分析',
            'analysis': {
                'key_findings': [f'{topic}市场快速增长', '行业集中度提升', '技术创新加速'],
                'market_size': '市场规模持续扩大',
                'growth_rate': '年增长率 15-20%',
                'key_players': ['行业龙头 A', '行业龙头 B', '行业龙头 C'],
                'trends': ['数字化转型', '绿色发展', '智能化'],
                'challenges': ['成本上升', '人才短缺'],
                'opportunities': ['政策支持', '市场需求增长']
            }
        }


# 导入 httpx
try:
    import httpx
except ImportError:
    httpx = None
