import json
import os
from openai import OpenAI
from models.base import BaseAI, InputRequest, Response
from functools import lru_cache
import jinja2

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class TinyAI(BaseAI):
    """
    Designed with the idea to be simple, stupid and thus fast.
    """

    def prompt(self, **kwargs):
        template = jinja2.Template("""
            You are an expert in frontend development.
            Your task is to: {{user_query}}
            Selected element: {{selected_element}}
            {"original_file":[
            {% for line in file_content.split("\n") %}
            "{{line}}",
            {% endfor %}
            ]}

            Output json should have one or multiple replace statements.

            {"changes":[{
            "before": "previous line that should be kept as is",
            "new": ["new lines of code"],
            "after":"next line that will be kept as is"
            }, {}]}
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
            response_format={"type": "json_object"},
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
        response = json.loads(full_response)

        for changes in response["changes"]:
            first_line = changes["before"]
            last_line = changes["after"]
            start_index = inputs.file_content.find(first_line)+len(first_line)
            if(start_index == -1):
                print("WARNING: Cannot find", first_line)
                yield "WARNING: Cannot find "+first_line
                continue
            end_index = start_index+inputs.file_content[start_index:].find(last_line)
            if(end_index == -1):
                print("WARNING: Cannot find", last_line)
                yield "WARNING: Cannot find "+last_line
                continue
            print("Replacing", start_index, end_index)
            inputs.file_content = inputs.file_content[:start_index]+"\n".join(changes["new"])+inputs.file_content[end_index:]

        # save new file
        with open(inputs.sourcefile, "w") as f:
            f.write(inputs.file_content)
        print('-------------------')
        return Response(file_name=inputs.sourcefile, file_content=inputs.file_content)
