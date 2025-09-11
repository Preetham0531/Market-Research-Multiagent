"""
Agent 1: Industry/Company Research Agent
Researches industries and companies using web browsing capabilities
"""

import json
import logging
from typing import Dict, List, Any
from tavily import TavilyClient
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResearchAgent:
    """
    Agent responsible for researching industries and companies
    """
    
    def __init__(self, fast_mode: bool = False):
        """Initialize the Research Agent"""
        self.tavily_client = TavilyClient(api_key=Config.TAVILY_API_KEY)
        self.fast_mode = fast_mode
        
        # Use fast mode settings if enabled
        max_tokens = Config.FAST_MODE_MAX_TOKENS if fast_mode else Config.MAX_TOKENS
        temperature = Config.FAST_MODE_TEMPERATURE if fast_mode else Config.TEMPERATURE
        
        self.llm = ChatOpenAI(
            model=Config.MODEL_NAME,
            temperature=temperature,
            max_tokens=max_tokens,
            openai_api_key=Config.OPENAI_API_KEY
        )
        
    def search_company_info(self, company_name: str) -> Dict[str, Any]:
        """
        Search for company information using Tavily with retry logic
        
        Args:
            company_name: Name of the company to research
            
        Returns:
            Dictionary containing company information
        """
        import time
        max_retries = 3
        retry_delay = 1
        
         # Multiple targeted queries (company-agnostic)
        queries = [
            f"site:{company_name.lower()}.com subsidiaries OR brands OR business units",
            f"{company_name} list of subsidiaries site:investor.{company_name.lower()}.com OR site:{company_name.lower()}.com/investors",
            f"{company_name} annual report 2024 subsidiaries pdf",
            f"{company_name} major products platforms services official site",
            f"{company_name} brands list official",
            f"{company_name} acquisitions 2023 2024 2025 list",
            f"{company_name} business segments site:{company_name.lower()}.com",
            f"site:wikipedia.org {company_name} subsidiaries brands (background only)",
        ]
        all_results = []
        for q in queries:
            for attempt in range(max_retries):
                try:
                    res = self.tavily_client.search(
                        query=q,
                        search_depth="advanced",
                        max_results=max(5, Config.MAX_SEARCH_RESULTS // len(queries) or 3)
                    )
                    for r in res.get("results", []):
                        r["_query"] = q
                    all_results.extend(res.get("results", []))
                    break
                except Exception as e:
                    logger.warning(f"Query failed '{q}' attempt {attempt+1}: {str(e)}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay * (attempt + 1))
                        continue
        if all_results:
            return {
                "company_name": company_name,
                "search_results": all_results,
                "search_queries": queries,
                "total_results": len(all_results)
            }
        return {
            "error": "No results",
            "error_type": "search_failed",
            "company_name": company_name,
            "attempts": max_retries
        }
    
    def search_industry_info(self, industry: str) -> Dict[str, Any]:
        """
        Search for industry information and trends
        
        Args:
            industry: Industry name to research
            
        Returns:
            Dictionary containing industry information
        """
        try:
            search_query = f"{industry} industry latest trends 2024 market dynamics growth opportunities strategic focus AI artificial intelligence automation digital transformation competitive landscape"
            search_results = self.tavily_client.search(
                query=search_query,
                search_depth="advanced",
                max_results=Config.MAX_SEARCH_RESULTS
            )
            
            return {
                "industry": industry,
                "search_results": search_results.get("results", []),
                "search_query": search_query
            }
            
        except Exception as e:
            logger.error(f"Error searching for industry info: {str(e)}")
            return {"error": str(e)}
    
    def _extract_context_from_results(self, search_results: List[Dict]) -> str:
        """
        Extract relevant context from search results
        
        Args:
            search_results: List of search result dictionaries
            
        Returns:
            Concatenated context string
        """
        context = ""
        for result in search_results:
            title = result.get("title", "")
            content = result.get("content", "")
            url = result.get("url", "")
            
            context += f"Title: {title}\n"
            context += f"Content: {content}\n"
            context += f"Source: {url}\n\n"
        
        return context
    
    def conduct_research(self, company_name: str) -> Dict[str, Any]:
        """
        Main method to conduct comprehensive research on a company
        
        Args:
            company_name: Name of the company to research
            
        Returns:
            Complete research report
        """
        logger.info(f"Starting research for company: {company_name}")
        
        # Step 1: Search for company information
        company_data = self.search_company_info(company_name)
        
        if "error" in company_data:
            return company_data
        
        # Step 2: Identify industry from initial results
        industry = self._identify_industry(company_data)
        
        # Step 3: Search for industry information
        industry_data = self.search_industry_info(industry)
        
        if "error" in industry_data:
            return industry_data
        
        # Step 4: Analyze and synthesize the information
        analysis = self.analyze_company_industry(company_data, industry_data)
        
        # Step 5: Compile final research report
        research_report = {
            "company_name": company_name,
            "identified_industry": industry,
            "raw_data": {
                "company_data": company_data,
                "industry_data": industry_data
            },
            "analysis": analysis,
            "agent": "ResearchAgent",
            "status": "completed"
        }
        
        logger.info(f"Research completed for company: {company_name}")
        return research_report
    
    def _identify_industry(self, company_data: Dict) -> str:
        """
        Identify the industry from company data using LLM
        
        Args:
            company_data: Company research data
            
        Returns:
            Identified industry name
        """
        try:
            context = self._extract_context_from_results(company_data.get("search_results", []))
            
            prompt = f"""
            Based on the following company information, identify the primary industry this company operates in.
            Return only the industry name (e.g., "Healthcare", "Automotive", "Finance", "Retail", "Manufacturing", etc.).
            
            Company Information:
            {context}
            
            Industry:
            """
            
            messages = [HumanMessage(content=prompt)]
            response = self.llm(messages)
            
            return response.content.strip()
            
        except Exception as e:
            logger.warning(f"Error identifying industry: {str(e)}")
            return "Technology"  # Default fallback
    
    def analyze_company_industry(self, company_data: Dict, industry_data: Dict) -> Dict[str, Any]:
        """
        Analyze company and industry data using LLM
        
        Args:
            company_data: Company research data
            industry_data: Industry research data
            
        Returns:
            Structured analysis of company and industry
        """
        try:
            # Prepare context for LLM analysis
            company_context = self._extract_context_from_results(company_data.get("search_results", []))
            industry_context = self._extract_context_from_results(industry_data.get("search_results", []))
            
            system_prompt = """
            You are an expert business analyst with advanced reasoning capabilities specializing in industry research and company analysis. 
            You use systematic thinking, multi-step reasoning, and deep analytical frameworks to provide comprehensive insights.
            
            ANALYSIS FRAMEWORK:
            1. SYSTEMATIC THINKING: Break down complex information into logical components
            2. MULTI-PERSPECTIVE ANALYSIS: Consider multiple viewpoints and stakeholders
            3. CAUSAL REASONING: Identify cause-and-effect relationships
            4. STRATEGIC THINKING: Connect current state to future opportunities
            5. EVIDENCE-BASED CONCLUSIONS: Support all claims with data and reasoning
            
            REQUIRED JSON OUTPUT FORMAT (EXHAUSTIVE LISTS WITH COMPETITORS & CITATIONS):
            {
                "company_analysis": {
                    "businesses": [  // include ALL known current business units/subsidiaries/brands
                        {
                            "name": "Business Unit Name",
                            "description": "Detailed description of this business unit and its operations"
                        }
                    ],
                    "products": [  // include ALL major products/platforms/services
                        {
                            "name": "Product/Service Name",
                            "description": "Detailed description of this product/service and its features"
                        }
                    ],
                    "segments": [  // include ALL segments/verticals/industries
                        {
                            "name": "Market Segment Name",
                            "description": "Detailed description of this market segment and target audience"
                        }
                    ],
                    "business_model": "Overall business model description",
                    "key_offerings": ["Offering 1", "Offering 2", "Offering 3"],
                    "strategic_focus": "Current strategic focus areas and priorities",
                    "competitors": [  // top competitors with brief rationale
                        {
                            "name": "Competitor Name",
                            "reason": "Why competitor is relevant (segment overlap, geography, product overlap)"
                        }
                    ]
                },
                "industry_analysis": {
                    "market_trends": [
                        {
                            "trend": "Trend Name",
                            "description": "Detailed description of this trend and its impact"
                        }
                    ],
                    "strategic_focus": [
                        {
                            "area": "Focus Area Name",
                            "description": "Detailed description of this strategic focus area"
                        }
                    ],
                    "growth_opportunities": [
                        {
                            "opportunity": "Opportunity Name",
                            "description": "Detailed description of this growth opportunity"
                        }
                    ]
                },
                "citations": [  // REQUIRED. full URLs + source names used across sections (prioritize official filings/pages)
                    {"title": "Source Title", "url": "https://...", "source": "Company IR / SEC / Reuters / Bloomberg / Wikipedia (bg)"}
                ]
            }
            
            FOCUS AREAS:
            1. Company's multiple business units and their specific operations
            2. All products and services with detailed descriptions
            3. All market segments the company operates in
            4. Latest industry trends and market dynamics
            5. Strategic focus areas with detailed explanations
            6. Growth opportunities with specific reasoning
            7. Current technology adoption and AI readiness
            8. Competitive landscape and market position
            
            REASONING PROCESS:
            - Research and identify all business units, products, and segments
            - Analyze latest industry trends from multiple sources
            - Identify strategic focus areas with detailed explanations
            - Find growth opportunities with specific reasoning
            - Provide comprehensive, data-driven insights
            
            Provide a comprehensive analysis in the exact JSON format specified above.
            Every factual list item should be supportable by sources. Include a final "citations" array with the key sources used.
            """
            
            human_prompt = f"""
            Please analyze the following company and industry information and provide REAL, SPECIFIC, DETAILED information with competitors and citations:
            
            COMPANY INFORMATION:
            {company_context}
            
            INDUSTRY INFORMATION:
            {industry_context}
            
            CRITICAL REQUIREMENTS:
            1. For BUSINESSES: List ALL actual business units/subsidiaries with real names (e.g., AWS, Whole Foods, etc.)
            2. For PRODUCTS: List ALL specific products/services by name (e.g., iPhone, iPad, etc.)
            3. For SEGMENTS: List ALL actual market segments the company operates in
            4. For TRENDS: Research and provide REAL 2024 industry trends
            5. For STRATEGIC FOCUS: Provide ACTUAL strategic priorities from recent company reports
            6. For GROWTH OPPORTUNITIES: Identify REAL growth opportunities based on current market analysis
            7. COMPETITORS: Include a competitors list with short rationale
            8. CITATIONS: Include a citations array (full URLs + source names). Prioritize official company filings/pages, then reputable media.
            
            NO GENERIC RESPONSES. Use web-searched data to provide specific, accurate, detailed information.
            """
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = self.llm(messages)
            
            content = response.content or ""
            # Extract JSON if wrapped in code fences
            if "```" in content:
                try:
                    fenced = content.split("```json")
                    if len(fenced) > 1:
                        json_block = fenced[1].split("```", 1)[0]
                    else:
                        json_block = content.split("```", 1)[1].split("```", 1)[0]
                    return json.loads(json_block)
                except Exception:
                    pass
            
            # Try direct JSON
            try:
                return json.loads(content)
            except Exception:
                return {"raw_analysis": content}
                
        except Exception as e:
            logger.error(f"Error analyzing company and industry: {str(e)}")
            return {"error": str(e)}