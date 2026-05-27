"""
Async Ollama client for local LLM inference.
"""

from typing import Any
import httpx

from .models import Message


class OllamaError(Exception):
    """Exception raised for Ollama API errors."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class OllamaClient:
    """Async client for Ollama API."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        default_model: str = "llama3.2",
        timeout: float = 60.0,
    ) -> None:
        """
        Initialize the Ollama client.

        Args:
            base_url: The base URL of the Ollama server
            default_model: The default model to use for generation
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
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
        """
        Generate a response from the Ollama API.

        Args:
            prompt: The prompt to send to the model
            model: The model to use (defaults to default_model)
            system: Optional system message
            stream: Whether to stream the response
            options: Additional options for the generation

        Returns:
            The generated response text

        Raises:
            OllamaError: If the API request fails
        """
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
            raise OllamaError(f"Request failed: {e}")
        except Exception as e:
            raise OllamaError(f"Unexpected error: {e}")

    async def chat(
        self,
        messages: list[Message],
        model: str | None = None,
        stream: bool = False,
        options: dict[str, Any] | None = None,
    ) -> str:
        """
        Chat with the Ollama API using conversation history.

        Args:
            messages: List of messages for context
            model: The model to use (defaults to default_model)
            stream: Whether to stream the response
            options: Additional options for the generation

        Returns:
            The generated response text

        Raises:
            OllamaError: If the API request fails
        """
        model = model or self.default_model
        url = f"{self.base_url}/api/chat"

        # Convert Message objects to Ollama format
        # Gemini-compatible: user, assistant (NOT model - that's OpenAI)
        ollama_messages = []
        for msg in messages:
            role = msg.role
            # Keep standard Ollama roles: user, assistant
            if role == "system":
                # System als user umwandeln für Gemini
                role = "user"
            
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
            raise OllamaError(f"Request failed: {e}")
        except Exception as e:
            raise OllamaError(f"Unexpected error: {e}")

    async def list_models(self) -> list[str]:
        """
        List available models from the Ollama server.

        Returns:
            List of model names

        Raises:
            OllamaError: If the API request fails
        """
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
            raise OllamaError(f"Request failed: {e}")
        except Exception as e:
            raise OllamaError(f"Unexpected error: {e}")

    async def health_check(self) -> bool:
        """
        Check if the Ollama server is healthy.

        Returns:
            True if the server is reachable, False otherwise
        """
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
