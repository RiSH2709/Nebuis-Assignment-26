# Strategy: Score files by importance, skip junk, fit within token budget

# Directories to completely skip
SKIP_DIRS = {
    'node_modules', '.git', '__pycache__', 'dist', 'build',
    '.venv', 'venv', 'vendor', '.next', '.nuxt', 'coverage',
    '.pytest_cache', '.mypy_cache', 'target', 'out', 'bin', 'obj'
}

# File extensions to skip (binary/generated/irrelevant)
SKIP_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.webp',
    '.mp4', '.mp3', '.wav', '.zip', '.tar', '.gz', '.exe',
    '.dll', '.so', '.pyc', '.class', '.map', '.min.js',
    '.lock', '.log'
}

# Exact filenames to skip
SKIP_FILES = {
    'package-lock.json', 'yarn.lock', 'poetry.lock', 'Pipfile.lock',
    'composer.lock', '.DS_Store', 'Thumbs.db'
}

def score_file(path: str) -> int:
    """Score a file 0-100 based on how useful it is for understanding the project."""
    name = path.split('/')[-1].lower()
    # Top priority: README
    if name in ('readme.md', 'readme.rst', 'readme.txt'):
        return 100
    # High priority: dependency files
    if name in ('package.json', 'pyproject.toml', 'cargo.toml', 'go.mod', 'pom.xml'):
        return 90
    if name in ('requirements.txt', 'setup.py', 'setup.cfg'):
        return 82
    # Config files
    if name in ('dockerfile', 'docker-compose.yml', 'docker-compose.yaml'):
        return 72
    if name.endswith(('.yml', '.yaml', '.toml', '.cfg', '.ini')) and '/' not in path:
        return 65
    # Entry points
    if name in ('main.py', 'app.py', 'index.js', 'index.ts', 'server.py', 'server.js'):
        return 55
    # Other source files get low-medium score
    return 20

def should_skip(path: str) -> bool:
    """Return True if this file should be excluded entirely."""
    parts = path.split('/')
    # Skip if in a junk directory
    for part in parts[:-1]:
        if part.lower() in SKIP_DIRS:
            return True
    filename = parts[-1]
    # Skip exact filenames
    if filename in SKIP_FILES:
        return True
    # Skip by extension
    for ext in SKIP_EXTENSIONS:
        if filename.lower().endswith(ext):
            return True
    return False

def select_files(all_files: list[dict]) -> list[str]:
    """Filter and rank files. Return top files by priority score."""
    candidates = []
    for f in all_files:
        path = f['path']
        if not should_skip(path):
            score = score_file(path)
            candidates.append((score, path))
    # Sort by score descending, then alphabetically
    candidates.sort(key=lambda x: (-x[0], x[1]))
    # Return top 50 file paths
    return [path for _, path in candidates[:50]]

def build_context(file_contents: dict[str, str], max_chars: int = 80000) -> str:
    """
    Combine file contents into a single context string.
    Respects a character budget to avoid exceeding LLM context window.
    """
    parts = []
    total = 0
    for path, content in file_contents.items():
        if not content.strip():
            continue
        header = f'\n\n=== FILE: {path} ===\n'
        # Truncate individual files that are too long
        truncated = content[:5000] if len(content) > 5000 else content
        chunk = header + truncated
        if total + len(chunk) > max_chars:
            break
        parts.append(chunk)
        total += len(chunk)
    return ''.join(parts)
