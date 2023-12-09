from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain.callbacks import get_openai_callback
from pydantic import BaseModel
import os
from typing import Optional, List
from agent.tools.file_managment.read_file import ReadFileTool
from agent.agent_gpt import get_agent
from models.base import InputRequest
from models.tiny import TinyAI
from models.snippet import SnippetAI
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


class Prompt(BaseModel):
    text: str
    html: Optional[str] = None


class Session(BaseModel):
    agent: str = None
    directory: str = os.environ.get("FRONTEND_DIR", '/frontend_dir')
    file: str = './app/page.tsx'
    file_content: str = None

session = Session()


class AutoGPTAgent():
    name = "auto_gpt"
    shortcut = "/a"
    def __init__(self) -> None:
        self.agent = get_agent(session.directory)

    def stream(self, prompt, session):
        yield json.dumps({"status": "AutoGPT is Working..."})
        task =  f"User request: {prompt.text}\n" \
                f"Currently user selected this element: {prompt.html}.\n"
        if(session.file):
            task += f"Currently user is looking at this file: {session.file}\n" \
                f"The content of the file is:\n" \
                f"{session.file_content}"

        with get_openai_callback() as cb:
            for update in self.agent.run([task]):
                if(isinstance(update, str)):
                   update = {"message": update}
                if(update.get('file_path')):
                    print(update.get('file_path'))
                    session.file = update.get('file_path')
                yield json.dumps({"status": json.dumps(update)})
            print(cb)
            yield json.dumps({"status": f'Done. ${round(cb.total_cost, 2)}'})

class TinyAIAgent():
    name = "tiny_ai"
    shortcut = "/t"
    def __init__(self) -> None:
        self.agent = TinyAI()

    def stream(self, prompt, session):
        yield json.dumps({"status": "TinyAI is Working..."})
        input = InputRequest(user_query=prompt.text, selected_element=prompt.html, source_file = session.directory+'/'+session.file, file_content=session.file_content)
        for status in self.agent.write_code(input):
            yield json.dumps({"status": status})
        yield json.dumps({"status": "Done."})

class SnippetAIAgent():
    name = "snippet_ai"
    shortcut = "/s"
    def __init__(self) -> None:
        self.agent = SnippetAI()

    def stream(self, prompt, session):
        yield json.dumps({"status": "SnippetAI is Working..."})
        input = InputRequest(user_query=prompt.text, selected_element=prompt.html, source_file = session.directory+'/'+session.file, file_content=session.file_content)
        for status in self.agent.write_code(input):
            yield json.dumps({"status": status})
        yield json.dumps({"status": "Done."})

class UndoAgent():
    name = "undo"
    shortcut = "/undo"
    def __init__(self) -> None:
        pass

    def stream(self, prompt, session):
        yield json.dumps({"status": "Undoing last change..."})
        print("undoing last change")
        if(session.file and session.file_content):
            open(session.directory+'/'+session.file, "w").write(session.file_content)
            session.file_content = None
            yield json.dumps({"status": "Done."})
        else:
            print('no backup stored')
            yield json.dumps({"status": "No backup stored."})

agents = {agent.name: agent for agent in [AutoGPTAgent(), TinyAIAgent(), SnippetAIAgent(), UndoAgent()]}

@app.post("/prompt")
async def generate(prompt: Prompt):
    print(prompt.text)

    # selection defaiult agent
    if not session.agent:
        if not session.file:
            session.agent = AutoGPTAgent.name
        else:
            session.agent = SnippetAIAgent.name

    # ovveride with user selection
    for agent in agents.values():
        if(prompt.text.startswith(agent.shortcut)):
            session.agent = agent.name
            prompt.text = prompt.text.replace(agent.shortcut, '', 1).strip()

    agent = agents[session.agent]

    if session.file and agent.name != UndoAgent.name:
        file_content = ReadFileTool(root_dir=session.directory).run(session.file)
        session.file_content = file_content

    return StreamingResponse(agent.stream(prompt, session), media_type="text/event-stream")


# TODO - combine with /prompt
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
