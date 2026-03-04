import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from backend.github_service import fetch_repo_files, fetch_file_contents, parse_github_url
from backend.repo_processor import select_files, build_context, build_directory_tree
from backend.llm_service import call_llm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI(title="GitHub Repo Summarizer")

# Custom exception handler for consistent error format
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail
        }
    )

# Serve the web UI
@app.get('/', response_class=HTMLResponse)
async def read_root():
    """Serve the web UI or return status"""
    try:
        with open('static/index.html', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return {"message": "GitHub Repo Summarizer API is running"}

# Health check endpoint
@app.get('/health')
async def health():
    """Health check endpoint for monitoring"""
    logger.info("Health check requested")
    return {'status': 'ok'}

# Request model
class SummarizeRequest(BaseModel):
    github_url: str

# Main summarize endpoint
@app.post('/summarize')
async def summarize(request: SummarizeRequest):
    """Analyze a GitHub repository and return summary"""
    start_time = datetime.now()
    logger.info(f"New summarize request for: {request.github_url}")
    
    try:
        # Parse and validate GitHub URL
        owner, repo = parse_github_url(request.github_url)
        logger.debug(f"Parsed URL: owner={owner}, repo={repo}")
        
        # Fetch repository file tree
        all_files = await fetch_repo_files(owner, repo)
        logger.info(f"Fetched {len(all_files)} files from {owner}/{repo}")
        
        if not all_files:
            logger.warning(f"Repository {owner}/{repo} is empty")
            raise HTTPException(
                status_code=400,
                detail=f"Repository {owner}/{repo} appears to be empty or has no accessible files"
            )
        
        # Build directory tree context
        tree_context = build_directory_tree(all_files)
        logger.debug(f"Built directory tree with {len(tree_context.splitlines())} lines")
        
        # Select important files
        selected_files = select_files(all_files)
        logger.info(f"Selected {len(selected_files)} important files for analysis")
        
        # Fetch file contents
        file_contents = await fetch_file_contents(owner, repo, selected_files)
        logger.info(f"Fetched contents of {len(file_contents)} files")
        
        # Build context with directory tree
        context = f"{tree_context}\n\n{build_context(file_contents)}"
        logger.debug(f"Built context of {len(context)} characters")
        
        # Send to LLM for analysis
        logger.info(f"Sending context to LLM for {owner}/{repo}")
        summary_data = await call_llm(context)
        
        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(f"Successfully analyzed {owner}/{repo} in {elapsed:.2f}s")
        
        return summary_data
    
    except ValueError as e:
        # Invalid URL or parsing errors
        logger.error(f"Invalid URL: {request.github_url} - {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions (already formatted correctly)
        raise
    
    except Exception as e:
        # Unexpected errors
        error_msg = str(e)
        logger.error(f"Error analyzing {request.github_url}: {error_msg}", exc_info=True)
        
        # Provide user-friendly error messages
        if "rate limit" in error_msg.lower():
            raise HTTPException(
                status_code=403,
                detail="GitHub API rate limit exceeded. Please add a GITHUB_TOKEN to your .env file for higher limits."
            )
        elif "not found" in error_msg.lower() or "404" in error_msg:
            raise HTTPException(
                status_code=400,
                detail=f"Repository not found or is private. Please check the URL: {request.github_url}"
            )
        elif "timeout" in error_msg.lower():
            raise HTTPException(
                status_code=500,
                detail="Request timeout. The repository may be too large or the service is slow. Please try again."
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while analyzing the repository: {error_msg}"
            )

logger.info("GitHub Repo Summarizer API started")
