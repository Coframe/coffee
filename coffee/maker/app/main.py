# import typer
# from ai import AI
# from utils import prompt_constructor, llm_write_file, build_directory_structure
# from config import HIERARCHY, GUIDELINES, MODIFY_FILE, WRITE_CODE, SINGLEFILE

# app = typer.Typer()

# class Globals:
#     def __init__(self, frontend_dir, ai):
#         self.frontend_dir = frontend_dir
#         self.ai = ai
        

# @app.command()
# def main(prompt: str):

#     frontend_dir = "../../../frontend/"
#     ai = AI(
#         model="gpt-4-32k",
#         temperature=0,
#     )

#     globals = Globals(frontend_dir, ai)

#     write_code_template = prompt_constructor(HIERARCHY, GUIDELINES, MODIFY_FILE, WRITE_CODE, SINGLEFILE)
#     file_content = ""
#     with open(frontend_dir+"app/page.tsx", "r") as f:
#         file_content = f.read()
    
#     prompt = write_code_template.format(prompt=prompt,
#                                         sourcefile=frontend_dir+"app/page.tsx",
#                                         file_content=file_content,
#                                         directory_structure=build_directory_structure(frontend_dir+"app/"),
#                                         guidelines=GUIDELINES)

#     llm_write_file(prompt,
#                     target_path=frontend_dir+"app/page.tsx",
#                     waiting_message=f"Writing code for app/page.tsx...",
#                     success_message=None,
#                     globals=globals)

# if __name__ == "__main__":
#     app()


from fastapi import FastAPI
from pydantic import BaseModel
from ai import AI
from utils import prompt_constructor, llm_write_file, build_directory_structure, debug_file
from config import HIERARCHY, GUIDELINES, MODIFY_FILE, WRITE_CODE, SINGLEFILE
import subprocess

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
async def generate(user_prompt: Prompt):
    frontend_dir = "../../../frontend/"
    ai = AI(
        model="gpt-4-32k",
        temperature=0,
    )

    globals = Globals(frontend_dir, ai)

    write_code_template = prompt_constructor(HIERARCHY, GUIDELINES, MODIFY_FILE, WRITE_CODE, SINGLEFILE)
    file_content = ""
    with open(frontend_dir+"app/page.tsx", "r") as f:
        file_content = f.read()
    
    prompt = write_code_template.format(prompt=user_prompt.text,
                                        sourcefile=frontend_dir+"app/page.tsx",
                                        file_content=file_content,
                                        directory_structure=build_directory_structure(frontend_dir+"app/"),
                                        guidelines=GUIDELINES)
    
    llm_write_file(prompt,
                    target_path=frontend_dir+"app/page.tsx",
                    waiting_message=f"Writing code for app/page.tsx...",
                    success_message=None,
                    globals=globals)
    
    debug_result = debug_file(globals)
    
    if debug_result == "success":
        # Commit and push the changes to GitHub
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', user_prompt.text], check=True)
        subprocess.run(['git', 'push'], check=True)
        print("Changes pushed to GitHub")
        return {"message": "Response written to file: app/page.tsx"}
    
    else:
        print("Build failed, changes not pushed to Git")
        return {"message": "Build failed, changes not pushed to Git", "error": debug_result}