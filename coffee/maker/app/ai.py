from langchain.chat_models import ChatOpenAI
import os
import openai
from utils import parse_code_string

OPENAI_API_KEY = "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"
openai.api_key = OPENAI_API_KEY

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
        response = openai.ChatCompletion.create(
            messages=message,
            stream=False,
            model=self.model_name,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        if response["choices"][0]["message"]["content"].startswith("INSTRUCTIONS:"):
            return ("INSTRUCTIONS:","",response["choices"][0]["message"]["content"][14:])
        else:
            code_triples = parse_code_string(response["choices"][0]["message"]["content"])
            return code_triples

    def run(self, prompt):
        message=[{"role": "user", "content": prompt}] 
        response = openai.ChatCompletion.create(
            messages=message,
            stream=True,
            model=self.model_name,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        chat = ""
        for chunk in response:
            delta = chunk["choices"][0]["delta"]
            msg = delta.get("content", "")
            chat += msg
        return chat
    

'''
EXPERIMENTATION WITH LANGCHAIN
'''
# from langchain.llms import OpenAI
# from langchain.chains import ConversationalRetrievalChain
# from langchain.embeddings.openai import OpenAIEmbeddings
# from langchain.vectorstores import Chroma

# embeddings = OpenAIEmbeddings()
# vectorstore = Chroma(embedding_function=embeddings)

# from langchain.memory import ConversationBufferMemory
# memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# qa = ConversationalRetrievalChain.from_llm(OpenAI(temperature=0,model_name="gpt-4-32k"), vectorstore.as_retriever(), memory=memory)

# query = "My name's Bob. How are you?"
# result = qa({"question": query})

# print(result)

# query = "What's my name?"
# result = qa({"question": query})

# print("NEW MESSAGE:",result)