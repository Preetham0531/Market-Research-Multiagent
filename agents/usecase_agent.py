"""
Agent 2: Market Standards & Use Case Generation Agent
Analyzes industry trends and generates relevant AI/ML use cases
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

class UseCaseAgent:
    """
    Agent responsible for generating AI/ML use cases based on industry analysis
    """
    
    def __init__(self, fast_mode: bool = False):
        """Initialize the Use Case Agent"""
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
    
    def research_industry_ai_trends(self, industry: str) -> Dict[str, Any]:
        """
        Research AI/ML trends and standards in the specific industry
        
        Args:
            industry: Industry name to research
            
        Returns:
            Dictionary containing AI trends information
        """
        try:
            search_queries = [
                f"{industry} AI use cases machine learning applications 2024",
                f"{industry} digital transformation artificial intelligence automation",
                f"{industry} AI implementation success stories case studies",
                f"{industry} machine learning business value ROI"
            ]
            
            all_results = []
            for query in search_queries:
                search_results = self.tavily_client.search(
                    query=query,
                    search_depth="advanced",
                    max_results=5
                )
                all_results.extend(search_results.get("results", []))
            
            return {
                "industry": industry,
                "search_results": all_results,
                "search_queries": search_queries
            }
            
        except Exception as e:
            logger.error(f"Error researching AI trends: {str(e)}")
            return {"error": str(e)}
    
    def generate_use_cases(self, research_data: Dict, ai_trends_data: Dict) -> Dict[str, Any]:
        """
        Generate relevant AI/ML use cases based on research and trends data
        
        Args:
            research_data: Company and industry research data from Agent 1
            ai_trends_data: AI trends research data
            
        Returns:
            Dictionary containing generated use cases
        """
        try:
            # Extract context from research data
            company_analysis = research_data.get("analysis", {})
            industry = research_data.get("identified_industry", "")
            company_name = research_data.get("company_name", "the company")
            
            # Extract AI trends context
            ai_trends_context = self._extract_context_from_results(
                ai_trends_data.get("search_results", [])
            )
            
            # Get industry-specific prompt
            system_prompt = self._get_industry_specific_prompt(industry, company_name)
            
            human_prompt = f"""
            Generate exactly 10 detailed development use cases for {company_name} in the {industry} industry.
            
            COMPANY ANALYSIS:
            {json.dumps(company_analysis, indent=2)}
            
            INDUSTRY: {industry}
            
            AI TRENDS IN INDUSTRY:
            {ai_trends_context}
            
            DISTRIBUTION REQUIREMENT (STRICT):
            - 50% (5 of 10) MUST be AI-related (AI/ML/DL/LLM excluding GenAI) such as computer vision, NLP (non-GenAI), forecasting, optimization, anomaly detection, recommendation systems
            - 30% (3 of 10) MUST be GenAI (RAG, agents, copilots, content generation, document AI, NL interfaces)
            - 20% (2 of 10) MUST be non-AI development (new products, partnerships, process/automation without AI, data governance, integration, UX, change management)
            - Incorporate not only market trends but also weakness signals and gaps observed in research (e.g., underperforming segments or missing capabilities) and propose concrete solutions
            
            FORMAT REQUIREMENTS (STRICT, UNIFIED FOR ALL USE CASES):
            Each use case must follow this exact format (no separate sectioning for GenAI vs AI; same schema for all):
            
            **Use Case 1: [Clear, Descriptive Title]**
            **Objective/Use Case:** [3–5 sentences: problem context, business driver, affected processes, desired outcomes, scope boundaries]
            **AI Application:** [3–6 sentences: specific techniques (CV/NLP/RL/forecasting/RAG/agents), model family or class, training vs. fine-tune vs. RAG rationale, latency/throughput, security/privacy (PII/PHI), deployment pattern]
            **Cross-Functional Benefit:** [Department 1: Benefit description; Department 2: Benefit description; Department 3: Benefit description]
            **Business Impact:** [3–5 bullets that describe value (qualitative; avoid numeric percentages). Tie to measurable KPIs without using % values.]
            **KPIs:** [Leading KPI: ...; Lagging KPI: ...]
            **Effort & Cost:** [Effort: S/M/L; Cost Band: Low/Medium/High]  
            **Risks & Compliance:** [Key risks, regulatory constraints, mitigation]
            
            CONSTRAINTS:
            - Do NOT include numeric percentages anywhere in the output.
            - Do NOT include a Pilot Plan section.
            
            **Use Case 2: [Clear, Descriptive Title]**
            **Objective/Use Case:** [Detailed objective explaining what this use case aims to achieve]
            **AI Application:** [Specific AI/ML technologies and implementation approach]
            **Cross-Functional Benefit:** [Department 1: Benefit description; Department 2: Benefit description; Department 3: Benefit description]
            
            Continue this pattern for all 10 use cases. Each use case should be comprehensive, specific to {company_name}, and relevant to the {industry} industry.

            After listing all 10 use cases, add a section named "Citations" as a bullet list of the top authoritative sources you used (full URLs). Prioritize company official pages/filings, then reputable media, then high-quality summaries.
            """
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = self.llm(messages)
            
            # Structure the response properly
            return self._structure_enhanced_use_cases(response.content, company_name, industry)
                
        except Exception as e:
            logger.error(f"Error generating use cases: {str(e)}")
            return {"error": str(e)}
    
    def prioritize_use_cases(self, use_cases: Dict, company_data: Dict) -> Dict[str, Any]:
        """
        Prioritize use cases based on company readiness and business impact
        
        Args:
            use_cases: Generated use cases
            company_data: Company analysis data
            
        Returns:
            Prioritized use cases with recommendations
        """
        try:
            company_name = company_data.get("company_name", "the company")
            industry = company_data.get("identified_industry", "")
            
            system_prompt = f"""
            You are a strategic AI consultant specializing in {industry} industry implementations.
            Your task is to prioritize the 10 AI/ML use cases for {company_name} based on:
            
            1. Business Impact (High/Medium/Low)
            2. Implementation Feasibility (High/Medium/Low) 
            3. Data Availability (High/Medium/Low)
            4. Technical Complexity (High/Medium/Low)
            5. Timeline to Value (Quick/Medium/Long-term)
            6. ROI Potential (High/Medium/Low)
            
            Provide a structured prioritization with:
            - Priority ranking (1-10)
            - Implementation timeline (Phase 1: 0-6 months, Phase 2: 6-18 months, Phase 3: 18+ months)
            - Resource requirements
            - Success metrics
            - Risk assessment
            """
            
            human_prompt = f"""
            Prioritize these 10 use cases for {company_name} in the {industry} industry:
            
            USE CASES:
            {use_cases.get('formatted_use_cases', '')}
            
            COMPANY DATA:
            {json.dumps(company_data, indent=2)}
            
            Provide detailed prioritization with clear justification and implementation roadmap.
            """
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = self.llm(messages)
            
            return {
                "prioritization_analysis": response.content,
                "structured": True
            }
                
        except Exception as e:
            logger.error(f"Error prioritizing use cases: {str(e)}")
            return {"error": str(e)}
    
    def generate_genai_solutions(self, company_data: Dict) -> Dict[str, Any]:
        """
        Generate specific GenAI solutions like document search, report generation, chat systems
        
        Args:
            company_data: Company analysis data
            
        Returns:
            Dictionary containing GenAI solution recommendations
        """
        try:
            company_analysis = company_data.get("analysis", {})
            company_name = company_data.get("company_name", "the company")
            industry = company_data.get("identified_industry", "")
            
            # Get industry-specific GenAI prompt
            system_prompt = self._get_industry_specific_genai_prompt(industry, company_name)
            
            human_prompt = f"""
            Generate GenAI solutions for {company_name} in the {industry} industry:
            
            COMPANY ANALYSIS:
            {json.dumps(company_analysis, indent=2)}
            
            Focus on practical, high-impact GenAI applications that complement traditional AI/ML use cases.
            """
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = self.llm(messages)
            
            return {
                "genai_solutions": response.content,
                "structured": True
            }
                
        except Exception as e:
            logger.error(f"Error generating GenAI solutions: {str(e)}")
            return {"error": str(e)}
    
    def process_use_case_generation(self, research_data: Dict) -> Dict[str, Any]:
        """
        Main method to process use case generation workflow
        
        Args:
            research_data: Research data from Agent 1
            
        Returns:
            Complete use case analysis and recommendations
        """
        logger.info("Starting use case generation process...")
        
        industry = research_data.get("identified_industry", "")
        
        # Step 1: Research AI trends in the industry
        ai_trends_data = self.research_industry_ai_trends(industry)
        
        if "error" in ai_trends_data:
            return ai_trends_data
        
        # Step 2: Generate use cases
        use_cases = self.generate_use_cases(research_data, ai_trends_data)
        
        if "error" in use_cases:
            return use_cases
        
        # Step 3: Prioritize use cases
        prioritized_use_cases = self.prioritize_use_cases(use_cases, research_data)
        
        # Step 4: Generate GenAI solutions
        genai_solutions = self.generate_genai_solutions(research_data)
        
        # Step 5: Compile final report
        use_case_report = {
            "industry": industry,
            "ai_trends_research": ai_trends_data,
            "generated_use_cases": use_cases,
            "prioritized_recommendations": prioritized_use_cases,
            "genai_solutions": genai_solutions,
            "agent": "UseCaseAgent",
            "status": "completed"
        }
        
        logger.info("Use case generation completed successfully")
        return use_case_report
    
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
    
    def _structure_use_cases(self, raw_content: str) -> Dict[str, Any]:
        """
        Structure raw use case content into a dictionary format
        
        Args:
            raw_content: Raw content from LLM
            
        Returns:
            Structured use cases dictionary
        """
        return {
            "raw_use_cases": raw_content,
            "structured": True,
            "note": "Use cases generated in text format"
        }
    
    def _structure_enhanced_use_cases(self, raw_content: str, company_name: str, industry: str) -> Dict[str, Any]:
        """
        Structure enhanced use case content with proper formatting
        
        Args:
            raw_content: Raw content from LLM
            company_name: Name of the company
            industry: Industry name
            
        Returns:
            Structured use cases dictionary
        """
        return {
            "company_name": company_name,
            "industry": industry,
            "formatted_use_cases": raw_content,
            "structured": True,
            "format": "enhanced_detailed",
            "note": "10 detailed use cases with objectives, AI applications, and cross-functional benefits"
        }
    
    def _get_industry_specific_prompt(self, industry: str, company_name: str) -> str:
        """
        Get industry-specific prompt for use case generation
        
        Args:
            industry: Industry name
            company_name: Company name
            
        Returns:
            Industry-specific system prompt
        """
        industry_lower = industry.lower()
        
        # Manufacturing & Industrial
        if any(keyword in industry_lower for keyword in ['manufacturing', 'steel', 'automotive', 'aerospace', 'chemical', 'pharmaceutical', 'textile', 'food processing', 'machinery', 'industrial']):
            return self._get_manufacturing_prompt(company_name, industry)
        
        # Technology & IT
        elif any(keyword in industry_lower for keyword in ['technology', 'software', 'it', 'tech', 'digital', 'cyber', 'data', 'cloud', 'saas', 'fintech', 'edtech', 'healthtech']):
            return self._get_technology_prompt(company_name, industry)
        
        # Healthcare & Medical
        elif any(keyword in industry_lower for keyword in ['healthcare', 'medical', 'pharmaceutical', 'biotech', 'hospital', 'clinic', 'health', 'medicine', 'life sciences']):
            return self._get_healthcare_prompt(company_name, industry)
        
        # Financial Services
        elif any(keyword in industry_lower for keyword in ['finance', 'banking', 'insurance', 'financial', 'investment', 'fintech', 'credit', 'lending']):
            return self._get_finance_prompt(company_name, industry)
        
        # Agriculture & Food
        elif any(keyword in industry_lower for keyword in ['agriculture', 'farming', 'food', 'agri', 'crop', 'livestock', 'dairy', 'poultry', 'fisheries', 'forestry']):
            return self._get_agriculture_prompt(company_name, industry)
        
        # Retail & E-commerce
        elif any(keyword in industry_lower for keyword in ['retail', 'ecommerce', 'e-commerce', 'shopping', 'fashion', 'consumer', 'marketplace', 'commerce']):
            return self._get_retail_prompt(company_name, industry)
        
        # Energy & Utilities
        elif any(keyword in industry_lower for keyword in ['energy', 'oil', 'gas', 'renewable', 'solar', 'wind', 'utilities', 'power', 'electricity', 'nuclear']):
            return self._get_energy_prompt(company_name, industry)
        
        # Transportation & Logistics
        elif any(keyword in industry_lower for keyword in ['transportation', 'logistics', 'shipping', 'aviation', 'railway', 'trucking', 'delivery', 'supply chain']):
            return self._get_transportation_prompt(company_name, industry)
        
        # Real Estate & Construction
        elif any(keyword in industry_lower for keyword in ['real estate', 'construction', 'property', 'building', 'infrastructure', 'architecture', 'engineering']):
            return self._get_real_estate_prompt(company_name, industry)
        
        # Education & Training
        elif any(keyword in industry_lower for keyword in ['education', 'training', 'learning', 'school', 'university', 'edtech', 'academic']):
            return self._get_education_prompt(company_name, industry)
        
        # Default prompt for unknown industries
        else:
            return self._get_default_prompt(company_name, industry)
    
    def _get_manufacturing_prompt(self, company_name: str, industry: str) -> str:
        """Manufacturing and industrial companies prompt"""
        return f"""
        You are an expert AI/ML consultant specializing in manufacturing and industrial companies.
        Your task is to generate exactly 10 detailed, structured AI/ML use cases for {company_name} in the {industry} industry.
        
        CRITICAL FORMAT REQUIREMENTS:
        Generate exactly 10 use cases in this EXACT format:
        
        **Use Case [X]: [Descriptive Title]**
        **Objective/Use Case:** [Clear business objective]
        **AI Application:** [Specific AI/ML technology and implementation approach]
        **Cross-Functional Benefit:** [Department 1: Specific benefit and impact; Department 2: Specific benefit and impact; Department 3: Specific benefit and impact]
        
        Focus areas for {industry} industry:
        1. Predictive maintenance and equipment optimization
        2. Quality control and defect detection
        3. Supply chain optimization and demand forecasting
        4. Process optimization and energy management
        5. Customer service and engagement
        6. Knowledge management and documentation
        7. Product design and development
        8. Contract and document processing
        9. Strategic planning and decision support
        10. Safety and compliance monitoring
        
        Each use case must include:
        - Clear, actionable objective
        - Specific AI/ML technology application
        - Cross-functional benefits for at least 3 departments
        - Industry-relevant implementation approach
        - Measurable business impact
        
        Generate exactly 10 use cases following this format precisely.
        """
    
    def _get_technology_prompt(self, company_name: str, industry: str) -> str:
        """Technology and IT companies prompt"""
        return f"""
        You are an expert AI/ML consultant specializing in technology and IT companies.
        Your task is to generate exactly 10 detailed, structured AI/ML use cases for {company_name} in the {industry} industry.
        
        CRITICAL FORMAT REQUIREMENTS:
        Generate exactly 10 use cases in this EXACT format:
        
        **Use Case [X]: [Descriptive Title]**
        **Objective/Use Case:** [Clear business objective]
        **AI Application:** [Specific AI/ML technology and implementation approach]
        **Cross-Functional Benefit:** [Department 1: Specific benefit and impact; Department 2: Specific benefit and impact; Department 3: Specific benefit and impact]
        
        Focus areas for {industry} industry:
        1. Software development automation and code generation
        2. Customer experience and personalization
        3. Data analytics and business intelligence
        4. Cybersecurity and threat detection
        5. Cloud infrastructure optimization
        6. Product recommendation systems
        7. Natural language processing applications
        8. DevOps and deployment automation
        9. Sales and marketing automation
        10. Customer support and chatbots
        
        Each use case must include:
        - Clear, actionable objective
        - Specific AI/ML technology application
        - Cross-functional benefits for at least 3 departments
        - Industry-relevant implementation approach
        - Measurable business impact
        
        Generate exactly 10 use cases following this format precisely.
        """
    
    def _get_healthcare_prompt(self, company_name: str, industry: str) -> str:
        """Healthcare and medical companies prompt"""
        return f"""
        You are an expert AI/ML consultant specializing in healthcare and medical companies.
        Your task is to generate exactly 10 detailed, structured AI/ML use cases for {company_name} in the {industry} industry.
        
        CRITICAL FORMAT REQUIREMENTS:
        Generate exactly 10 use cases in this EXACT format:
        
        **Use Case [X]: [Descriptive Title]**
        **Objective/Use Case:** [Clear business objective]
        **AI Application:** [Specific AI/ML technology and implementation approach]
        **Cross-Functional Benefit:** [Department 1: Specific benefit and impact; Department 2: Specific benefit and impact; Department 3: Specific benefit and impact]
        
        Focus areas for {industry} industry:
        1. Medical diagnosis and imaging analysis
        2. Drug discovery and development
        3. Patient monitoring and care management
        4. Electronic health records optimization
        5. Clinical decision support systems
        6. Telemedicine and remote care
        7. Medical research and data analysis
        8. Healthcare operations optimization
        9. Patient engagement and communication
        10. Regulatory compliance and reporting
        
        Each use case must include:
        - Clear, actionable objective
        - Specific AI/ML technology application
        - Cross-functional benefits for at least 3 departments
        - Industry-relevant implementation approach
        - Measurable business impact
        - HIPAA compliance considerations where applicable
        
        Generate exactly 10 use cases following this format precisely.
        """
    
    def _get_finance_prompt(self, company_name: str, industry: str) -> str:
        """Financial services companies prompt"""
        return f"""
        You are an expert AI/ML consultant specializing in financial services companies.
        Your task is to generate exactly 10 detailed, structured AI/ML use cases for {company_name} in the {industry} industry.
        
        CRITICAL FORMAT REQUIREMENTS:
        Generate exactly 10 use cases in this EXACT format:
        
        **Use Case [X]: [Descriptive Title]**
        **Objective/Use Case:** [Clear business objective]
        **AI Application:** [Specific AI/ML technology and implementation approach]
        **Cross-Functional Benefit:** [Department 1: Specific benefit and impact; Department 2: Specific benefit and impact; Department 3: Specific benefit and impact]
        
        Focus areas for {industry} industry:
        1. Fraud detection and prevention
        2. Credit risk assessment and scoring
        3. Algorithmic trading and portfolio management
        4. Customer service and chatbots
        5. Regulatory compliance and reporting
        6. Anti-money laundering (AML) systems
        7. Insurance underwriting and claims processing
        8. Personalized financial advice
        9. Market analysis and forecasting
        10. Operational risk management
        
        Each use case must include:
        - Clear, actionable objective
        - Specific AI/ML technology application
        - Cross-functional benefits for at least 3 departments
        - Industry-relevant implementation approach
        - Measurable business impact
        - Regulatory compliance considerations
        
        Generate exactly 10 use cases following this format precisely.
        """
    
    def _get_agriculture_prompt(self, company_name: str, industry: str) -> str:
        """Agriculture and food companies prompt"""
        return f"""
        You are an expert AI/ML consultant specializing in agriculture and food companies.
        Your task is to generate exactly 10 detailed, structured AI/ML use cases for {company_name} in the {industry} industry.
        
        CRITICAL FORMAT REQUIREMENTS:
        Generate exactly 10 use cases in this EXACT format:
        
        **Use Case [X]: [Descriptive Title]**
        **Objective/Use Case:** [Clear business objective]
        **AI Application:** [Specific AI/ML technology and implementation approach]
        **Cross-Functional Benefit:** [Department 1: Specific benefit and impact; Department 2: Specific benefit and impact; Department 3: Specific benefit and impact]
        
        Focus areas for {industry} industry:
        1. Precision agriculture and crop monitoring
        2. Livestock health and management
        3. Weather prediction and climate adaptation
        4. Soil analysis and nutrient optimization
        5. Pest and disease detection
        6. Supply chain and logistics optimization
        7. Food safety and quality control
        8. Yield prediction and optimization
        9. Water management and irrigation
        10. Market analysis and pricing optimization
        
        Each use case must include:
        - Clear, actionable objective
        - Specific AI/ML technology application
        - Cross-functional benefits for at least 3 departments
        - Industry-relevant implementation approach
        - Measurable business impact
        - Sustainability considerations
        
        Generate exactly 10 use cases following this format precisely.
        """
    
    def _get_retail_prompt(self, company_name: str, industry: str) -> str:
        """Retail and e-commerce companies prompt"""
        return f"""
        You are an expert AI/ML consultant specializing in retail and e-commerce companies.
        Your task is to generate exactly 10 detailed, structured AI/ML use cases for {company_name} in the {industry} industry.
        
        CRITICAL FORMAT REQUIREMENTS:
        Generate exactly 10 use cases in this EXACT format:
        
        **Use Case [X]: [Descriptive Title]**
        **Objective/Use Case:** [Clear business objective]
        **AI Application:** [Specific AI/ML technology and implementation approach]
        **Cross-Functional Benefit:** [Department 1: Specific benefit and impact; Department 2: Specific benefit and impact; Department 3: Specific benefit and impact]
        
        Focus areas for {industry} industry:
        1. Personalized product recommendations
        2. Inventory management and demand forecasting
        3. Customer service and chatbots
        4. Price optimization and dynamic pricing
        5. Fraud detection and prevention
        6. Visual search and product discovery
        7. Supply chain optimization
        8. Customer analytics and segmentation
        9. Marketing automation and personalization
        10. Store operations and layout optimization
        
        Each use case must include:
        - Clear, actionable objective
        - Specific AI/ML technology application
        - Cross-functional benefits for at least 3 departments
        - Industry-relevant implementation approach
        - Measurable business impact
        
        Generate exactly 10 use cases following this format precisely.
        """
    
    def _get_energy_prompt(self, company_name: str, industry: str) -> str:
        """Energy and utilities companies prompt"""
        return f"""
        You are an expert AI/ML consultant specializing in energy and utilities companies.
        Your task is to generate exactly 10 detailed, structured AI/ML use cases for {company_name} in the {industry} industry.
        
        CRITICAL FORMAT REQUIREMENTS:
        Generate exactly 10 use cases in this EXACT format:
        
        **Use Case [X]: [Descriptive Title]**
        **Objective/Use Case:** [Clear business objective]
        **AI Application:** [Specific AI/ML technology and implementation approach]
        **Cross-Functional Benefit:** [Department 1: Specific benefit and impact; Department 2: Specific benefit and impact; Department 3: Specific benefit and impact]
        
        Focus areas for {industry} industry:
        1. Energy demand forecasting and grid optimization
        2. Predictive maintenance for power infrastructure
        3. Renewable energy integration and management
        4. Smart grid and distribution optimization
        5. Energy trading and market analysis
        6. Customer energy management and billing
        7. Environmental monitoring and compliance
        8. Asset performance optimization
        9. Cybersecurity for critical infrastructure
        10. Carbon footprint tracking and reduction
        
        Each use case must include:
        - Clear, actionable objective
        - Specific AI/ML technology application
        - Cross-functional benefits for at least 3 departments
        - Industry-relevant implementation approach
        - Measurable business impact
        - Sustainability and environmental considerations
        
        Generate exactly 10 use cases following this format precisely.
        """
    
    def _get_transportation_prompt(self, company_name: str, industry: str) -> str:
        """Transportation and logistics companies prompt"""
        return f"""
        You are an expert AI/ML consultant specializing in transportation and logistics companies.
        Your task is to generate exactly 10 detailed, structured AI/ML use cases for {company_name} in the {industry} industry.
        
        CRITICAL FORMAT REQUIREMENTS:
        Generate exactly 10 use cases in this EXACT format:
        
        **Use Case [X]: [Descriptive Title]**
        **Objective/Use Case:** [Clear business objective]
        **AI Application:** [Specific AI/ML technology and implementation approach]
        **Cross-Functional Benefit:** [Department 1: Specific benefit and impact; Department 2: Specific benefit and impact; Department 3: Specific benefit and impact]
        
        Focus areas for {industry} industry:
        1. Route optimization and fleet management
        2. Predictive maintenance for vehicles
        3. Demand forecasting and capacity planning
        4. Real-time tracking and visibility
        5. Driver behavior monitoring and safety
        6. Fuel efficiency and emissions reduction
        7. Customer service and delivery optimization
        8. Supply chain visibility and coordination
        9. Risk management and insurance
        10. Autonomous vehicle integration
        
        Each use case must include:
        - Clear, actionable objective
        - Specific AI/ML technology application
        - Cross-functional benefits for at least 3 departments
        - Industry-relevant implementation approach
        - Measurable business impact
        
        Generate exactly 10 use cases following this format precisely.
        """
    
    def _get_real_estate_prompt(self, company_name: str, industry: str) -> str:
        """Real estate and construction companies prompt"""
        return f"""
        You are an expert AI/ML consultant specializing in real estate and construction companies.
        Your task is to generate exactly 10 detailed, structured AI/ML use cases for {company_name} in the {industry} industry.
        
        CRITICAL FORMAT REQUIREMENTS:
        Generate exactly 10 use cases in this EXACT format:
        
        **Use Case [X]: [Descriptive Title]**
        **Objective/Use Case:** [Clear business objective]
        **AI Application:** [Specific AI/ML technology and implementation approach]
        **Cross-Functional Benefit:** [Department 1: Specific benefit and impact; Department 2: Specific benefit and impact; Department 3: Specific benefit and impact]
        
        Focus areas for {industry} industry:
        1. Property valuation and pricing optimization
        2. Construction project management and scheduling
        3. Building energy efficiency and smart systems
        4. Property maintenance and facility management
        5. Market analysis and investment decisions
        6. Customer relationship management
        7. Risk assessment and insurance
        8. Regulatory compliance and permitting
        9. Virtual property tours and visualization
        10. Tenant screening and management
        
        Each use case must include:
        - Clear, actionable objective
        - Specific AI/ML technology application
        - Cross-functional benefits for at least 3 departments
        - Industry-relevant implementation approach
        - Measurable business impact
        
        Generate exactly 10 use cases following this format precisely.
        """
    
    def _get_education_prompt(self, company_name: str, industry: str) -> str:
        """Education and training companies prompt"""
        return f"""
        You are an expert AI/ML consultant specializing in education and training companies.
        Your task is to generate exactly 10 detailed, structured AI/ML use cases for {company_name} in the {industry} industry.
        
        CRITICAL FORMAT REQUIREMENTS:
        Generate exactly 10 use cases in this EXACT format:
        
        **Use Case [X]: [Descriptive Title]**
        **Objective/Use Case:** [Clear business objective]
        **AI Application:** [Specific AI/ML technology and implementation approach]
        **Cross-Functional Benefit:** [Department 1: Specific benefit and impact; Department 2: Specific benefit and impact; Department 3: Specific benefit and impact]
        
        Focus areas for {industry} industry:
        1. Personalized learning and adaptive education
        2. Student performance analytics and intervention
        3. Automated grading and assessment
        4. Virtual tutoring and learning assistants
        5. Curriculum optimization and content generation
        6. Student engagement and retention
        7. Administrative process automation
        8. Learning management system optimization
        9. Career guidance and pathway planning
        10. Research and academic analytics
        
        Each use case must include:
        - Clear, actionable objective
        - Specific AI/ML technology application
        - Cross-functional benefits for at least 3 departments
        - Industry-relevant implementation approach
        - Measurable business impact
        - Educational outcome considerations
        
        Generate exactly 10 use cases following this format precisely.
        """
    
    def _get_default_prompt(self, company_name: str, industry: str) -> str:
        """Default prompt for unknown industries"""
        return f"""
        You are an expert AI/ML consultant specializing in business use case generation.
        Your task is to generate exactly 10 detailed, structured AI/ML use cases for {company_name} in the {industry} industry.
        
        CRITICAL FORMAT REQUIREMENTS:
        Generate exactly 10 use cases in this EXACT format:
        
        **Use Case [X]: [Descriptive Title]**
        **Objective/Use Case:** [Clear business objective]
        **AI Application:** [Specific AI/ML technology and implementation approach]
        **Cross-Functional Benefit:** [Department 1: Specific benefit and impact; Department 2: Specific benefit and impact; Department 3: Specific benefit and impact]
        
        Focus on general business areas:
        1. Process automation and optimization
        2. Customer experience enhancement
        3. Data analytics and insights
        4. Predictive analytics and forecasting
        5. Operational efficiency improvements
        6. Cost reduction and optimization
        7. Revenue generation opportunities
        8. Risk management and compliance
        9. Employee productivity and engagement
        10. Innovation and competitive advantage
        
        Each use case must include:
        - Clear, actionable objective
        - Specific AI/ML technology application
        - Cross-functional benefits for at least 3 departments
        - Industry-relevant implementation approach
        - Measurable business impact
        
        Generate exactly 10 use cases following this format precisely.
        """
    def _get_industry_specific_genai_prompt(self, industry: str, company_name: str) -> str:
        """Get industry-specific GenAI prompt"""
        industry_lower = industry.lower()
        
        if any(keyword in industry_lower for keyword in ['manufacturing', 'steel', 'automotive', 'aerospace', 'chemical', 'pharmaceutical', 'textile', 'food processing', 'machinery', 'industrial']):
            return f"""
            You are a GenAI solutions architect specializing in manufacturing and industrial companies.
            Generate 5-7 specific Generative AI solutions for {company_name} in the {industry} industry.
            
            Focus on manufacturing-specific GenAI applications:
            1. Technical documentation and SOP generation
            2. Equipment maintenance manuals and troubleshooting guides
            3. Quality control reports and compliance documentation
            4. Training materials for safety and operations
            5. Supplier communication and contract processing
            6. Customer technical support chatbots
            7. Process optimization recommendations
            8. Safety incident analysis and reporting
            
            For each solution, provide:
            - Solution name and clear description
            - Specific business benefits for {industry}
            - Technical implementation approach
            - Integration with existing manufacturing systems
            - Expected ROI and success metrics
            - Implementation timeline and resources
            """
        elif any(keyword in industry_lower for keyword in ['technology', 'software', 'it', 'tech', 'digital', 'cyber', 'data', 'cloud', 'saas', 'fintech', 'edtech', 'healthtech']):
            return f"""
            You are a GenAI solutions architect specializing in technology and IT companies.
            Generate 5-7 specific Generative AI solutions for {company_name} in the {industry} industry.
            
            Focus on tech-specific GenAI applications:
            1. Code generation and documentation automation
            2. Technical support and developer assistance
            3. API documentation and integration guides
            4. Customer onboarding and training materials
            5. Bug report analysis and resolution suggestions
            6. Product requirement generation and refinement
            7. Technical blog and content creation
            8. Code review and quality assurance assistance
            
            For each solution, provide:
            - Solution name and clear description
            - Specific business benefits for {industry}
            - Technical implementation approach
            - Integration with existing development workflows
            - Expected ROI and success metrics
            - Implementation timeline and resources
            """
        elif any(keyword in industry_lower for keyword in ['healthcare', 'medical', 'pharmaceutical', 'biotech', 'hospital', 'clinic', 'health', 'medicine', 'life sciences']):
            return f"""
            You are a GenAI solutions architect specializing in healthcare and medical companies.
            Generate 5-7 specific Generative AI solutions for {company_name} in the {industry} industry.
            
            Focus on healthcare-specific GenAI applications:
            1. Medical documentation and clinical notes generation
            2. Patient education materials and treatment guides
            3. Research paper analysis and literature reviews
            4. Regulatory compliance documentation
            5. Medical training and continuing education content
            6. Patient communication and appointment scheduling
            7. Clinical decision support and treatment recommendations
            8. Medical coding and billing assistance
            
            For each solution, provide:
            - Solution name and clear description
            - Specific business benefits for {industry}
            - Technical implementation approach
            - HIPAA compliance considerations
            - Integration with existing healthcare systems
            - Expected ROI and success metrics
            - Implementation timeline and resources
            """
        elif any(keyword in industry_lower for keyword in ['finance', 'banking', 'insurance', 'financial', 'investment', 'fintech', 'credit', 'lending']):
            return f"""
            You are a GenAI solutions architect specializing in financial services companies.
            Generate 5-7 specific Generative AI solutions for {company_name} in the {industry} industry.
            
            Focus on finance-specific GenAI applications:
            1. Financial report generation and analysis
            2. Regulatory compliance documentation
            3. Customer financial education and guidance
            4. Risk assessment and credit analysis reports
            5. Investment research and market analysis
            6. Customer service and financial advisory chatbots
            7. Fraud detection and investigation reports
            8. Training materials for financial products
            
            For each solution, provide:
            - Solution name and clear description
            - Specific business benefits for {industry}
            - Technical implementation approach
            - Regulatory compliance considerations
            - Integration with existing financial systems
            - Expected ROI and success metrics
            - Implementation timeline and resources
            """
        elif any(keyword in industry_lower for keyword in ['agriculture', 'farming', 'food', 'agri', 'crop', 'livestock', 'dairy', 'poultry', 'fisheries', 'forestry']):
            return f"""
            You are a GenAI solutions architect specializing in agriculture and food companies.
            Generate 5-7 specific Generative AI solutions for {company_name} in the {industry} industry.
            
            Focus on agriculture-specific GenAI applications:
            1. Farming guides and crop management documentation
            2. Weather analysis and agricultural advisory content
            3. Livestock health monitoring and care instructions
            4. Supply chain and logistics documentation
            5. Food safety and quality control reports
            6. Market analysis and pricing recommendations
            7. Sustainable farming practice guides
            8. Agricultural training and education materials
            
            For each solution, provide:
            - Solution name and clear description
            - Specific business benefits for {industry}
            - Technical implementation approach
            - Sustainability considerations
            - Integration with existing agricultural systems
            - Expected ROI and success metrics
            - Implementation timeline and resources
            """
        else:
            return f"""
            You are a GenAI solutions architect specializing in business applications.
            Generate 5-7 specific Generative AI solutions for {company_name} in the {industry} industry.
            
            Focus on general GenAI applications:
            1. Document search and knowledge management systems
            2. Automated report generation and documentation
            3. AI-powered chatbots (internal and customer-facing)
            4. Content creation and personalization
            5. Code generation and technical documentation
            6. Email and communication automation
            7. Training and onboarding assistants
            8. Contract and compliance document processing
            
            For each solution, provide:
            - Solution name and clear description
            - Specific business benefits for {industry}
            - Technical implementation approach
            - Integration with existing systems
            - Expected ROI and success metrics
            - Implementation timeline and resources
            """
