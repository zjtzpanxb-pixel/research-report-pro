"""
搜索专家 Agent - 使用 Jina AI 搜索

通过 Jina AI 的搜索服务获取真实网络数据
"""

import asyncio
import os
from typing import Dict, List, Any
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
        
        # 权威来源
        self.authoritative_sources = [
            ('gov.cn', '政府'),
            ('miit.gov.cn', '工信部'),
            ('ndrc.gov.cn', '发改委'),
            ('stats.gov.cn', '国家统计局'),
            ('cnki.net', '中国知网'),
            ('wanfangdata.com.cn', '万方数据'),
            ('xinhuanet.com', '新华网'),
        ]
    
    async def search(self, queries: List[str], depth: str = 'deep') -> List[Dict]:
        """执行多查询搜索"""
        logger.info(f"执行 {len(queries)} 个查询的网络搜索")
        
        tasks = [self._search_query(query, depth) for query in queries]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_results = []
        for result in results:
            if isinstance(result, list):
                all_results.extend(result)
        
        # 去重
        seen_urls = set()
        unique_results = []
        for r in all_results:
            url = r.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(r)
        
        logger.info(f"搜索完成，{len(unique_results)} 个结果")
        return unique_results
    
    async def _search_query(self, query: str, depth: str) -> List[Dict]:
        """执行单个查询"""
        results = []
        
        # 使用 Jina AI 搜索
        if httpx:
            jina_results = await self._jina_search(query)
            results.extend(jina_results)
        
        # 补充：抓取权威网站相关内容
        if len(results) < 5:
            for domain, source_name in self.authoritative_sources[:5]:
                content = await self._search_site(query, domain, source_name)
                if content:
                    results.append(content)
        
        # 深度搜索：获取详细内容
        if depth == 'deep' and results:
            results = await self._fetch_content(results)
        
        return results[:self.max_results]
    
    async def _jina_search(self, query: str) -> List[Dict]:
        """使用 Jina AI 搜索"""
        try:
            # Jina AI 搜索服务
            url = f"https://s.jina.ai/{query}"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                
                if response.status_code == 200:
                    return self._parse_jina_search(response.text, query)
        except Exception as e:
            logger.debug(f"Jina 搜索失败：{e}")
        
        return []
    
    def _parse_jina_search(self, content: str, query: str) -> List[Dict]:
        """解析 Jina 搜索结果"""
        results = []
        lines = content.split('\n')
        current = {}
        
        for line in lines:
            line = line.strip()
            if line.startswith('[') and '](' in line:
                if current.get('title'):
                    results.append({
                        'title': current['title'][:100],
                        'url': current.get('url', ''),
                        'snippet': current.get('snippet', '')[:500],
                        'source': self._extract_source(current.get('url', '')),
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'search_engine': 'jina',
                        'raw_content': current.get('snippet', ''),
                        'credibility': 'medium',
                    })
                current = {}
                
                try:
                    title_end = line.index('](')
                    current['title'] = line[1:title_end]
                    url_start = title_end + 2
                    url_end = line.index(')', url_start)
                    current['url'] = line[url_start:url_end]
                    current['snippet'] = ''
                except:
                    pass
            elif current and line and not line.startswith('#'):
                current['snippet'] += line + ' '
        
        if current.get('title'):
            results.append({
                'title': current['title'][:100],
                'url': current.get('url', ''),
                'snippet': current.get('snippet', '')[:500],
                'source': self._extract_source(current.get('url', '')),
                'date': datetime.now().strftime('%Y-%m-%d'),
                'search_engine': 'jina',
                'raw_content': current.get('snippet', ''),
                'credibility': 'medium',
            })
        
        return results[:10]
    
    async def _search_site(self, query: str, domain: str, source_name: str) -> Dict:
        """搜索特定网站"""
        try:
            # 使用 Jina AI 的 site: 搜索
            search_url = f"https://s.jina.ai/{query} site:{domain}"
            
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.get(search_url)
                
                if response.status_code == 200:
                    content = response.text
                    # 提取第一条结果
                    lines = content.split('\n')
                    for line in lines:
                        if line.strip().startswith('[') and '](' in line:
                            try:
                                title_end = line.index('](')
                                title = line[1:title_end][:100]
                                url_start = title_end + 2
                                url_end = line.index(')', url_start)
                                url = line[url_start:url_end]
                                
                                return {
                                    'title': f'{query} - {source_name}',
                                    'url': url,
                                    'snippet': f'{source_name}关于{query}的内容',
                                    'source': source_name,
                                    'date': datetime.now().strftime('%Y-%m-%d'),
                                    'search_engine': 'jina_site',
                                    'raw_content': content[:3000],
                                    'credibility': 'high',
                                }
                            except:
                                pass
        except Exception as e:
            logger.debug(f"搜索 {source_name} 失败：{e}")
        
        return {}
    
    async def _fetch_content(self, results: List[Dict]) -> List[Dict]:
        """获取详细内容"""
        if not httpx:
            return results
        
        semaphore = asyncio.Semaphore(5)
        
        async def fetch(r):
            async with semaphore:
                try:
                    url = r.get('url', '')
                    if url:
                        jina_url = f"https://r.jina.ai/{url}"
                        async with httpx.AsyncClient(timeout=10) as client:
                            resp = await client.get(jina_url)
                            if resp.status_code == 200:
                                r['raw_content'] = resp.text[:5000]
                except:
                    pass
            return r
        
        tasks = [fetch(r) for r in results[:10]]
        return await asyncio.gather(*tasks)
    
    def _extract_source(self, url: str) -> str:
        """从 URL 提取来源"""
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc.lower()
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except:
            return 'unknown'
    
    def classify_source(self, url: str, title: str = '') -> Dict:
        """分类来源可信度"""
        text = (url + ' ' + title).lower()
        
        for kw in ['gov.cn', '国务院', '发改委', '工信部']:
            if kw in text:
                return {'credibility': 'high', 'tier': 'tier1'}
        
        for kw in ['edu.cn', '知网', '万方']:
            if kw in text:
                return {'credibility': 'high', 'tier': 'tier2'}
        
        return {'credibility': 'medium', 'tier': 'tier3'}
