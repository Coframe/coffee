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


# class EditFileInput(BaseModel):
#     """Input for EditFileTool."""
#     file_path: str = Field(..., description="Full Path of the file to edit.")
#     operation: str = Field(..., description="Operation type: " + \
#                                             "'insert' will use `lines.insert(line_index, text + '\n')`;" + \
#                                             "'replace' will use `lines[start_index:end_index] = [text + '\n']`;" + \
#                                             "'delete' will use `del lines[start_index:end_index]`")
#     line_index: int = Field(
#         None,
#         description="Line index at which to start the 'insert' operation (0-indexed) - "
#                     "lines.insert(line_index, text + '\n'). For 'replace' and 'delete', use 'range'"
#                     " instead."
#     )
#     range: Optional[Tuple[int, int]] = Field(
#         None,
#         description="Tuple of two line indexes (start, end) defining the range "
#                     "for 'replace' or 'delete' operations (0-indexed, "
#                     "end exclusive!)."
#     )
#     text: Optional[str] = Field(
#         None,
#         description="Text to insert or use for replacement. Required for 'insert' and "
#                     "'replace'; not used for 'delete'."
#     )
#
#
# class EditFileTool(BaseFileToolMixin, BaseTool):
#     """Tool that edits a file on a line-by-line basis."""
#
#     name: str = "edit_file"
#     args_schema: Type[BaseModel] = EditFileInput
#     description: str = "Edit file on a line basis without rewriting from scratch."
#
#     def _run(
#             self,
#             file_path: str,
#             operation: str,
#             line_index: int = None,
#             range: Optional[Tuple[int, int]] = None,
#             text: Optional[str] = None,
#             run_manager: Optional[CallbackManagerForToolRun] = None,
#     ) -> str:
#         try:
#             edit_path = self.get_relative_path(file_path)
#         except FileValidationError:
#             return INVALID_PATH_TEMPLATE.format(arg_name="file_path", value=file_path)
#
#         try:
#             with edit_path.open("r+", encoding="utf-8") as f:
#                 lines = f.readlines()
#
#                 if operation == "insert":
#                     if line_index < 0 or line_index > len(lines):
#                         return "Error: 'position' out of range."
#                     if text is None:
#                         return "Error: 'text' is required for the 'insert' operation."
#                     lines.insert(line_index, text + '\n')
#
#                 elif operation in ["replace", "delete"]:
#                     start, end = range
#                     if start < 0 or end > len(lines) or start >= end:
#                         return "Error: 'range' is invalid or out of range."
#                     if operation == "replace":
#                         if text is None:
#                             return "Error: 'text' is required for the 'replace' operation."
#                         lines[start:end] = [text + '\n']
#                     elif operation == "delete":
#                         del lines[start:end]
#
#                 else:
#                     return "Invalid operation specified."
#
#                 f.seek(0)
#                 f.writelines(lines)
#                 f.truncate()
#             read_file_tool = ReadFileTool(root_path=self.root_dir)
#             return f"File edited successfully at {file_path}.\nRead file content with `{read_file_tool.name}`:\n{read_file_tool._run(str(edit_path))}"
#         except Exception as e:
#             return "Error: " + str(e)

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
