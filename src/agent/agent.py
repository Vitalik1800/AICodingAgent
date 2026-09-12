from ..tools.list_files import ListFilesTool
from ..tools.project_scanner import ProjectScanner
from ..tools.read_file import ReadFileTool
from ..tools.search_code import SearchCodeTool
from ..tools.tool_result import ToolResult
from .conversation import Conversation
from .prompt_builder import PromptBuilder


class Agent:
    def __init__(self, llm_client, project_path="."):
        self.llm_client = llm_client
        self.conversation = Conversation()
        self.prompt_builder = PromptBuilder()

        self.project_scanner = ProjectScanner(project_path)

        self.list_files_tool = ListFilesTool(project_path)
        self.read_file_tool = ReadFileTool(project_path)
        self.search_code_tool = SearchCodeTool(project_path)

    def ask(self, message):
        self.conversation.add_message(
            "user",
            message
        )

        messages = self.conversation.get_messages()

        prompt = self.prompt_builder.build(messages)

        response = self.llm_client.generate(prompt)

        self.conversation.add_message(
            "assistant",
            response
        )

        return response

    def get_project_structure(self):
        return self.project_scanner.get_structure()

    def list_files(self):
        try:
            result = self.list_files_tool.execute()

            return ToolResult(
                tool="list_files",
                success=True,
                result=result
            )

        except Exception as error:
            return ToolResult(
                tool="list_files",
                success=False,
                error=str(error)
            )

    def read_file(self, file_path):
        try:
            result = self.read_file_tool.execute(file_path)

            return ToolResult(
                tool="read_file",
                success=True,
                result=result
            )

        except Exception as error:
            return ToolResult(
                tool="read_file",
                success=False,
                error=str(error)
            )

    def search_code(self, query):
        try:
            result = self.search_code_tool.execute(query)

            return ToolResult(
                tool="search_code",
                success=True,
                result=result
            )

        except Exception as error:
            return ToolResult(
                tool="search_code",
                success=False,
                error=str(error)
            )

    def clear_conversation(self):
        self.conversation.clear()
