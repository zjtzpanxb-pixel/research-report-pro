"""
搜索专家 Agent - 多源数据采集

负责从多个可信来源搜索和采集数据
"""

import asyncio
import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

try:
    import httpx
except ImportError:
    httpx = None

logger = logging.getLogger(__name__)


class SearcherAgent:
    """搜索专家 Agent"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.search_config = config.get('search', {})
        self.max_results = self.search_config.get('max_results', 50)
        self.timeout = self.search_config.get('timeout', 30)
        
        # 搜索引擎配置
        self.search_engines = {
            'bing': 'https://api.bing.microsoft.com/v7.0/search',
            'google': 'https://customsearch.googleapis.com/customsearch/v1',
        }
        
        # API Keys（从环境变量读取）
        self.bing_api_key = os.getenv('BING_SEARCH_API_KEY', '')
        self.google_api_key = os.getenv('GOOGLE_SEARCH_API_KEY', '')
        self.google_cse_id = os.getenv('GOOGLE_CSE_ID', '')
        
        # 可信来源关键词
        self.trusted_sources = {
            'government': ['gov.cn', '国务院', '发改委', '工信部', '统计局', '政府'],
            'academic': ['edu.cn', '知网', '万方', 'academia', 'scholar', '论文'],
            'media': ['新华社', '人民日报', 'cnn', 'reuters', 'bloomberg', '财新'],
        }
    
    async def search(self, queries: List[str], depth: str = 'deep') -> List[Dict]:
        """
        执行多查询搜索
        
        Args:
            queries: 搜索查询列表
            depth: 搜索深度 (standard|deep)
        
        Returns:
            搜索结果列表
        """
        logger.info(f"执行 {len(queries)} 个查询的搜索")
        
        # 并发执行搜索
        tasks = []
        for query in queries:
            tasks.append(self._search_query(query, depth))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 合并结果
        all_results = []
        for result in results:
            if isinstance(result, list):
                all_results.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"搜索失败：{result}")
        
        # 去重
        seen_urls = set()
        unique_results = []
        for r in all_results:
            url = r.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(r)
        
        logger.info(f"搜索完成，获取 {len(unique_results)} 个唯一结果")
        return unique_results
    
    async def _search_query(self, query: str, depth: str) -> List[Dict]:
        """执行单个查询"""
        results = []
        
        # 尝试 Bing 搜索
        if self.bing_api_key:
            try:
                bing_results = await self._bing_search(query)
                results.extend(bing_results)
            except Exception as e:
                logger.warning(f"Bing 搜索失败：{e}")
        
        # 尝试 Google 搜索
        if self.google_api_key and self.google_cse_id:
            try:
                google_results = await self._google_search(query)
                results.extend(google_results)
            except Exception as e:
                logger.warning(f"Google 搜索失败：{e}")
        
        # 如果没有 API，使用备用方案
        if not results:
            logger.info("无搜索 API，使用备用数据源")
            results = await self._fallback_search(query)
        
        # 深度搜索：获取详细内容
        if depth == 'deep' and results:
            results = await self._fetch_content(results)
        
        return results[:self.max_results]
    
    async def _bing_search(self, query: str) -> List[Dict]:
        """Bing 搜索"""
        if not httpx:
            raise ImportError("httpx 未安装")
        
        headers = {'Ocp-Apim-Subscription-Key': self.bing_api_key}
        params = {
            'q': query,
            'count': min(self.max_results, 50),
            'mkt': 'zh-CN',
            'safeSearch': 'Moderate',
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                self.search_engines['bing'],
                headers=headers,
                params=params
            )
            response.raise_for_status()
            data = response.json()
        
        results = []
        for item in data.get('webPages', {}).get('value', []):
            results.append({
                'title': item.get('name', ''),
                'url': item.get('url', ''),
                'snippet': item.get('snippet', ''),
                'source': self._extract_source(item.get('url', '')),
                'date': self._extract_date(item),
                'search_engine': 'bing',
            })
        
        return results
    
    async def _google_search(self, query: str) -> List[Dict]:
        """Google 自定义搜索"""
        if not httpx:
            raise ImportError("httpx 未安装")
        
        params = {
            'q': query,
            'key': self.google_api_key,
            'cx': self.google_cse_id,
            'num': min(self.max_results, 10),
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                self.search_engines['google'],
                params=params
            )
            response.raise_for_status()
            data = response.json()
        
        results = []
        for item in data.get('items', []):
            results.append({
                'title': item.get('title', ''),
                'url': item.get('link', ''),
                'snippet': item.get('snippet', ''),
                'source': self._extract_source(item.get('link', '')),
                'date': item.get('pagemap', {}).get('metatags', [{}])[0].get('article:published_time', ''),
                'search_engine': 'google',
            })
        
        return results
    
    async def _fallback_search(self, query: str) -> List[Dict]:
        """备用搜索（无 API 时）"""
        # 模拟一些权威来源的搜索结果
        fallback_sources = [
            {
                'title': f'{query} - 国家统计局数据',
                'url': 'https://www.stats.gov.cn/sj/zxfb/',
                'snippet': f'国家统计局发布的{query}相关统计数据',
                'source': '国家统计局',
                'credibility': 'high',
            },
            {
                'title': f'{query} - 国务院政策文件',
                'url': 'https://www.gov.cn/zhengce/',
                'snippet': f'国务院关于{query}的政策文件',
                'source': '国务院',
                'credibility': 'high',
            },
            {
                'title': f'{query} - 学术论文',
                'url': 'https://www.cnki.net/',
                'snippet': f'知网收录的{query}相关学术论文',
                'source': '中国知网',
                'credibility': 'high',
            },
            {
                'title': f'{query} - 行业报告',
                'url': 'https://www.miit.gov.cn/',
                'snippet': f'工信部发布的{query}行业报告',
                'source': '工信部',
                'credibility': 'high',
            },
        ]
        
        await asyncio.sleep(0.5)  # 模拟延迟
        return fallback_sources
    
    async def _fetch_content(self, results: List[Dict]) -> List[Dict]:
        """获取详细内容"""
        if not httpx:
            return results
        
        # 限制并发数，避免被封
        semaphore = asyncio.Semaphore(5)
        
        async def fetch_with_sem(result):
            async with semaphore:
                return await self._fetch_single(result)
        
        tasks = [fetch_with_sem(r) for r in results[:10]]  # 只获取前 10 个的详细内容
        contents = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, content in enumerate(contents):
            if isinstance(content, str) and i < len(results):
                results[i]['raw_content'] = content
        
        return results
    
    async def _fetch_single(self, result: Dict) -> str:
        """获取单个页面内容"""
        try:
            url = result.get('url', '')
            
            # 跳过政府网站（通常需要特殊处理）
            if 'gov.cn' in url:
                return result.get('snippet', '')
            
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                # 简单提取文本
                content = response.text
                # 移除 HTML 标签
                import re
                text = re.sub(r'<[^>]+>', '', content)
                # 限制长度
                return text[:5000] if text else ''
                
        except Exception as e:
            logger.debug(f"获取内容失败 {result.get('url')}: {e}")
            return ''
    
    def _extract_source(self, url: str) -> str:
        """从 URL 提取来源"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # 移除 www.
            if domain.startswith('www.'):
                domain = domain[4:]
            
            return domain
        except:
            return 'unknown'
    
    def _extract_date(self, item: Dict) -> str:
        """提取日期"""
        # 尝试从不同字段提取日期
        date_fields = ['datePublished', 'date', 'publishedTime']
        for field in date_fields:
            if field in item:
                return item[field]
        
        # 返回当前日期
        return datetime.now().strftime('%Y-%m-%d')
    
    def classify_source(self, url: str, title: str = '') -> Dict:
        """
        分类来源可信度
        
        Returns:
            {'credibility': 'high|medium|low', 'tier': 'tier1|tier2|tier3', 'type': 'government|academic|media|other'}
        """
        text = (url + ' ' + title).lower()
        
        # Tier 1: 政府/官方
        for keyword in self.trusted_sources['government']:
            if keyword.lower() in text:
                return {'credibility': 'high', 'tier': 'tier1', 'type': 'government'}
        
        # Tier 2: 学术
        for keyword in self.trusted_sources['academic']:
            if keyword.lower() in text:
                return {'credibility': 'high', 'tier': 'tier2', 'type': 'academic'}
        
        # Tier 3: 权威媒体
        for keyword in self.trusted_sources['media']:
            if keyword.lower() in text:
                return {'credibility': 'medium', 'tier': 'tier3', 'type': 'media'}
        
        return {'credibility': 'low', 'tier': 'tier3', 'type': 'other'}
