# Multi-Agent Market Research System - Setup Guide

## Quick Start (Local Development)

### 1. Prerequisites
- Python 3.9+ (recommended: Python 3.11)
- Git
- Internet connection for API calls

### 2. Installation

```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd "Multiagent Market Research Agent"

# Install dependencies
pip install -r requirements.txt

# Or install individually:
pip install streamlit langchain langchain-openai langchain-community python-dotenv requests beautifulsoup4 pandas matplotlib seaborn plotly tavily-python PyGithub huggingface-hub
```

### 3. API Keys Setup

Create a `.env` file in the project root with your API keys:

```bash
# Copy the example file
cp env_example.txt .env

# Edit the .env file with your actual API keys
nano .env
```

**Required API Keys:**
```env
# REQUIRED - Core functionality
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here

# OPTIONAL - Enhanced resource collection
KAGGLE_USERNAME=your_kaggle_username_here
KAGGLE_KEY=your_kaggle_key_here
GITHUB_TOKEN=your_github_token_here
HUGGINGFACE_TOKEN=your_huggingface_token_here
```

### 4. Run the Application

```bash
# Start the Streamlit web interface
streamlit run streamlit_app.py

# Or if using conda:
/opt/anaconda3/bin/streamlit run streamlit_app.py
```

The application will be available at: **http://localhost:8501**

## API Keys Required

### 1. OpenAI API Key (REQUIRED)
- **Purpose**: AI analysis, use case generation, and content creation
- **Cost**: Pay-per-use (typically $0.01-0.10 per analysis)
- **Get it**: https://platform.openai.com/api-keys
- **Setup**: Create account → API Keys → Create new secret key

### 2. Tavily API Key (REQUIRED)
- **Purpose**: Web search and research data collection
- **Cost**: Free tier available, paid plans for higher usage
- **Get it**: https://tavily.com/
- **Setup**: Sign up → Dashboard → API Keys → Create new key

### 3. Kaggle API (OPTIONAL)
- **Purpose**: Dataset collection for AI/ML resources
- **Cost**: Free
- **Get it**: https://www.kaggle.com/account
- **Setup**: Account → API → Create new token → Download kaggle.json

### 4. GitHub Token (OPTIONAL)
- **Purpose**: Repository and code resource collection
- **Cost**: Free
- **Get it**: https://github.com/settings/tokens
- **Setup**: Settings → Developer settings → Personal access tokens → Generate new token

### 5. HuggingFace Token (OPTIONAL)
- **Purpose**: Model and dataset collection
- **Cost**: Free
- **Get it**: https://huggingface.co/settings/tokens
- **Setup**: Settings → Access Tokens → New token

## Features Available

### With Required APIs Only:
- ✅ Company and industry research
- ✅ AI/ML use case generation (10 detailed use cases)
- ✅ Industry-specific analysis
- ✅ Basic resource suggestions
- ✅ Professional reports and recommendations

### With All APIs:
- ✅ Everything above PLUS
- ✅ Live dataset collection from Kaggle
- ✅ Model and dataset collection from HuggingFace
- ✅ GitHub repository discovery
- ✅ Comprehensive resource markdown files
- ✅ Enhanced resource recommendations

## Troubleshooting

### Common Issues:

1. **"ModuleNotFoundError: No module named 'streamlit'"**
   ```bash
   pip install streamlit
   # Or use conda:
   conda install streamlit
   ```

2. **"Unauthorized: missing or invalid API key"**
   - Check your `.env` file exists
   - Verify API keys are correct
   - Ensure no extra spaces in the .env file

3. **"Connection timeout" or "API rate limit"**
   - Check internet connection
   - Wait a few minutes and try again
   - Consider upgrading API plans if hitting limits

4. **Streamlit not starting**
   ```bash
   # Try different Python environment
   which python
   /opt/anaconda3/bin/streamlit run streamlit_app.py
   ```

### File Structure:
```
Multiagent Market Research Agent/
├── agents/                 # AI agents
├── utils/                  # Utility functions
├── docs/                   # Documentation
├── sample_output/          # Example outputs
├── output/                 # Generated reports
├── reports/                # Analysis reports
├── .env                    # API keys (create this)
├── streamlit_app.py        # Web interface
├── orchestrator.py         # Main coordinator
└── requirements.txt        # Dependencies
```

## Usage

1. **Start the application**: `streamlit run streamlit_app.py`
2. **Open browser**: Navigate to http://localhost:8501
3. **Enter company name**: Type any company name (e.g., "Tesla", "Amazon")
4. **Click "Start Analysis"**: Wait for the multi-agent analysis
5. **Review results**: Check the generated use cases, resources, and recommendations
6. **Download reports**: Use the download buttons for markdown files

## Output Files

The system automatically generates:
- **Analysis Report**: Complete markdown report with all findings
- **Resource File**: Markdown file with collected datasets and resources
- **Use Cases**: Detailed AI/ML use case recommendations
- **Implementation Plan**: Step-by-step implementation roadmap

All files are saved in the `output/` and `reports/` directories.

## Support

If you encounter issues:
1. Check the terminal for error messages
2. Verify all API keys are correctly set
3. Ensure all dependencies are installed
4. Check the logs in the Streamlit interface

The system is designed to work with minimal setup - just the two required API keys will give you full functionality!
