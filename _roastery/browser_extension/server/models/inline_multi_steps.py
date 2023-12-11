import json
import os

from openai import OpenAI

from models.base import BaseAI, InputRequest, Response

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

system = """Your are an expert in frontend development. Your task is to change the website INLINE based on users query. You will iterate over multiple steps to solve the task.

# Inputs

You will be given a json input with 2 fields:
- website_code: in .tsx format
- user_query: user request


# Outputs

Your task is to response with inline edit:
- notes: str - optional field for you to think step by step, plan how you gonna solve the given task, validate previous steps, check on errors in the final solution.
- code_to_be_replaced: str - copy paste the code you want to edit.
- code_to_replace_with: str - edited code, so that our backend API can swap it.
- require_additional_steps: bool -  `true` if it requires one more iteration to complete the query, else `false`.

All fields in response can not be empty strings!

Make sure that if our backend change the code one by one, it will not change any other code. So consider that original_code and updated_code pairs must be unique in the codebase.


# Pipeline

Make sure your final step is validation and confirming your solution. Your final response should be with empty code fields!
```
{"notes": "Let's evaluate and validate our solution step by step:\n1. ...", "code_to_be_replaced": "", "code_to_replace_with": "", "require_additional_steps": True/False (depends on the `notes`)}
```
To make additional step without changes keep both `code_to_be_replaced` and `code_to_replace_with` empty strings, and `require_additional_steps` set to True


# Code quality

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


class InlineMultiStepsAI(BaseAI):
    conversation_history: list = [
        {"role": "system", "content": system}
    ]

    def write_code(self, inputs: InputRequest) -> Response:
        print("User query:", inputs.user_query)
        require_additional_steps = True
        num_iterations = 0
        while require_additional_steps is True:
            response = self._iteration(inputs, num_iterations)
            print(f"ITERATION {num_iterations}")
            print("Note:", response["notes"])
            print(response)
            inputs.file_content = inputs.file_content.replace(
                response["code_to_be_replaced"],
                response["code_to_replace_with"]
            )
            require_additional_steps = bool(response["require_additional_steps"])
            num_iterations += 1
        return Response(
            file_name=inputs.source_file,
            file_content=inputs.file_content
        )

    def _iteration(self, inputs, num_iterations):
        openai_inputs = {"website_code": inputs.file_content}
        if num_iterations == 0:
            openai_inputs["user_query"] = inputs.user_query

        self.conversation_history.append(
            {"role": "user", "content": str(openai_inputs)}
        )
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            response_format={"type": "json_object"},
            messages=self.conversation_history,
            temperature=0.7
        )
        self.conversation_history.append(
            {"role": "assistant", "content": str(response.choices[0].message.content)}
        )
        response = json.loads(response.choices[0].message.content)
        return response
