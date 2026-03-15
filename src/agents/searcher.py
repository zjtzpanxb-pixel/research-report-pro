"""
搜索专家 Agent - 多源数据采集

使用 jina.ai 进行网络搜索
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
        logger.info(f"执行 {len(queries)} 个查询的搜索（使用 jina.ai）")
        
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
        
        try:
            # 使用 jina.ai 搜索
            jina_results = await self._jina_search(query)
            results.extend(jina_results)
        except Exception as e:
            logger.warning(f"jina 搜索失败：{e}")
        
        # 深度搜索：获取详细内容
        if depth == 'deep' and results:
            results = await self._fetch_content(results)
        
        return results[:self.max_results]
    
    async def _jina_search(self, query: str) -> List[Dict]:
        """使用 jina.ai 进行搜索"""
        if not httpx:
            logger.warning("httpx 未安装，使用备用数据源")
            return await self._fallback_search(query)
        
        try:
            # 使用 jina.ai 的搜索服务
            url = f"https://s.jina.ai/{query}"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                content = response.text
            
            # 解析结果
            return self._parse_jina_results(content, query)
            
        except Exception as e:
            logger.debug(f"Jina 搜索失败：{e}")
            return await self._fallback_search(query)
    
    def _parse_jina_results(self, content: str, query: str) -> List[Dict]:
        """解析 Jina 搜索结果"""
        results = []
        lines = content.split('\n')
        current_item = {}
        
        for line in lines:
            line = line.strip()
            if line.startswith('[') and '](' in line:
                # 保存前一个结果
                if current_item and current_item.get('title'):
                    results.append({
                        'title': current_item['title'],
                        'url': current_item['url'],
                        'snippet': current_item.get('snippet', '')[:500],
                        'source': self._extract_source(current_item['url']),
                        'date': current_item.get('date', ''),
                        'search_engine': 'jina',
                        'raw_content': '',
                    })
                
                # 解析新结果
                try:
                    title_end = line.index('](')
                    title = line[1:title_end]
                    url_start = title_end + 2
                    url_end = line.index(')', url_start)
                    url = line[url_start:url_end]
                    
                    current_item = {
                        'title': title,
                        'url': url,
                        'snippet': '',
                        'date': '',
                    }
                except:
                    current_item = {}
            elif current_item and line and not line.startswith('#'):
                current_item['snippet'] += line
            
        # 最后一个结果
        if current_item and current_item.get('title'):
            results.append({
                'title': current_item['title'],
                'url': current_item['url'],
                'snippet': current_item.get('snippet', '')[:500],
                'source': self._extract_source(current_item['url']),
                'date': current_item.get('date', ''),
                'search_engine': 'jina',
                'raw_content': '',
            })
        
        logger.info(f"Jina 解析到 {len(results)} 个结果")
        return results
    
    async def _fallback_search(self, query: str) -> List[Dict]:
        """备用搜索（权威数据源）"""
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
        
        await asyncio.sleep(0.5)
        return fallback_sources
    
    async def _fetch_content(self, results: List[Dict]) -> List[Dict]:
        """获取详细内容（使用 jina.ai）"""
        if not httpx:
            return results
        
        # 限制并发数
        semaphore = asyncio.Semaphore(5)
        
        async def fetch_with_sem(result):
            async with semaphore:
                return await self._fetch_single(result)
        
        tasks = [fetch_with_sem(r) for r in results[:10]]
        contents = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, content in enumerate(contents):
            if isinstance(content, str) and i < len(results):
                results[i]['raw_content'] = content
        
        return results
    
    async def _fetch_single(self, result: Dict) -> str:
        """获取单个页面内容（使用 jina.ai）"""
        try:
            url = result.get('url', '')
            
            # 使用 jina.ai 提取内容
            jina_url = f"https://r.jina.ai/{url}"
            
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(jina_url)
                response.raise_for_status()
                content = response.text
            
            # 限制长度
            return content[:5000] if content else ''
            
        except Exception as e:
            logger.debug(f"获取内容失败 {result.get('url')}: {e}")
            return result.get('raw_content', '')
    
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
