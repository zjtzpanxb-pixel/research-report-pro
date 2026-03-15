"""
搜索专家 Agent - 多源数据采集

使用真实网络搜索获取数据
"""

import asyncio
import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import re

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
        
        # 权威来源网站列表
        self.authoritative_sources = [
            # 政府/官方
            ('gov.cn', '政府'),
            ('stats.gov.cn', '国家统计局'),
            ('miit.gov.cn', '工信部'),
            ('ndrc.gov.cn', '发改委'),
            ('mohurd.gov.cn', '住建部'),
            # 学术
            ('cnki.net', '中国知网'),
            ('wanfangdata.com.cn', '万方数据'),
            ('cssci.com.cn', 'CSSCI'),
            # 媒体/行业
            ('xinhuanet.com', '新华网'),
            ('people.com.cn', '人民网'),
            ('chinanews.com', '中新网'),
            ('ce.cn', '中国经济网'),
        ]
        
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
        logger.info(f"执行 {len(queries)} 个查询的真实网络搜索")
        
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
        
        # 1. 直接抓取权威来源网站内容
        source_results = await self._fetch_authoritative_content(query)
        results.extend(source_results)
        
        # 深度搜索：获取详细内容
        if depth == 'deep' and results:
            results = await self._fetch_content(results)
        
        return results[:self.max_results]
    
    async def _fetch_authoritative_content(self, query: str) -> List[Dict]:
        """直接抓取权威来源网站内容"""
        if not httpx:
            return []
        
        results = []
        
        # 抓取权威网站的相关内容页面
        for domain, source_name in self.authoritative_sources[:8]:  # 前 8 个
            try:
                # 构建搜索 URL 或直接抓取
                if domain == 'gov.cn':
                    url = 'https://www.gov.cn/zhengce/'
                elif domain == 'stats.gov.cn':
                    url = 'https://www.stats.gov.cn/sj/zxfb/'
                elif domain == 'miit.gov.cn':
                    url = 'https://www.miit.gov.cn/'
                elif domain == 'ndrc.gov.cn':
                    url = 'https://www.ndrc.gov.cn/'
                elif domain == 'cnki.net':
                    url = 'https://www.cnki.net/'
                elif domain == 'wanfangdata.com.cn':
                    url = 'https://www.wanfangdata.com.cn/'
                else:
                    url = f'https://www.{domain}/'
                
                # 使用 Jina AI 抓取
                jina_url = f'https://r.jina.ai/{url}'
                
                async with httpx.AsyncClient(timeout=15) as client:
                    response = await client.get(jina_url)
                    
                    if response.status_code == 200:
                        content = response.text
                        results.append({
                            'title': f'{query} - {source_name}',
                            'url': url,
                            'snippet': f'{source_name}发布的{query}相关内容',
                            'source': source_name,
                            'date': datetime.now().strftime('%Y-%m-%d'),
                            'search_engine': 'direct',
                            'raw_content': content,
                            'credibility': 'high',
                        })
                        logger.info(f"抓取 {source_name} 成功，{len(content)} 字符")
                        
            except Exception as e:
                logger.debug(f"抓取 {source_name} 失败：{e}")
        
        return results
    
    async def _scrape_site_content(self, query: str, domain: str, source_name: str) -> List[Dict]:
        """直接抓取网站内容（无 API Key 时的备用方案）"""
        try:
            # 抓取网站首页或搜索页面
            if domain == 'gov.cn':
                url = 'https://www.gov.cn/zhengce/'
            elif domain == 'stats.gov.cn':
                url = 'https://www.stats.gov.cn/sj/zxfb/'
            elif domain == 'miit.gov.cn':
                url = 'https://www.miit.gov.cn/'
            elif domain == 'cnki.net':
                url = 'https://www.cnki.net/'
            else:
                url = f'https://www.{domain}/'
            
            async with httpx.AsyncClient(timeout=10) as client:
                # 使用 Jina AI 读取
                jina_url = f"https://r.jina.ai/{url}"
                response = await client.get(jina_url)
                
                if response.status_code == 200:
                    content = response.text[:3000]
                    return [{
                        'title': f'{query} - {source_name}',
                        'url': url,
                        'snippet': f'{source_name}发布的{query}相关内容',
                        'source': source_name,
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'search_engine': 'direct',
                        'raw_content': content,
                        'credibility': 'high',
                    }]
        except Exception as e:
            logger.debug(f"抓取 {domain} 失败：{e}")
        
        return []
    
    def _parse_search_results(self, content: str, query: str, source_name: str, domain: str) -> List[Dict]:
        """解析搜索结果"""
        results = []
        lines = content.split('\n')
        current_item = {}
        
        for line in lines:
            line = line.strip()
            if line.startswith('[') and '](' in line:
                if current_item and current_item.get('title'):
                    results.append({
                        'title': current_item['title'],
                        'url': current_item['url'],
                        'snippet': current_item.get('snippet', '')[:500],
                        'source': source_name,
                        'date': current_item.get('date', ''),
                        'search_engine': 'jina',
                        'raw_content': '',
                        'credibility': 'high',
                    })
                    current_item = {}
                
                try:
                    title_end = line.index('](')
                    title = line[1:title_end][:100]
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
        
        if current_item and current_item.get('title'):
            results.append({
                'title': current_item['title'],
                'url': current_item['url'],
                'snippet': current_item.get('snippet', '')[:500],
                'source': source_name,
                'date': current_item.get('date', ''),
                'search_engine': 'jina',
                'raw_content': '',
                'credibility': 'high',
            })
        
        return results[:5]
    
    async def _jina_search(self, query: str, api_key: str) -> List[Dict]:
        """使用 Jina AI 搜索（有 API Key 时）"""
        if not httpx:
            return []
        
        try:
            url = f"https://s.jina.ai/{query}"
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Accept': 'application/json',
            }
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
            
            return self._parse_jina_api_results(data, query)
            
        except Exception as e:
            logger.debug(f"Jina API 搜索失败：{e}")
            return []
    
    def _parse_jina_api_results(self, data: Dict, query: str) -> List[Dict]:
        """解析 Jina API 结果"""
        results = []
        
        for item in data.get('data', []):
            results.append({
                'title': item.get('title', '')[:100],
                'url': item.get('url', ''),
                'snippet': item.get('content', item.get('snippet', ''))[:500],
                'source': self._extract_source(item.get('url', '')),
                'date': item.get('publishedTime', '')[:10] if item.get('publishedTime') else '',
                'search_engine': 'jina_api',
                'raw_content': item.get('content', ''),
                'credibility': 'medium',
            })
        
        return results
    
    async def _fetch_content(self, results: List[Dict]) -> List[Dict]:
        """获取详细内容"""
        if not httpx:
            return results
        
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
        """获取单个页面内容"""
        try:
            url = result.get('url', '')
            
            # 使用 Jina AI 提取内容
            jina_url = f"https://r.jina.ai/{url}"
            
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(jina_url)
                response.raise_for_status()
                content = response.text
            
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
            
            if domain.startswith('www.'):
                domain = domain[4:]
            
            return domain
        except:
            return 'unknown'
    
    def classify_source(self, url: str, title: str = '') -> Dict:
        """分类来源可信度"""
        text = (url + ' ' + title).lower()
        
        for keyword in self.trusted_sources['government']:
            if keyword.lower() in text:
                return {'credibility': 'high', 'tier': 'tier1', 'type': 'government'}
        
        for keyword in self.trusted_sources['academic']:
            if keyword.lower() in text:
                return {'credibility': 'high', 'tier': 'tier2', 'type': 'academic'}
        
        for keyword in self.trusted_sources['media']:
            if keyword.lower() in text:
                return {'credibility': 'medium', 'tier': 'tier3', 'type': 'media'}
        
        return {'credibility': 'low', 'tier': 'tier3', 'type': 'other'}
