import os
from openai import OpenAI
import jinja2
import json
import tiktoken

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class ComponentPathAgent():
    """
    Use LLM to deduce the path to the component file.
    """
    conversation_history: list = []
    cache = {}

    def prompt(self, **kwargs):
        template = jinja2.Template("""
            Which file is used to render this component?
            `{{component}}`

            This is import statement from {{parent_file_path}}:
            ```
            {{import_statement}}
            ```

            This is directory structure:
            {{directory_structure}}

            Output path to the file, you think is responsing for {{component}} and nothing else.
            Output format is JSON:
            {"file_path": "path/to/file"}
        """, trim_blocks=True, lstrip_blocks=True, autoescape=False)
        return template.render(**kwargs)


    def run(self, **args) -> None:
        yield('------PROMPT-------')
        prompt = self.prompt(**args)
        yield(prompt)
        yield('------STREAM---------')

        self.conversation_history = [
            {"role": "user", "content": prompt}
        ]

        gpt_args = dict(
            model="gpt-4-1106-preview",
            messages=self.conversation_history,
            response_format={"type": "json_object"},
            stream=True,
        )

        response_stream = self._cached_generator(
            fx = client.chat.completions.create,
            fx_args = gpt_args,
            cache_key = hash(args['component'])+len(self.conversation_history)
        )

        full_response = ""
        chunked_delta = ""
        for chunk in response_stream:
            delta = chunk.choices[0].delta.content
            if(delta == None):
                continue
            full_response+=delta
            chunked_delta+=delta
            if("\n" in delta):
                yield chunked_delta
                chunked_delta = ""
        yield chunked_delta
        yield('------DONE---------')
        cost = self._approx_costs(gpt_args, full_response)
        yield(f"Total cost: ${round(cost['total_cost'], 2)}")
        json_response = json.loads(full_response)
        yield({"file_path": json_response['file_path']})
        return

    def _cached_generator(self, fx=None, fx_args=None, cache_key=None):
        print("Cache key:", cache_key)
        if(cache_key in self.cache):
            print("Using cache for", cache_key)
            for chunk in self.cache[cache_key]:
                yield chunk
        else:
            self.cache[cache_key] = []
            for chunk in fx(**fx_args):
                yield chunk
                self.cache[cache_key].append(chunk)

    def _approx_costs(self, fx_args, full_response):
        encoding = tiktoken.encoding_for_model(fx_args['model'])
        input_tokens = 0
        for message in fx_args['messages']:
            input_tokens += 3 + len(encoding.encode(message['content']))
        output_tokens = 3 + len(encoding.encode(full_response))
        total_cost = MODEL_COST_PER_1K_TOKENS[fx_args['model']] * input_tokens / 1000 + MODEL_COST_PER_1K_TOKENS[fx_args['model'] + '-completion'] * output_tokens / 1000
        return dict(total_cost=total_cost, total_tokens=input_tokens + output_tokens)

# TODO: use langchain variable, if we will start using langchain for future agents
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
}
