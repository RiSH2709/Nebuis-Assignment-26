import json
import httpx
from openai import AsyncOpenAI
from backend.config import LLM_PROVIDER, get_api_key

# Base URLs per provider
PROVIDER_BASES = {
    'nebius': 'https://api.studio.nebius.ai/v1',
    'openai': 'https://api.openai.com/v1',
}

# Default model per provider
PROVIDER_MODELS = {
    'nebius': 'meta-llama/Llama-3.3-70B-Instruct',
    'openai': 'gpt-4o-mini',
    'anthropic': 'claude-3-5-haiku-latest',
}

SYSTEM_PROMPT = '''You are an expert software engineer reviewing a codebase.
Analyze the provided repository files carefully.

Return ONLY a JSON object (no markdown, no preamble) with exactly these keys:
- summary: 2-3 sentences. What does this project DO? Who is it for?
- technologies: Array of strings. List languages, frameworks, and major libraries.
- structure: 1-2 sentences. How is the code organized?

Example output:
{
  "summary": "Flask is a lightweight Python web framework...",
  "technologies": ["Python", "Jinja2", "Werkzeug"],
  "structure": "Single package with routing, templating, and WSGI support."
}

Respond with ONLY the JSON object. Nothing else.'''


async def _summarize_with_openai_compatible(context: str) -> dict:
    client = AsyncOpenAI(
        api_key=get_api_key(),
        base_url=PROVIDER_BASES.get(LLM_PROVIDER, PROVIDER_BASES['nebius'])
    )
    model = PROVIDER_MODELS.get(LLM_PROVIDER, PROVIDER_MODELS['nebius'])
    user_message = f'Here are the repository files:\n{context}\n\nSummarize this project.'
    response = await client.chat.completions.create(
        model=model,
        messages=[
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': user_message}
        ],
        max_tokens=1000,
        temperature=0.3
    )
    raw = response.choices[0].message.content.strip()
    raw = raw.replace('```json', '').replace('```', '').strip()
    return json.loads(raw)


async def _summarize_with_anthropic(context: str) -> dict:
    model = PROVIDER_MODELS['anthropic']
    payload = {
        'model': model,
        'max_tokens': 1000,
        'temperature': 0.3,
        'system': SYSTEM_PROMPT,
        'messages': [
            {'role': 'user', 'content': f'Here are the repository files:\n{context}\n\nSummarize this project.'}
        ],
    }
    headers = {
        'x-api-key': get_api_key(),
        'anthropic-version': '2023-06-01',
        'content-type': 'application/json',
    }
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post('https://api.anthropic.com/v1/messages', headers=headers, json=payload)
        response.raise_for_status()
    data = response.json()
    content = data.get('content', [])
    text_parts = [part.get('text', '') for part in content if part.get('type') == 'text']
    raw = ''.join(text_parts).strip().replace('```json', '').replace('```', '').strip()
    return json.loads(raw)

async def summarize_repo(context: str) -> dict:
    """Send repo context to LLM and return structured summary."""
    if LLM_PROVIDER == 'anthropic':
        return await _summarize_with_anthropic(context)
    return await _summarize_with_openai_compatible(context)
