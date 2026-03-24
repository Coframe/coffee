"""
Integration tests for MiniMax LLM provider.

These tests make real API calls to MiniMax and require:
  - MINIMAX_API_KEY environment variable to be set
  - LLM_PROVIDER=minimax

Run with:
  LLM_PROVIDER=minimax MINIMAX_API_KEY=your_key pytest tests/test_minimax_integration.py -v
"""

import os
import unittest

# Skip all tests if MINIMAX_API_KEY is not set
MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY")
SKIP_REASON = "MINIMAX_API_KEY not set; skipping integration tests"


@unittest.skipUnless(MINIMAX_API_KEY, SKIP_REASON)
class TestMiniMaxIntegration(unittest.TestCase):
    def setUp(self):
        os.environ["LLM_PROVIDER"] = "minimax"

    def tearDown(self):
        os.environ.pop("LLM_PROVIDER", None)

    def test_minimax_chat_completion(self):
        from agents.llm_provider import get_client, get_default_model

        client = get_client()
        response = client.chat.completions.create(
            model=get_default_model(),
            messages=[{"role": "user", "content": "Say hello in one word."}],
            stream=False,
        )
        self.assertIsNotNone(response.choices)
        self.assertGreater(len(response.choices), 0)
        self.assertIsNotNone(response.choices[0].message.content)

    def test_minimax_streaming(self):
        from agents.llm_provider import get_client, get_default_model

        client = get_client()
        stream = client.chat.completions.create(
            model=get_default_model(),
            messages=[
                {"role": "user", "content": "Write a short greeting message."}
            ],
            stream=True,
        )
        chunks = []
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                chunks.append(chunk.choices[0].delta.content)
        self.assertGreater(len(chunks), 0)

    def test_minimax_code_generation_prompt(self):
        from agents.llm_provider import get_client, get_default_model

        client = get_client()
        response = client.chat.completions.create(
            model=get_default_model(),
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Write a simple React button component that says 'Click Me'. "
                        "Output only the code within ``` and nothing else."
                    ),
                }
            ],
            stream=False,
        )
        content = response.choices[0].message.content
        self.assertIn("Click Me", content)


if __name__ == "__main__":
    unittest.main()
