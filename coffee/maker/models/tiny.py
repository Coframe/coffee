import json
import os
from openai import OpenAI
from models.base import BaseAI, InputRequest, Response
from functools import lru_cache
import jinja2
import ijson
import difflib
import re

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
            "original_line": "first line in snippet that should be deleted or replaced",
            "new_lines": ["new lines of code"],
            "next_line":"next line that will be kept as is"
            }, {}]}
        """, trim_blocks=True, lstrip_blocks=True, autoescape=False)
        return template.render(**kwargs)


    def write_code(self, inputs: InputRequest) -> Response:
        print('-------------------', inputs.source_file, '-------------------')

        prompt = self.prompt(**inputs.dict())
        print("\n".join(prompt.split("\n")[0:7]))
        self.conversation_history = [{"role": "user", "content": prompt}]


        response_stream = client.chat.completions.create(
            model="gpt-3.5-turbo-1106", #"gpt-4-1106-preview",
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
            print(delta, end="", flush=True)
            full_response+=delta
            new_line+=delta
            if("\n" in delta):
                yield new_line
                new_line = ""
            changes = self.parse_partial_response(full_response)
            if(len(changes) > changes_length):
                changes_length = len(changes)
                for message in self.apply_changes(inputs.source_file, inputs.file_content, changes):
                    yield message

        return Response(file_name=inputs.source_file, file_content=inputs.file_content)

    def apply_changes(self, source_file, original_content, changes):
        print('applying changes')
        new_content = original_content.split("\n")

        for change in changes:
            first_line = change["original_line"]
            last_line = change["next_line"]
            start_index = self.find_line_index(new_content,first_line)
            if(start_index == -1):
                print("WARNING: Cannot find first line", first_line)
                yield "WARNING: Cannot find first line"+first_line
                continue
            end_index = self.find_line_index(new_content[start_index:], last_line)
            if(end_index == -1):
                print("WARNING: Cannot find last line", last_line)
                yield "WARNING: Cannot find last line"+last_line
                continue

            end_index += start_index

            # start_line = new_content[start_index]
            # indentation = re.match(r"^\s*", start_line).group(0)
            new_lines = change["new_lines"]

            print("Replacing", start_index, end_index)
            print("<<<<<< Original")
            print('\n'.join(new_content[start_index:end_index]))
            print("======")
            print('\n'.join(new_lines))
            print(">>>>>> New")

            new_content = new_content[:start_index]+new_lines+new_content[end_index:]

            with open(source_file, "w") as f:
                f.write("\n".join(new_content))
                yield "Saved to "+source_file

    def parse_partial_response(self, json_stream):
        # Initialize a parser for the JSON stream
        parser = ijson.parse(json_stream)
        # Initialize variables to hold the parsed data
        changes = []
        # Process the JSON as it is being parsed
        try:
            current_change = {}
            for prefix, event, value in parser:
                if prefix.endswith('.original_line') and event == 'string':
                    current_change['original_line'] = value
                    if 'new_lines' not in current_change:
                        current_change['new_lines'] = []
                elif prefix.endswith('.new_lines.item') and event == 'string':
                    current_change['new_lines'].append(value)
                elif prefix.endswith('.next_line') and event == 'string':
                    current_change['next_line'] = value
                    # Once a complete change is parsed, add it to the list and reset for the next change
                    changes.append(current_change)
                    current_change = {}

        except ijson.common.IncompleteJSONError:
            pass  # Handle incomplete JSON, perhaps logging a warning

        return changes

    def find_line_index(self, lines, target, threshold=0.99):
        for index, line in enumerate(lines):
            if target in line:
                print("Found exact line:", target, line)
                return index

            similarity = difflib.SequenceMatcher(None, target.strip(), line.strip()).ratio()
            if similarity >= threshold:
                print("Found similar line:", similarity, target, line)
                return index  # Return the index of the first similar enough line

        return -1  # No line was similar enough

