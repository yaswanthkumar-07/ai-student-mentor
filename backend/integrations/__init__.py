"""Optional external API clients. Each one has a local fallback or clear unavailable state."""
from .esco import ESCOClient
from .gemini import GeminiClient
from .github import GitHubClient
from .jobs_api import JobsAPIClient
from .youtube import YouTubeClient

__all__ = ["ESCOClient", "GeminiClient", "GitHubClient", "JobsAPIClient",
           "YouTubeClient", "get_integration_status"]


def get_integration_status() -> dict[str, dict]:
    """Non-sensitive readiness summary for every integration."""
    clients = (ESCOClient(), GitHubClient(), YouTubeClient(), JobsAPIClient(), GeminiClient())
    return {client.name: client.status() for client in clients}
