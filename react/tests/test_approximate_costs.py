import unittest
from agents.approximate_costs import approximate_costs, MODEL_COST_PER_1K_TOKENS


class TestApproximateCostsOpenAI(unittest.TestCase):
    def test_gpt4_cost(self):
        fx_args = {
            "model": "gpt-4-1106-preview",
            "messages": [{"role": "user", "content": "Hello world"}],
        }
        result = approximate_costs(fx_args, "Hi there!")
        self.assertIn("total_cost", result)
        self.assertIn("total_tokens", result)
        self.assertGreater(result["total_cost"], 0)
        self.assertGreater(result["total_tokens"], 0)


class TestApproximateCostsMiniMax(unittest.TestCase):
    def test_minimax_m25_in_cost_table(self):
        self.assertIn("MiniMax-M2.5", MODEL_COST_PER_1K_TOKENS)
        self.assertIn("MiniMax-M2.5-completion", MODEL_COST_PER_1K_TOKENS)

    def test_minimax_m25_highspeed_in_cost_table(self):
        self.assertIn("MiniMax-M2.5-highspeed", MODEL_COST_PER_1K_TOKENS)
        self.assertIn("MiniMax-M2.5-highspeed-completion", MODEL_COST_PER_1K_TOKENS)

    def test_minimax_cost_calculation(self):
        fx_args = {
            "model": "MiniMax-M2.5",
            "messages": [{"role": "user", "content": "Hello world, this is a test prompt."}],
        }
        result = approximate_costs(fx_args, "Hi there, this is a test response!")
        self.assertIn("total_cost", result)
        self.assertIn("total_tokens", result)
        self.assertGreater(result["total_cost"], 0)
        self.assertGreater(result["total_tokens"], 0)

    def test_minimax_highspeed_cheaper_than_standard(self):
        fx_args_standard = {
            "model": "MiniMax-M2.5",
            "messages": [{"role": "user", "content": "Hello world"}],
        }
        fx_args_highspeed = {
            "model": "MiniMax-M2.5-highspeed",
            "messages": [{"role": "user", "content": "Hello world"}],
        }
        response = "This is a test response."
        cost_standard = approximate_costs(fx_args_standard, response)
        cost_highspeed = approximate_costs(fx_args_highspeed, response)
        self.assertGreater(cost_standard["total_cost"], cost_highspeed["total_cost"])

    def test_unknown_model_returns_zero_cost(self):
        fx_args = {
            "model": "unknown-model",
            "messages": [{"role": "user", "content": "test"}],
        }
        result = approximate_costs(fx_args, "response")
        self.assertEqual(result["total_cost"], 0)
        self.assertGreater(result["total_tokens"], 0)


if __name__ == "__main__":
    unittest.main()
