import os

from openai import OpenAI

from models.base import BaseAI, InputRequest, Response
from utils import prompt_constructor, parse_code_string
from config import HIERARCHY, GUIDELINES, MODIFY_FILE, WRITE_CODE, SINGLEFILE

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


class BaselineAI(BaseAI):

    def write_code(self, inputs: InputRequest) -> Response:
        prompt = self._construct_prompt(inputs)
        message = [{"role": "user", "content": prompt}]
        response = client.chat.completions.create(
            messages=message,
            stream=False,
            model="gpt-4-1106-preview",
            temperature=1.0
        )

        content = response.choices[0].message.content

        code_triples = parse_code_string(content)
        file_name, language, file_content = code_triples[0]
        return Response(
            file_name=file_name,
            file_content=file_content
        )

    def _construct_prompt(self, inputs: InputRequest):
        write_code_template = prompt_constructor(HIERARCHY, GUIDELINES, MODIFY_FILE, WRITE_CODE, SINGLEFILE)

        prompt = write_code_template.format(
            prompt=inputs.user_query,
            sourcefile=inputs.sourcefile,
            file_content=inputs.file_content,
            directory_structure=inputs.directory_structure,
            guidelines=GUIDELINES
        )
        return prompt
