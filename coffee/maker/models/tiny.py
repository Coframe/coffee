import json
import os
from openai import OpenAI
from models.base import BaseAI, InputRequest, Response
from functools import lru_cache
import jinja2
import ijson

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class TinyAI(BaseAI):
    """
    Designed with the idea to be simple, stupid and thus fast.
    """

    def prompt(self, **kwargs):
        template = jinja2.Template("""
            You are an expert in frontend development.
            User selected element: {{selected_element}}
            User asked to: {{user_query}}
            {"original_file":[
            {% for line in file_content.split("\n") %}
            "{{line}}",
            {% endfor %}
            ]}

            Output json should have one or multiple replace statements.

            {"changes":[{
            "original": "first line that should be replaced",
            "new": ["new lines of code"],
            "after":"next line that will be kept as is"
            }, {}]}
        """, trim_blocks=True, lstrip_blocks=True, autoescape=False)
        return template.render(**kwargs)


    def write_code(self, inputs: InputRequest) -> Response:
        print('-------------------')

        prompt = self.prompt(**inputs.dict())
        print(prompt)
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
        new_line = ""
        changes_length = 0
        changes = []
        for chunk in response_stream:
            delta = chunk.choices[0].delta.content
            if(delta == None):
                continue
            # print(delta, end="", flush=True)
            full_response+=delta
            new_line+=delta
            if("\n" in delta):
                yield new_line
                new_line = ""
            changes = self.parse_partial_response(full_response)
            if(len(changes) > changes_length):
                changes_length = len(changes)
                for message in self.apply_changes(inputs.sourcefile, inputs.file_content, changes):
                    yield message

        return Response(file_name=inputs.sourcefile, file_content=inputs.file_content)

    def apply_changes(self, sourcefile, original_content, changes):
        print('applying changes')
        new_content = original_content

        for change in changes:
            first_line = change["original"]
            last_line = change["after"]
            start_index = new_content.find(first_line)
            if(start_index == -1):
                print("WARNING: Cannot find", first_line)
                yield "WARNING: Cannot find "+first_line
                continue
            end_index = start_index+new_content[start_index:].find(last_line)
            if(end_index == -1):
                print("WARNING: Cannot find", last_line)
                yield "WARNING: Cannot find "+last_line
                continue
            print("Replacing", start_index, end_index)
            yield "Replacing "+str(start_index)+":"+str(end_index)
            new_content = new_content[:start_index]+"\n".join(change["new"])+new_content[end_index:]

            with open(sourcefile, "w") as f:
                f.write(new_content)
                yield "Saved to "+sourcefile

    def parse_partial_response(self, json_stream):
        # Initialize a parser for the JSON stream
        parser = ijson.parse(json_stream)
        # Initialize variables to hold the parsed data
        changes = []
        # Process the JSON as it is being parsed
        try:
            current_change = {}
            for prefix, event, value in parser:
                if prefix.endswith('.original') and event == 'string':
                    current_change['original'] = value
                elif prefix.endswith('.new.item') and event == 'string':
                    if 'new' not in current_change:
                        current_change['new'] = []
                    current_change['new'].append(value)
                elif prefix.endswith('.after') and event == 'string':
                    current_change['after'] = value
                    # Once a complete change is parsed, add it to the list and reset for the next change
                    changes.append(current_change)
                    current_change = {}

        except ijson.common.IncompleteJSONError:
            pass  # Handle incomplete JSON, perhaps logging a warning

        return changes

