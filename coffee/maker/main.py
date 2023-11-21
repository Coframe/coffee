from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain.callbacks import get_openai_callback
from pydantic import BaseModel
import os

from agent.agent_gpt import get_agent

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


agent = get_agent(os.environ.get("FRONTEND_DIR"))


@app.post("/prompt")
async def generate(prompt: Prompt):
    task = f"User query: {prompt.text}\n\n" \
           f"Currently user is looking at this file: pages/contact-us.tsx."
    print(task)
    with get_openai_callback() as cb:
        agent.run([task])
        print(cb)
    return {"message": "Response written to file: pages/contact-us.tsx"}
