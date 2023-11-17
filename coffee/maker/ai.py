from langchain.chat_models import ChatOpenAI
import os
from openai import OpenAI

client = OpenAI()
from utils import parse_code_string

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

class AI:
    def __init__(self, model="gpt-4-32k", temperature=0.1, max_tokens=10000):
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.model_name = model
        try:
            self.model = ChatOpenAI(model_name=model, temperature=temperature, openai_api_key=OPENAI_API_KEY)
        except Exception as e:
            print(e)
            self.model = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=temperature, openai_api_key=OPENAI_API_KEY)
            self.model_name = "gpt-3.5-turbo"

    def write_code(self, prompt):
        message=[{"role": "user", "content": prompt}]
        print('sending request to', self.model_name)
        response = client.chat.completions.create(messages=message,
            stream=False,
            model=self.model_name,
            max_tokens=self.max_tokens,
            temperature=self.temperature)
        print('got response from', self.model_name)
        content = response.choices[0].message.content
        if content.startswith("INSTRUCTIONS:"):
            return ("INSTRUCTIONS:","",content[14:])
        else:
            code_triples = parse_code_string(content)
            return code_triples

    def run(self, prompt):
        message=[{"role": "user", "content": prompt}]
        response = client.chat.completions.create(messages=message,
            stream=True,
            model=self.model_name,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        chat = ""
        for chunk in response:
            delta = chunk.choices[0].delta
            msg = delta.get("content", "")
            chat += msg
        return chat
