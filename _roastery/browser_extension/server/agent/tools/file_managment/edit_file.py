from typing import Optional, Type, Tuple

from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools.base import BaseTool
from langchain.tools.file_management.utils import (
    INVALID_PATH_TEMPLATE,
    BaseFileToolMixin,
    FileValidationError,
)

from agent.tools.file_managment.read_file import ReadFileTool


class EditFileInput(BaseModel):
    """Input for EditFileTool."""
    file_path: str = Field(..., description="Full Path of the file to edit.")
    existing_content: str = Field(..., description="Unique existing content of the file to find for replacement.")
    new_content: str = Field(..., description="New content to replace the `existing_content`.")


class EditFileTool(BaseFileToolMixin, BaseTool):
    """Tool that edits a file by replacing a unique part with new content."""

    name: str = "edit_file"
    args_schema: Type[BaseModel] = EditFileInput
    description: str = "Edit file by replacing a unique existing content with new content."

    def _run(
            self,
            file_path: str,
            existing_content: str,
            new_content: str,
            run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        try:
            edit_path = self.get_relative_path(file_path)
        except FileValidationError:
            return INVALID_PATH_TEMPLATE.format(arg_name="file_path", value=file_path)

        try:
            with edit_path.open("r+", encoding="utf-8") as f:
                content = f.read()

                if existing_content not in content:
                    return "Error: Unique part not found in the file."

                updated_content = content.replace(existing_content, new_content)

                f.seek(0)
                f.write(updated_content)
                f.truncate()

            read_file_tool = ReadFileTool(root_path=self.root_dir)
            return f"File edited successfully at {file_path}.\n" \
                   f"Read file content with `{read_file_tool.name}`:\n" \
                   f"{read_file_tool._run(str(edit_path))} "
        except Exception as e:
            return "Error: " + str(e)
