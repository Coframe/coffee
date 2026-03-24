"""
LLM provider factory for Coffee.

Supports OpenAI and MiniMax (via OpenAI-compatible API).
Set the LLM_PROVIDER environment variable to select the provider:
  - "openai" (default): Uses the OpenAI API with OPENAI_API_KEY
  - "minimax": Uses the MiniMax API with MINIMAX_API_KEY

MiniMax models are accessed via their OpenAI-compatible endpoint
(https://api.minimax.io/v1).
"""

import os
from openai import OpenAI


# Default models for each provider
DEFAULT_MODELS = {
    "openai": "gpt-4-1106-preview",
    "minimax": "MiniMax-M2.5",
}

# MiniMax temperature must be in (0.0, 1.0]
_MINIMAX_TEMP_MIN = 0.01
_MINIMAX_TEMP_MAX = 1.0


def get_provider() -> str:
    """Return the configured LLM provider name (lowercase)."""
    provider = os.environ.get("LLM_PROVIDER", "openai").lower()
    if provider not in ("openai", "minimax"):
        raise ValueError(
            f"Unsupported LLM_PROVIDER: {provider!r}. "
            "Supported providers: openai, minimax"
        )
    return provider


def get_client() -> OpenAI:
    """Create an OpenAI-compatible client for the configured provider."""
    provider = get_provider()

    if provider == "minimax":
        api_key = os.environ.get("MINIMAX_API_KEY")
        if not api_key:
            raise ValueError(
                "MINIMAX_API_KEY environment variable is required "
                "when LLM_PROVIDER=minimax"
            )
        return OpenAI(
            api_key=api_key,
            base_url="https://api.minimax.io/v1",
        )

    # Default: OpenAI
    return OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def get_default_model() -> str:
    """Return the default model name for the configured provider."""
    return DEFAULT_MODELS[get_provider()]


def clamp_temperature(temperature: float) -> float:
    """Clamp temperature to the provider's supported range.

    MiniMax requires temperature in (0.0, 1.0].
    OpenAI accepts [0.0, 2.0].
    """
    if get_provider() == "minimax":
        return max(_MINIMAX_TEMP_MIN, min(temperature, _MINIMAX_TEMP_MAX))
    return temperature


def prepare_chat_args(
    messages: list,
    response_format: dict | None = None,
    stream: bool = True,
    **kwargs,
) -> dict:
    """Build chat completion kwargs suitable for the current provider.

    Automatically selects the default model and adjusts parameters
    for provider compatibility (e.g. MiniMax does not support
    ``response_format={"type": "json_object"}`` reliably, so we
    fall back to ``{"type": "text"}`` and parse the output ourselves).
    """
    model = kwargs.pop("model", None) or get_default_model()
    provider = get_provider()

    args = {
        "model": model,
        "messages": messages,
        "stream": stream,
        **kwargs,
    }

    if response_format is not None:
        if provider == "minimax" and response_format.get("type") == "json_object":
            # MiniMax may not fully support json_object mode; use text
            args["response_format"] = {"type": "text"}
        else:
            args["response_format"] = response_format

    return args
