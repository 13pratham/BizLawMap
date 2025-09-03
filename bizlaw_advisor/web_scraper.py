"""
Web scraping service for legal sources
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Optional
from urllib.parse import urlparse
import time

from .models import LegalSource
from .config import AppConfig

class WebScraperService:
    """Service for scraping legal information from official sources"""
    
    def __init__(self):
        self.config = AppConfig()
        self.session = requests.Session()
    
    def validate_domain(self, url: str) -> bool:
        """Validate if the domain is from an official source"""
        domain = urlparse(url).netloc.lower()
        return any(priority_domain in domain for priority_domain in self.config.SOURCES.DOMAIN_PRIORITY)
    
    def scrape_legal_source(self, url: str, jurisdiction: str) -> Optional[LegalSource]:
        """Scrape legal information from a single source"""
        try:
            if not self.validate_domain(url):
                return None
                
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title and description
            title = soup.title.string if soup.title else url
            description = ""
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                description = meta_desc.get('content', '')
            
            return LegalSource(
                url=url,
                jurisdiction=jurisdiction,
                title=title,
                description=description,
                relevance_score=1.0
            )
            
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return None
    
    def search_federal_laws(self, query: str) -> List[LegalSource]:
        """Search for federal laws based on query"""
        sources = []
        for domain in self.config.SOURCES.FEDERAL_SOURCES:
            # In a real implementation, this would use the official API or search functionality
            # For demo purposes, we'll just create placeholder sources
            source = LegalSource(
                url=f"https://{domain}/example",
                jurisdiction="Federal",
                title=f"Federal Law - {domain}",
                description=f"Example federal law from {domain}",
                relevance_score=1.0
            )
            sources.append(source)
        return sources
    
    def search_state_laws(self, state: str, query: str) -> List[LegalSource]:
        """Search for state laws based on query"""
        # Placeholder for state law search
        return [
            LegalSource(
                url=f"https://{state.lower()}.gov/example",
                jurisdiction="State",
                title=f"State Law - {state}",
                description=f"Example state law from {state}",
                relevance_score=1.0
            )
        ]
    
    def search_local_laws(self, city: str, state: str, query: str) -> List[LegalSource]:
        """Search for local laws based on query"""
        # Placeholder for local law search
        return [
            LegalSource(
                url=f"https://{city.lower()}.{state.lower()}.gov/example",
                jurisdiction="Local",
                title=f"Local Law - {city}",
                description=f"Example local law from {city}, {state}",
                relevance_score=1.0
            )
        ]
