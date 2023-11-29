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
    phrase: str = Field(..., description="Phrase to search for.")

class GrepTool(BaseFileToolMixin, BaseTool):
    """Tool that uses grep to search for files containing a specific phrase, excluding patterns listed in .gitignore."""

    name: str = "grep"
    args_schema: Type[BaseModel] = GrepInput
    description: str = "Search for files containing a specific phrase using grep, while excluding patterns in .gitignore."

    def _run(
            self,
            phrase: str,
            run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        try:
            # Parse .gitignore and construct exclude options
            # gitignore_path = self.get_relative_path('.gitignore')
            # exclude_options = self.parse_gitignore(gitignore_path)

            dir =  self.get_relative_path('.')
            # Construct the grep command
            command = f"find '{dir}' -type f -not -path '*/\.*' | xargs grep -Ril '{phrase}'"
            print('>', command)
            # Execute the command
            process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE, text=True)
            stdout, stderr = process.communicate()
            print('stdout', stdout)
            print('stderr', stderr)
            if stderr:
                return f"Error: {stderr}"
            if not stdout:
                return "No files found."

            return stdout.strip()
        except Exception as e:
            return "Error: " + str(e)

    def parse_gitignore(self, gitignore_path):
        exclude_options = ""
        if os.path.exists(gitignore_path):
            with open(gitignore_path, 'r') as file:
                for line in file:
                    clean_line = line.strip()
                    # Ignore comments and empty lines
                    if clean_line and not clean_line.startswith('#'):
                        # Convert to grep exclude pattern
                        clean_line = re.escape(clean_line)
                        whole_path = self.get_relative_path(clean_line)
                        exclude_options += f" --exclude='{whole_path}'"
        return exclude_options

