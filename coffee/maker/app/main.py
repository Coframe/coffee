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
# from pyparsing import Optional
from ai import AI
from utils import prompt_constructor, llm_write_file, build_directory_structure, debug_file
from config import HIERARCHY, GUIDELINES, MODIFY_FILE, WRITE_CODE, SINGLEFILE
import subprocess
import shlex

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
    # html: Optional[str] = None

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
    
    debug_result = debug_file(frontend_dir)
    
    if debug_result == "success":
        # Commit and push the changes to GitHub
        commit_message = shlex.quote(user_prompt.text)[:47] + "..."
        print("Commit message:", commit_message)
        try: 
            subprocess.run(['git', 'add', '.'], check=True)
            print("Changes added to Git")
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)
            # subprocess.run(['git', 'push'], check=True)
            return {"message": "Response written to file: app/page.tsx"}
        except Exception as e:
            print("Error pushing changes to GitHub:", e)
            return {"message": "Response written to file: app/page.tsx", "error": "Error pushing changes to GitHub"}
    
    else:
        # TODO debug and try again
        return {"message": "Build failed, changes not pushed to Git", "error": debug_result}