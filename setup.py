"""
Setup script for the Multi-Agent Market Research System
"""

import os
import subprocess
import sys
from pathlib import Path

def create_directories():
    """Create necessary directories"""
    directories = [
        "output",
        "reports", 
        "logs",
        "docs",
        "agents",
        "utils"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def create_env_file():
    """Create .env file template if it doesn't exist"""
    env_file = ".env"
    
    if not os.path.exists(env_file):
        env_template = """# Multi-Agent Market Research System - Environment Variables

# Required API Keys
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here

# Optional API Keys (for enhanced resource collection)
KAGGLE_USERNAME=your_kaggle_username
KAGGLE_KEY=your_kaggle_key
GITHUB_TOKEN=your_github_token_here
HUGGINGFACE_TOKEN=your_huggingface_token_here

# Application Settings (optional)
MAX_SEARCH_RESULTS=10
MAX_DATASETS_PER_PLATFORM=5
"""
        
        with open(env_file, 'w') as f:
            f.write(env_template)
        
        print(f"✅ Created {env_file} template")
        print("⚠️  Please edit .env file and add your API keys!")
    else:
        print(f"ℹ️  {env_file} already exists")

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def verify_installation():
    """Verify that key packages are installed"""
    required_packages = [
        "streamlit",
        "langchain",
        "openai",
        "tavily-python",
        "python-dotenv"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package} installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} missing")
    
    return len(missing_packages) == 0

def create_sample_config():
    """Create sample configuration files"""
    # Create .streamlit directory and config
    streamlit_dir = Path(".streamlit")
    streamlit_dir.mkdir(exist_ok=True)
    
    config_content = """[general]
dataFrameSerialization = "legacy"

[server]
headless = true
port = 8501

[theme]
primaryColor = "#667eea"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
"""
    
    config_file = streamlit_dir / "config.toml"
    if not config_file.exists():
        with open(config_file, 'w') as f:
            f.write(config_content)
        print("✅ Created Streamlit configuration")

def display_api_key_instructions():
    """Display instructions for obtaining API keys"""
    print("\n" + "=" * 60)
    print("🔑 API KEY SETUP INSTRUCTIONS")
    print("=" * 60)
    
    instructions = {
        "OpenAI API": {
            "url": "https://platform.openai.com/api-keys",
            "required": True,
            "description": "Required for GPT-4 analysis and generation"
        },
        "Tavily Search API": {
            "url": "https://tavily.com/",
            "required": True,
            "description": "Required for web search and research"
        },
        "Kaggle API": {
            "url": "https://www.kaggle.com/settings/account",
            "required": False,
            "description": "Optional: For dataset discovery"
        },
        "HuggingFace API": {
            "url": "https://huggingface.co/settings/tokens",
            "required": False,
            "description": "Optional: For model and dataset search"
        },
        "GitHub API": {
            "url": "https://github.com/settings/tokens",
            "required": False,
            "description": "Optional: For repository search"
        }
    }
    
    for service, info in instructions.items():
        status = "REQUIRED" if info["required"] else "OPTIONAL"
        print(f"\n{service} ({status}):")
        print(f"  📝 {info['description']}")
        print(f"  🔗 Get your key: {info['url']}")
    
    print(f"\n💡 After obtaining your API keys:")
    print(f"   1. Edit the .env file")
    print(f"   2. Replace 'your_api_key_here' with your actual keys")
    print(f"   3. Save the file")

def run_test():
    """Run system test"""
    print("\n🧪 Running system test...")
    
    try:
        result = subprocess.run([sys.executable, "test_system.py", "config"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ System test passed")
            return True
        else:
            print("❌ System test failed")
            print("Output:", result.stdout)
            print("Error:", result.stderr)
            return False
    except Exception as e:
        print(f"❌ Could not run system test: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 MULTI-AGENT MARKET RESEARCH SYSTEM - SETUP")
    print("=" * 60)
    
    # Step 1: Create directories
    print("\n📁 Creating directories...")
    create_directories()
    
    # Step 2: Create environment file
    print("\n⚙️  Setting up environment...")
    create_env_file()
    
    # Step 3: Install dependencies
    print("\n📦 Installing dependencies...")
    if not install_dependencies():
        print("❌ Setup failed during dependency installation")
        return False
    
    # Step 4: Verify installation
    print("\n🔍 Verifying installation...")
    if not verify_installation():
        print("❌ Some packages are missing. Please check the installation.")
        return False
    
    # Step 5: Create configuration files
    print("\n⚙️  Creating configuration files...")
    create_sample_config()
    
    # Step 6: Display API key instructions
    display_api_key_instructions()
    
    # Step 7: Final instructions
    print("\n" + "=" * 60)
    print("🎉 SETUP COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    
    print("\n📋 NEXT STEPS:")
    print("1. Edit the .env file and add your API keys")
    print("2. Test the system: python test_system.py")
    print("3. Start the web interface: streamlit run streamlit_app.py")
    
    print("\n📚 USEFUL COMMANDS:")
    print("• Test configuration: python test_system.py config")
    print("• Run analysis test: python test_system.py analysis")
    print("• Interactive test: python test_system.py interactive")
    print("• Start web app: streamlit run streamlit_app.py")
    
    # Offer to run test
    response = input("\n🧪 Would you like to run a configuration test now? (y/n): ").lower()
    if response in ['y', 'yes']:
        run_test()
    
    print("\n🚀 System is ready! Happy researching! 🤖")

if __name__ == "__main__":
    main()
