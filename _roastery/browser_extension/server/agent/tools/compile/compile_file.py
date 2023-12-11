from typing import Optional, Type
import subprocess
import os

from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools.base import BaseTool
from langchain.tools.file_management.utils import (
    INVALID_PATH_TEMPLATE,
    BaseFileToolMixin,
    FileValidationError,
)

from agent.tools.file_managment.read_file import ReadFileTool


class CompileFileInput(BaseModel):
    """Input for CompileFileTool."""
    file_path: str = Field(..., description="Path of the file to compile")


class CompileFileTool(BaseFileToolMixin, BaseTool):
    """Tool that compiles a given file to check if any errors."""

    name: str = "compile_file"
    args_schema: Type[BaseModel] = CompileFileInput
    description: str = "Compile a file to check if any errors."

    def _run(
            self,
            file_path: str,
            run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        try:
            compile_path = self.get_relative_path(file_path)
        except FileValidationError:
            return INVALID_PATH_TEMPLATE.format(arg_name="file_path", value=file_path)
        if not compile_path.exists():
            return f"Error: no such file or directory: {file_path}"

        file_extension = os.path.splitext(file_path)[1]
        command = get_compile_command(file_extension, str(compile_path))

        if command is None:
            return f"No compiler available for files with '{file_extension}' extension."

        read_file_tool = ReadFileTool(root_path=self.root_dir)

        read_file_response = f"Read file content with `{read_file_tool.name}`:\n{read_file_tool._run(str(compile_path))}"

        try:
            result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output = result.stdout.decode()
            errors = result.stderr.decode()
            return "Compilation Successful:\n" + output if not errors else f"Compilation Errors:\n{errors}\n{read_file_response}"
        except subprocess.CalledProcessError as e:
            output = e.stdout.decode()
            errors = e.stderr.decode()
            return f"Compilation Failed:\n{errors}\nOutput:\n{output}\n{read_file_response}"


def get_compile_command(file_extension: str, file_path: str) -> Optional[list]:
    if file_extension == '.tsx':
        return ['tsc', file_path]
    elif file_extension == '.py':
        return ['python', '-m', 'py_compile', file_path]
    elif file_extension == '.java':
        return ['javac', file_path]
    return None
