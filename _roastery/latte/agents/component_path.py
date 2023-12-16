import os
import jinja2
import json
from openai import OpenAI
from agents.approximate_costs import approximate_costs

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


class ComponentPathAgent:
    """
    Use LLM to deduce the path to the component file.
    """

    conversation_history: list = []
    cache = {}

    def prompt(self, **kwargs):
        template = jinja2.Template(
            """
            Your task is to determine which file is used to render the following component:
            `{{component}}`

            This is the import statement from {{parent_file_path}}:
            ```
            {{import_statement}}
            ```

            These are the files in the directory:
            {{files}}

            Output the path to the file that you think is responsible for {{component}}, JSON:
            {"file_path": "path/to/file.tsx"}
        """,
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=False,
        )
        return template.render(**kwargs)

    def run(self, **args) -> None:
        yield ("------PROMPT------")
        command = f"find {args['directory']} -type f \\( -name \"*.tsx\" -o -name \"*.jsx\" \\) -not -path \"*/node_modules/*\""
        files = os.popen(command).read()

        prompt = self.prompt(files=files, **args)
        yield (prompt)
        yield ("------STREAM------")

        self.conversation_history = [{"role": "user", "content": prompt}]

        gpt_args = dict(
            model="gpt-4-1106-preview",
            messages=self.conversation_history,
            response_format={"type": "json_object"},
            stream=True,
        )

        response_stream = self._cached_generator(
            fx=client.chat.completions.create,
            fx_args=gpt_args,
            cache_key=hash(args["component"]) + len(self.conversation_history),
        )

        full_response = ""
        chunked_delta = ""
        for chunk in response_stream:
            delta = chunk.choices[0].delta.content
            if delta is None:
                continue
            full_response += delta
            chunked_delta += delta
            if "\n" in delta:
                yield chunked_delta
                chunked_delta = ""
        yield chunked_delta
        yield ("------DONE------")
        cost = approximate_costs(gpt_args, full_response)
        yield (f"Total cost: ${round(cost['total_cost'], 2)}")
        json_response = json.loads(full_response)
        yield ({"file_path": json_response["file_path"]})
        return

    def _cached_generator(self, fx=None, fx_args=None, cache_key=None):
        print("Cache key:", cache_key)
        if cache_key in self.cache:
            print("Using cache for", cache_key)
            for chunk in self.cache[cache_key]:
                yield chunk
        else:
            self.cache[cache_key] = []
            for chunk in fx(**fx_args):
                yield chunk
                self.cache[cache_key].append(chunk)
