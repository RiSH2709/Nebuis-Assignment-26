# GitHub Repository Summarizer

A FastAPI application that analyzes GitHub repositories and generates human-readable summaries using Large Language Models (LLMs). The system intelligently selects the most important files from a repository and uses AI to provide comprehensive project insights.

---

## 🚀 Quick Start (For Evaluators)

### Prerequisites

- **Python 3.10+** (Check with: `python --version`)
- **pip** (Included with Python)
- **API Key** for one of the following LLM providers:
  - Nebius AI Studio (recommended)
  - OpenAI
  - Anthropic

### Step 1: Clone and Navigate

```bash
git clone https://github.com/RiSH2709/Nebuis-Assignment-26.git
cd Nebuis-Assignment-26/nebius-repo-summarizer
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed fastapi-0.115.0 uvicorn-0.30.6 httpx-0.27.2 ...
```

### Step 3: Configure API Key

Create a `.env` file in the project root:

```bash
# For Nebius AI Studio (recommended)
NEBIUS_API_KEY=your_nebius_api_key_here
LLM_PROVIDER=nebius

# OR for OpenAI
# OPENAI_API_KEY=your_openai_api_key_here
# LLM_PROVIDER=openai

# OR for Anthropic
# ANTHROPIC_API_KEY=your_anthropic_api_key_here
# LLM_PROVIDER=anthropic

# Optional: GitHub token for higher API rate limits (5000 req/hr instead of 60)
# GITHUB_TOKEN=your_github_token_here
```

**⚠️ Important:** 
- Replace `your_nebius_api_key_here` with your actual API key
- Do NOT commit the `.env` file (already in `.gitignore`)
- If using a different LLM provider, update both the API key and `LLM_PROVIDER`

### Step 4: Start the Server

```bash
python -m uvicorn backend.main:app --reload --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

The server is now running at **http://localhost:8000**

### Step 5: Test the API

**Option A: Web Interface (Easiest)**
```bash
# Open in your browser:
http://localhost:8000/
```

**Option B: cURL Command (For Testing)**
```bash
curl -X POST http://localhost:8000/summarize \
  -H "Content-Type: application/json" \
  -d '{"github_url": "https://github.com/psf/requests"}'
```

**Expected Response:**
```json
{
  "summary": "Requests is a simple, yet elegant, HTTP library for Python...",
  "technologies": ["Python", "charset_normalizer", "idna", "urllib3", "certifi"],
  "structure": "The code is organized into a single package with a clear structure..."
}
```

**Option C: Interactive API Docs**
```bash
# Open in your browser:
http://localhost:8000/docs
```

### Step 6: Try Different Repositories

```bash
# Example: Analyze Flask
curl -X POST http://localhost:8000/summarize \
  -H "Content-Type: application/json" \
  -d '{"github_url": "https://github.com/pallets/flask"}'

# Example: Analyze FastAPI
curl -X POST http://localhost:8000/summarize \
  -H "Content-Type: application/json" \
  -d '{"github_url": "https://github.com/tiangolo/fastapi"}'
```

---

## 🤖 Model Choice

I chose **meta-llama/Llama-3.3-70B-Instruct** via **Nebius AI Studio** (`LLM_PROVIDER=nebius`) as the default model. It provides strong code understanding, reliable structured JSON output, and good response quality for repository summarization. It also offers a practical free-tier path for evaluation and quick local testing.

## 📦 Repository Content Handling Approach

To stay within context limits and improve summary quality, the API sends only high-signal repository files to the LLM.

### What is included
- README files (project purpose and usage)
- Dependency and build files (`requirements.txt`, `pyproject.toml`, `package.json`, etc.)
- Entry-point files (`main.py`, `app.py`, `index.js`, etc.)
- Important configuration files (`.yml`, `.yaml`, `.toml`, `.cfg`, `.ini`, Docker files)
- Additional source files ranked by importance score

### What is skipped
- Heavy/generated/vendor folders (`node_modules`, `.git`, `dist`, `build`, `__pycache__`, etc.)
- Binary and media assets (`.png`, `.jpg`, `.zip`, `.exe`, etc.)
- Lock/cache/log artifacts (`package-lock.json`, `yarn.lock`, `*.lock`, `*.log`, etc.)

### Why this approach
This filtering keeps context focused on architecture and behavior instead of noise, reduces token usage and latency, and avoids exceeding model context windows on large repositories.

---

## 📖 Detailed Documentation

### Features

- ✅ **Multi-Provider LLM Support**: Works with Nebius AI, OpenAI, and Anthropic
- ✅ **Smart File Selection**: Intelligently prioritizes README, configs, and source code
- ✅ **Context Management**: Stays within LLM token limits (80K character budget)
- ✅ **Directory Tree Analysis**: Provides repository structure context to the LLM
- ✅ **Concurrent Processing**: Fetches multiple files in parallel for speed
- ✅ **Error Handling**: Clear error messages for rate limits, 404s, and timeouts
- ✅ **Comprehensive Logging**: Tracks all requests, timing, and errors
- ✅ **Health Check Endpoint**: Monitor service status with `GET /health`
- ✅ **Beautiful Web UI**: User-friendly interface with purple gradient design
- ✅ **Interactive API Docs**: Auto-generated Swagger UI at `/docs`

## Usage

### Web Interface (Recommended)

Open your browser and navigate to:
```
http://localhost:8000/
```

Enter any GitHub repository URL and click "Analyze Repository" to get instant insights with a beautiful purple gradient interface.

### Interactive API Documentation

Explore and test endpoints using Swagger UI:
```
http://localhost:8000/docs
```

### Command Line Examples

```bash
# Basic usage
curl -X POST http://localhost:8000/summarize \
  -H 'Content-Type: application/json' \
  -d '{"github_url": "https://github.com/psf/requests"}'

# Pretty print with jq
curl -X POST http://localhost:8000/summarize \
  -H 'Content-Type: application/json' \
  -d '{"github_url": "https://github.com/pallets/flask"}' | jq .

# Save to file
curl -X POST http://localhost:8000/summarize \
  -H 'Content-Type: application/json' \
  -d '{"github_url": "https://github.com/tiangolo/fastapi"}' > summary.json
```

---

## 🔧 Troubleshooting

### Server Won't Start

**Problem:** `ModuleNotFoundError: No module named 'fastapi'`
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

**Problem:** `Address already in use`
```bash
# Solution: Use a different port
python -m uvicorn backend.main:app --reload --port 8001
```

### API Key Issues

**Problem:** `HTTPException: No API key configured`
```bash
# Solution: Check your .env file exists and has correct key
cat .env
# Should show: NEBIUS_API_KEY=v1....
```

**Problem:** `401 Unauthorized` or `Invalid API key`
```bash
# Solution: Verify your API key is correct
# - Check for extra spaces or quotes
# - Regenerate key if needed
# - Ensure LLM_PROVIDER matches the key you're using
```

### GitHub API Issues

**Problem:** `403 Forbidden` or "rate limit exceeded"
```bash
# Solution: Add GitHub token to .env
GITHUB_TOKEN=ghp_your_token_here
# This increases rate limit from 60 to 5000 requests/hour
```

**Problem:** Repository not found (404)
```bash
# Solution: Verify the repository URL
# - Must be a public repository
# - Check spelling of owner and repo name
# - Private repos require authentication
```

### LLM Response Issues

**Problem:** "Request timeout"
```bash
# Causes:
# - Repository is very large (10,000+ files)
# - LLM service is slow
# - Network issues
# 
# Solutions:
# - Try a smaller repository first
# - Wait 30 seconds and retry
# - Check LLM provider status page
```

**Problem:** Invalid JSON response from LLM
```bash
# This is handled automatically by the application
# The system will retry and clean the response
# Check app.log for details
```

### Viewing Logs

```bash
# Real-time log monitoring
tail -f app.log

# View last 50 lines
tail -50 app.log

# Search for errors
grep ERROR app.log
```

---

### LLM Provider Configuration

This application supports three LLM providers. Configure your preferred provider in the `.env` file:

#### Nebius AI Studio (Recommended)
```bash
LLM_PROVIDER=nebius
NEBIUS_API_KEY=your_nebius_api_key_here
```
- **Model Used:** `meta-llama/Llama-3.3-70B-Instruct`
- **Why:** Free tier available, excellent code comprehension, fast response time
- **Get API Key:** https://studio.nebius.ai/

#### OpenAI
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your_openai_key_here
```
- **Model Used:** `gpt-4o-mini`
- **Why:** High quality, reliable, widely tested
- **Get API Key:** https://platform.openai.com/api-keys

#### Anthropic Claude
```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your_anthropic_key_here
```
- **Model Used:** `claude-3-5-haiku-latest`
- **Why:** Excellent reasoning, large context window
- **Get API Key:** https://console.anthropic.com/


## 📂 Project Structure

```
nebius-repo-summarizer/
├── backend/
│   ├── __init__.py              # Package initialization
│   ├── config.py                # Environment variables & configuration
│   ├── github_service.py        # GitHub API client (fetch repo data)
│   ├── repo_processor.py        # File filtering, scoring, and context building
│   ├── llm_service.py           # LLM API integration (Nebius/OpenAI/Anthropic)
│   └── main.py                  # FastAPI app, routes, and error handling
├── static/
│   └── index.html               # Web UI with purple gradient design
├── .env                         # Your API keys (NEVER COMMIT THIS!)
├── .env.example                 # Template for environment variables
├── .gitignore                   # Git exclusion rules (includes .env, logs)
├── app.log                      # Application logs (auto-generated)
├── requirements.txt             # Python dependencies
├── Procfile (experiment)                   # Railway deployment config
├── render.yaml                  # Render.com deployment config
├── runtime.txt                  # Python version specification
└── README.md                    # This file
```

**Key Files Explained:**

- **`backend/config.py`**: Loads environment variables, validates API keys
- **`backend/github_service.py`**: Handles GitHub API calls (fetch tree, file contents)
- **`backend/repo_processor.py`**: Scores files, filters junk, builds context with 80K char limit
- **`backend/llm_service.py`**: Routes to appropriate LLM provider, parses JSON response
- **`backend/main.py`**: FastAPI endpoints, custom exception handler, logging setup
- **`static/index.html`**: User-facing web interface with form and result display

---

## 🏗️ Architecture & Design Decisions

### Why FastAPI?
- ✅ **Async Support**: Concurrent GitHub API calls (fetch 20 files in parallel)
- ✅ **Auto Documentation**: Built-in Swagger UI at `/docs`
- ✅ **Type Safety**: Pydantic models with validation
- ✅ **Modern Python**: Uses async/await, type hints (Python 3.10+)
- ✅ **Performance**: One of the fastest Python web frameworks

### Why Intelligently Filter Files?
**Problem:** Most repositories have 1,000+ files, but LLMs have token limits (4K-128K tokens).

**Solution:** Score-based prioritization
- **Token Efficiency**: Only send important files to LLM (reduces cost)
- **Quality**: README + configs give better insight than 1000 random files
- **Speed**: Fetching 20 files is faster than 1000
- **Cost**: Fewer tokens = lower API costs

**Example:** A 5,000-file repo → filtered to top 20 files → 15-20 second response time

### Why Multiple LLM Providers?
- **Flexibility**: Users can choose based on cost/quality tradeoffs
- **Reliability**: Fallback if one provider has outages
- **Testing**: Easy to compare model outputs
- **Free Tier**: Nebius offers free access for development

### Error Handling Strategy
1. **GitHub API Errors**
   - 404: Clear message about invalid repo
   - 403: Suggest adding GITHUB_TOKEN
   - Timeout: Retry recommendation

2. **LLM Errors**
   - JSON parsing: Clean markdown formatting
   - Rate limits: Clear error message
   - Timeout: Retry with smaller context

3. **Consistent Format**
   - All errors return: `{"status": "error", "message": "..."}`
   - HTTP status codes match error type (400/403/500)

### Security Best Practices
- ✅ **No Hardcoded Keys**: All credentials in `.env` file
- ✅ **Environment Variables**: Never commit `.env` to Git
- ✅ **Input Validation**: Pydantic models validate requests
- ✅ **Error Messages**: Don't expose internal details
- ✅ **HTTPS Ready**: Works with reverse proxies (nginx, Caddy)

---

## ⚡ Performance Optimizations

1. **Concurrent File Fetching**
   - Use `asyncio.gather()` to fetch 20 files in parallel
   - Reduces total fetch time from 20+ seconds to 2-3 seconds

2. **Smart Caching** (Future Enhancement)
   - Could cache repository analyses in Redis
   - Would reduce redundant GitHub API calls

3. **Context Budget Management**
   - 80,000 character limit prevents excessive LLM costs
   - Prioritizes important files first

4. **Streaming Responses** (Future Enhancement)
   - Could stream LLM responses for faster perceived performance

---


### API Endpoints

#### `GET /`
**Description:** Serves the web UI interface

**Response:** HTML page with the interactive repository analyzer

---

#### `GET /health`
**Description:** Health check endpoint for monitoring

**Response:**
```json
{
  "status": "ok"
}
```

---

#### `POST /summarize`
**Description:** Analyzes a GitHub repository and returns a structured summary

**Request Body:**
```json
{
  "github_url": "https://github.com/owner/repo"
}
```

**Success Response (200 OK):**
```json
{
  "summary": "2-3 sentence description of what the project does and who it's for",
  "technologies": ["Python", "FastAPI", "PostgreSQL", "..."],
  "structure": "1-2 sentences describing how the code is organized"
}
```

**Error Response Format:**
```json
{
  "status": "error",
  "message": "Description of what went wrong"
}
```

**Error Codes:**
- `400 Bad Request`: Invalid GitHub URL or repository not found
- `403 Forbidden`: GitHub API rate limit exceeded (add GITHUB_TOKEN to .env)
- `500 Internal Server Error`: LLM API error, timeout, or unexpected server error

**Common Error Messages:**
- "Repository not found or is private. Please check the URL"
- "GitHub API rate limit exceeded. Please add a GITHUB_TOKEN to your .env file"
- "Request timeout. The repository may be too large or the service is slow"

---

#### `GET /docs`
**Description:** Interactive Swagger UI for exploring and testing the API

**URL:** http://localhost:8000/docs

---

### Environment Variables Reference

All configuration is done via a `.env` file in the project root. **Never commit this file to version control!**

**Minimal Configuration (Required):**
```bash
# Choose your LLM provider
LLM_PROVIDER=nebius

# Add the corresponding API key
NEBIUS_API_KEY=your_api_key_here
```

**Full Configuration (Optional):**
```bash
# LLM Provider Selection (required)
LLM_PROVIDER=nebius                    # Options: nebius, openai, anthropic

# LLM API Keys (at least one required)
NEBIUS_API_KEY=v1.CmQK...              # Nebius AI Studio key
OPENAI_API_KEY=sk-...                  # OpenAI key
ANTHROPIC_API_KEY=sk-ant-...           # Anthropic key

# GitHub API (optional but recommended)
GITHUB_TOKEN=ghp_...                   # Increases rate limit from 60 to 5000/hr
```

**Getting API Keys:**

1. **Nebius AI Studio** (Recommended)
   - Sign up: https://studio.nebius.ai/
   - Navigate to API Keys section
   - Create new key
   - Copy key starting with `v1.`

2. **GitHub Personal Access Token** (Optional)
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scope: `public_repo` (for public repositories only)
   - Generate and copy token starting with `ghp_`
   - **Benefit:** Increases rate limit from 60 to 5000 requests/hour

3. **OpenAI** (Alternative)
   - Sign up: https://platform.openai.com/signup
   - Navigate to API keys
   - Create key starting with `sk-`

4. **Anthropic** (Alternative)
   - Sign up: https://console.anthropic.com/
   - Generate key starting with `sk-ant-`

**Using .env.example:**
```bash
# Quick setup from template
cp .env.example .env
# Then edit .env with your real keys
```

---

## 🧪 Testing & Validation

### Health Check
```bash
curl http://localhost:8000/health
# Expected: {"status": "ok"}
```

### Test with Small Repository
```bash
curl -X POST http://localhost:8000/summarize \
  -H "Content-Type: application/json" \
  -d '{"github_url": "https://github.com/kennethreitz/setup.py"}'
```

### Test with Medium Repository
```bash
curl -X POST http://localhost:8000/summarize \
  -H "Content-Type: application/json" \
  -d '{"github_url": "https://github.com/pallets/flask"}'
```

### Test Error Handling
```bash
# Invalid repository
curl -X POST http://localhost:8000/summarize \
  -H "Content-Type: application/json" \
  -d '{"github_url": "https://github.com/invalid/nonexistent"}'

# Expected: {"status": "error", "message": "Repository not found..."}
```

### Monitor Logs
```bash
# View application logs
tail -f app.log
```

---

## 🔮 Limitations & Future Improvements

### Current Limitations
- **Default Branch Only**: Analyzes `main` or `master` branch only
- **File Limit**: Maximum 50 files selected, 20 files fetched
- **Public Repositories**: Private repos require GitHub token with proper scopes
- **No Caching**: Each request fetches fresh data from GitHub
- **Single Analysis**: No repository comparison features
- **No Persistence**: Results not stored in database

### Planned Improvements
- [ ] **Redis Caching**: Cache analyses for 24 hours to reduce API calls
- [ ] **Database Storage**: SQLite/PostgreSQL for analysis history
- [ ] **Branch Selection**: Allow users to specify which branch to analyze
- [ ] **Private Repo Support**: OAuth flow for authenticated repo access
- [ ] **Batch Processing**: Analyze multiple repos concurrently
- [ ] **Visual Diagrams**: Auto-generate architecture diagrams (Mermaid)
- [ ] **Custom Prompts**: User-defined analysis focus areas
- [ ] **Webhooks**: Auto-analyze on repository push events
- [ ] **Comparison Mode**: Side-by-side comparison of similar repos
- [ ] **Language Stats**: Add GitHub Linguist language breakdown

---

## 🛡️ Security & Best Practices

⚠️ **Critical Security Notice**

**NEVER commit your `.env` file to version control!**

The `.gitignore` file is pre-configured to exclude:
- `.env` - Your real API keys and secrets
- `__pycache__/`, `*.pyc` - Python bytecode
- `.venv/`, `venv/` - Virtual environments
- `*.egg-info/` - Package metadata
- `.pytest_cache/` - Test cache
- `*.log` - Application logs (contains request data)

**Security Checklist:**
- ✅ Use environment variables for ALL sensitive data
- ✅ Never hardcode API keys in source code
- ✅ Rotate API keys regularly (every 90 days)
- ✅ Use separate keys for development/staging/production
- ✅ Limit GitHub token scopes (only `public_repo` for public repos)
- ✅ Review `.gitignore` before committing
- ✅ Use `.env.example` as a safe template (no real keys)
- ✅ Enable 2FA on GitHub and LLM provider accounts

**If You Accidentally Commit a Secret:**
1. Revoke the exposed API key immediately
2. Generate a new key
3. Update `.env` with new key
4. Remove the secret from Git history using `git filter-branch` or BFG Repo-Cleaner

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

### Development Setup
```bash
# 1. Fork the repository on GitHub
# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/Nebuis-Assignment-26.git
cd Nebuis-Assignment-26/nebius-repo-summarizer

# 3. Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create .env file
cp .env.example .env
# Add your API keys

# 6. Create a feature branch
git checkout -b feature/amazing-feature

# 7. Make your changes and test
python -m uvicorn backend.main:app --reload

# 8. Commit and push
git add .
git commit -m 'Add amazing feature'
git push origin feature/amazing-feature

# 9. Open a Pull Request on GitHub
```

### Code Style Guidelines
- Follow PEP 8 for Python code
- Use type hints for all function parameters and returns
- Add docstrings to all functions
- Keep functions small and focused (max 50 lines)
- Use descriptive variable names
- Add comments for complex logic

### Testing Checklist
Before submitting a PR:
- [ ] Code passes all existing tests
- [ ] Added tests for new features
- [ ] Tested with all 3 LLM providers (Nebius, OpenAI, Anthropic)
- [ ] Tested error handling (invalid URLs, rate limits)
- [ ] Updated README if needed
- [ ] No hardcoded secrets or API keys

---

## 📄 License

This project is licensed under the **MIT License** - feel free to use it for learning, personal projects, or commercial applications.

---

## 👤 Author

**Created as part of Nebius Assignment 26**

- **GitHub:** [@RiSH2709](https://github.com/RiSH2709)
- **Repository:** [Nebuis-Assignment-26](https://github.com/RiSH2709/Nebuis-Assignment-26)

---

## 🙏 Acknowledgments

- **Nebius AI Studio** - For providing free access to state-of-the-art LLMs
- **FastAPI** - For the excellent async Python web framework
- **GitHub API** - For comprehensive repository data access
- **Open Source Community** - For inspiration and best practices

---


### Need Help?

- 🐛 **Bug Reports:** [Open an issue](https://github.com/RiSH2709/Nebuis-Assignment-26/issues)
- 💡 **Feature Requests:** [Start a discussion](https://github.com/RiSH2709/Nebuis-Assignment-26/discussions)
- 📖 **Documentation:** Check the inline comments and docstrings
- 🔧 **API Testing:** Use Swagger UI at http://localhost:8000/docs

### Quick Links

- [Installation Guide](#-quick-start-for-evaluators)
- [API Documentation](#api-endpoints)
- [Troubleshooting](#-troubleshooting)
- [Environment Variables](#environment-variables-reference)

---

**⭐ If you find this project useful, please consider giving it a star on GitHub!**

---

*Built with ❤️ using FastAPI, Python, and AI*
