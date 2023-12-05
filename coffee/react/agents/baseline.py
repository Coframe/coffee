import os
from openai import OpenAI
import jinja2
import re
import tiktoken

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class BaselineAgent():
    """
    Designed with the idea to be simple & stupid.
    It rewrites the whole file from scratch.
    No history. No JSON. No Reasoning.
    """
    conversation_history: list = []
    cache = {}

    def prompt(self, **kwargs):
        template = jinja2.Template("""
            You are an expert in the frontend development.
            Your task is to create a react component file according to the user query:
            {{user_query}}

            This is current content of component file:
            ```
            {% for line in file_content.split("\n") %}
            {{ line }}
            {% endfor %}
            ```

            This is parent component file, it uses <Coffee> component to render component that you should create.
            ```
            {% for line in parent_file_content.split("\n") %}
            {{ line }}
            {% endfor %}
            ```

            Output whole new file for {{source_file}} within ``` and nothing else. It will be saved as is to the component file {{source_file}} and should work out of the box.
            Do not add any new libraries. Put everything into single file: styles, types, etc.
        """, trim_blocks=True, lstrip_blocks=True, autoescape=False)
        return template.render(**kwargs)


    def write_code(self, **args) -> None:
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
            response_format={"type": "text"},
            stream=True,
        )

        response_stream = self._cached_generator(
            fx = client.chat.completions.create,
            fx_args = gpt_args,
            cache_key = hash(args['user_query'])
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
        # find and extract content within ``` using regex
        pattern = r'```.*?\n(.*?)```'
        matches = re.findall(pattern, full_response, re.DOTALL)
        if(len(matches) == 0):
            yield("No code found in response")
            return

        new_content = matches[0]

        if(new_content == args['file_content']):
            yield('No changes')
            return

        yield('------FILE-------')
        yield(new_content)

        # save new file
        with open(args['source_file'], "w") as f:
            f.write(new_content)

        yield('-------------------')
        cost = self._approx_costs(gpt_args, full_response)
        yield(f"Cost: ${round(cost['total_cost'], 4)}, tokens: {cost['total_tokens']}")

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

# From langchain
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
