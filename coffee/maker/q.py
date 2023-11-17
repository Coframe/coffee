from functools import lru_cache
from typing import List, Dict, Any
from openai import OpenAI
import ijson
import typer
import os

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


class StreamFunction:
    # It's a function that can to be execute as LLM generates structured output
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def openai_schema(self) -> Dict[str, Any]:
        raise NotImplementedError("Schema method should be implemented in child classes")

    def call(self, partial_json=None, finished=True, **kwargs) -> Any:
        raise NotImplementedError("Execute method should be implemented in child classes")

class UpdateFile(StreamFunction):
    def __init__(self):
        super().__init__("update_file", "Update file content")
        self.lines = None

    def openai_schema(self):
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "insert_after_index": {"type": "number", "description": "Insert new lines after this index"},
                    "clear_before_index": {"type": "number", "description": "Remove all lines after insert and before this index"},
                    "new_lines": {"type": "array", "items": {"type": "string"}, "description": "New content to replace the original with. Make sure you escape json characters."}
                },
                "required": ["insert_after_index", "clear_before_index" "new_lines"]
            }
        }



    def call(self, partial_json=None, finished=True, filename=None):
        if(not filename or not partial_json):
            return None

        print('Updating filename:', filename)
        if(not self.lines):
            with open(filename, 'r') as f:
                self.lines = f.readlines()

        parsed_args = self.parse_json(partial_json)

        insert_after_index = parsed_args["insert_after_index"]
        clear_before_index = parsed_args["clear_before_index"]
        new_lines = parsed_args["new_lines"]

        new_lines = [line for item in new_lines for line in item.split('\n')]
        clear_before_index = clear_before_index or insert_after_index

        if not finished:
            print(new_lines)

        if finished:
            updated_lines = (
                self.lines[:insert_after_index-1] +
                [l.rstrip() + '\n' for l in new_lines] +  # Add new lines
                self.lines[clear_before_index:]
            )

            # Write the updated content back to the file
            with open(filename, 'w') as f:
                f.writelines(updated_lines)


    def parse_json(self, partial_json):
        parser = ijson.parse(partial_json)

        insert_after_index = None
        clear_before_index = None
        new_lines = []

        try:
            for prefix, event, value in parser:
                if (prefix, event) == ('insert_after_index', 'number'):
                    insert_after_index = value
                elif (prefix, event) == ('clear_before_index', 'number'):
                    clear_before_index = value
                elif prefix == 'new_lines.item':
                    new_lines.append(value)
        except ijson.common.IncompleteJSONError:
            pass

        return dict(insert_after_index=insert_after_index, clear_before_index=clear_before_index, new_lines=new_lines)


# Initialize message history
message_history = [{
    "role": "system",
    "content": """
        You are smart react code assistant, called Q.
        User will provide you with a prompt, and you will update file accordingly.
        Operate within 1 file. Do not import or export anything.
        Ensure conciseness, maintainabile and readabile of producted code:
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
}]

def llm_run(user_message, filename, function=UpdateFile()):
    global message_history

    if(not filename):
        return "Can't run Q, no file in the context."

    file_content = open(filename, 'r').read()
    content_with_line_numbers = "\n".join([f"{i+1}: {line}" for i, line in enumerate(file_content.splitlines())])
    if(len(content_with_line_numbers) > 30000):
        return "File too large to process. Please select a smaller file."

    message_history.append({"role": "user", "content": f"Current file is `{filename}`. Content is:\n```\n{content_with_line_numbers}\n```"})
    if(user_message):
        message_history.append({"role": "user", "content": user_message})

    # Remove earlier message from history to fit within smaller context
    char_count = sum(len(m["content"]) for m in message_history)
    while char_count > 30000:
        removed_message = message_history.pop(0)
        char_count -= len(removed_message["content"])


    # Functions available for GPT to call
    functions = [function.openai_schema()]
    function_call = {"name": function.name}

    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=message_history,
        stream=True,
        **({"functions": functions} if functions else {}),
        **({"function_call": function_call} if function_call else {})
    )

    text = ""
    function_name = ""
    function_args_json = ""

    print('Streaming response....')
    for event in response:
        try:
            if(not event.choices or event.choices[0].finish_reason == 'stop' or  not event.choices[0].delta):
                break

            message = event.choices[0].delta

            if(message.content):
                text += message.content
                print(message.content, end='')

            if(message.function_call):
                name = message.function_call.name
                args = message.function_call.arguments

                if(name):
                    function_name += name
                    print(f"Function `{function_name}` called")
                if(args):
                    function_args_json += args
                    if(function_name == function.name):
                        function.call(filename=filename, partial_json=function_args_json, finished=False)
        except Exception as e:
            print(event)
            print(e)

    if(function_args_json):
        function.call(filename=filename, partial_json=function_args_json, finished=True)

    if(text):
        message_history.append({"role": "assistant", "content": text})

    if(function_name):
        message_history.append({"role": "system", "content": f"Function `{function_name}` called with arguments:\n```\n{function_args_json}\n```\n"})

    print('function_args_json', function_args_json)
    return text+function_name
