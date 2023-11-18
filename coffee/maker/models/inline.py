import json
import os

from openai import OpenAI

from models.base import BaseAI, InputRequest, Response

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

system = """Your are an expert in frontend development. Your task is to change the website INLINE based on users query.
You will be given a json input with 2 fields:
- website_code: in .tsx format
- user_query: user request

Your task is to response with inline edit:
- updates: List of updates, where is update is:
  - original_code: copy paste the code you want to edit
  - updated_code: edited code, so that our backend API can swap it.

Make sure that if our backend change the code one by one, it will not change any other code. So consider that original_code and updated_code pairs must be unique in the codebase.
Ensure conciseness, maintainable and readable of production-ready code:
- DRY
- Single responsibility principle
- Self-evident naming
- Minimum side effects
- No deep nesting
- No magic numbers
- No long files/functions
- No long lines
- No unnecessary comments/code
- More types
- Very concise and easy to read code
"""


class InlineAI(BaseAI):
    conversation_history: list = [
        {"role": "system", "content": system}
    ]

    def write_code(self, inputs: InputRequest) -> Response:
        openai_inputs = {
            "website_code": inputs.file_content,
            "user_query": inputs.user_query
        }

        self.conversation_history.append(
            {"role": "user", "content": str(openai_inputs)}
        )
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            response_format={"type": "json_object"},
            messages=self.conversation_history,
        )
        self.conversation_history.append(
            {"role": "assistant", "content": str(response.choices[0].message.content)}
        )
        updates = json.loads(response.choices[0].message.content)["updates"]
        new_code = inputs.file_content
        for update in updates:
            new_code = new_code.replace(update["original_code"], update["updated_code"])
        return Response(
            file_name=inputs.sourcefile,
            file_content=new_code
        )
