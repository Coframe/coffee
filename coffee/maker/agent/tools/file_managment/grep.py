from typing import Optional, Type
from subprocess import Popen, PIPE
import os
import re

from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools.base import BaseTool
from langchain.tools.file_management.utils import BaseFileToolMixin
from langchain.callbacks.manager import CallbackManagerForToolRun


class GrepInput(BaseModel):
    """Input for GrepTool."""
    phrase: str = Field(..., description="Phrase to search for. Search for text content, not classes or ids.")

class GrepTool(BaseFileToolMixin, BaseTool):
    """Tool that uses grep to search for files containing a specific phrase"""

    name: str = "grep"
    args_schema: Type[BaseModel] = GrepInput
    description: str = "Search for files containing a specific phrase using grep"

    def _run(
            self,
            phrase: str,
            run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        try:

            dir =  self.get_relative_path('.')
            # Construct the grep command, ignoring files in hidden folders.
            command = f"find '{dir}' -type f -not -path '*/\.*' | xargs grep -Ril '{phrase}'"
            print('>', command)
            # Execute the command
            process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE, text=True)
            stdout, stderr = process.communicate()
            # removing the root dir from the output
            stdout = stdout.replace(str(dir)+'/', './')
            print(stdout)

            if stderr:
                return f"Error: {stderr}"
            if not stdout:
                return "No files found."

            return stdout.strip()
        except Exception as e:
            return "Error: " + str(e)

