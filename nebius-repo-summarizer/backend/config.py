import os
from dotenv import load_dotenv

load_dotenv()

# LLM provider selection
LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'nebius')

# API Keys
NEBIUS_API_KEY = os.getenv('NEBIUS_API_KEY', '')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')

# GitHub token (optional)
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')

def get_api_key() -> str:
    keys = {
        'nebius': NEBIUS_API_KEY,
        'openai': OPENAI_API_KEY,
        'anthropic': ANTHROPIC_API_KEY,
    }
    key = keys.get(LLM_PROVIDER, '')
    if not key:
        raise ValueError(f'API key not set for provider: {LLM_PROVIDER}')
    return key
