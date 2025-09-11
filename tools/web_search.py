"""
Web search tools for the multi-agent system
"""
import requests
from typing import List, Dict, Any
from tavily import TavilyClient
from config import Config

class WebSearchTool:
    def __init__(self):
        if Config.TAVILY_API_KEY:
            self.tavily_client = TavilyClient(api_key=Config.TAVILY_API_KEY)
        else:
            self.tavily_client = None
    
    def search_company_info(self, company_name: str, industry: str = "") -> List[Dict[str, Any]]:
        """Search for comprehensive company information"""
        query = f"{company_name} company profile business model products services"
        if industry:
            query += f" {industry} industry"
        
        return self._perform_search(query, max_results=10)
    
    def search_industry_trends(self, industry: str) -> List[Dict[str, Any]]:
        """Search for industry trends and AI adoption"""
        query = f"{industry} industry trends AI artificial intelligence automation digital transformation 2024"
        return self._perform_search(query, max_results=8)
    
    def search_ai_use_cases(self, industry: str, company_type: str = "") -> List[Dict[str, Any]]:
        """Search for AI use cases in specific industry"""
        query = f"{industry} AI use cases machine learning automation generative AI"
        if company_type:
            query += f" {company_type}"
        
        return self._perform_search(query, max_results=10)
    
    def search_datasets(self, topic: str, platform: str = "") -> List[Dict[str, Any]]:
        """Search for relevant datasets"""
        if platform:
            query = f"site:{platform} {topic} dataset"
        else:
            query = f"{topic} dataset kaggle huggingface github"
        
        return self._perform_search(query, max_results=15)
    
    def search_competitors(self, company_name: str, industry: str) -> List[Dict[str, Any]]:
        """Search for competitor analysis"""
        query = f"{company_name} competitors {industry} market analysis competitive landscape"
        return self._perform_search(query, max_results=8)
    
    def _perform_search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Perform the actual search using Tavily with backoff and rate-limit fallback"""
        if not self.tavily_client:
            return self._fallback_search(query, max_results)
        
        try:
            response = self.tavily_client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results,
                include_domains=None,
                exclude_domains=["facebook.com", "twitter.com", "instagram.com"]
            )
            
            results = []
            for result in response.get('results', []):
                results.append({
                    'title': result.get('title', ''),
                    'url': result.get('url', ''),
                    'content': result.get('content', ''),
                    'score': result.get('score', 0)
                })
            
            return results
            
        except Exception as e:
            # Don't expose API keys or sensitive details in error messages
            error_msg = str(e)
            if "api" in error_msg.lower() and len(error_msg) > 50:
                error_msg = "API request failed"
            print(f"Tavily search error: {error_msg}")
            return self._fallback_search(query, max_results)
    
    def _fallback_search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Fallback search method when Tavily is not available"""
        # This is a simplified fallback - in production, you'd implement
        # alternative search methods like Google Custom Search, Bing, etc.
        return [
            {
                'title': f"Search result for: {query}",
                'url': 'https://example.com',
                'content': f"This is a fallback result for query: {query}. Please configure Tavily API key for real search results.",
                'score': 0.5
            }
        ]
