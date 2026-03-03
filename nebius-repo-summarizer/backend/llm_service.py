import json
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
}

SYSTEM_PROMPT = '''You are a senior software engineer.
Analyze the provided repository files and return ONLY a JSON object with these keys:
- summary: A 2-3 sentence human-readable description of what the project does
- technologies: An array of strings listing main technologies, languages, frameworks
- structure: A 1-2 sentence description of how the project is organized

Respond ONLY with valid JSON. No markdown fences. No extra text.'''

async def summarize_repo(context: str) -> dict:
    """Send repo context to LLM and return structured summary."""
    client = AsyncOpenAI(
        api_key=get_api_key(),
        base_url=PROVIDER_BASES.get(LLM_PROVIDER, PROVIDER_BASES['nebius'])
    )
    model = PROVIDER_MODELS.get(LLM_PROVIDER, 'nvidia/Llama-3.1-8B-Instruct')
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
    # Clean up markdown fences if model adds them
    raw = raw.replace('```json', '').replace('```', '').strip()
    return json.loads(raw)
