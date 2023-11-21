from __future__ import annotations

from typing import List, Optional

from langchain.chains.llm import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.chat_models.base import BaseChatModel
from langchain.memory import ChatMessageHistory
from langchain.schema import (
    BaseChatMessageHistory,
    Document,
)
from langchain.schema.messages import AIMessage, HumanMessage, SystemMessage
from langchain.schema.vectorstore import VectorStoreRetriever
from langchain.tools.base import BaseTool
from langchain.tools.human.tool import HumanInputRun

from langchain_experimental.autonomous_agents.autogpt.output_parser import (
    AutoGPTOutputParser,
    BaseAutoGPTOutputParser,
)
# from langchain_experimental.autonomous_agents.autogpt.prompt import AutoGPTPrompt
from langchain_experimental.autonomous_agents.autogpt.prompt_generator import (
    FINISH_NAME,
)
from langchain_experimental.pydantic_v1 import ValidationError
import json
from agent.prompt import AutoGPTPrompt

from agent.tools.file_managment.toolkit import FileManagementToolkit
from agent.tools.compile.compile_file import CompileFileTool


class AutoGPT:
    """Agent class for interacting with Auto-GPT."""

    def __init__(
            self,
            ai_name: str,
            chain: LLMChain,
            output_parser: BaseAutoGPTOutputParser,
            tools: List[BaseTool],
            feedback_tool: Optional[HumanInputRun] = None,
            chat_history_memory: Optional[BaseChatMessageHistory] = None,
    ):
        self.ai_name = ai_name
        self.next_action_count = 0
        self.chain = chain
        self.output_parser = output_parser
        self.tools = tools
        self.feedback_tool = feedback_tool
        self.chat_history_memory = chat_history_memory or ChatMessageHistory()

    @classmethod
    def from_llm_and_tools(
            cls,
            ai_name: str,
            ai_role: str,
            tools: List[BaseTool],
            llm: BaseChatModel,
            human_in_the_loop: bool = False,
            output_parser: Optional[BaseAutoGPTOutputParser] = None,
            chat_history_memory: Optional[BaseChatMessageHistory] = None,
    ) -> AutoGPT:
        prompt = AutoGPTPrompt(
            ai_name=ai_name,
            ai_role=ai_role,
            tools=tools,
            input_variables=["messages", "goals", "user_input"],
            token_counter=llm.get_num_tokens,
        )
        human_feedback_tool = HumanInputRun() if human_in_the_loop else None
        chain = LLMChain(llm=llm, prompt=prompt)
        return cls(
            ai_name,
            chain,
            output_parser or AutoGPTOutputParser(),
            tools,
            feedback_tool=human_feedback_tool,
            chat_history_memory=chat_history_memory,
        )

    def run(self, goals: List[str]) -> str:
        self.chat_history_memory.add_message(
            HumanMessage(
                content=str(goals[0]) if len(goals) == 1 else "Goals:\n" + "- " + "\n- ".join(goals)
            )
        )

        user_input = (
            "Determine which next command to use to complete user queries, "
            "and respond using the format specified above:"
        )
        # Interaction Loop
        loop_count = 0
        while True:
            # Discontinue if continuous limit is reached
            loop_count += 1

            # Send message to AI, get response
            assistant_reply = self.chain.run(
                goals=goals,
                messages=self.chat_history_memory.messages,
                user_input=user_input,
            )
            print(assistant_reply)
            try:
                parsed_assistant_reply = json.loads(assistant_reply)
                yield parsed_assistant_reply
            except:
                pass

            # Assistant thoughts
            self.chat_history_memory.add_message(HumanMessage(content=user_input))
            self.chat_history_memory.add_message(AIMessage(content=assistant_reply))

            # Get command name and arguments
            action = self.output_parser.parse(assistant_reply)

            tools = {t.name: t for t in self.tools}
            if action.name == FINISH_NAME:
                return action.args["response"]
            if action.name in tools:
                tool = tools[action.name]
                try:
                    observation = tool.run(action.args)
                except ValidationError as e:
                    observation = (
                        f"Validation Error in args: {str(e)}, args: {action.args}"
                    )
                except Exception as e:
                    observation = (
                        f"Error: {str(e)}, {type(e).__name__}, args: {action.args}"
                    )
                result = f"Command {tool.name} returned: {observation}"
            elif action.name == "ERROR":
                result = f"Error: {action.args}. "
            else:
                result = (
                    f"Unknown command '{action.name}'. "
                    f"Please refer to the 'COMMANDS' list for available "
                    f"commands and only respond in the specified JSON format."
                )

            if self.feedback_tool is not None:
                feedback = f"\n{self.feedback_tool.run('Input: ')}"
                if feedback in {"q", "stop"}:
                    print("EXITING")
                    return "EXITING"

            self.chat_history_memory.add_message(SystemMessage(content=result))


def get_agent(root_dir):
    tools = []
    toolkit = FileManagementToolkit(
        root_dir=root_dir
    )
    tools += toolkit.get_tools()
    # tools += [CompileFileTool(root_dir=root_dir)] - Compilation doesn't work yet

    agent = AutoGPT.from_llm_and_tools(
        ai_name="Coffee",
        ai_role=f"Expert Web Developer, working in directory {toolkit.root_dir}. All path are relative to this path.",
        tools=tools,
        llm=ChatOpenAI(temperature=0.7, model="gpt-4-1106-preview",
                       model_kwargs={"response_format": {"type": "json_object"}}),
    )
    agent.chain.verbose = False
    return agent
