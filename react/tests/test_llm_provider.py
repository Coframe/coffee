import os
import unittest
from unittest.mock import patch, MagicMock

from agents.llm_provider import (
    get_provider,
    get_client,
    get_default_model,
    clamp_temperature,
    prepare_chat_args,
    DEFAULT_MODELS,
)


class TestGetProvider(unittest.TestCase):
    @patch.dict(os.environ, {}, clear=True)
    def test_default_provider_is_openai(self):
        os.environ.pop("LLM_PROVIDER", None)
        self.assertEqual(get_provider(), "openai")

    @patch.dict(os.environ, {"LLM_PROVIDER": "openai"})
    def test_openai_provider(self):
        self.assertEqual(get_provider(), "openai")

    @patch.dict(os.environ, {"LLM_PROVIDER": "minimax"})
    def test_minimax_provider(self):
        self.assertEqual(get_provider(), "minimax")

    @patch.dict(os.environ, {"LLM_PROVIDER": "MiniMax"})
    def test_provider_case_insensitive(self):
        self.assertEqual(get_provider(), "minimax")

    @patch.dict(os.environ, {"LLM_PROVIDER": "unsupported"})
    def test_unsupported_provider_raises(self):
        with self.assertRaises(ValueError) as ctx:
            get_provider()
        self.assertIn("unsupported", str(ctx.exception).lower())


class TestGetClient(unittest.TestCase):
    @patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test123"}, clear=False)
    def test_openai_client(self):
        os.environ.pop("LLM_PROVIDER", None)
        client = get_client()
        self.assertIsNotNone(client)

    @patch.dict(
        os.environ,
        {"LLM_PROVIDER": "minimax", "MINIMAX_API_KEY": "mm-test123"},
    )
    def test_minimax_client(self):
        client = get_client()
        self.assertIsNotNone(client)
        self.assertEqual(str(client.base_url), "https://api.minimax.io/v1/")

    @patch.dict(os.environ, {"LLM_PROVIDER": "minimax"}, clear=False)
    def test_minimax_without_api_key_raises(self):
        os.environ.pop("MINIMAX_API_KEY", None)
        with self.assertRaises(ValueError) as ctx:
            get_client()
        self.assertIn("MINIMAX_API_KEY", str(ctx.exception))


class TestGetDefaultModel(unittest.TestCase):
    @patch.dict(os.environ, {}, clear=False)
    def test_openai_default_model(self):
        os.environ.pop("LLM_PROVIDER", None)
        self.assertEqual(get_default_model(), "gpt-4-1106-preview")

    @patch.dict(os.environ, {"LLM_PROVIDER": "minimax"})
    def test_minimax_default_model(self):
        self.assertEqual(get_default_model(), "MiniMax-M2.5")


class TestClampTemperature(unittest.TestCase):
    @patch.dict(os.environ, {}, clear=False)
    def test_openai_no_clamping(self):
        os.environ.pop("LLM_PROVIDER", None)
        self.assertEqual(clamp_temperature(0.0), 0.0)
        self.assertEqual(clamp_temperature(2.0), 2.0)

    @patch.dict(os.environ, {"LLM_PROVIDER": "minimax"})
    def test_minimax_clamps_zero(self):
        self.assertEqual(clamp_temperature(0.0), 0.01)

    @patch.dict(os.environ, {"LLM_PROVIDER": "minimax"})
    def test_minimax_clamps_high(self):
        self.assertEqual(clamp_temperature(1.5), 1.0)

    @patch.dict(os.environ, {"LLM_PROVIDER": "minimax"})
    def test_minimax_valid_temp(self):
        self.assertEqual(clamp_temperature(0.7), 0.7)


class TestPrepareChatArgs(unittest.TestCase):
    @patch.dict(os.environ, {}, clear=False)
    def test_openai_defaults(self):
        os.environ.pop("LLM_PROVIDER", None)
        msgs = [{"role": "user", "content": "hello"}]
        args = prepare_chat_args(messages=msgs)
        self.assertEqual(args["model"], "gpt-4-1106-preview")
        self.assertEqual(args["messages"], msgs)
        self.assertTrue(args["stream"])
        self.assertNotIn("response_format", args)

    @patch.dict(os.environ, {"LLM_PROVIDER": "minimax"})
    def test_minimax_defaults(self):
        msgs = [{"role": "user", "content": "hello"}]
        args = prepare_chat_args(messages=msgs)
        self.assertEqual(args["model"], "MiniMax-M2.5")

    @patch.dict(os.environ, {"LLM_PROVIDER": "minimax"})
    def test_minimax_json_object_falls_back_to_text(self):
        msgs = [{"role": "user", "content": "hello"}]
        args = prepare_chat_args(
            messages=msgs,
            response_format={"type": "json_object"},
        )
        self.assertEqual(args["response_format"], {"type": "text"})

    @patch.dict(os.environ, {}, clear=False)
    def test_openai_json_object_preserved(self):
        os.environ.pop("LLM_PROVIDER", None)
        msgs = [{"role": "user", "content": "hello"}]
        args = prepare_chat_args(
            messages=msgs,
            response_format={"type": "json_object"},
        )
        self.assertEqual(args["response_format"], {"type": "json_object"})

    @patch.dict(os.environ, {}, clear=False)
    def test_custom_model_override(self):
        os.environ.pop("LLM_PROVIDER", None)
        msgs = [{"role": "user", "content": "hello"}]
        args = prepare_chat_args(messages=msgs, model="gpt-4")
        self.assertEqual(args["model"], "gpt-4")

    @patch.dict(os.environ, {"LLM_PROVIDER": "minimax"})
    def test_text_response_format_preserved_for_minimax(self):
        msgs = [{"role": "user", "content": "hello"}]
        args = prepare_chat_args(
            messages=msgs,
            response_format={"type": "text"},
        )
        self.assertEqual(args["response_format"], {"type": "text"})


if __name__ == "__main__":
    unittest.main()
