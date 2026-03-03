# GitHub Repository Summarizer

A Python API that analyzes GitHub repositories and generates human-readable summaries using an LLM. Built with FastAPI, this tool intelligently selects and processes repository files to provide comprehensive project insights.

## Features

- 🔍 Analyzes any public GitHub repository
- 🤖 Uses Nebius AI (Llama-3.1-8B-Instruct) for intelligent summarization
- 📊 Extracts technologies, project structure, and key insights
- 🎨 Beautiful web UI for easy interaction
- 📡 RESTful API with interactive Swagger documentation
- ⚡ Smart file filtering and context management

## Setup

**Requirements:** Python 3.10+

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
├── Procfile                 # Deployment config (Heroku/Railway)
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

## Testing

Start the server and test locally:

```bash
# Terminal 1: Start server
python -m uvicorn backend.main:app --reload --port 8000

# Terminal 2: Test with curl
curl -X POST http://localhost:8000/summarize \
  -H 'Content-Type: application/json' \
  -d '{"github_url": "https://github.com/psf/requests"}'

# Or open browser
open http://localhost:8000/
open http://localhost:8000/docs
```

## Limitations & Future Improvements

**Current Limitations:**
- Only analyzes default branch (usually `main` or `master`)
- 50 file limit to stay within context window
- Public repositories only (unless GitHub token provided)
- No caching (re-fetches files each request)

**Potential Improvements:**
- [ ] Add Redis caching for frequently analyzed repos
- [ ] Support private repositories with OAuth
- [ ] Allow branch selection
- [ ] Generate visual architecture diagrams
- [ ] Add repository comparison feature
- [ ] Support for monorepos (analyze specific subdirectories)
- [ ] Store analysis history in database

## Security Notes

⚠️ **Never commit your `.env` file to GitHub!**

The `.gitignore` file is configured to exclude:
- `.env` (your real API keys)
- `__pycache__/` (Python bytecode)
- Virtual environments (`venv/`, `.venv/`)

Always use environment variables for sensitive data, never hardcode API keys.

## License

MIT License - Feel free to use this project for learning or production.

## Author

Created as part of Nebius Assignment 26  
GitHub: [@RiSH2709](https://github.com/RiSH2709)

## Acknowledgments

- **Nebius AI Studio** for providing free LLM access
- **FastAPI** for the excellent web framework
- **GitHub** for the comprehensive REST API
