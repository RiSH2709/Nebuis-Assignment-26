from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from backend.github_service import parse_github_url, fetch_repo_tree, fetch_file_content
from backend.repo_processor import select_files, build_context
from backend.llm_service import summarize_repo
import asyncio

app = FastAPI(title='GitHub Repo Summarizer')

class SummarizeRequest(BaseModel):
    github_url: str

@app.post('/summarize')
async def summarize(request: SummarizeRequest):
    try:
        # Step 1: Parse the URL
        owner, repo = parse_github_url(request.github_url)

        # Step 2: Get all files in the repo
        all_files = await fetch_repo_tree(owner, repo)
        if not all_files:
            return JSONResponse(status_code=400,
                content={'status': 'error', 'message': 'Repository is empty'})

        # Step 3: Select important files
        selected_paths = select_files(all_files)

        # Step 4: Fetch file contents concurrently
        tasks = [fetch_file_content(owner, repo, path) for path in selected_paths[:20]]
        contents_list = await asyncio.gather(*tasks)
        file_contents = dict(zip(selected_paths[:20], contents_list))

        # Step 5: Build context string within token budget
        context = build_context(file_contents)

        # Step 6: Call LLM
        result = await summarize_repo(context)

        return result

    except ValueError as e:
        return JSONResponse(status_code=400,
            content={'status': 'error', 'message': str(e)})
    except Exception as e:
        return JSONResponse(status_code=500,
            content={'status': 'error', 'message': f'Internal error: {str(e)}'})

@app.get('/')
async def root():
    return {'message': 'GitHub Repo Summarizer API is running'}
