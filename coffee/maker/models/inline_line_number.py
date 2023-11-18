import json
import os
import copy

from openai import OpenAI
from pydantic import BaseModel

from models.base import BaseAI, InputRequest, Response
from utils import prompt_constructor, parse_code_string
from config import HIERARCHY, GUIDELINES, MODIFY_FILE, WRITE_CODE, SINGLEFILE

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

system = """Your are an expert in frontend development. Your task is to change the website INLINE based on users query.
You will be given a json input with 2 fields:
- website_code: in .tsx format with added line numbers
- user_query: user request

Your task is to response with inline edit:
- start_line: int - Insert new lines starting with this index (including).
- end_line: int - Remove all lines after insert and before this index (including).
- updated_code: new content to replace with original on,  so that our backend API can swap it. Do not include line numbers here.
- require_additional_steps: true if it requires one more iteration to complete the query, else false.

Make sure that if our backend change the code one by one, it will not change any other code. Consider that you replace original code with updated_code (do not forget deleted code back!) by deleting lines with this code:
```python
file_lines = file_content.split("\n")
updated_lines = file_lines[:start_line] + response["updated_code"].split("\n") + file_lines[end_line + 1:]
file_content = "\n".join(updated_lines)
```

# Example with importance of "\n     </ul>" in the end of `updated_code`
website_code:
```
0: <nav className="bg-opacity-75 p-4">
1:     <ul className="flex justify-between items-center">
2:      <li><a href="#" className="text-blue-600 hover:text-white bg-blue-300 px-3 py-2 rounded-md text-sm font-medium">Home</a></li>
3:      <li><a href="#about" className="text-blue-600 hover:text-white bg-blue-300 px-3 py-2 rounded-md text-sm font-medium">About</a></li>
4:      <li><a href="#contact" className="text-blue-600 hover:text-white bg-blue-300 px-3 py-2 rounded-md text-sm font-medium">Contact</a></li>
5:     </ul>
6: </nav>
```
your response:
```
{
  "start_line": 5,
  "end_line": 5,
  "updated_code": "      <li><a href="#join" className="text-blue-600 hover:text-white bg-blue-300 px-3 py-2 rounded-md text-sm font-medium">Join</a></li>\n     </ul>"
}
```
Updated website after your response:
```
0: <nav className="bg-opacity-75 p-4">
1:     <ul className="flex justify-between items-center">
2:      <li><a href="#" className="text-blue-600 hover:text-white bg-blue-300 px-3 py-2 rounded-md text-sm font-medium">Home</a></li>
3:      <li><a href="#about" className="text-blue-600 hover:text-white bg-blue-300 px-3 py-2 rounded-md text-sm font-medium">About</a></li>
4:      <li><a href="#contact" className="text-blue-600 hover:text-white bg-blue-300 px-3 py-2 rounded-md text-sm font-medium">Contact</a></li>
5:      <li><a href="#join" className="text-blue-600 hover:text-white bg-blue-300 px-3 py-2 rounded-md text-sm font-medium">Join</a></li>
6:     </ul>
7: </nav>
```

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


class InlineLineNumberAI(BaseAI):
    conversation_history: list = [
        {"role": "system", "content": system}
    ]

    def write_code(self, inputs: InputRequest) -> Response:
        file_content = copy.deepcopy(inputs.file_content)
        require_additional_steps = True
        num_iterations = 0
        while require_additional_steps:
            response = self._interation(file_content, inputs.user_query, num_iterations)
            file_content = self._update_file_content(file_content, response)
            require_additional_steps = bool(response["require_additional_steps"])
            num_iterations += 1

        return Response(
            file_name=inputs.sourcefile,
            file_content=file_content
        )

    def _append_line_numbers(self, file_content):
        lines = file_content.split("\n")
        lines_with_numbers = [f"{i}: {line}" for i, line in enumerate(lines)]
        return "\n".join(lines_with_numbers)

    def _interation(self, file_content, user_query, num_iterations):
        website_code_with_numbers = self._append_line_numbers(file_content)
        openai_inputs = {
            "website_code": website_code_with_numbers,
        }
        if num_iterations == 0:
            openai_inputs["user_query"] = user_query

        self.conversation_history.append({"role": "user", "content": str(openai_inputs)})
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            response_format={"type": "json_object"},
            messages=self.conversation_history,
            temperature=0.3
        )
        self.conversation_history.append(
            {"role": "assistant", "content": str(response.choices[0].message.content)}
        )
        update = json.loads(response.choices[0].message.content)
        return update

    def _update_file_content(self, file_content, response):
        file_lines = file_content.split("\n")
        start_line = int(response["start_line"])
        end_line = int(response["end_line"])
        updated_lines = file_lines[:start_line] + response["updated_code"].split("\n") + file_lines[end_line + 1:]
        file_content = "\n".join(updated_lines)
        return file_content
