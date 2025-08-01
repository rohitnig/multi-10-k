# Aegis Financial Intelligence

A next-generation AI-powered financial analysis platform featuring a stunning professional web interface and sophisticated multi-agent architecture. The system implements a "Mixture of Experts" (MoE) approach using LangChain, with a beautiful Apple-inspired UI that provides real-time financial insights.

## 🎯 **Live Demo**

![Aegis Financial Intelligence](https://via.placeholder.com/800x500/000000/007aff?text=Aegis+Financial+Intelligence)

**🌐 [Launch Web Interface](http://localhost:8000)** (after setup)

## ✨ **Key Features**

### 🎨 **Professional Web Interface**
- **Apple-Inspired Design**: Sleek dark theme with glass morphism effects
- **Real-Time Interactions**: Smooth animations and instant feedback
- **Responsive Design**: Perfect experience on desktop, tablet, and mobile
- **Smart Loading States**: Brain-pulsing animations with step-by-step progress
- **Quick Actions**: Pre-built financial analysis templates
- **Copy & Share**: One-click results sharing and clipboard integration

### 🤖 **Multi-Agent Intelligence**
- **ReAct Architecture**: Advanced reasoning and acting patterns
- **Tool Orchestration**: Web search, document analysis, and database queries
- **Dynamic Prompting**: Adaptive examples based on available tools
- **Intelligent Routing**: Automatic tool selection for optimal results

### 🛠 **Modular Architecture**
- **Agent Orchestrator**: Reusable core module for both web and CLI interfaces
- **Toggle-able Tools**: Enable/disable 10K RAG functionality on demand
- **Professional API**: FastAPI backend with comprehensive error handling

## 🏗️ Architecture

```
┌─────────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Web Interface      │───▶│ Agent Orchestrator│───▶│  Tool Selection │
│  (Apple-inspired)   │    │   (GPT-4o-mini)   │    │   (Dynamic)     │
└─────────────────────┘    └──────────────────┘    └─────────────────┘
          │                                                   │
          ▼                                                   ▼
┌─────────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Real-time UI       │    │   Multi-Tools    │    │  Final Response │
│  • Loading States   │    │ • Web Search     │    │  • Formatted    │
│  • Progress Steps   │    │ • 10-K RAG       │    │  • Copyable     │
│  • Smooth Anims     │    │ • SQL Database   │    │  • Shareable    │
└─────────────────────┘    └──────────────────┘    └─────────────────┘
```

### System Components
- **Web Interface**: Professional React-like experience with Apple design language
- **Agent Orchestrator**: Modular core (`agent_orchestrator.py`) for both CLI and web
- **ReAct Agent**: GPT-4o-mini powered reasoning with dynamic prompt adaptation
- **Multi-Tool System**: Web search (Tavily), Document RAG (ChromaDB + Gemini), SQL queries
- **Docker Stack**: ChromaDB, FastAPI server, containerized services

## 🚀 **Quick Start**

### Prerequisites
- Docker and Docker Compose
- 4GB+ RAM (for web interface)
- API Keys: `OPENAI_API_KEY`, `TAVILY_API_KEY`, and optionally `GEMINI_API_KEY`

### 1. **Launch the Web Interface** ⚡
```bash
# Clone and navigate
git clone <repo-url>
cd multi-10-k

# Set your API keys
export OPENAI_API_KEY="your-openai-key"
export TAVILY_API_KEY="your-tavily-key"
export GEMINI_API_KEY="your-gemini-key"  # Optional

# Launch the stunning web interface
docker compose --profile api up -d

# Open your browser
open http://localhost:8000
```

### 2. **Experience the Magic** ✨
- **Instant Analysis**: Use quick-action buttons for common queries
- **Custom Queries**: Type your own financial questions
- **Real-time Progress**: Watch AI agents work through your request
- **Professional Results**: Get formatted, copyable, shareable insights

### 3. **Optional: CLI Mode**
```bash
# For developers who prefer command line
cd app/
python main.py
```

### 4. **Data Setup** (Optional)
```bash
# Enable 10K document analysis (requires GEMINI_API_KEY)
docker compose --profile ingest up
ENABLE_10K_RAG=true docker compose --profile api up -d
```

## 🛠️ **Development**

### Project Structure
```
multi-10-k/
├── app/                           # Core application
│   ├── agent_orchestrator.py     # 🧠 Main agent logic (reusable)
│   ├── api.py                    # 🌐 FastAPI web server
│   ├── main.py                   # 💻 CLI entry point
│   ├── tools/                    # 🔧 Agent tools
│   │   ├── file_tools.py         #   📄 10-K document analysis
│   │   ├── web_tools.py          #   🌍 Real-time web search
│   │   └── sql_tools.py          #   🗄️ Database queries
│   ├── templates/                # 🎨 Web interface
│   │   └── index.html            #   Beautiful Apple-inspired UI
│   ├── static/                   # 💫 Assets
│   │   ├── css/style.css         #   Sophisticated styling
│   │   └── js/app.js             #   Interactive JavaScript
│   ├── ingest.py                 # 📊 Data ingestion
│   └── db_setup.py              # 🏗️ Database initialization
├── tests/                        # 🧪 Test suite
├── docker-compose.yml            # 🐳 Service orchestration
└── requirements.txt              # 📦 Dependencies
```

### **Development Commands**
```bash
# 🚀 Web Interface Development
uvicorn api:app --reload --host 0.0.0.0 --port 8000

# 🔧 Service Management
docker compose --profile api up -d    # Launch web interface
docker compose logs -f api            # View real-time logs
docker compose down                   # Stop all services

# 🧪 Testing
pytest                               # Run all tests
pytest tests/test_file_tools.py -v   # Test specific components
pytest --cov=app tests/             # Coverage report

# 🗄️ Data Management
python app/db_setup.py              # Initialize SQL database
docker compose --profile ingest up   # Populate document database
```

### **Environment Variables**
```bash
# Required
OPENAI_API_KEY="sk-..."          # GPT-4o-mini for agent reasoning
TAVILY_API_KEY="tvly-..."        # Real-time web search

# Optional
GEMINI_API_KEY="AI..."           # 10K document synthesis (if enabled)
ENABLE_10K_RAG="true"           # Toggle document analysis tool
CHROMA_HOST="chromadb"          # Database host (Docker default)
MOCK_MODE="false"               # Testing mode
```

## 🧪 **Example Queries**

Experience the power of multi-agent analysis with these sample queries:

### 📊 **Investment Analysis**
```
"I'm considering investing in Google after their strong 2023 performance. 
Can you provide a comprehensive investment analysis including:
1) Our internal quarterly profit data for comparison
2) Google's major business risks from official filings  
3) Current market sentiment and stock price trends
Please synthesize this into an investment recommendation."
```

### 📈 **Market Research**
```
"What are the current AI and technology market trends, and how do they 
compare with our internal revenue performance this quarter?"
```

### ⚠️ **Risk Assessment**
```
"Analyze the key risk factors for investing in large tech companies, 
with specific examples from Google's 2023 10-K filing."
```

### 💰 **Financial Performance**
```
"Compare our quarterly profit margins with industry benchmarks and 
provide recommendations for improvement."
```

## 🔧 **Troubleshooting**

### 🚫 **Common Issues**

**Web Interface Not Loading**
```bash
# Check if services are running
docker compose ps

# Restart with fresh build
docker compose down && docker compose build --no-cache && docker compose --profile api up -d
```

**API Keys Not Working**
```bash
# Verify environment variables are set
echo $OPENAI_API_KEY
echo $TAVILY_API_KEY

# Restart with new keys
docker compose down && docker compose --profile api up -d
```

**Database Connection Issues**
```bash
# Initialize SQL database
python app/db_setup.py

# Check ChromaDB health
docker compose logs chromadb
```

**Agent Not Responding**
```bash
# Check agent logs for errors
docker compose logs -f api

# Verify all required tools are available
curl http://localhost:8000/health
```

## 📊 **Technical Specifications**

### 🧠 **AI Architecture**
- **Agent Reasoning**: OpenAI GPT-4o-mini (fast, reliable, cost-effective)
- **Document Synthesis**: Google Gemini API (high-quality content generation)
- **Web Search**: Tavily API (real-time information retrieval)
- **Pattern**: ReAct (Reasoning + Acting) with dynamic prompt adaptation

### 🗄️ **Data Systems**
- **Vector Database**: ChromaDB with SentenceTransformer embeddings
- **SQL Database**: SQLite with quarterly financial data
- **Document Processing**: HTML parsing and intelligent chunking
- **Search**: Semantic similarity with contextual retrieval

### 🎨 **Frontend Technology**
- **Design**: Apple-inspired UI with glass morphism effects
- **Animations**: CSS3 transitions with JavaScript orchestration
- **Responsiveness**: Mobile-first design with adaptive layouts
- **Performance**: Optimized loading states and smooth interactions

## 🤝 **Contributing**

### 🔧 **Adding New Tools**
1. Create tool in `app/tools/new_tool.py`
2. Use LangChain `@tool` decorator
3. Import in `agent_orchestrator.py`
4. Add to tools list with configuration
5. Write comprehensive tests

### 🧪 **Testing**
```bash
# Full test suite with coverage
pytest --cov=app tests/

# Test specific components
pytest tests/test_file_tools.py -v

# Test web interface (manual)
open http://localhost:8000
```

### 🎨 **UI Improvements**
- Modify `templates/index.html` for structure
- Update `static/css/style.css` for styling
- Enhance `static/js/app.js` for interactions

## 🚀 **What's Next**

### ✅ **Completed Features**
- **Professional Web Interface** with Apple-inspired design
- **Modular Architecture** with `agent_orchestrator.py`
- **Multi-Tool Integration** (Web search, RAG, SQL)
- **Real-time Interactions** with loading states and animations
- **Responsive Design** for all devices

### 🚧 **Future Enhancements**
- **Advanced Analytics Dashboard** with charts and graphs
- **Multi-User Support** with authentication and sessions
- **Custom Tool Builder** for non-technical users
- **Real-time Collaboration** features
- **Mobile App** with native experience

## 📄 **License**

MIT License - Feel free to use this in your projects!

## 🙋‍♀️ **Support & Community**

- **📖 Documentation**: Check `CLAUDE.md` for detailed technical docs
- **🐛 Issues**: Report bugs via GitHub Issues
- **💬 Discussions**: Join our community discussions
- **📧 Contact**: Reach out for enterprise support

---

**🎯 Status**: **PROJECT COMPLETE** 🚀 | Enterprise-ready financial intelligence platform with world-class UI