# 🚀 Quick Start Guide - Multi-Agent Market Research System

Get up and running with the Multi-Agent Market Research System in just a few minutes!

## ⚡ Prerequisites

- **Python 3.8+** installed on your system
- **API Keys** for OpenAI and Tavily (required)
- **Internet connection** for API access

## 🔧 Installation (5 minutes)

### 1. Download & Setup
```bash
# Navigate to the project directory
cd "Multiagent Market Research Agent"

# Run the automated setup
python setup.py
```

### 2. Configure API Keys
Edit the `.env` file created during setup:

```env
# Required (get these first!)
OPENAI_API_KEY=sk-your-openai-key-here
TAVILY_API_KEY=tvly-your-tavily-key-here

# Optional (for enhanced features)
KAGGLE_USERNAME=your-kaggle-username
KAGGLE_KEY=your-kaggle-api-key
GITHUB_TOKEN=ghp_your-github-token
HUGGINGFACE_TOKEN=hf_your-huggingface-token
```

### 3. Get Your API Keys

#### OpenAI API Key (Required) 🔑
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign up/login to your account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)

#### Tavily API Key (Required) 🔍
1. Visit [Tavily](https://tavily.com/)
2. Sign up for a free account
3. Get your API key from dashboard
4. Copy the key (starts with `tvly-`)

## 🧪 Test the System (2 minutes)

```bash
# Test configuration
python test_system.py config

# Test full system
python test_system.py

# Interactive test
python test_system.py interactive
```

## 🌐 Launch Web Interface

```bash
streamlit run streamlit_app.py
```

The web interface will open at: `http://localhost:8501`

## 🎯 Your First Analysis

1. **Open the web interface** (streamlit app)
2. **Enter a company name** (e.g., "Tesla", "Microsoft", "OpenAI")
3. **Click "Start Analysis"**
4. **Wait 3-5 minutes** for completion
5. **Explore the results** in different tabs

## 📊 What You'll Get

### 🔍 Company Research
- Industry analysis and positioning
- Business model breakdown
- Strategic focus areas
- Competitive landscape

### 💡 AI/ML Use Cases
- 8-12 tailored use case recommendations
- Priority ranking by business impact
- Implementation complexity assessment
- GenAI solutions (chatbots, automation, etc.)

### 📚 Implementation Resources
- Relevant Kaggle datasets
- HuggingFace models and datasets  
- GitHub repositories and code
- Clickable resource documentation

### 📋 Executive Summary
- Complete analysis report
- Implementation roadmap
- Next steps and recommendations

## 🚨 Troubleshooting

### Common Issues

**"Configuration validation failed"**
- Check your `.env` file exists
- Verify API keys are correct
- Ensure no extra spaces in keys

**"API rate limiting"**
- Wait a few minutes between requests
- Check API key quota/billing

**"Module not found"**
```bash
pip install -r requirements.txt
```

**Streamlit not starting**
```bash
pip install streamlit
streamlit run streamlit_app.py
```

## 🎮 Example Commands

```bash
# Quick configuration test
python test_system.py config

# Test specific company
python test_system.py analysis "Apple"

# Demo with multiple companies  
python test_system.py demo

# Interactive testing mode
python test_system.py interactive

# Start web interface
streamlit run streamlit_app.py
```

## 📁 Output Files

After running an analysis, you'll find:

```
output/
├── resources_[industry].md       # Clickable resource links
reports/
├── complete_analysis_[company].json  # Full results
├── summary_report_[company].md      # Human-readable summary
```

## 🎯 Success Indicators

✅ **System Working** if you see:
- "Analysis completed successfully!"
- Resource files generated
- Use cases displayed in web interface
- No error messages in console

## 🔄 Typical Workflow

1. **Setup** (one time): Run `python setup.py`
2. **Configure** (one time): Add API keys to `.env`
3. **Test** (verify): Run `python test_system.py`
4. **Analyze** (repeat): Use web interface or command line
5. **Review** (results): Check generated reports and resources

## 💡 Pro Tips

- **Start with well-known companies** (Tesla, Apple, Microsoft) for best results
- **Use specific company names** rather than generic terms
- **Wait for completion** - the analysis takes 3-5 minutes
- **Check output directories** for saved files
- **Try different industries** to see varied recommendations

## 🆘 Need Help?

1. **Check the logs** in `logs/app.log`
2. **Run the test suite** with `python test_system.py`
3. **Verify API keys** are working with individual tests
4. **Check documentation** in `docs/` folder

## 🎉 You're Ready!

The system is now configured and ready to provide intelligent market research and AI use case recommendations for any company or industry!

**Next**: Try analyzing your favorite company or a business you're curious about! 🚀
