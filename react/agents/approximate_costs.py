import tiktoken

# TODO: use langchain if we will use it for future agents
MODEL_COST_PER_1K_TOKENS = {
    # GPT-4 input
    "gpt-4": 0.03,
    "gpt-4-0314": 0.03,
    "gpt-4-0613": 0.03,
    "gpt-4-32k": 0.06,
    "gpt-4-32k-0314": 0.06,
    "gpt-4-32k-0613": 0.06,
    "gpt-4-vision-preview": 0.01,
    "gpt-4-1106-preview": 0.01,
    # GPT-4 output
    "gpt-4-completion": 0.06,
    "gpt-4-0314-completion": 0.06,
    "gpt-4-0613-completion": 0.06,
    "gpt-4-32k-completion": 0.12,
    "gpt-4-32k-0314-completion": 0.12,
    "gpt-4-32k-0613-completion": 0.12,
    "gpt-4-vision-preview-completion": 0.03,
    "gpt-4-1106-preview-completion": 0.03,
    # GPT-3.5 input
    "gpt-3.5-turbo": 0.0015,
    "gpt-3.5-turbo-0301": 0.0015,
    "gpt-3.5-turbo-0613": 0.0015,
    "gpt-3.5-turbo-1106": 0.001,
    "gpt-3.5-turbo-instruct": 0.0015,
    "gpt-3.5-turbo-16k": 0.003,
    "gpt-3.5-turbo-16k-0613": 0.003,
    # GPT-3.5 output
    "gpt-3.5-turbo-completion": 0.002,
    "gpt-3.5-turbo-0301-completion": 0.002,
    "gpt-3.5-turbo-0613-completion": 0.002,
    "gpt-3.5-turbo-1106-completion": 0.002,
    "gpt-3.5-turbo-instruct-completion": 0.002,
    "gpt-3.5-turbo-16k-completion": 0.004,
    "gpt-3.5-turbo-16k-0613-completion": 0.004,
    # MiniMax input (per 1K tokens, https://platform.minimaxi.com/document/Price)
    "MiniMax-M2.5": 0.0011,
    "MiniMax-M2.5-highspeed": 0.0004,
    # MiniMax output (per 1K tokens)
    "MiniMax-M2.5-completion": 0.0044,
    "MiniMax-M2.5-highspeed-completion": 0.0016,
}


def approximate_costs(fx_args, full_response):
    model = fx_args["model"]

    # For models without tiktoken support (e.g. MiniMax), estimate ~4 chars per token
    try:
        encoding = tiktoken.encoding_for_model(model)
        input_tokens = 0
        for message in fx_args["messages"]:
            input_tokens += 3 + len(encoding.encode(message["content"]))
        output_tokens = 3 + len(encoding.encode(full_response))
    except KeyError:
        input_tokens = 0
        for message in fx_args["messages"]:
            input_tokens += 3 + len(message["content"]) // 4
        output_tokens = 3 + len(full_response) // 4

    input_cost_key = model
    output_cost_key = model + "-completion"

    if input_cost_key not in MODEL_COST_PER_1K_TOKENS:
        return dict(total_cost=0, total_tokens=input_tokens + output_tokens)

    total_cost = (
        MODEL_COST_PER_1K_TOKENS[input_cost_key] * input_tokens / 1000
        + MODEL_COST_PER_1K_TOKENS[output_cost_key] * output_tokens / 1000
    )
    return dict(total_cost=total_cost, total_tokens=input_tokens + output_tokens)
