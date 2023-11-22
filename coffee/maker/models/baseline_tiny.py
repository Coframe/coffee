import json
import os
from openai import OpenAI
from models.base import BaseAI, InputRequest, Response
from functools import lru_cache
import jinja2

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class BaselineTinyAI(BaseAI):
    """
    Designed with the idea to be simple & stupid.
    It rewrites the whole file.
    """

    def prompt(self, **kwargs):
        template = jinja2.Template("""
            You are an expert in frontend development.
            Your task is to: {{user_query}}
            Selected element: {{selected_element}}
            File:
            {% for line in file_content.split("\n") %}
            {{ line }}
            {% endfor %}
            Do not use any libraries.

            Modify and output whole file and nothing else (no markdown). It will be saved as is to the file.
        """, trim_blocks=True, lstrip_blocks=True, autoescape=False)
        return template.render(**kwargs)


    def write_code(self, inputs: InputRequest) -> Response:
        print('-------------------')


        prompt = self.prompt(**inputs.dict())
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
        print(full_response)
        full_response.replace(r"\'\'\'.+", "\n")

        # save new file
        with open(inputs.sourcefile, "w") as f:
            f.write(full_response)
        print('-------------------')
        return Response(file_name=inputs.sourcefile, file_content=inputs.file_content)
