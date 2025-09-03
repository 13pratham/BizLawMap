"""
Search service using Langchain and multiple search tools
"""
from typing import List, Dict, Optional
from langchain_community.utilities import GoogleSerperAPIWrapper
from bs4 import BeautifulSoup
import requests
import asyncio
import aiohttp
from urllib.parse import urlparse
import re
# from playwright.async_api import async_playwright
import time
import os

from .models import LegalSource
from .config import AppConfig

class SearchService:
    """Service for searching legal information using multiple tools"""
    
    def __init__(self):
        self.config = AppConfig()
        os.environ["SERPER_API_KEY"] = os.getenv("Serper_API_Key", "bb4475e3408c9bb8d9d2e7ba1342d32b2e5443a2")
        self.search = GoogleSerperAPIWrapper()
        self._session = None
    
    async def get_session(self):
        """Get or create an aiohttp session"""
        if self._session is None:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def close(self):
        """Close the aiohttp session"""
        if self._session is not None:
            await self._session.close()
            self._session = None

    def is_official_source(self, url: str) -> bool:
        """Check if URL is from an official source"""
        domain = urlparse(url).netloc.lower()
        return any(domain.endswith(ext) for ext in self.config.SOURCES.DOMAIN_PRIORITY)

    async def extract_content(self, url: str) -> Optional[str]:
        """Extract main content from a webpage using Playwright"""
        try:
            session = await self.get_session()
            async with session.get(url) as response:
                if response.status != 200:
                    return None
                    
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Remove unwanted elements
                for element in soup.select('nav, footer, header, aside, script, style'):
                    element.decompose()
                
                # Find main content
                main_content = soup.select_one('main, article, .content, #content, .main')
                if main_content:
                    return main_content.get_text(strip=True)
                return soup.body.get_text(strip=True) if soup.body else None
                
        except Exception as e:
            print(f"Error extracting content from {url}: {str(e)}")
            return None

    async def search_legal_sources(self, query: str, jurisdiction: str = None, state: str = None) -> List[Dict]:
        """Search for legal sources using DuckDuckGo"""
        sources = []
        
        # Construct jurisdiction-specific query
        search_query = query
        if jurisdiction == "Federal":
            search_query = f"{query} site:(.gov)"
        elif jurisdiction == "State" and state:
            search_query = f"{query} {state} state law site:(.gov)"
        elif jurisdiction == "Local" and state:
            search_query = f"{query} local law site:(.gov)"
            
        # Perform search
        try:
            search_results = self.search.results(search_query)
            
            for result in search_results['organic']:
                if not self.is_official_source(result["link"]):
                    continue
                    
                # content = await self.extract_content(result["link"])
                # if not content:
                #     continue
                    
                source = {
                    "url": result["link"],
                    "jurisdiction": jurisdiction or "Unknown",
                    "title": result["title"],
                    "description": result["snippet"],
                    "relevance_score": 1.0,
                    "content": str(result)
                }
                sources.append(source)
                
        except Exception as e:
            print(f"Error in search: {str(e)}")
            
        return sources

    async def get_federal_laws(self, query: str) -> List[LegalSource]:
        """Search for federal laws"""
        federal_sources = []
        
        # Search each federal domain
        for domain in self.config.SOURCES.FEDERAL_SOURCES:
            results = await self.search_legal_sources(
                f"{query} site:{domain}",
                jurisdiction="Federal"
            )
            federal_sources.extend(results)
            
        return federal_sources

    async def get_state_laws(self, query: str, state: str) -> List[LegalSource]:
        """Search for state laws"""
        return await self.search_legal_sources(query, jurisdiction="State", state=state)

    async def get_local_laws(self, query: str, city: str, state: str) -> List[LegalSource]:
        """Search for local laws"""
        local_query = f"{query} {city} {state}"
        return await self.search_legal_sources(local_query, jurisdiction="Local", state=state)
