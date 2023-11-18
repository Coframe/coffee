import os

from openai import OpenAI
from pydantic import BaseModel

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


class InputRequest(BaseModel):
    user_query: str
    sourcefile: str
    file_content: str
    directory_structure: str
    guidelines: str


class Response(BaseModel):
    file_name: str
    file_content: str


class BaseAI(BaseModel):
    conversation_history: list = []

    def write_code(self, inputs: InputRequest) -> Response:
        updated_file_content = inputs.file_content + "TEST"
        return Response(file_content=updated_file_content, file_name=inputs.sourcefile)
