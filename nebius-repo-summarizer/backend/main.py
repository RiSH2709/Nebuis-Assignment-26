from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from backend.github_service import parse_github_url, fetch_repo_tree, fetch_file_content
from backend.repo_processor import select_files, build_context, build_directory_tree
from backend.llm_service import summarize_repo
import asyncio
import os
import logging
from datetime import datetime

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

app = FastAPI(title='GitHub Repo Summarizer')

# Log application startup
logger.info("GitHub Repo Summarizer API started")

# Mount static files
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

class SummarizeRequest(BaseModel):
    github_url: str

@app.post('/summarize')
async def summarize(request: SummarizeRequest):
    start_time = datetime.now()
    logger.info(f"New summarize request for: {request.github_url}")
    
    try:
        # Step 1: Parse the URL
        owner, repo = parse_github_url(request.github_url)
        logger.debug(f"Parsed repo: {owner}/{repo}")

        # Step 2: Get all files in the repo
        all_files = await fetch_repo_tree(owner, repo)
        if not all_files:
            logger.warning(f"Repository {owner}/{repo} is empty")
            return JSONResponse(status_code=400,
                content={'status': 'error', 'message': 'Repository is empty'})
        
        logger.info(f"Fetched {len(all_files)} files from {owner}/{repo}")

        # Step 3: Select important files
        selected_paths = select_files(all_files)
        logger.debug(f"Selected {len(selected_paths)} important files")

        # Step 4: Fetch file contents concurrently
        tasks = [fetch_file_content(owner, repo, path) for path in selected_paths[:20]]
        contents_list = await asyncio.gather(*tasks)
        file_contents = dict(zip(selected_paths[:20], contents_list))

        # Step 5: Build context string with directory structure and file content
        directory_tree = build_directory_tree(all_files)
        file_context = build_context(file_contents)
        context = f'{directory_tree}\n\n{file_context}'
        logger.debug(f"Built context: {len(context)} characters")

        # Step 6: Call LLM
        logger.info(f"Sending context to LLM for {owner}/{repo}")
        result = await summarize_repo(context)

        # Log success with timing
        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(f"Successfully analyzed {owner}/{repo} in {elapsed:.2f}s")

        return result

    except ValueError as e:
        logger.error(f"Invalid URL or repo not found: {request.github_url} - {str(e)}")
        return JSONResponse(status_code=400,
            content={'status': 'error', 'message': str(e)})
    except Exception as e:
        elapsed = (datetime.now() - start_time).total_seconds()
        logger.error(f"Error analyzing {request.github_url} after {elapsed:.2f}s: {str(e)}", exc_info=True)
        return JSONResponse(status_code=500,
            content={'status': 'error', 'message': f'Internal error: {str(e)}'})

@app.get('/')
async def root():
    index_path = os.path.join(static_dir, 'index.html')
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {'message': 'GitHub Repo Summarizer API is running'}


@app.get('/health')
async def health():
    logger.debug("Health check requested")
    return {'status': 'ok'}
