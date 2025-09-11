"""
Streamlit Web Interface for Multi-Agent Market Research System
"""

import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime
from io import BytesIO
from orchestrator import MarketResearchOrchestrator
from config import Config
import plotly.express as px
import plotly.graph_objects as go

# Auto-clean .env file on startup
try:
    from utils.env_cleaner import auto_fix_env_file
    auto_fix_env_file()
except ImportError:
    pass  # Continue if env_cleaner is not available

# Configure Streamlit page
st.set_page_config(
    page_title="AI Market Research Agent",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    
    .agent-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
        color: #333333;
    }
    
    .agent-card h3 {
        color: #333333 !important;
        margin-bottom: 1rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    
    .error-message {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
        color: #721c24;
    }
    
    .warning-message {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 1rem;
        color: #856404;
    }
    /* Sidebar chat message color */
    .chatline { color: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'analysis_running' not in st.session_state:
        st.session_state.analysis_running = False
    if 'orchestrator' not in st.session_state:
        st.session_state.orchestrator = None
    if 'nav_section' not in st.session_state:
        st.session_state.nav_section = "Company Overview"
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []  # list of {role, content}

def _repo_search(query: str, max_hits: int = 3) -> list:
    """Lightweight keyword search across docs and key files."""
    import glob
    import os
    hits = []
    # Restrict to safe, known file patterns only
    allowed_files = [
        "PROJECT_SUMMARY.md", "QUICK_START.md", "SETUP_GUIDE.md", "SECURITY_REPORT.md",
        "docs/**/*.md", "agents/**/*.py", "orchestrator.py", "streamlit_app.py"
    ]
    patterns = []
    for pattern in allowed_files:
        # Prevent path traversal by normalizing and checking paths
        matches = glob.glob(pattern, recursive=True)
        for match in matches:
            normalized = os.path.normpath(match)
            # Only allow files in current directory tree
            if not normalized.startswith('..') and os.path.exists(normalized):
                patterns.append(normalized)
    
    query_l = query.lower()[:100]  # Limit query length
    for path in patterns[:20]:  # Limit file count
        try:
            # Additional safety: check file size before reading
            if os.path.getsize(path) > 1024 * 1024:  # Skip files > 1MB
                continue
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read(50000)  # Limit read size
            if query_l in text.lower():
                # capture a short snippet
                snippet = text[max(0, text.lower().find(query_l) - 100): text.lower().find(query_l) + 200]
                hits.append({"file": os.path.basename(path), "snippet": snippet.strip()[:300]})
                if len(hits) >= max_hits:
                    break
        except Exception:
            continue
    return hits

def _assistant_answer(question: str) -> str:
    """Intelligent AI assistant with comprehensive access to all analysis data."""
    q = question.strip().lower()
    
    # Get current analysis results
    results = st.session_state.get('analysis_results', {})
    running = st.session_state.get('analysis_running', False)
    
    # Check if analysis exists and is complete
    has_analysis = results and isinstance(results, dict) and results.get('workflow_status') == 'completed'
    company_name = results.get('company_name', 'the company') if has_analysis else None
    
    # Helper function to get comprehensive analysis data
    def _get_comprehensive_data():
        if not has_analysis:
            return None
        
        data = {
            'company': company_name,
            'research': {},
            'use_cases': {},
            'resources': {},
            'implementation': {}
        }
        
        agent_results = results.get('agent_results', {})
        
        # Research Agent data
        research_data = agent_results.get('research', {})
        if research_data:
            data['research'] = {
                'industry': research_data.get('identified_industry', ''),
                'analysis': research_data.get('analysis', {}),
                'citations': research_data.get('citations', [])
            }
        
        # Use Case Agent data
        usecase_data = agent_results.get('use_cases', {})
        if usecase_data:
            data['use_cases'] = {
                'formatted': usecase_data.get('formatted_use_cases', ''),
                'raw': usecase_data.get('raw_use_cases', ''),
                'prioritized': usecase_data.get('prioritized_recommendations', {}),
                'genai': usecase_data.get('genai_solutions', {})
            }
        
        # Resource Agent data
        resource_data = agent_results.get('resources', {})
        if resource_data:
            data['resources'] = {
                'list': resource_data.get('resources', []),
                'industry': resource_data.get('industry', ''),
                'file': results.get('resource_file', ''),
                'datasets_md': results.get('datasets_markdown', '')
            }
        
        # Implementation data
        final_proposal = results.get('final_proposal', {})
        if final_proposal:
            data['implementation'] = {
                'roadmap': final_proposal.get('implementation_roadmap', {}),
                'next_steps': final_proposal.get('next_steps', []),
                'summary': final_proposal.get('summary', '')
            }
        
        return data
    
    # Get comprehensive data
    data = _get_comprehensive_data()
    
    # Handle different types of questions
    if any(p in q for p in ["hi", "hello", "hey", "greetings"]):
        if has_analysis:
            return f"Hello! I can help you with detailed questions about the analysis of {company_name}. I have access to all the research data, use cases, resources, and implementation plans. What would you like to know?"
        else:
            return "Hello! I'm your AI assistant. Please run an analysis first by entering a company name and clicking Start Analysis, then I can help you with detailed questions about the results."
    
    # Check if analysis exists
    if not has_analysis:
        if any(p in q for p in ["did i run", "have i run", "analysis", "run analysis"]):
            return "No, you haven't run an analysis yet. Please enter a company name in the input field and click 'Start Analysis' to begin. Once the analysis is complete, I'll have access to all the detailed data and can answer any questions you have."
        return "No analysis available yet. Please run an analysis first by entering a company name and clicking Start Analysis, then I can provide detailed answers about the results."
    
    # Use case specific questions
    if any(p in q for p in ["use case", "use cases", "explain", "detail", "detailed", "cloud infrastructure", "optimization", "ai-enhanced", "data analytics", "business insights", "predictive", "recommendation", "automation", "intelligent"]):
        if data and data['use_cases'].get('formatted'):
            formatted_cases = data['use_cases']['formatted']
            
            # Search for specific use case by keywords
            lines = formatted_cases.split('\n')
            matching_cases = []
            current_case = []
            in_use_case = False
            
            for line in lines:
                if line.startswith('**Use Case') and ':' in line:
                    if current_case and in_use_case:
                        case_text = '\n'.join(current_case).lower()
                        # Check if this case matches the query
                        if any(keyword in case_text for keyword in q.split()):
                            matching_cases.append('\n'.join(current_case))
                    current_case = [line]
                    in_use_case = True
                elif in_use_case and line.strip():
                    current_case.append(line)
                    if len(current_case) > 30:  # Full case details
                        case_text = '\n'.join(current_case).lower()
                        if any(keyword in case_text for keyword in q.split()):
                            matching_cases.append('\n'.join(current_case))
                        current_case = []
                        in_use_case = False
            
            if current_case and in_use_case:
                case_text = '\n'.join(current_case).lower()
                if any(keyword in case_text for keyword in q.split()):
                    matching_cases.append('\n'.join(current_case))
            
            if matching_cases:
                response = f"Here are the matching use cases for '{question}':\n\n"
                for i, case in enumerate(matching_cases[:2], 1):
                    response += f"--- MATCHING USE CASE {i} ---\n{case}\n\n"
                return response
            
            # If no specific match, show first few detailed use cases
            detailed_cases = []
            current_case = []
            in_use_case = False
            
            for line in lines:
                if line.startswith('**Use Case') and ':' in line:
                    if current_case and in_use_case:
                        detailed_cases.append('\n'.join(current_case))
                    current_case = [line]
                    in_use_case = True
                elif in_use_case and line.strip():
                    current_case.append(line)
                    if len(current_case) > 25:  # Full case details
                        detailed_cases.append('\n'.join(current_case))
                        current_case = []
                        in_use_case = False
            
            if current_case and in_use_case:
                detailed_cases.append('\n'.join(current_case))
            
            if detailed_cases:
                response = f"Here are the detailed AI/ML use cases for {company_name}:\n\n"
                for i, case in enumerate(detailed_cases[:3], 1):
                    response += f"--- USE CASE {i} ---\n{case}\n\n"
                
                remaining = len(detailed_cases) - 3
                if remaining > 0:
                    response += f"... and {remaining} more use cases. See the Development Use Cases section for complete details."
                
                return response
        
        return f"No use cases found for '{question}'. The analysis may still be processing or the use cases may not contain those specific terms."
    
    # Company/business questions
    if any(p in q for p in ["company", "business", "industry", "analysis", "what is", "tell me about"]):
        if data and data['research']:
            research = data['research']
            analysis = research.get('analysis', {})
            
            response = f"**Comprehensive Analysis of {company_name}:**\n\n"
            
            if research.get('industry'):
                response += f"**Industry:** {research['industry']}\n\n"
            
            if analysis.get('business_model'):
                response += f"**Business Model:** {analysis['business_model']}\n\n"
            
            if analysis.get('key_offerings'):
                offerings = analysis['key_offerings']
                if isinstance(offerings, list):
                    response += f"**Key Offerings:** {', '.join(offerings)}\n\n"
                else:
                    response += f"**Key Offerings:** {offerings}\n\n"
            
            if analysis.get('strategic_focus'):
                response += f"**Strategic Focus:** {analysis['strategic_focus']}\n\n"
            
            if analysis.get('market_position'):
                response += f"**Market Position:** {analysis['market_position']}\n\n"
            
            if analysis.get('growth_opportunities'):
                opportunities = analysis['growth_opportunities']
                if isinstance(opportunities, list):
                    response += f"**Growth Opportunities:** {', '.join(opportunities)}\n\n"
                else:
                    response += f"**Growth Opportunities:** {opportunities}\n\n"
            
            if analysis.get('competitors'):
                competitors = analysis['competitors']
                if isinstance(competitors, list):
                    response += f"**Competitors:** {', '.join(competitors)}\n\n"
                else:
                    response += f"**Competitors:** {competitors}\n\n"
            
            return response
        
        return f"No detailed company analysis available for {company_name}."
    
    # Resource questions
    if any(p in q for p in ["resource", "resources", "dataset", "datasets", "kaggle", "huggingface", "github"]):
        if data and data['resources'].get('list'):
            resources = data['resources']['list']
            
            response = f"**Resources Found for {company_name}:**\n\n"
            response += f"**Total Resources:** {len(resources)}\n\n"
            
            # Group by platform
            platforms = {}
            for res in resources:
                platform = res.get('platform', 'Unknown')
                if platform not in platforms:
                    platforms[platform] = []
                platforms[platform].append(res)
            
            for platform, platform_resources in platforms.items():
                response += f"**{platform} ({len(platform_resources)} resources):**\n"
                for res in platform_resources[:5]:  # Show first 5 per platform
                    title = res.get('title', 'Unknown')
                    url = res.get('url', '')
                    if url:
                        response += f"• <a href=\"{url}\" target=\"_blank\">{title}</a>\n"
                    else:
                        response += f"• {title}\n"
                response += "\n"
            
            if data['resources'].get('datasets_md'):
                response += f"**Datasets Markdown:** Available at `{data['resources']['datasets_md']}`\n"
            
            return response
        
        return f"No resources available for {company_name}."
    
    # Implementation questions
    if any(p in q for p in ["implementation", "roadmap", "plan", "timeline", "cost", "effort", "next steps"]):
        if data and data['implementation']:
            impl = data['implementation']
            
            response = f"**Implementation Plan for {company_name}:**\n\n"
            
            if impl.get('roadmap'):
                response += "**Implementation Roadmap:**\n"
                for phase, desc in impl['roadmap'].items():
                    response += f"• **{phase.replace('_', ' ').title()}:** {desc}\n"
                response += "\n"
            
            if impl.get('next_steps'):
                response += "**Next Steps:**\n"
                for i, step in enumerate(impl['next_steps'], 1):
                    response += f"{i}. {step}\n"
                response += "\n"
            
            if impl.get('summary'):
                response += f"**Summary:** {impl['summary']}\n"
            
            return response
        
        return f"No implementation plan available for {company_name}."
    
    # General questions - provide comprehensive overview
    if data:
        response = f"**Complete Analysis Summary for {company_name}:**\n\n"
        
        # Research summary
        if data['research']:
            research = data['research']
            response += f"**Industry:** {research.get('industry', 'N/A')}\n"
            analysis = research.get('analysis', {})
            if analysis.get('business_model'):
                response += f"**Business Model:** {analysis['business_model']}\n"
            response += "\n"
        
        # Use cases summary
        if data['use_cases'].get('formatted'):
            total_cases = data['use_cases']['formatted'].count('**Use Case')
            response += f"**Use Cases Generated:** {total_cases} detailed AI/ML solutions\n\n"
        
        # Resources summary
        if data['resources'].get('list'):
            resources = data['resources']['list']
            response += f"**Resources Found:** {len(resources)} high-quality datasets and repositories\n"
            
            # Platform distribution
            platforms = {}
            for res in resources:
                platform = res.get('platform', 'Unknown')
                platforms[platform] = platforms.get(platform, 0) + 1
            
            platform_dist = ', '.join([f"{k}: {v}" for k, v in platforms.items()])
            response += f"**Platform Distribution:** {platform_dist}\n\n"
        
        response += "I can provide detailed information about any specific aspect. What would you like to know more about?"
        return response
    
    return "I have access to comprehensive analysis data. Please ask me specific questions about the company, use cases, resources, or implementation plans, and I'll provide detailed answers."

def load_orchestrator():
    """Load and initialize the orchestrator"""
    try:
        if st.session_state.orchestrator is None:
            with st.spinner("Initializing AI agents..."):
                        st.session_state.orchestrator = MarketResearchOrchestrator(fast_mode=True, ultra_fast_mode=False)
        return True
    except Exception as e:
        st.error(f"Failed to initialize the system: {str(e)}")
        st.error("Please check your API keys in the .env file")
        return False

def display_header():
    """Display the main header and description"""
    st.markdown('<h1 class="main-header">Multi-Agent Market Research System</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; font-size: 1.2rem; color: #666; margin-bottom: 2rem;">
        Intelligent AI-powered market research with industry analysis, use case generation, and resource collection
    </div>
    """, unsafe_allow_html=True)
    
    # Display agent information
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="agent-card">
            <h3>Research Agent</h3>
            <p>Conducts comprehensive industry and company research using advanced web browsing capabilities</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="agent-card">
            <h3>Use Case Agent</h3>
            <p>Generates relevant AI/ML use cases and analyzes market standards for digital transformation</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="agent-card">
            <h3>Resource Agent</h3>
            <p>Collects datasets and resources from Kaggle, HuggingFace, and GitHub for implementation</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Chatbot UI above Company Analysis
    st.markdown("---")
    st.markdown("### Customer AI Assistance")
    if not st.session_state.chat_history:
        st.write("Type a question below to get help.")
    for msg in st.session_state.chat_history[-6:]:
        role = msg.get('role', 'assistant')
        content = msg.get('content', '')
        if role == 'user':
            st.markdown(f"<span class='chatline'><strong>You:</strong> {content}</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"<span class='chatline'><strong>Assistant:</strong> {content}</span>", unsafe_allow_html=True)
    with st.form("assistant_form_main", clear_on_submit=True):
        user_q = st.text_input("Ask a question", key="assistant_q_main", label_visibility="collapsed")
        submitted = st.form_submit_button("Send")
    if submitted and user_q.strip():
        st.session_state.chat_history.append({"role": "user", "content": user_q.strip()})
        answer = _assistant_answer(user_q)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()

def validate_company_name(company_name):
    """Validate and sanitize company name input"""
    if not company_name:
        return None, "Company name cannot be empty"
    
    # Remove extra whitespace
    company_name = company_name.strip()
    
    # Check length
    if len(company_name) < 2:
        return None, "Company name must be at least 2 characters"
    
    if len(company_name) > 100:
        return None, "Company name must be less than 100 characters"
    
    # Check for potentially malicious input
    dangerous_patterns = ['<script', 'javascript:', 'data:', 'vbscript:', 'onload=', 'onerror=']
    for pattern in dangerous_patterns:
        if pattern.lower() in company_name.lower():
            return None, "Invalid characters detected in company name"
    
    # Check for SQL injection patterns
    sql_patterns = ['union', 'select', 'insert', 'delete', 'drop', 'update', 'exec', 'execute']
    for pattern in sql_patterns:
        if pattern.lower() in company_name.lower():
            return None, "Invalid characters detected in company name"
    
    # Allow only alphanumeric, spaces, hyphens, apostrophes, and periods
    import re
    if not re.match(r"^[a-zA-Z0-9\s\-'\.&]+$", company_name):
        return None, "Company name contains invalid characters"
    
    return company_name, None

def display_input_form():
    """Display the input form for company analysis"""
    st.markdown("## Company Analysis")
    
    with st.form("analysis_form"):
        company_name = st.text_input(
            "Enter Company Name",
            placeholder="e.g., Tesla, Amazon, Microsoft",
            help="Enter the name of the company you want to analyze",
            max_chars=100
        )
        
        col1, col2 = st.columns([1, 2])
        with col1:
            start_btn = st.form_submit_button("Start Analysis", type="primary")
        with col2:
            quick_btn = st.form_submit_button("Quick Analysis Download")
        
        if start_btn or quick_btn:
            if not company_name:
                st.error("Please enter a company name")
                return None
            
            # Validate input
            validated_name, error = validate_company_name(company_name)
            if error:
                st.error(error)
                return None
            
            return {"action": "quick" if quick_btn and not start_btn else "start", "company": validated_name}
    
    return None

def run_analysis(company_name):
    """Run the complete analysis workflow"""
    st.session_state.analysis_running = True
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Research Agent
        status_text.text("Research Agent: Ultra-fast analysis...")
        progress_bar.progress(25)
        
        # Step 2: Use Case Agent
        status_text.text("Use Case Agent: Generating AI/ML use cases...")
        progress_bar.progress(50)
        
        # Step 3: Resource Agent
        status_text.text("Resource Agent: Fast resource collection...")
        progress_bar.progress(75)
        
        # Run the actual analysis
        results = st.session_state.orchestrator.run_complete_analysis(company_name)
        
        # Complete
        status_text.text("Analysis completed successfully!")
        progress_bar.progress(100)
        
        st.session_state.analysis_results = results
        st.session_state.analysis_running = False
        
        if results.get("workflow_status") == "completed":
            st.success("Analysis completed successfully!")
        elif results.get("workflow_status") == "partial":
            st.warning(f"Analysis completed with warnings: {results.get('error', 'Unknown error occurred')}")
        else:
            st.error(f"Analysis failed: {results.get('error', 'Unknown error occurred')}")
            
    except Exception as e:
        st.error(f"Analysis failed: {str(e)}")
        st.session_state.analysis_running = False

def quick_download(company_name):
    """Generate a quick Excel with use cases, descriptions, and dataset links without full analysis."""
    try:
        orch = st.session_state.orchestrator
        # Prefer existing analysis if present for richer descriptions
        existing = st.session_state.get('analysis_results') or {}
        formatted = existing.get('agent_results', {}).get('use_cases', {}).get('generated_use_cases', {}).get('formatted_use_cases', '')
        if not formatted:
            # Fast fallback research and expanded use cases (10)
            research = orch._fallback_research(company_name)
            uc = orch._fallback_use_cases(research)
            formatted = uc.get("generated_use_cases", {}).get("formatted_use_cases", "")
        use_cases = parse_use_cases(formatted)
        resource_agent = getattr(orch, 'resource_agent', None)
        # Build Excel data
        excel_rows = []
        for i, use_case in enumerate(use_cases, 1):
            title = use_case.get("title", f"Use Case {i}")
            desc_parts = [use_case.get("objective", "Description not available")]
            ai_app = use_case.get("ai_application")
            if ai_app and ai_app not in desc_parts[0]:
                desc_parts.append(f"AI Application: {ai_app}")
            desc = " \n".join([p for p in desc_parts if p])
            refs = []
            if resource_agent:
                try:
                    fetched = resource_agent.fetch_datasets(title, desc)
                    for r in fetched:
                        url = r.get('url', '')
                        name = r.get('title') or url
                        if url:
                            # Plain URL lines for Excel per sample format
                            refs.append(url)
                except Exception:
                    pass
            excel_rows.append({
                "Use Case": title,
                "Description": desc,
                "References": "\n".join(refs) if refs else "No dataset found"
            })
        import pandas as pd
        from io import BytesIO
        output = BytesIO()
        df = pd.DataFrame(excel_rows)
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Quick Analysis', index=False)
            ws = writer.sheets['Quick Analysis']
            for column in ws.columns:
                max_len = 0
                col_letter = column[0].column_letter
                for cell in column:
                    try:
                        max_len = max(max_len, len(str(cell.value)))
                    except Exception:
                        pass
                ws.column_dimensions[col_letter].width = min(max_len + 2, 60)
        output.seek(0)
        st.download_button(
            label="📥 Download Quick Analysis (Excel)",
            data=output.getvalue(),
            file_name=f"quick_analysis_{company_name.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"quick_dl_{company_name}_{datetime.now().timestamp()}"
        )
        st.success("Quick analysis ready for download.")
    except Exception as e:
        st.error(f"Quick download failed: {e}")

def display_results():
    """Display the analysis results based on sidebar navigation"""
    if not st.session_state.analysis_results:
        return
    
    results = st.session_state.analysis_results
    if results.get("workflow_status") != "completed":
        return
    
    st.markdown("## Analysis Results")
    section = st.session_state.get('nav_section', "Company Overview")
    
    if section == "Company Overview":
        display_company_overview(results)
    elif section == "Development Use Cases":
        display_recommendations(results)
    elif section == "Resources":
        display_resources(results)
    elif section == "Implementation Plan":
        display_implementation_plan(results)

def parse_use_cases(formatted_text):
    """Parse the formatted use cases text into structured data"""
    use_cases = []
    if not formatted_text:
        return use_cases
    # Primary format: blocks starting with **Use Case...
    use_case_blocks = formatted_text.split("**Use Case")
    for block in use_case_blocks[1:]:
        if not block.strip():
            continue
        use_case = {}
        title_part = ""
        if "**Objective" in block:
            title_part = block.split("**Objective")[0].strip()
        else:
            lines = block.strip().split('\n')
            title_part = lines[0].strip() if lines else "Use Case"
        if ":" in title_part:
            use_case["title"] = title_part.split(":", 1)[1].strip()
        else:
            use_case["title"] = title_part.replace("**", "").strip()
        objective_text = ""
        if "**Objective/Use Case:" in block:
            obj_start = block.find("**Objective/Use Case:")
            if "**AI Application:" in block:
                obj_end = block.find("**AI Application:")
                objective_text = block[obj_start:obj_end].strip()
            else:
                objective_text = block[obj_start:].strip()
        elif "**Objective:" in block:
            obj_start = block.find("**Objective:")
            if "**AI Application:" in block:
                obj_end = block.find("**AI Application:")
                objective_text = block[obj_start:obj_end].strip()
            else:
                objective_text = block[obj_start:].strip()
        if objective_text:
            if ":" in objective_text:
                use_case["objective"] = objective_text.split(":", 1)[1].strip().replace("**", "")
            else:
                use_case["objective"] = objective_text.replace("**Objective/Use Case:", "").replace("**Objective:", "").replace("**", "").strip()
        else:
            use_case["objective"] = "Objective not available"
        if use_case.get("title") and use_case["title"] != "Use Case":
            use_cases.append(use_case)
    # Fallback format: blocks like **Title** then **Objective:** ...
    if not use_cases:
        import re
        pattern = re.compile(r"\*\*([^*]+)\*\*[\s\S]*?\*\*Objective[^:]*:\s*(.*?)(?:\n\*\*|$)", re.MULTILINE)
        for m in pattern.finditer(formatted_text):
            title = m.group(1).strip()
            objective = m.group(2).strip()
            if title:
                use_cases.append({
                    "title": title,
                    "objective": objective
                })
    return use_cases

def display_company_overview(results):
    """Display enhanced company overview with robust parsing and fallbacks"""
    st.markdown("### Company Overview")
    
    research_data = results.get("agent_results", {}).get("research", {})
    company_analysis = research_data.get("analysis", {})
    # If analysis contains raw JSON inside a string, try to extract
    if isinstance(company_analysis, dict) and "raw_analysis" in company_analysis:
        raw = company_analysis.get("raw_analysis", "")
        try:
            if "```" in raw:
                block = raw.split("```json")
                if len(block) > 1:
                    json_block = block[1].split("```", 1)[0]
                else:
                    json_block = raw.split("```", 1)[1].split("```", 1)[0]
                company_analysis = json.loads(json_block)
            else:
                company_analysis = json.loads(raw)
        except Exception:
            pass
    company_name = research_data.get("company_name", "the company")
    industry = research_data.get("identified_industry", "")
    
    if isinstance(company_analysis, dict):
        if "company_analysis" in company_analysis:
            ca = company_analysis["company_analysis"]
            
            # Enhanced Business Information
            st.markdown("### **Businesses**")
            businesses = ca.get('businesses', [])
            if businesses and isinstance(businesses, list):
                for business in businesses:
                    if isinstance(business, dict):
                        st.markdown(f"**• {business.get('name', 'Business')}**")
                        st.write(f"   {business.get('description', 'Description not available')}")
                    else:
                        st.write(f"• {business}")
            else:
                # Fallback to business_model if businesses not available
                business_model = ca.get('business_model', 'Information not available')
                st.write(business_model)
            
            # Enhanced Products Information
            st.markdown("### **Products**")
            products = ca.get('products', [])
            if products and isinstance(products, list):
                for product in products:
                    if isinstance(product, dict):
                        st.markdown(f"**• {product.get('name', 'Product')}**")
                        st.write(f"   {product.get('description', 'Description not available')}")
                    else:
                        st.write(f"• {product}")
            else:
                # Fallback to key_offerings if products not available
                offerings = ca.get('key_offerings', 'Information not available')
                if isinstance(offerings, list):
                    for offering in offerings:
                        st.write(f"• {offering}")
                else:
                    st.write(offerings)
            
            # Enhanced Segments Information
            st.markdown("### **Segments**")
            segments = ca.get('segments', [])
            if segments and isinstance(segments, list):
                for segment in segments:
                    if isinstance(segment, dict):
                        st.markdown(f"**• {segment.get('name', 'Segment')}**")
                        st.write(f"   {segment.get('description', 'Description not available')}")
                    else:
                        st.write(f"• {segment}")
            else:
                # Fallback to industry if segments not available
                st.write(industry if industry else "Information not available")

            # Competitors
            competitors = ca.get('competitors', [])
            if competitors:
                st.markdown("### **Competitors**")
                for comp in competitors:
                    if isinstance(comp, dict):
                        name = comp.get('name', 'Competitor')
                        reason = comp.get('reason', '')
                        if reason:
                            st.write(f"• {name}: {reason}")
                        else:
                            st.write(f"• {name}")
                    else:
                        st.write(f"• {comp}")
        
        # Enhanced Industry Analysis
        if "industry_analysis" in company_analysis:
            ia = company_analysis["industry_analysis"]
            
            st.markdown("### **Industry Trends**")
            trends = ia.get('market_trends', 'Information not available')
            if isinstance(trends, list):
                for trend in trends:
                    if isinstance(trend, dict):
                        st.markdown(f"**• {trend.get('trend', 'Trend')}**")
                        st.write(f"   {trend.get('description', 'Description not available')}")
                    else:
                        st.write(f"• {trend}")
            else:
                st.write(trends)
            
            st.markdown("### **Strategic Focus**")
            focus = ia.get('strategic_focus', 'Information not available')
            if isinstance(focus, list):
                for item in focus:
                    if isinstance(item, dict):
                        st.markdown(f"**• {item.get('area', 'Area')}**")
                        st.write(f"   {item.get('description', 'Description not available')}")
                    else:
                        st.write(f"• {item}")
            else:
                st.write(focus)
            
            st.markdown("### **Growth Opportunities**")
            opportunities = ia.get('growth_opportunities', 'Information not available')
            if isinstance(opportunities, list):
                for opportunity in opportunities:
                    if isinstance(opportunity, dict):
                        st.markdown(f"**• {opportunity.get('opportunity', 'Opportunity')}**")
                        st.write(f"   {opportunity.get('description', 'Description not available')}")
                    else:
                        st.write(f"• {opportunity}")
            else:
                st.write(opportunities)
        # Citations if present
        citations = company_analysis.get("citations") if isinstance(company_analysis, dict) else None
        if citations:
            st.markdown("### **Citations**")
            for c in citations:
                if isinstance(c, dict):
                    title = c.get("title", c.get("url", "Source"))
                    url = c.get("url", "")
                    src = c.get("source", "")
                    st.write(f"• [{title}]({url}) — {src}")
    else:
        st.write("Company overview information is being processed...")

def display_recommendations(results):
    """Display top recommendations section"""
    st.markdown("### Development Use Cases")
    
    usecase_data = results.get("agent_results", {}).get("use_cases", {})
    
    # Display the 10 detailed use cases with proper formatting
    generated_use_cases = usecase_data.get("generated_use_cases", {})
    if isinstance(generated_use_cases, dict) and "formatted_use_cases" in generated_use_cases:
        formatted_text = generated_use_cases["formatted_use_cases"]
        
        # Parse and format the use cases properly
        use_cases = parse_use_cases(formatted_text)
        
        for i, use_case in enumerate(use_cases, 1):
            title = use_case.get('title', 'Use Case')
            st.markdown(f"### **{title}**")
            
            # Objective (always)
            st.markdown(f"**Objective/Use Case:** {use_case.get('objective', 'Objective not available')}")
            
            # AI Application (fallback to heuristic if missing)
            ai_app = use_case.get('ai_application')
            if not ai_app:
                ai_app = "Apply machine learning models to the described objective, leveraging available first-party and third-party datasets to deliver measurable outcomes."
            st.markdown(f"**AI Application:** {ai_app}")
            
            # Cross-Functional Benefit (fallback list)
            cf = use_case.get('cross_functional_benefit')
            if not cf:
                cf = "- Operations: Improved efficiency and throughput\n- Finance: Better forecasting and cost control\n- IT/Data: Stronger data pipelines and governance"
            st.markdown("**Cross-Functional Benefit:**")
            st.markdown(cf)

            # Business Impact (only if provided by generator)
            if use_case.get('business_impact'):
                st.markdown("**Business Impact:**")
                st.markdown(use_case['business_impact'])

            # KPIs, Effort/Cost, Risks, Pilot (if present)
            if use_case.get('kpis'):
                st.markdown("**KPIs:**")
                st.markdown(use_case['kpis'])
            if use_case.get('effort_cost'):
                st.markdown("**Effort & Cost:**")
                st.markdown(use_case['effort_cost'])
            if use_case.get('risks'):
                st.markdown("**Risks & Compliance:**")
                st.markdown(use_case['risks'])
            # Pilot plan removed by spec (no rendering)
            
            st.markdown("---")  # Separator between use cases
    
    # Include GenAI solutions inline if available
    genai_block = usecase_data.get("genai_solutions", {})
    if isinstance(genai_block, dict) and "genai_solutions" in genai_block:
        st.markdown("### GenAI Solutions")
        st.markdown(genai_block["genai_solutions"]) 
    
    # Citations at end if present in generated data
    citations = usecase_data.get("citations") or generated_use_cases.get("citations")
    if citations and isinstance(citations, list):
        st.markdown("### Citations")
        for c in citations:
            if isinstance(c, dict):
                title = c.get("title", c.get("url", "Source"))
                url = c.get("url", "")
                src = c.get("source", "")
                st.write(f"• [{title}]({url}) — {src}")

def display_genai_solutions(results):
    """Display GenAI solutions section"""
    st.markdown("### Generative AI Solutions")
    
    usecase_data = results.get("agent_results", {}).get("use_cases", {})
    genai_solutions = usecase_data.get("genai_solutions", {})
    
    if isinstance(genai_solutions, dict) and "genai_solutions" in genai_solutions:
        st.markdown(genai_solutions["genai_solutions"])
    elif isinstance(genai_solutions, str):
        st.markdown(genai_solutions)
    else:
        st.write("GenAI solutions will be displayed here")

def display_resources(results):
    """Display resources section with downloadable Excel format"""
    st.markdown("### Resources & Datasets")
    # Be robust to missing keys and partial results
    agent_results = results.get("agent_results", {}) or {}
    resource_data = agent_results.get("resources", {}) or {}
    usecase_data = agent_results.get("use_cases", {}) or {}
    generated_use_cases = usecase_data.get("generated_use_cases", {}) or {}
    
    if (resource_data or generated_use_cases) and isinstance(generated_use_cases, dict):
        # Parse use cases to get titles and descriptions
        formatted_text = generated_use_cases.get("formatted_use_cases", "")
        use_cases = parse_use_cases(formatted_text)
        
        # Create Excel data using prioritized fetch per use case
        excel_data = []
        resource_agent = getattr(st.session_state.orchestrator, 'resource_agent', None)
        for i, use_case in enumerate(use_cases, 1):
            use_case_title = use_case.get("title", f"Use Case {i}")
            description = use_case.get("objective", "Description not available")
            refs = []
            if resource_agent:
                try:
                    fetched = resource_agent.fetch_datasets(use_case_title, description)
                    for r in fetched:
                        title = r.get('title') or r.get('url')
                        url = r.get('url', '')
                        if url:
                            # Show as raw HTML anchor tag with target="_blank"
                            refs.append(f"{title} - <a href=\"{url}\" target=\"_blank\">{url}</a>")
                except Exception:
                    pass
            # Fallback: if no refs found
            ref_cell = "\n".join(refs) if refs else "No dataset found"
            excel_data.append({
                "Use Case": use_case_title,
                "Description": description,
                "References": ref_cell
            })
        
        # Create DataFrame
        import pandas as pd
        df = pd.DataFrame(excel_data)
        
        # Display the data in a table
        st.markdown("#### Resource Collection Summary")
        st.dataframe(df, width='stretch')
        
        # Also render clickable HTML links so users can open in new tabs
        st.markdown("#### Resources Datasets Links")
        for row in excel_data:
            use_case_name = row.get("Use Case", "Use Case")
            refs_text = row.get("References", "") or ""
            st.markdown(f"**{use_case_name}**")
            if refs_text and refs_text != "No dataset found":
                # Each reference is newline-separated; ensure each is an anchor tag
                for ref_line in refs_text.split("\n"):
                    ref_line = ref_line.strip()
                    if not ref_line:
                        continue
                    # If not already an anchor, convert plain URL to anchor
                    if '<a ' not in ref_line and 'http' in ref_line:
                        url_only = ref_line.split()[-1]
                        safe_title = ref_line.replace(url_only, '').strip(' -') or url_only
                        html_line = f"- <a href=\"{url_only}\" target=\"_blank\">{safe_title or url_only}</a>"
                    else:
                        html_line = f"- {ref_line}"
                    st.markdown(html_line, unsafe_allow_html=True)
            else:
                st.markdown("- No dataset found")
        
        # Create Excel download
        from io import BytesIO
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='AI Use Cases & Resources', index=False)
            
            # Auto-adjust column widths
            worksheet = writer.sheets['AI Use Cases & Resources']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        output.seek(0)
        
        # Download button
        st.download_button(
            label="📥 Download Resources as Excel",
            data=output.getvalue(),
            file_name=f"ai_use_cases_resources_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        # Detailed Resources section removed per request
        # Citations for resources file path
        resource_file = results.get("resource_file", "")
        if resource_file:
            st.markdown("### Citations")
            st.write(f"• Resources file: `{resource_file}`")
    else:
        st.info("No resources available. Run an analysis or use Quick Analysis to generate a downloadable Excel.")

def display_implementation_plan(results):
    """Display implementation plan section"""
    st.markdown("### Implementation Roadmap")
    
    final_proposal = results.get("final_proposal", {})
    roadmap = final_proposal.get("implementation_roadmap", {})
    next_steps = final_proposal.get("next_steps", [])
    
    if roadmap:
        for phase, description in roadmap.items():
            st.write(f"**{phase.replace('_', ' ').title()}**: {description}")
    
    if next_steps:
        st.markdown("### Next Steps")
        for i, step in enumerate(next_steps, 1):
            st.write(f"{i}. {step}")
    
    # Download complete report
    results_file = results.get("results_file", "")
    if results_file and os.path.exists(results_file):
        with open(results_file, 'r', encoding='utf-8') as f:
            st.download_button(
                label="📥 Download Complete Analysis Report",
                data=f.read(),
                file_name=os.path.basename(results_file),
                mime="application/json"
            )
    
    # Citations section (link to report file as master citation set)
    if results_file:
        st.markdown("### Citations")
        st.write(f"• Full report: `{results_file}`")

def display_sidebar():
    """Display the sidebar with navigation and status"""
    with st.sidebar:
        st.markdown("## Navigation")
        nav_choice = st.radio(
            label="Navigation",
            label_visibility="collapsed",
            options=[
                "Company Overview",
                "Development Use Cases",
                "Resources",
                "Implementation Plan"
            ],
            index=[
                "Company Overview",
                "Development Use Cases",
                "Resources",
                "Implementation Plan"
            ].index(st.session_state.get('nav_section', "Company Overview"))
        )
        st.session_state.nav_section = nav_choice
        
        st.markdown("---")
        try:
            Config.validate_config()
            st.success("✅ System Ready")
        except:
            st.error("❌ Configuration Error")
            st.markdown("Please check your `.env` file")
        
        # (Chatbot moved to main content area above Company Analysis)

def main():
    """Main Streamlit application"""
    initialize_session_state()
    
    # Load orchestrator
    if not load_orchestrator():
        st.stop()
    
    # Display sidebar
    display_sidebar()
    
    # Display main content
    display_header()
    
    # Input form
    if not st.session_state.analysis_running:
        response = display_input_form()
        if isinstance(response, dict):
            if response.get("action") == "quick":
                quick_download(response.get("company"))
            else:
                run_analysis(response.get("company"))
    else:
        st.info("Analysis in progress... Please wait.")
    
    # Display results
    display_results()

    # (Removed floating chat UI)

if __name__ == "__main__":
    main()
