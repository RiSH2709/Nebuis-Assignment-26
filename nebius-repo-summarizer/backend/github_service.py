# backend/github_service.py
import httpx
from backend.config import GITHUB_TOKEN

def parse_github_url(github_url: str) -> tuple[str, str]:
    """Extract owner and repo name from GitHub URL."""
    parts = github_url.rstrip('/').split('/')
    if len(parts) < 2:
        raise ValueError('Invalid GitHub URL format')
    return parts[-2], parts[-1]

def get_headers() -> dict:
    headers = {'Accept': 'application/vnd.github.v3+json'}
    if GITHUB_TOKEN:
        headers['Authorization'] = f'token {GITHUB_TOKEN}'
    return headers

async def fetch_repo_tree(owner: str, repo: str) -> list[dict]:
    """Fetch the full file tree of a repository."""
    url = f'https://api.github.com/repos/{owner}/{repo}/git/trees/HEAD?recursive=1'
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(url, headers=get_headers())
        if response.status_code == 404:
            raise ValueError('Repository not found or is private')
        if response.status_code == 403:
            raise ValueError('GitHub rate limit exceeded. Add GITHUB_TOKEN to .env')
        response.raise_for_status()
    data = response.json()
    return [item for item in data.get('tree', []) if item['type'] == 'blob']

async def fetch_file_content(owner: str, repo: str, path: str) -> str:
    """Fetch the content of a single file."""
    url = f'https://api.github.com/repos/{owner}/{repo}/contents/{path}'
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(url, headers=get_headers())
        if response.status_code != 200:
            return ''
    data = response.json()
    import base64
    content = data.get('content', '')
    if not content:
        return ''
    try:
        return base64.b64decode(content).decode('utf-8', errors='replace')
    except Exception:
        return ''
