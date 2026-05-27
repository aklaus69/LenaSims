"""
Async Ollama client for local LLM inference.
FORCED to use localhost:11434 - ignores environment variables.
"""

from typing import Any
import httpx
import os

from .models import Message


class OllamaError(Exception):
    """Exception raised for Ollama API errors."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class OllamaClient:
    """Async client for Ollama API - forced to localhost."""

    # HARDCODED: Ignores env vars that might break things
    DEFAULT_URL = "http://localhost:11434"

    def __init__(
        self,
        base_url: str | None = None,  # Changed: None means use DEFAULT_URL
        default_model: str = "llama3.2",
        timeout: float = 60.0,
    ) -> None:
        """
        Initialize the Ollama client.

        Args:
            base_url: Ignored! Always uses localhost:11434
            default_model: The default model to use for generation
            timeout: Request timeout in seconds
        """
        # FORCE localhost:11434 - never use env vars
        self.base_url = self.DEFAULT_URL
        self.default_model = default_model
        self.timeout = timeout
        self._client = httpx.AsyncClient(timeout=timeout)

    async def generate(
        self,
        prompt: str,
        model: str | None = None,
        system: str | None = None,
        stream: bool = False,
        options: dict[str, Any] | None = None,
    ) -> str:
        """Generate a response from the Ollama API."""
        model = model or self.default_model
        url = f"{self.base_url}/api/generate"

        payload: dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
        }

        if system:
            payload["system"] = system

        if options:
            payload["options"] = options

        try:
            response = await self._client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")
        except httpx.HTTPStatusError as e:
            raise OllamaError(
                f"HTTP error {e.response.status_code}: {e.response.text}",
                status_code=e.response.status_code,
            )
        except httpx.RequestError as e:
            raise OllamaError(f"Request failed (is Ollama running on localhost:11434?): {e}")
        except Exception as e:
            raise OllamaError(f"Unexpected error: {e}")

    async def chat(
        self,
        messages: list[Message],
        model: str | None = None,
        stream: bool = False,
        options: dict[str, Any] | None = None,
    ) -> str:
        """Chat with the Ollama API using conversation history."""
        model = model or self.default_model
        url = f"{self.base_url}/api/chat"

        # Convert Message objects to Ollama format
        ollama_messages = []
        for msg in messages:
            role = msg.role
            # Keep standard Ollama roles: user, assistant
            if role == "system":
                role = "user"  # Gemini compatibility
            
            ollama_messages.append({
                "role": role,
                "content": msg.content,
            })

        payload: dict[str, Any] = {
            "model": model,
            "messages": ollama_messages,
            "stream": stream,
        }

        if options:
            payload["options"] = options

        try:
            response = await self._client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            content = data.get("message", {}).get("content", "")
            return content
        except httpx.HTTPStatusError as e:
            raise OllamaError(
                f"HTTP error {e.response.status_code}: {e.response.text}",
                status_code=e.response.status_code,
            )
        except httpx.RequestError as e:
            raise OllamaError(f"Request failed (is Ollama running on localhost:11434?): {e}")
        except Exception as e:
            raise OllamaError(f"Unexpected error: {e}")

    async def list_models(self) -> list[str]:
        """List available models from the Ollama server."""
        url = f"{self.base_url}/api/tags"

        try:
            response = await self._client.get(url)
            response.raise_for_status()
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
        except httpx.HTTPStatusError as e:
            raise OllamaError(
                f"HTTP error {e.response.status_code}: {e.response.text}",
                status_code=e.response.status_code,
            )
        except httpx.RequestError as e:
            raise OllamaError(f"Request failed (is Ollama running on localhost:11434?): {e}")
        except Exception as e:
            raise OllamaError(f"Unexpected error: {e}")

    async def health_check(self) -> bool:
        """Check if the Ollama server is healthy."""
        try:
            await self.list_models()
            return True
        except OllamaError:
            return False

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.aclose()

    async def __aenter__(self) -> "OllamaClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()
