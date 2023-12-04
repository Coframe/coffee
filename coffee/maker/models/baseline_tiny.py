import json
import os
from openai import OpenAI
from models.base import BaseAI, InputRequest, Response
from functools import lru_cache
import jinja2
import re

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class BaselineTinyAI(BaseAI):
    """
    Designed with the idea to be simple & stupid.
    It rewrites the whole file.
    """

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


    def write_code(self, **args) -> Response:
        print('-------------------')


        prompt = self.prompt(**args)
        print(prompt)
        print('-------------------')
        self.conversation_history.append(
            {"role": "user", "content": prompt}
        )

        response_stream = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=self.conversation_history,
            response_format={"type": "text"},
            stream=True,
        )

        full_response = ""
        chunked_delta = ""
        for chunk in response_stream:
            delta = chunk.choices[0].delta.content
            if(delta == None):
                continue
            print(delta, end="", flush=True)
            full_response+=delta
            chunked_delta+=delta
            if("\n" in delta):
                yield chunked_delta
                chunked_delta = ""

        # find and extract content within ``` using regex
        pattern = r'```.*?\n(.*?)```'
        matches = re.findall(pattern, full_response, re.DOTALL)
        if(len(matches) == 0):
            raise Exception("No code found in response")
        new_content = matches[0]

        print('-------------------')
        print(new_content)
        # save new file
        with open(args['source_file'], "w") as f:
            f.write(new_content)

        print('-------------------')
        return Response(file_name=args['source_file'], file_content=new_content)
