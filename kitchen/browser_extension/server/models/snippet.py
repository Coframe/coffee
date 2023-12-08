import json
import os
from openai import OpenAI
from models.base import BaseAI, InputRequest, Response
from functools import lru_cache
import jinja2

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class SnippetAI(BaseAI):
    """
    Designed with the idea to split code into sections(snippets) and ask gpt to update only necessary sections.
    """

    def prompt(self, **kwargs):
        return jinja2.Template("""
            You are an expert in frontend development.

            User selected element: {{selected_element}}
            User asked to: {{user_query}}

            Original code:
            {{sections_json}}

            Select sections to update and output new implementation of such section with following JSON:

            { updated_sections: [
                { id: "X", lines: [
                    "old code for section X",
                    "",
                    "new line",
                    "",
                    "continuation of old code for section X",
                ]},
                { id: "Y", lines: [
                    "..."
                ]}
            ]}

            It's important to output whole section implementation, even parts that preserved, it would be swapped in the original file.
            It's important to keep indentation.
            It's important to break current section into smaller ones by adding empty lines.
        """, trim_blocks=True, lstrip_blocks=True, autoescape=False).render(**kwargs)

    # command can be insert(after:10), replace(lines:10-20), delete(lines:10-20)
    def split_into_sections(self, file_content):
        """ splits file into logical blocks by empty lines """
        sections = []
        current_section = []

        def sec_id(current_section):
            return str(current_section[0][0])
        for index, line in enumerate(file_content.split("\n")):
            must_split = len(current_section) > 10
            can_split = line.strip() == ""
            if(can_split or must_split):
                if(not can_split):
                    current_section.append((index, line))

                if(len(current_section) == 0):
                    continue

                sections.append(dict(id=sec_id(current_section), lines=current_section, end="\n" if can_split else ''))
                current_section = []
                must_split = False
            else:
                current_section.append((index, line))


        if(len(current_section) > 0):
            sections.append((sec_id(current_section), current_section))

        return sections

    def write_code(self, inputs: InputRequest) -> Response:
        print('-------------------', inputs.source_file, '-------------------')
        sections = self.split_into_sections(inputs.file_content)
        sections_json = {"sections": []}
        for section in sections:
            sections_json["sections"].append({"id": section["id"], "lines": [line for _, line in section["lines"]]})

        prompt = self.prompt(**inputs.dict(), sections=sections, sections_json=json.dumps(sections_json, indent=4))
        print("\n".join(prompt.split("\n")[0:40]+['...']))
        self.conversation_history = [{"role": "user", "content": prompt}]

        response_stream = client.chat.completions.create(
            model="gpt-4-1106-preview", #"gpt-3.5-turbo-1106",
            messages=self.conversation_history,
            response_format={"type": "json_object"},
            stream=True,
        )

        full_response = ""
        new_line = ""
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

        # save new file
        new_file_lines = []
        updated_sections = self.parse_response(full_response)

        for section in sections:
            lines = section["lines"]
            if section["id"] in updated_sections:
                new_lines = updated_sections[ section["id"]]
                print('<<<<<< Original',  section["id"])
                print("\n".join([line for _, line in lines]))
                print('======')
                print("\n".join([line for _, line in new_lines]))
                print('>>>>>> New')
                lines = new_lines

            new_file_lines += [line for _, line in lines]
            new_file_lines[-1] += section["end"]

        new_file_content = "\n".join(new_file_lines)

        with open(inputs.source_file, "w") as f:
            f.write(new_file_content)

        return Response(file_name=inputs.source_file, file_content=inputs.file_content)

    def parse_response(self, response):
        sections = json.loads(response)["updated_sections"]
        return {section["id"]: [(0,l) for l in section["lines"]] for section in sections}
