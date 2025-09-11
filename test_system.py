"""
Test script for the Multi-Agent Market Research System
"""

import os
import sys
import time
from datetime import datetime
from orchestrator import MarketResearchOrchestrator
from utils.helpers import PerformanceMonitor, setup_logging
from config import Config

def test_configuration():
    """Test system configuration"""
    print("=" * 60)
    print("🔧 TESTING SYSTEM CONFIGURATION")
    print("=" * 60)
    
    try:
        Config.validate_config()
        print("✅ Configuration validation passed")
        return True
    except Exception as e:
        print(f"❌ Configuration validation failed: {str(e)}")
        print("\nPlease ensure you have:")
        print("1. Created a .env file with your API keys")
        print("2. Set OPENAI_API_KEY and TAVILY_API_KEY")
        return False

def test_agent_initialization():
    """Test agent initialization"""
    print("\n" + "=" * 60)
    print("🤖 TESTING AGENT INITIALIZATION")
    print("=" * 60)
    
    try:
        orchestrator = MarketResearchOrchestrator()
        print("✅ All agents initialized successfully")
        return orchestrator
    except Exception as e:
        print(f"❌ Agent initialization failed: {str(e)}")
        return None

def test_sample_analysis(orchestrator, company_name="OpenAI"):
    """Test sample analysis"""
    print("\n" + "=" * 60)
    print(f"📊 TESTING SAMPLE ANALYSIS - {company_name}")
    print("=" * 60)
    
    monitor = PerformanceMonitor()
    monitor.start()
    
    try:
        print(f"Starting analysis for {company_name}...")
        
        # Run the analysis
        results = orchestrator.run_complete_analysis(company_name)
        
        monitor.checkpoint("analysis_complete")
        
        # Check results
        if results.get("workflow_status") == "completed":
            print("✅ Analysis completed successfully!")
            
            # Display summary
            final_proposal = results.get("final_proposal", {})
            exec_summary = final_proposal.get("executive_summary", {})
            
            print(f"\n📋 ANALYSIS SUMMARY:")
            print(f"   Company: {exec_summary.get('company', 'N/A')}")
            print(f"   Industry: {exec_summary.get('industry', 'N/A')}")
            print(f"   Use Cases Generated: {exec_summary.get('total_use_cases_generated', 0)}")
            print(f"   Resources Found: {exec_summary.get('total_resources_found', 0)}")
            
            # File outputs
            print(f"\n📁 OUTPUT FILES:")
            if results.get("results_file"):
                print(f"   Complete Results: {results.get('results_file')}")
            if results.get("resource_file"):
                print(f"   Resource Collection: {results.get('resource_file')}")
            
            # Generate summary report
            summary_file = orchestrator.generate_summary_report(results)
            if summary_file:
                print(f"   Summary Report: {summary_file}")
            
            return True
            
        else:
            print(f"❌ Analysis failed: {results.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Test analysis failed: {str(e)}")
        return False
    
    finally:
        # Performance summary
        perf_summary = monitor.get_summary()
        print(f"\n⏱️  PERFORMANCE SUMMARY:")
        print(f"   Total Time: {perf_summary.get('total_time', 0):.2f} seconds")

def test_web_interface():
    """Test web interface availability"""
    print("\n" + "=" * 60)
    print("🌐 TESTING WEB INTERFACE")
    print("=" * 60)
    
    try:
        import streamlit
        print("✅ Streamlit installed and available")
        print("🚀 To start the web interface, run:")
        print("   streamlit run streamlit_app.py")
        return True
    except ImportError:
        print("❌ Streamlit not installed")
        print("💡 Install with: pip install streamlit")
        return False

def run_comprehensive_test():
    """Run comprehensive system test"""
    print("🧪 MULTI-AGENT MARKET RESEARCH SYSTEM - COMPREHENSIVE TEST")
    print("=" * 70)
    
    # Setup logging
    setup_logging("INFO")
    
    # Test 1: Configuration
    if not test_configuration():
        print("\n❌ SYSTEM TEST FAILED - Configuration issues")
        return False
    
    # Test 2: Agent Initialization
    orchestrator = test_agent_initialization()
    if not orchestrator:
        print("\n❌ SYSTEM TEST FAILED - Agent initialization issues")
        return False
    
    # Test 3: Sample Analysis
    analysis_success = test_sample_analysis(orchestrator)
    if not analysis_success:
        print("\n❌ SYSTEM TEST FAILED - Analysis issues")
        return False
    
    # Test 4: Web Interface
    web_success = test_web_interface()
    
    # Final Results
    print("\n" + "=" * 70)
    if analysis_success and web_success:
        print("🎉 ALL TESTS PASSED - SYSTEM READY FOR USE!")
    elif analysis_success:
        print("⚠️  CORE SYSTEM WORKING - Web interface needs attention")
    else:
        print("❌ SYSTEM TEST FAILED - Please address issues above")
    print("=" * 70)
    
    return analysis_success

def demo_workflow():
    """Demonstrate the complete workflow with multiple companies"""
    print("🎬 DEMO WORKFLOW - MULTIPLE COMPANY ANALYSIS")
    print("=" * 60)
    
    companies = ["Tesla", "Microsoft", "Airbnb"]
    
    try:
        orchestrator = MarketResearchOrchestrator()
        
        for company in companies:
            print(f"\n🏢 Analyzing {company}...")
            results = orchestrator.run_complete_analysis(company)
            
            if results.get("workflow_status") == "completed":
                print(f"✅ {company} analysis completed")
                
                # Quick summary
                final_proposal = results.get("final_proposal", {})
                exec_summary = final_proposal.get("executive_summary", {})
                print(f"   Industry: {exec_summary.get('industry', 'N/A')}")
                print(f"   Use Cases: {exec_summary.get('total_use_cases_generated', 0)}")
                print(f"   Resources: {exec_summary.get('total_resources_found', 0)}")
            else:
                print(f"❌ {company} analysis failed")
            
            print("-" * 40)
        
        print("\n🎉 Demo workflow completed!")
        
    except Exception as e:
        print(f"❌ Demo workflow failed: {str(e)}")

def interactive_test():
    """Interactive test mode"""
    print("🎮 INTERACTIVE TEST MODE")
    print("=" * 40)
    
    try:
        orchestrator = MarketResearchOrchestrator()
        
        while True:
            company_name = input("\n🏢 Enter company name (or 'quit' to exit): ").strip()
            
            if company_name.lower() in ['quit', 'exit', 'q']:
                break
            
            if not company_name:
                print("Please enter a valid company name")
                continue
            
            print(f"\n🔍 Analyzing {company_name}...")
            start_time = time.time()
            
            results = orchestrator.run_complete_analysis(company_name)
            
            elapsed_time = time.time() - start_time
            
            if results.get("workflow_status") == "completed":
                print(f"✅ Analysis completed in {elapsed_time:.1f} seconds")
                
                # Show quick results
                final_proposal = results.get("final_proposal", {})
                exec_summary = final_proposal.get("executive_summary", {})
                
                print(f"\n📊 Quick Results:")
                print(f"   Industry: {exec_summary.get('industry', 'N/A')}")
                print(f"   Use Cases Generated: {exec_summary.get('total_use_cases_generated', 0)}")
                print(f"   Resources Found: {exec_summary.get('total_resources_found', 0)}")
                
                # Show file locations
                if results.get("results_file"):
                    print(f"\n📁 Full results saved to: {results.get('results_file')}")
                
            else:
                print(f"❌ Analysis failed: {results.get('error', 'Unknown error')}")
        
        print("\n👋 Thanks for testing the system!")
        
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user")
    except Exception as e:
        print(f"❌ Interactive test failed: {str(e)}")

def main():
    """Main test function"""
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == "config":
            test_configuration()
        elif mode == "agents":
            test_agent_initialization()
        elif mode == "analysis":
            orchestrator = test_agent_initialization()
            if orchestrator:
                company = sys.argv[2] if len(sys.argv) > 2 else "OpenAI"
                test_sample_analysis(orchestrator, company)
        elif mode == "demo":
            demo_workflow()
        elif mode == "interactive":
            interactive_test()
        elif mode == "web":
            test_web_interface()
        else:
            print("Usage: python test_system.py [config|agents|analysis|demo|interactive|web]")
    else:
        # Run comprehensive test by default
        run_comprehensive_test()

if __name__ == "__main__":
    main()
