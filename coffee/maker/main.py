from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain.callbacks import get_openai_callback
from pydantic import BaseModel
import os
from typing import Optional, List
from agent.tools.file_managment.read_file import ReadFileTool
from agent.agent_gpt import get_agent
from models.tiny import TinyAI, InputRequest
from models.baseline_tiny import BaselineTinyAI
import json


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
    file: str = None
    directory: str = None
    html: Optional[str] = None
    agent: Optional[str] = "tiny_ai"

auto_gpt = get_agent(os.environ.get("FRONTEND_DIR"))
tiny_ai = TinyAI()


@app.post("/prompt")
async def generate(prompt: Prompt):
    print(prompt.agent)
    prompt.directory = os.environ.get('FRONTEND_DIR')
    prompt.file = prompt.file or "app/page.tsx"
    file_content = ReadFileTool(root_dir=os.environ.get('FRONTEND_DIR')).run(prompt.file)

    def auto_gpt_stream():
        yield json.dumps({"status": "AutoGPT is Working..."})
        task =  f"User request: {prompt.text}\n" \
                f"Currently user selected this element: {prompt.html}.\n" \
                f"Currently user is looking at this file: {prompt.file}\n" \
                f"The content of the file is:\n" \
                f"{file_content}"
        with get_openai_callback() as cb:
            for status in auto_gpt.run([task]):
                yield json.dumps({"status": status.get("thoughts", {}).get("plan", "Working...")})
            print(cb)
            yield json.dumps({"status": f'Done. ${round(cb.total_cost, 2)}'})

    def tiny_ai_stream():
        yield json.dumps({"status": "TinyAI is Working..."})
        input = InputRequest(user_query=prompt.text, sourcefile = prompt.directory+prompt.file, selected_element=prompt.html, file_content=file_content)
        for status in tiny_ai.write_code(input):
            yield json.dumps({"status": status})

    stream = dict(auto_gpt=auto_gpt_stream, tiny_ai=tiny_ai_stream)[prompt.agent]
    return StreamingResponse(stream(), media_type="text/event-stream")


class Error(BaseModel):
    message: str

@app.post("/errors")
async def handle_errors(errors:List[Error]):
    error_messages = '\n'.join([e.message for e in errors])
    task =  f"Browser logged errors: {error_messages}\n. Fix it."
    print(task)
    def stream():
          with get_openai_callback() as cb:
            for status in auto_gpt.run([task]):
                yield json.dumps({"status": status.get("thoughts", {}).get("plan", "Working...")})
            print(cb)
            yield json.dumps({"status": f'Done. ${round(cb.total_cost, 2)}'})

    return StreamingResponse(stream(), media_type="text/event-stream")
