from .arvan_provider import ArvanProvider

# Map provider names to their implementation classes
PROVIDERS = {
    'arvan': ArvanProvider,
    # Add other providers here: 'cloudflare': CloudflareProvider, etc.
}

def get_provider(provider_name: str):
    """Get provider class by name"""
    provider_class = PROVIDERS.get(provider_name.lower())
    if not provider_class:
        raise ValueError(f"Unsupported provider: {provider_name}")
    return provider_class