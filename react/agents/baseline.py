import os
from openai import OpenAI
import jinja2
import re
from agents.approximate_costs import approximate_costs

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


    def modify_file(self, **args) -> None:
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
        cost = approximate_costs(gpt_args, full_response)
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
