from fastapi import FastAPI
from pydantic import BaseModel
import os

from models.inline import InlineAI
from models.baseline import BaselineAI
from models.inline_line_number import InlineLineNumberAI
from models.inline_multi_steps import InlineMultiStepsAI
from models.base import InputRequest
from utils import prompt_constructor, llm_write_file, build_directory_structure
from config import HIERARCHY, GUIDELINES, MODIFY_FILE, WRITE_CODE, SINGLEFILE

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


class Globals:
    def __init__(self, frontend_dir, ai):
        self.frontend_dir = frontend_dir
        self.ai = ai


class Prompt(BaseModel):
    text: str


ai = InlineMultiStepsAI()


@app.post("/prompt")
async def generate(prompt: Prompt):
    # get env variable
    frontend_dir = os.environ.get("FRONTEND_DIR")
    print('frontend_dir', frontend_dir)

    file_content = ""
    with open(frontend_dir + "pages/contact-us.tsx", "r") as f:
        file_content = f.read()

    inputs = InputRequest(
        user_query=prompt.text,
        sourcefile=frontend_dir + "pages/contact-us.tsx",
        file_content=file_content,
        directory_structure=build_directory_structure(frontend_dir + "pages/"),
        guidelines=GUIDELINES
    )

    globals = Globals(frontend_dir, ai)

    llm_write_file(inputs,
                   target_path=frontend_dir + "pages/contact-us.tsx",
                   waiting_message=f"Writing code for pages/contact-us.tsx...",
                   success_message=None,
                   globals=globals)

    return {"message": "Response written to file: pages/contact-us.tsx"}
