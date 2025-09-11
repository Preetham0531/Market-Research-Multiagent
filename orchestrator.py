"""
Main Orchestrator for Multi-Agent Market Research System
Coordinates all agents and manages the workflow
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, Any
from agents.research_agent import ResearchAgent
from agents.usecase_agent import UseCaseAgent
from agents.resource_agent import ResourceAgent
from config import Config

# Auto-clean .env file on startup
try:
    from utils.env_cleaner import auto_fix_env_file
    auto_fix_env_file()
except ImportError:
    pass  # Continue if env_cleaner is not available

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketResearchOrchestrator:
    """
    Main orchestrator that coordinates all agents in the multi-agent system
    """
    
    def __init__(self, fast_mode: bool = True, ultra_fast_mode: bool = False):
        """Initialize the orchestrator and all agents"""
        try:
            # Validate configuration
            Config.validate_config()
            
            # Initialize agents; force exhaustive research and detailed use cases
            self.research_agent = ResearchAgent(fast_mode=False)
            self.usecase_agent = UseCaseAgent(fast_mode=False)
            self.resource_agent = ResourceAgent()
            
            # Initialize configurable parameters
            self.use_case_count = 10  # Default number of use cases
            self.fast_mode = fast_mode  # Fast mode for resource collection
            self.ultra_fast_mode = ultra_fast_mode  # Ultra fast mode skips some steps
            
            logger.info(f"Market Research Orchestrator initialized successfully (Fast Mode: {fast_mode}, Ultra Fast: {ultra_fast_mode})")
            
        except Exception as e:
            logger.error(f"Failed to initialize orchestrator: {str(e)}")
            raise
    
    def run_complete_analysis(self, company_name: str) -> Dict[str, Any]:
        """
        Run the complete multi-agent analysis workflow
        
        Args:
            company_name: Name of the company to analyze
            
        Returns:
            Complete analysis results from all agents
        """
        logger.info(f"Starting complete analysis for company: {company_name}")
        
        # Initialize results dictionary
        results = {
            "company_name": company_name,
            "timestamp": datetime.now().isoformat(),
            "workflow_status": "in_progress",
            "agent_results": {}
        }
        
        try:
            # Step 1: Research Agent - Industry and Company Research
            logger.info("Step 1: Running Research Agent...")
            if self.ultra_fast_mode:
                logger.info("Ultra-fast mode: Using pre-built research template")
                research_results = self._get_ultra_fast_research(company_name)
            else:
                research_results = self.research_agent.conduct_research(company_name)
            
            if "error" in research_results:
                error_type = research_results.get("error_type", "unknown")
                if error_type == "search_failed":
                    # Try fallback approach
                    logger.warning("Primary search failed, attempting fallback...")
                    research_results = self._fallback_research(company_name)
                    if "error" in research_results:
                        results["workflow_status"] = "failed"
                        results["error"] = f"Research Agent failed: {research_results['error']}"
                        results["error_type"] = "research_failed"
                        return results
                else:
                    results["workflow_status"] = "failed"
                    results["error"] = f"Research Agent failed: {research_results['error']}"
                    results["error_type"] = "research_failed"
                    return results
            
            results["agent_results"]["research"] = research_results
            logger.info("Research Agent completed successfully")
            
            # Step 2: Use Case Agent - Generate AI/ML Use Cases
            logger.info("Step 2: Running Use Case Agent...")
            try:
                usecase_results = self.usecase_agent.process_use_case_generation(research_results)
                
                if "error" in usecase_results:
                    # Try with reduced complexity
                    logger.warning("Use case generation failed, attempting simplified approach...")
                    usecase_results = self._fallback_use_cases(research_results)
                    if "error" in usecase_results:
                        results["workflow_status"] = "partial"
                        results["error"] = f"Use Case Agent failed: {usecase_results['error']}"
                        results["error_type"] = "usecase_failed"
                        # Continue with partial results
                    else:
                        results["agent_results"]["use_cases"] = usecase_results
                        logger.info("Use Case Agent completed with fallback")
                else:
                    results["agent_results"]["use_cases"] = usecase_results
                    logger.info("Use Case Agent completed successfully")
                    
            except Exception as e:
                logger.error(f"Use Case Agent exception: {str(e)}")
                results["workflow_status"] = "partial"
                results["error"] = f"Use Case Agent failed: {str(e)}"
                results["error_type"] = "usecase_exception"
            
            # Step 3: Resource Agent - Collect Datasets and Resources
            logger.info("Step 3: Running Resource Agent...")
            try:
                if self.fast_mode:
                    logger.info("Fast mode: Using fallback resources for speed")
                    resource_results = self._get_fast_fallback_resources(company_name)
                else:
                    resource_results = self.resource_agent.collect_resources_for_use_cases(
                        results["agent_results"].get("use_cases", {})
                    )
                
                if "error" in resource_results:
                    logger.warning("Resource collection failed, continuing without resources...")
                    resource_results = {"resources": [], "error": "Resource collection failed"}
                
                results["agent_results"]["resources"] = resource_results
                logger.info("Resource Agent completed")
                
            except Exception as e:
                logger.error(f"Resource Agent exception: {str(e)}")
                results["agent_results"]["resources"] = {"resources": [], "error": str(e)}
            
            # Step 4: Save resources to markdown file
            logger.info("Step 4: Saving resources to file...")
            resource_file = self.resource_agent.save_resources_to_file(resource_results)
            results["resource_file"] = resource_file

            # Build datasets.md mapping each use case to dataset links
            try:
                uc = results["agent_results"].get("use_cases", {})
                datasets_md = self.resource_agent.create_datasets_markdown(uc, output_path="datasets.md")
                if datasets_md:
                    results["datasets_markdown"] = datasets_md
            except Exception as e:
                logger.warning(f"Failed to create datasets.md: {e}")
            
            # Step 5: Generate final proposal
            logger.info("Step 5: Generating final proposal...")
            final_proposal = self.generate_final_proposal(results)
            results["final_proposal"] = final_proposal
            
            # Save complete results
            results_file = self.save_complete_results(results)
            results["results_file"] = results_file
            
            results["workflow_status"] = "completed"
            logger.info(f"Complete analysis finished successfully for {company_name}")
            
        except Exception as e:
            logger.error(f"Error during analysis workflow: {str(e)}")
            results["workflow_status"] = "failed"
            results["error"] = str(e)
        
        return results
    
    def _fallback_research(self, company_name: str) -> Dict[str, Any]:
        """Fallback research method when primary search fails"""
        try:
            logger.info("Attempting fallback research approach...")
            # Simple fallback with basic company info
            return {
                "company_name": company_name,
                "identified_industry": "Technology",  # Default fallback
                "analysis": {
                    "company_analysis": {
                        "business_model": f"{company_name} is a technology company",
                        "key_offerings": "Technology products and services",
                        "strategic_focus": "Innovation and growth"
                    },
                    "industry_analysis": {
                        "industry": "Technology",
                        "market_trends": "Digital transformation and AI adoption",
                        "growth_opportunities": "AI/ML implementation"
                    }
                },
                "agent": "ResearchAgent",
                "status": "fallback_completed"
            }
        except Exception as e:
            logger.error(f"Fallback research failed: {str(e)}")
            return {"error": str(e), "error_type": "fallback_failed"}
    
    def _fallback_use_cases(self, research_data: Dict) -> Dict[str, Any]:
        """Fallback use case generation when primary method fails (10 detailed use cases)"""
        try:
            logger.info("Attempting fallback use case generation...")
            company_name = research_data.get("company_name", "the company")
            industry = research_data.get("identified_industry", "Technology")
            
            # Generate a broader, detailed fallback set (10)
            basic_use_cases = [
                {
                    "title": "Supply Chain Optimization",
                    "objective": "Enhance demand forecasting, inventory planning, and logistics to reduce costs, waste, and stockouts while speeding delivery.",
                    "ai_application": "Time-series forecasting (Prophet/LSTM), multi-echelon inventory optimization, and route optimization with heuristics.",
                    "cross_functional_benefit": "Operations, Finance, Logistics"
                },
                {
                    "title": "Predictive Maintenance",
                    "objective": "Predict equipment failures to minimize unplanned downtime and optimize maintenance schedules.",
                    "ai_application": "Sensor-based anomaly detection and Remaining Useful Life (RUL) estimation with gradient boosting and LSTMs.",
                    "cross_functional_benefit": "Manufacturing, Operations, Finance"
                },
                {
                    "title": "Personalized Recommendations",
                    "objective": "Increase conversion and AOV via personalized product/content recommendations across channels.",
                    "ai_application": "Collaborative filtering, content-based, and hybrid recommenders; re-ranking with session context.",
                    "cross_functional_benefit": "Marketing, Sales, Product"
                },
                {
                    "title": "Customer Churn Prediction",
                    "objective": "Identify at-risk customers and trigger retention offers to reduce churn and boost LTV.",
                    "ai_application": "Classification models on behavioral, transactional, and support signals; uplift modeling.",
                    "cross_functional_benefit": "Customer Success, Marketing, Finance"
                },
                {
                    "title": "Fraud Detection",
                    "objective": "Detect and prevent fraudulent transactions with minimal false positives.",
                    "ai_application": "Supervised and semi-supervised anomaly detection; graph-based fraud rings; feature stores.",
                    "cross_functional_benefit": "Risk, Compliance, Engineering"
                },
                {
                    "title": "Dynamic Pricing Optimization",
                    "objective": "Optimize prices to balance margin, volume, and competitiveness in real time.",
                    "ai_application": "Price elasticity modeling, contextual bandits, and constrained optimization.",
                    "cross_functional_benefit": "Revenue, Sales, Finance"
                },
                {
                    "title": "Demand Forecasting",
                    "objective": "Forecast demand at SKU/channel granularity to inform procurement and replenishment.",
                    "ai_application": "Hierarchical forecasting, causal features (promo/seasonality), and feature-importance diagnostics.",
                    "cross_functional_benefit": "Supply Chain, Merchandising, Finance"
                },
                {
                    "title": "Defect Detection (Computer Vision)",
                    "objective": "Improve quality by detecting defects on the line and reducing scrap/rework.",
                    "ai_application": "CNNs/Transformers for visual inspection; active learning for continuous improvement.",
                    "cross_functional_benefit": "Quality, Manufacturing, R&D"
                },
                {
                    "title": "Support Ticket Triage (NLP)",
                    "objective": "Auto-classify, route, and summarize support tickets to cut response times.",
                    "ai_application": "Text classification with fine-tuned transformers; summarization for agent assistance.",
                    "cross_functional_benefit": "Customer Success, IT, Operations"
                },
                {
                    "title": "Inventory Optimization",
                    "objective": "Right-size safety stock and reorder points to improve cash flow and service levels.",
                    "ai_application": "Probabilistic demand modeling, service-level constraints, and stochastic optimization.",
                    "cross_functional_benefit": "Supply Chain, Finance, Operations"
                }
            ]
            
            return {
                "generated_use_cases": {
                    "formatted_use_cases": "\n\n".join([
                        f"**{uc['title']}**\n"
                        f"**Objective**: {uc['objective']}\n"
                        f"**AI Application**: {uc['ai_application']}\n"
                        f"**Cross-Functional Benefit**: {uc['cross_functional_benefit']}"
                        for uc in basic_use_cases
                    ])
                },
                "prioritized_recommendations": {
                    "prioritization_analysis": "Basic prioritization based on implementation complexity"
                },
                "agent": "UseCaseAgent",
                "status": "fallback_completed"
            }
        except Exception as e:
            logger.error(f"Fallback use case generation failed: {str(e)}")
            return {"error": str(e), "error_type": "fallback_failed"}
    
    def generate_final_proposal(self, complete_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate the final proposal with top recommendations
        
        Args:
            complete_results: Complete results from all agents
            
        Returns:
            Final proposal with prioritized recommendations
        """
        try:
            company_name = complete_results.get("company_name", "")
            research_data = complete_results.get("agent_results", {}).get("research", {})
            usecase_data = complete_results.get("agent_results", {}).get("use_cases", {})
            resource_data = complete_results.get("agent_results", {}).get("resources", {})
            
            # Extract key information
            industry = research_data.get("identified_industry", "")
            company_analysis = research_data.get("analysis", {})
            prioritized_use_cases = usecase_data.get("prioritized_recommendations", {})
            genai_solutions = usecase_data.get("genai_solutions", {})
            
            # Build final proposal
            final_proposal = {
                "executive_summary": {
                    "company": company_name,
                    "industry": industry,
                    "analysis_date": complete_results.get("timestamp", ""),
                    "total_use_cases_generated": self._count_use_cases(usecase_data),
                    "total_resources_found": self._count_resources(resource_data)
                },
                "company_overview": company_analysis,
                "top_recommendations": prioritized_use_cases,
                "genai_solutions": genai_solutions,
                "implementation_roadmap": self._generate_implementation_roadmap(prioritized_use_cases),
                "resource_summary": {
                    "kaggle_datasets": resource_data.get("kaggle", {}).get("count", 0),
                    "huggingface_resources": resource_data.get("huggingface", {}).get("count", 0),
                    "github_repositories": resource_data.get("github", {}).get("count", 0),
                    "resource_file": complete_results.get("resource_file", "")
                },
                "next_steps": [
                    "Review and validate the proposed use cases with business stakeholders",
                    "Conduct detailed feasibility assessment for priority use cases",
                    "Develop proof-of-concept for the highest priority use case",
                    "Establish AI governance framework and data infrastructure",
                    "Plan team training and skill development initiatives"
                ]
            }
            
            return final_proposal
            
        except Exception as e:
            logger.error(f"Error generating final proposal: {str(e)}")
            return {"error": str(e)}
    
    def save_complete_results(self, results: Dict[str, Any]) -> str:
        """
        Save complete results to a JSON file
        
        Args:
            results: Complete analysis results
            
        Returns:
            Path to the saved results file
        """
        try:
            company_name = results.get("company_name", "unknown").replace(" ", "_").lower()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{Config.REPORTS_DIR}/complete_analysis_{company_name}_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Complete results saved to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error saving complete results: {str(e)}")
            return ""
    
    def generate_summary_report(self, results: Dict[str, Any]) -> str:
        """
        Generate a human-readable summary report
        
        Args:
            results: Complete analysis results
            
        Returns:
            Path to the saved summary report
        """
        try:
            company_name = results.get("company_name", "Unknown")
            final_proposal = results.get("final_proposal", {})
            
            # Generate markdown report
            report_content = f"""# Market Research Analysis Report

## Company: {company_name}

### Executive Summary
- **Industry**: {final_proposal.get('executive_summary', {}).get('industry', 'N/A')}
- **Analysis Date**: {final_proposal.get('executive_summary', {}).get('analysis_date', 'N/A')}
- **Use Cases Generated**: {final_proposal.get('executive_summary', {}).get('total_use_cases_generated', 0)}
- **Resources Found**: {final_proposal.get('executive_summary', {}).get('total_resources_found', 0)}

### Top Recommendations

{self._format_recommendations_markdown(final_proposal.get('top_recommendations', {}))}

### GenAI Solutions

{self._format_genai_solutions_markdown(final_proposal.get('genai_solutions', {}))}

### Implementation Roadmap

{self._format_roadmap_markdown(final_proposal.get('implementation_roadmap', {}))}

### Resources Available

- **Kaggle Datasets**: {final_proposal.get('resource_summary', {}).get('kaggle_datasets', 0)}
- **HuggingFace Resources**: {final_proposal.get('resource_summary', {}).get('huggingface_resources', 0)}
- **GitHub Repositories**: {final_proposal.get('resource_summary', {}).get('github_repositories', 0)}

[View Detailed Resources]({final_proposal.get('resource_summary', {}).get('resource_file', '')})

### Next Steps

{self._format_next_steps_markdown(final_proposal.get('next_steps', []))}

---

*Generated by Multi-Agent Market Research System*
"""
            
            # Save report
            company_name_clean = company_name.replace(" ", "_").lower()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{Config.REPORTS_DIR}/summary_report_{company_name_clean}_{timestamp}.md"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            logger.info(f"Summary report saved to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error generating summary report: {str(e)}")
            return ""
    
    def _count_use_cases(self, usecase_data: Dict) -> int:
        """Count total number of use cases generated"""
        try:
            use_cases = usecase_data.get("generated_use_cases", {})
            if isinstance(use_cases, dict):
                # For enhanced format, we know there are exactly 10 use cases
                if use_cases.get("format") == "enhanced_detailed":
                    return 10
                # Count nested use cases for other formats
                count = 0
                for category in use_cases.values():
                    if isinstance(category, list):
                        count += len(category)
                    elif isinstance(category, dict):
                        count += len(category)
                return count
            elif isinstance(use_cases, list):
                return len(use_cases)
            return 0
        except:
            return 0
    
    def _get_fast_fallback_resources(self, company_name: str) -> Dict[str, Any]:
        """Get fast fallback resources without API calls"""
        logger.info("Using fast fallback resources...")
        
        # Quick fallback resources that don't require API calls
        fallback_resources = {
            "kaggle": {
                "datasets": [
                    {
                        "title": f"{company_name} Industry Dataset",
                        "url": "https://www.kaggle.com/datasets",
                        "description": "Industry-specific datasets for AI/ML applications",
                        "platform": "Kaggle",
                        "search_term": "industry"
                    }
                ],
                "count": 1
            },
            "huggingface": {
                "resources": [
                    {
                        "title": "Industry AI Models",
                        "url": "https://huggingface.co/models",
                        "description": "Pre-trained models for industry applications",
                        "platform": "HuggingFace",
                        "type": "model",
                        "search_term": "industry"
                    }
                ],
                "count": 1
            },
            "github": {
                "repositories": [
                    {
                        "title": "AI Industry Solutions",
                        "url": "https://github.com",
                        "description": "Open source AI solutions for industry applications",
                        "platform": "GitHub",
                        "search_term": "industry"
                    }
                ],
                "count": 1
            },
            "search_terms_used": ["industry", "AI", "ML"],
            "industry": "General",
            "agent": "ResourceAgent",
            "status": "fast_fallback_completed"
        }
        
        return fallback_resources
    
    def _get_ultra_fast_research(self, company_name: str) -> Dict[str, Any]:
        """Get ultra-fast research using pre-built templates"""
        logger.info("Using ultra-fast research template...")
        
        # Pre-built research template for common companies
        research_templates = {
            "tesla": {
                "company_name": "Tesla",
                "identified_industry": "Automotive",
                "analysis": {
                    "company_analysis": {
                        "business_model": "Electric vehicle manufacturer and clean energy company",
                        "key_offerings": "Electric vehicles, energy storage, solar panels, autonomous driving",
                        "strategic_focus": "Sustainable transportation and energy solutions"
                    },
                    "industry_analysis": {
                        "industry": "Automotive",
                        "market_trends": "Electric vehicle adoption, autonomous driving, sustainability",
                        "growth_opportunities": "AI-powered autonomous vehicles, energy management, manufacturing optimization"
                    }
                },
                "agent": "ResearchAgent",
                "status": "ultra_fast_completed"
            },
            "apple": {
                "company_name": "Apple",
                "identified_industry": "Technology",
                "analysis": {
                    "company_analysis": {
                        "business_model": "Consumer electronics and software company",
                        "key_offerings": "iPhone, iPad, Mac, Apple Watch, services, software",
                        "strategic_focus": "Innovation, user experience, ecosystem integration"
                    },
                    "industry_analysis": {
                        "industry": "Technology",
                        "market_trends": "Mobile computing, wearables, services, AI integration",
                        "growth_opportunities": "AI-powered features, health monitoring, augmented reality"
                    }
                },
                "agent": "ResearchAgent",
                "status": "ultra_fast_completed"
            }
        }
        
        # Check if we have a template for this company
        company_key = company_name.lower()
        if company_key in research_templates:
            return research_templates[company_key]
        
        # Generic template for unknown companies
        return {
            "company_name": company_name,
            "identified_industry": "Technology",
            "analysis": {
                "company_analysis": {
                    "business_model": f"{company_name} is a technology company",
                    "key_offerings": "Technology products and services",
                    "strategic_focus": "Innovation and growth"
                },
                "industry_analysis": {
                    "industry": "Technology",
                    "market_trends": "Digital transformation and AI adoption",
                    "growth_opportunities": "AI/ML implementation, automation, data analytics"
                }
            },
            "agent": "ResearchAgent",
            "status": "ultra_fast_completed"
        }
    
    def set_use_case_count(self, count: int):
        """
        Set the number of use cases to generate (configurable)
        
        Args:
            count: Number of use cases to generate (default: 10)
        """
        self.use_case_count = count
    
    def _count_resources(self, resource_data: Dict) -> int:
        """Count total number of resources found"""
        try:
            total = 0
            total += resource_data.get("kaggle", {}).get("count", 0)
            total += resource_data.get("huggingface", {}).get("count", 0)
            total += resource_data.get("github", {}).get("count", 0)
            return total
        except:
            return 0
    
    def _generate_implementation_roadmap(self, prioritized_use_cases: Dict) -> Dict[str, Any]:
        """Generate a detailed implementation roadmap with tasks and durations"""
        return {
            "Phase 1 - Discovery (1-2 weeks)": [
                "Stakeholder alignment and scope definition",
                "Data inventory and access provisioning",
                "Success metrics and KPI baselining"
            ],
            "Phase 2 - Prototype (3-4 weeks)": [
                "Feature engineering and model baselines",
                "Rapid iterations with offline evaluation",
                "Demo with business stakeholders"
            ],
            "Phase 3 - Pilot (4-6 weeks)": [
                "Integrate data pipelines (batch/stream)",
                "Deploy API/notebook for limited audience",
                "A/B testing and KPI uplift measurement"
            ],
            "Phase 4 - Productionization (4-8 weeks)": [
                "MLOps setup (CI/CD, model registry, monitoring)",
                "Security, compliance, and rollback strategy",
                "Runbooks and handover"
            ],
            "Phase 5 - Scale & Enablement (ongoing)": [
                "Scale to additional use cases",
                "Training and center-of-excellence",
                "Continuous improvement backlog"
            ]
        }
    
    def _format_recommendations_markdown(self, recommendations: Dict) -> str:
        """Format recommendations for markdown"""
        if isinstance(recommendations, str):
            return recommendations
        elif isinstance(recommendations, dict) and "prioritization_analysis" in recommendations:
            return recommendations["prioritization_analysis"]
        return "Top AI/ML recommendations will be displayed here."
    
    def _format_genai_solutions_markdown(self, genai_solutions: Dict) -> str:
        """Format GenAI solutions for markdown"""
        if isinstance(genai_solutions, str):
            return genai_solutions
        elif isinstance(genai_solutions, dict) and "genai_solutions" in genai_solutions:
            return genai_solutions["genai_solutions"]
        return "GenAI solutions will be displayed here."
    
    def _format_roadmap_markdown(self, roadmap: Dict) -> str:
        """Format implementation roadmap for markdown"""
        if not roadmap:
            return "Implementation roadmap will be generated."
        
        markdown = ""
        for phase, description in roadmap.items():
            markdown += f"**{phase}**\n"
            if isinstance(description, list):
                for t in description:
                    markdown += f"- {t}\n"
            else:
                markdown += f"- {description}\n"
            markdown += "\n"
        return markdown
    
    def _format_next_steps_markdown(self, next_steps: list) -> str:
        """Format next steps for markdown"""
        if not next_steps:
            return "Next steps will be provided."
        
        markdown = ""
        for i, step in enumerate(next_steps, 1):
            markdown += f"{i}. {step}\n"
        return markdown


def main():
    """Main function for testing the orchestrator"""
    orchestrator = MarketResearchOrchestrator()
    
    # Test with a sample company
    test_company = "Tesla"
    results = orchestrator.run_complete_analysis(test_company)
    
    if results.get("workflow_status") == "completed":
        print(f"Analysis completed successfully for {test_company}")
        print(f"Results saved to: {results.get('results_file')}")
        
        # Generate summary report
        summary_file = orchestrator.generate_summary_report(results)
        print(f"Summary report saved to: {summary_file}")
    else:
        print(f"Analysis failed: {results.get('error', 'Unknown error')}")


if __name__ == "__main__":
    main()
