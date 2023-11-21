import json
import time
from typing import Any, Callable, List

from langchain.prompts.chat import (
    BaseChatPromptTemplate,
)
from langchain.schema.messages import BaseMessage, HumanMessage, SystemMessage
from langchain.schema.vectorstore import VectorStoreRetriever
from langchain.tools.base import BaseTool

from langchain_experimental.autonomous_agents.autogpt.prompt_generator import PromptGenerator
from langchain_experimental.pydantic_v1 import BaseModel


class AutoGPTPrompt(BaseChatPromptTemplate, BaseModel):  # type: ignore[misc]
    """Prompt for AutoGPT."""

    ai_name: str
    ai_role: str
    tools: List[BaseTool]
    token_counter: Callable[[str], int]
    send_token_limit: int = 4196 * 20

    def construct_full_prompt(self, goals: List[str]) -> str:
        prompt_start = (
            "Your decisions must always be made independently "
            "without seeking user assistance.\n"
            "Play to your strengths as an LLM and pursue simple "
            "strategies with no legal complications.\n"
            "If you have completed all your tasks, make sure to "
            'use the "finish" command.'
        )
        # Construct full prompt
        full_prompt = (
            f"You are {self.ai_name}, {self.ai_role}.\n{prompt_start}\n\n{code_quality}"
        )
        # for i, goal in enumerate(goals):
        #     full_prompt += f"{i + 1}. {goal}\n"

        full_prompt += f"\n\n{get_prompt(self.tools)}"
        return full_prompt

    def format_messages(self, **kwargs: Any) -> List[BaseMessage]:
        base_prompt = SystemMessage(content=self.construct_full_prompt(kwargs["goals"]))
        time_prompt = SystemMessage(
            content=f"The current time and date is {time.strftime('%c')}"
        )
        used_tokens = self.token_counter(base_prompt.content) + self.token_counter(
            time_prompt.content
        )
        previous_messages = kwargs["messages"]

        historical_messages: List[BaseMessage] = []
        for message in previous_messages[-20:][::-1]:
            message_tokens = self.token_counter(message.content)
            if used_tokens + message_tokens > self.send_token_limit - 1000:
                break
            historical_messages = [message] + historical_messages
            used_tokens += message_tokens
        input_message = HumanMessage(content=kwargs["user_input"])
        messages: List[BaseMessage] = [base_prompt, time_prompt]
        messages += historical_messages
        messages.append(input_message)
        return messages


def get_prompt(tools: List[BaseTool]) -> str:
    """Generates a prompt string.

    It includes various constraints, commands, resources, and performance evaluations.

    Returns:
        str: The generated prompt string.
    """

    # Initialize the PromptGenerator object
    prompt_generator = CustomPromptGenerator()

    # Add constraints to the PromptGenerator object
    # prompt_generator.add_constraint(
    #     "~4000 word limit for short term memory. "
    #     "Your short term memory is short, "
    #     "so immediately save important information to files."
    # )
    prompt_generator.add_constraint(
        "If you are unsure how you previously did something "
        "or want to recall past events, "
        "thinking about similar events will help you remember."
    )
    prompt_generator.add_constraint("No user assistance")
    prompt_generator.add_constraint(
        "Always write complete response and do not use `[REDACTED]` or any other placeholders."
    )
    prompt_generator.add_constraint(
        'Exclusively use the commands listed in double quotes e.g. "command name"'
    )

    # Add commands to the PromptGenerator object
    for tool in tools:
        prompt_generator.add_tool(tool)

    # Add resources to the PromptGenerator object
    # prompt_generator.add_resource(
    #     "Internet access for searches and information gathering."
    # )
    # prompt_generator.add_resource("Long Term memory management.")
    # prompt_generator.add_resource(
    #     "GPT-4 powered Agents for delegation of simple tasks."
    # )
    # prompt_generator.add_resource("File output.")

    # Add performance evaluations to the PromptGenerator object
    prompt_generator.add_performance_evaluation(
        "Continuously review and analyze your actions "
        "to ensure you are performing to the best of your abilities."
    )
    prompt_generator.add_performance_evaluation(
        "Constructively self-criticize your big-picture behavior constantly."
    )
    prompt_generator.add_performance_evaluation(
        "Reflect on past decisions and strategies to refine your approach."
    )
    prompt_generator.add_performance_evaluation(
        "Every command has a cost, so be smart and efficient. "
        "Aim to complete tasks in the least number of steps."
    )

    # Generate the prompt string
    prompt_string = prompt_generator.generate_prompt_string()

    return prompt_string


class CustomPromptGenerator(PromptGenerator):
    def __init__(self):
        super().__init__()
        self.response_format = {
            "thoughts": {
                "plan": "short bulleted\n- list that conveys\n- long-term plan"
            },
            "command": {
                "name": "command name",
                "args": {
                    "arg name": "value",
                },
            }
        }


    def generate_prompt_string(self) -> str:
        """Generate a prompt string.

        Returns:
            str: The generated prompt string.
        """
        formatted_response_format = json.dumps(self.response_format, indent=4)

        prompt_string = (
            f"Constraints:\n{self._generate_numbered_list(self.constraints)}\n\n"
            f"Commands:\n"
            f"{self._generate_numbered_list(self.commands, item_type='command')}\n\n"
            # f"Resources:\n{self._generate_numbered_list(self.resources)}\n\n"
            f"Performance Evaluation:\n"
            f"{self._generate_numbered_list(self.performance_evaluation)}\n\n"
            f"You should only respond in JSON format as described below "
            f"\nResponse Format: \n{formatted_response_format} "
            f"\nEnsure the response can be parsed by Python json.loads"
        )

        return prompt_string


code_quality = """Code quality:
- Ensure conciseness, maintainable and readable of production-ready code
- DRY
- Single responsibility principle
- Self-evident naming
- Minimum side effects
- No deep nesting
- No magic numbers
- No long files/functions
- No long lines
- No unnecessary comments/code
- More types
- Very concise and easy to read code"""
