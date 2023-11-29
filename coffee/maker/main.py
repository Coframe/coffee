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
import enum

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
    html: Optional[str] = None


class Session(BaseModel):
    file: str = None
    agent: str = None
    directory: str = os.environ.get("FRONTEND_DIR")

session = Session()
class Agent(enum.Enum):
    auto_gpt = "auto_gpt"
    tiny_ai = "tiny_ai"

auto_gpt = get_agent(session.directory)
tiny_ai = TinyAI()


@app.post("/prompt")
async def generate(prompt: Prompt):
    print(prompt.text)
    if not session.file:
        session.agent = Agent.auto_gpt
    else:
        session.agent = Agent.tiny_ai

    if session.file:
        file_content = ReadFileTool(root_dir=session.directory).run(session.file)

    def auto_gpt_stream():
        yield json.dumps({"status": "AutoGPT is Working..."})
        task =  f"User request: {prompt.text}\n" \
                f"Currently user selected this element: {prompt.html}.\n"
        if(session.file):
            task += f"Currently user is looking at this file: {session.file}\n" \
                f"The content of the file is:\n" \
                f"{file_content}"

        with get_openai_callback() as cb:
            for update in auto_gpt.run([task]):
                if(isinstance(update, str)):
                   update = {"message": update}
                if(update.get('file_path')):
                    print(update.get('file_path'))
                    session.file = update.get('file_path')
                yield json.dumps({"status": json.dumps(update)})
            print(cb)
            yield json.dumps({"status": f'Done. ${round(cb.total_cost, 2)}'})

    def tiny_ai_stream():
        yield json.dumps({"status": "TinyAI is Working..."})
        input = InputRequest(user_query=prompt.text, selected_element=prompt.html, source_file = session.directory+'/'+session.file, file_content=file_content)
        for status in tiny_ai.write_code(input):
            yield json.dumps({"status": status})

    stream = {Agent.auto_gpt: auto_gpt_stream, Agent.tiny_ai: tiny_ai_stream}[session.agent]
    return StreamingResponse(stream(), media_type="text/event-stream")


class BrowserError(BaseModel):
    message: str

@app.post("/fix_errors")
async def fix_errors(errors:List[BrowserError]):
    error_messages = '\n'.join([e.message for e in errors])
    task =  f"Browser logged errors: {error_messages}\n. Fix it."
    print(task)
    def stream():
          with get_openai_callback() as cb:
            for status in auto_gpt.run([task]):
                yield json.dumps({"status": json.dumps(status)})
            print(cb)
            yield json.dumps({"status": f'Done. ${round(cb.total_cost, 2)}'})

    return StreamingResponse(stream(), media_type="text/event-stream")
