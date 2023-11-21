from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain.callbacks import get_openai_callback
from pydantic import BaseModel
import os
from typing import Optional, List
from agent.tools.file_managment.read_file import ReadFileTool
from agent.agent_gpt import get_agent
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
    html: Optional[str] = None


agent = get_agent(os.environ.get("FRONTEND_DIR"))

@app.post("/prompt")
async def generate(prompt: Prompt):
    prompt.file = prompt.file or "app/page.tsx"
    task =  f"User request: {prompt.text}\n" \
            f"Currently user selected this element: {prompt.html}.\n" \
            f"Currently user is looking at this file: {prompt.file}\n" \
            f"The content of the file is:\n" \
            f"{ReadFileTool(root_dir=os.environ.get('FRONTEND_DIR')).run(prompt.file)}"

    def stream():
          with get_openai_callback() as cb:
            for status in agent.run([task]):
                yield json.dumps({"status": status.get("thoughts", {}).get("plan", "Working...")})
            print(cb)
            yield json.dumps({"status": f'Done. ${round(cb.total_cost, 2)}'})

    return StreamingResponse(stream(), media_type="text/event-stream")

    # return {"message": "Done"}

class Error(BaseModel):
    message: str

@app.post("/errors")
async def handle_errors(errors:List[Error]):
    error_messages = '\n'.join([e.message for e in errors])
    task =  f"Browser logged errors: {error_messages}\n. Fix it."
    print(task)
    def stream():
          with get_openai_callback() as cb:
            for status in agent.run([task]):
                yield json.dumps({"status": status.get("thoughts", {}).get("plan", "Working...")})
            print(cb)
            yield json.dumps({"status": f'Done. ${round(cb.total_cost, 2)}'})

    return StreamingResponse(stream(), media_type="text/event-stream")
