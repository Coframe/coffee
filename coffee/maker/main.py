from fastapi import FastAPI
from pydantic import BaseModel
import os
from ai import AI
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

@app.post("/prompt")
async def generate(prompt: Prompt):
    # get env variable
    frontend_dir = os.environ.get("FRONTEND_DIR")
    print('frontend_dir', frontend_dir)

    ai = AI(
        model="gpt-4-32k",
        temperature=0,
    )

    globals = Globals(frontend_dir, ai)

    write_code_template = prompt_constructor(HIERARCHY, GUIDELINES, MODIFY_FILE, WRITE_CODE, SINGLEFILE)
    file_content = ""
    with open(frontend_dir+"app/page.tsx", "r") as f:
        file_content = f.read()

    prompt = write_code_template.format(prompt=prompt.text,
                                        sourcefile=frontend_dir+"app/page.tsx",
                                        file_content=file_content,
                                        directory_structure=build_directory_structure(frontend_dir+"app/"),
                                        guidelines=GUIDELINES)

    llm_write_file(prompt,
                    target_path=frontend_dir+"app/page.tsx",
                    waiting_message=f"Writing code for app/page.tsx...",
                    success_message=None,
                    globals=globals)

    return {"message": "Response written to file: app/page.tsx"}
