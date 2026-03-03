# GitHub Repository Summarizer

A Python API that analyzes GitHub repositories and generates human-readable summaries using an LLM. Built with FastAPI, this tool intelligently selects and processes repository files to provide comprehensive project insights.

## Features

- **Repository Analysis**: Automatically analyze any public GitHub repository
- **Multiple LLM Providers**: Support for Nebius AI, OpenAI, and Anthropic
- **Smart File Selection**: Intelligently selects the most important repository files (README, configuration, source code)
- **Beautiful Web Interface**: Modern, responsive UI for easy interaction
- **RESTful API**: Interactive Swagger documentation for API testing
- **Context Management**: Intelligent file filtering and token budget management
- **GitHub Token Support**: Add Personal Access Token for higher API rate limits (60 → 5,000 req/hr)

## Prerequisites

- Python 3.10 or higher
- pip (comes with Python)

## Local Development Setup

### 1. Clone the Repository

```bash
# 1. Clone the repo
git clone https://github.com/RiSH2709/Nebuis-Assignment-26
cd Nebuis-Assignment-26/nebius-repo-summarizer

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file
cp .env.example .env
# Edit .env and add your real API keys:
# - NEBIUS_API_KEY (required)
# - GITHUB_TOKEN (optional, increases rate limits)

# 4. Start the server
python -m uvicorn backend.main:app --reload --port 8000
```

## Usage

### Web Interface (Recommended)

Open your browser and navigate to:
```
http://localhost:8000/
```

Enter any GitHub repository URL and click "Summarize Repository" to get instant insights.

### Swagger UI (API Testing)

Interactive API documentation available at:
```
http://localhost:8000/docs
```

### Command Line (curl)

```bash
curl -X POST http://localhost:8000/summarize \
  -H 'Content-Type: application/json' \
  -d '{"github_url": "https://github.com/psf/requests"}'
```

**Response Format:**
```json
{
  "summary": "A 2-3 sentence description of what the project does",
  "technologies": ["Python", "pytest", "urllib3", "..."],
  "structure": "Description of how the project is organized"
}
```

## Model Choice

I selected **nvidia/Llama-3.1-8B-Instruct** via Nebius AI Studio for several key reasons:

### Why This Model?
- ✅ **Strong Code Comprehension**: Trained on extensive code datasets, excellent at understanding software projects
- ✅ **Large Context Window**: 8K+ tokens allows processing multiple files simultaneously
- ✅ **Fast Inference**: 8B parameter model provides quick responses (< 5 seconds)
- ✅ **Structured Output**: Reliable JSON generation for consistent API responses
- ✅ **Cost-Effective**: Free tier available on Nebius AI Studio
- ✅ **Latest Model**: Llama 3.1 series with improved instruction following

### Alternative Models Supported
The system also supports:
- **OpenAI GPT-4o-mini**: Higher quality but paid
- **Anthropic Claude**: Excellent reasoning, larger context window

Simply change `LLM_PROVIDER` in your `.env` file to switch models.

## Repository Processing Strategy

The system uses intelligent file selection to stay within LLM context limits while maximizing insight quality.


**How it works:**
1. Fetch complete file tree from GitHub API
2. Filter out excluded directories and file types
3. Score each remaining file (0-100 points)
4. Sort by score (descending) then alphabetically
5. Select top 50 files
6. Fetch file contents concurrently (max 20 files)
7. Build context string until 80K char budget reached
8. Send to LLM for analysis

This ensures the LLM receives the most relevant information about the repository without exceeding context limits or token costs.

## Project Structure

```
nebius-repo-summarizer/
├── backend/
│   ├── __init__.py          # Package marker
│   ├── config.py            # Environment variable loading
│   ├── github_service.py    # GitHub API client
│   ├── repo_processor.py    # File filtering and scoring logic
│   ├── llm_service.py       # LLM API integration
│   └── main.py              # FastAPI application and routes
├── static/
│   └── index.html           # Web UI interface
├── .env                     # Your API keys (DO NOT COMMIT)
├── .env.example             # Template for environment variables
├── .gitignore               # Git exclusion rules
├── requirements.txt         # Python dependencies
├── Procfile                 # Deployment config (Heroku/Railway)(experimental)
├── render.yaml              # Render.com deployment config
├── vercel.json              # Vercel deployment config (experimental)
└── README.md                # This file
```

## API Endpoints

### `GET /`
Returns the web UI interface or API status message.

**Response:**
```json
{"message": "GitHub Repo Summarizer API is running"}
```

### `POST /summarize`
Analyzes a GitHub repository and returns a structured summary.

**Request Body:**
```json
{
  "github_url": "https://github.com/owner/repo"
}
```

**Success Response (200):**
```json
{
  "summary": "Project description...",
  "technologies": ["Python", "FastAPI", "..."],
  "structure": "Project organization details..."
}
```

**Error Responses:**
- `400 Bad Request`: Invalid URL or repository not found
- `403 Forbidden`: GitHub rate limit exceeded (add GITHUB_TOKEN)
- `500 Internal Server Error`: LLM API error or other server issues

### `GET /docs`
Interactive Swagger UI for testing the API.

## Environment Variables

Create a `.env` file in the project root:

```bash
# Required: LLM provider selection
LLM_PROVIDER=nebius

# Required: At least one API key
NEBIUS_API_KEY=v1.CmQK...your_actual_key...
OPENAI_API_KEY=sk-...          # Optional
ANTHROPIC_API_KEY=sk-ant-...   # Optional

# Optional: GitHub token for higher rate limits
GITHUB_TOKEN=ghp_...your_token...
```

**Getting API Keys:**
- **Nebius**: Sign up at https://studio.nebius.ai/
- **GitHub Token**: https://github.com/settings/tokens (select `public_repo` scope)


## Technical Decisions & Trade-offs

### Why FastAPI?
- Async support for concurrent GitHub API calls
- Built-in API documentation (Swagger UI)
- Modern Python with type hints
- Easy to deploy

### Why Not Include All Files?
- **Token costs**: LLMs charge per token
- **Context limits**: Most models have 4K-128K token limits
- **Quality**: Too much noise reduces summary accuracy
- **Speed**: Processing 10,000 files takes too long



### Error Handling
- GitHub API errors return clear 400/403 status codes
- LLM errors caught and returned as 500 with error message
- Invalid JSON from LLM handled gracefully

## Limitations & Future Improvements

### Current Limitations
- Only analyzes the default branch (usually `main` or `master`)
- Maximum 50 files processed to stay within context window
- Public repositories only (private repos require GitHub token with appropriate permissions)
- No caching mechanism (re-fetches files on each request)
- Single repository analysis (no comparison features)

### Planned Improvements
- [ ] **Caching Layer**: Add Redis caching for frequently analyzed repositories
- [ ] **Private Repository Support**: Implement OAuth for private repo access
- [ ] **Branch Selection**: Allow users to specify which branch to analyze
- [ ] **Visual Diagrams**: Generate architecture diagrams automatically
- [ ] **Repository Comparison**: Compare multiple repositories side-by-side
- [ ] **Monorepo Support**: Analyze specific subdirectories in large monorepos
- [ ] **Analysis History**: Store previous analyses in a database
- [ ] **Batch Processing**: Analyze multiple repositories concurrently
- [ ] **Custom Prompts**: Allow users to customize the LLM analysis prompt

## Security & Best Practices

⚠️ **Critical Security Notice**

**Never commit your `.env` file to version control!**

The `.gitignore` file is pre-configured to exclude:
- `.env` - Your real API keys and sensitive information
- `__pycache__/` - Python bytecode cache
- `*.pyc` - Compiled Python files
- `.venv/`, `venv/` - Virtual environments
- `*.egg-info/` - Package metadata
- `.pytest_cache/` - Test cache

**Best Practices:**
- ✅ Always use environment variables for sensitive data
- ✅ Never hardcode API keys in source code
- ✅ Use `.env.example` as a template (safe to commit)
- ✅ Rotate API keys regularly
- ✅ Use separate keys for development and production
- ✅ Set appropriate GitHub token scopes (only `public_repo` if analyzing public repos)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - feel free to use it for learning or production.

## Author

**Created as part of Nebius Assignment 26**

- GitHub: [@RiSH2709](https://github.com/RiSH2709)
- Repository: [Nebuis-Assignment-26](https://github.com/RiSH2709/Nebuis-Assignment-26)

## Acknowledgments

- **Nebius AI Studio** - For providing free access to state-of-the-art LLMs
- **FastAPI** - For the excellent Python web framework
- **GitHub** - For the comprehensive REST API
- **Open Source Community** - For inspiration and best practices

---

**Need Help?** Open an issue on GitHub or check the [Swagger documentation](http://localhost:8000/docs) when running locally.
