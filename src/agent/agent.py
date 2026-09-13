from ..tools.list_files import ListFilesTool
from ..tools.project_scanner import ProjectScanner
from ..tools.read_file import ReadFileTool
from ..tools.search_code import SearchCodeTool
from ..tools.tool_result import ToolResult
from .tool_registry import ToolDefinition, ToolRegistry
from .tool_call_parser import ToolCallParser
from .conversation import Conversation
from .prompt_builder import PromptBuilder
from .final_answer_parser import FinalAnswerParser
from .project_context import ProjectContext
from .context_formatter import ContextFormatter


class Agent:
    def __init__(
        self,
        llm_client,
        project_path=".",
        project_context=None
    ):
        self.llm_client = llm_client
        self.project_context = project_context
        self.conversation = Conversation()
        self.prompt_builder = PromptBuilder(
            ContextFormatter()
        )

        self.project_scanner = ProjectScanner(project_path)

        self.list_files_tool = ListFilesTool(project_path)
        self.read_file_tool = ReadFileTool(project_path)
        self.search_code_tool = SearchCodeTool(project_path)
        self.final_answer_parser = FinalAnswerParser()

        self.tool_call_parser = ToolCallParser()
        self.tool_registry = ToolRegistry()

        self.tool_registry.register(
            "list_files",
            self.list_files_tool,
            ToolDefinition(
                name="list_files",
                description="List files and directories in the current project."
            )
        )

        self.tool_registry.register(
            "read_file",
            self.read_file_tool,
            ToolDefinition(
                name="read_file",
                description="Read the contents of a file from the current project.",
                parameters={
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file inside the project.",
                        "required": True
                    }
                }
            )
        )

        self.tool_registry.register(
            "search_code",
            self.search_code_tool,
            ToolDefinition(
                name="search_code",
                description="Search for a text query in the project source files.",
                parameters={
                    "query": {
                        "type": "string",
                        "description": "Text to search for in the project.",
                        "required": True
                    }
                }
            )
        )

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

    def select_tool(self, message):
        definitions = self.tool_registry.get_definitions()

        tools_description = []

        for definition in definitions.values():
            parameters = definition.parameters

            if parameters:
                parameter_lines = []

                for name, details in parameters.items():
                    parameter_lines.append(
                        f"- {name}: {details['type']} - "
                        f"{details['description']}"
                    )

                parameters_text = "\n".join(parameter_lines)
            else:
                parameters_text = "No parameters."

            tools_description.append(
                f"Tool: {definition.name}\n"
                f"Description: {definition.description}\n"
                f"Parameters:\n{parameters_text}"
            )

        tools_text = "\n\n".join(tools_description)

        prompt = f"""
    You are a tool selection system.
    
    Available tools:
    
    {tools_text}
    
    User request:
    {message}
    
    Select the single most appropriate tool for this request.
    
    Return only the tool name.
    If no tool is required, return:
    none
    """.strip()

        response = self.llm_client.generate(prompt).strip()

        if response == "none":
            return None

        if self.tool_registry.has(response):
            return response

        return None

    def _validate_tool_call(self, tool_call):
        if not isinstance(tool_call.tool, str) or not tool_call.tool:
            raise ValueError("Tool name must be a non-empty string.")

        if not self.tool_registry.has(tool_call.tool):
            raise ValueError(
                f"Tool '{tool_call.tool}' is not registered."
            )

        if not isinstance(tool_call.arguments, dict):
            raise ValueError(
                "Tool call arguments must be a dictionary."
            )

        definition = self.tool_registry.get_definition(tool_call.tool)

        if definition is None:
            return

        parameters = definition.parameters

        for name, details in parameters.items():
            if details.get("required", False):
                if name not in tool_call.arguments:
                    raise ValueError(
                        f"Missing required argument: {name}"
                    )

        for argument in tool_call.arguments:
            if argument not in parameters:
                raise ValueError(
                    f"Unexpected argument: {argument}"
                )

            expected_type = parameters[argument].get("type")

            if expected_type == "string":
                if not isinstance(tool_call.arguments[argument], str):
                    raise ValueError(
                        f"Argument '{argument}' must be a string."
                    )

    def execute_tool_call(self, tool_call):
        try:
            self._validate_tool_call(tool_call)

            result = self.tool_registry.execute_call(tool_call)

            return ToolResult(
                tool=tool_call.tool,
                success=True,
                result=result
            )
        except Exception as error:
            return ToolResult(
                tool=tool_call.tool,
                success=False,
                error=str(error)
            )

    def format_tool_result(self, tool_result):
        if tool_result.success:
            return (
                f"TOOL: {tool_result.tool}\n"
                f"STATUS: success\n"
                f"RESULT:\n{tool_result.result}"
            )

        return (
            f"TOOL: {tool_result.tool}\n"
            f"STATUS: error\n"
            f"ERROR:\n{tool_result.error}"
        )

    def send_tool_result_to_llm(self, tool_result):
        tool_result_text = self.format_tool_result(tool_result)

        self.conversation.add_message(
            "tool",
            tool_result_text
        )

        messages = self.conversation.get_messages()
        prompt = self.prompt_builder.build(messages)

        return self.llm_client.generate(prompt).strip()

    def run_tool_loop(self, message, max_tool_calls=5):
        self.conversation.add_message(
            "user",
            message
        )

        tool_calls_count = 0

        while tool_calls_count < max_tool_calls:
            prompt = self._build_tool_loop_prompt()

            response = self.llm_client.generate(prompt).strip()

            print("\n[AGENT] LLM response:")
            print(response)

            try:
                tool_call = self.tool_call_parser.parse(response)

            except ValueError:
                try:
                    final_answer = self.final_answer_parser.parse(
                        response
                    )

                except ValueError:
                    print(
                        "[AGENT] Response is neither a tool call "
                        "nor a final answer."
                    )

                    self.conversation.add_message(
                        "assistant",
                        response
                    )

                    return response

                print(
                    "[AGENT] Final answer received."
                )

                self.conversation.add_message(
                    "assistant",
                    final_answer
                )

                return final_answer

            print(
                f"[AGENT] Tool call: {tool_call.tool}"
            )

            print(
                f"[AGENT] Arguments: {tool_call.arguments}"
            )

            self.conversation.add_message(
                "assistant",
                response
            )

            tool_calls_count += 1

            print(
                f"[AGENT] Executing tool call "
                f"{tool_calls_count}/{max_tool_calls}"
            )

            tool_result = self.execute_tool_call(
                tool_call
            )

            print(
                "[AGENT] Tool result:"
            )
            print(
                self.format_tool_result(tool_result)
            )

            tool_result_text = self.format_tool_result(
                tool_result
            )

            self.conversation.add_message(
                "tool",
                tool_result_text
            )

        print(
            "[AGENT] Maximum number of tool calls reached."
        )

        return (
            "The maximum number of tool calls has been reached. "
            "Please continue with the available information."
        )

    def _build_tool_loop_prompt(self):
        messages = self.conversation.get_messages()

        conversation_text = self.prompt_builder.build(
            messages,
            self.project_context
        )

        tool_definitions = self.tool_registry.get_definitions()

        tools_text = ["AVAILABLE TOOLS:"]

        for name, definition in tool_definitions.items():
            tools_text.append(
                f"{name}: {definition.description}"
            )

            if definition.parameters:
                tools_text.append(
                    f"Parameters: {definition.parameters}"
                )

        tools_text.append("")
        tools_text.append("RULES:")
        tools_text.append(
            "1. Use a tool when project information is required."
        )
        tools_text.append(
            "2. If a requested file has not been read, use read_file first."
        )
        tools_text.append(
            "3. Never claim to have inspected a file without using a tool."
        )
        tools_text.append(
            "4. After a tool result, continue the task."
        )
        tools_text.append(
            "5. Return ONLY valid JSON."
        )
        tools_text.append("")
        tools_text.append(
            "For a tool call, you MUST return the arguments inside the arguments field."
        )
        tools_text.append(
            'The ONLY valid tool call format is: '
            '{"type":"tool_call","tool":"TOOL_NAME","arguments":{"PARAMETER":"VALUE"}}'
        )
        tools_text.append(
            'For read_file, the file path MUST be inside arguments, like this: '
            '{"type":"tool_call","tool":"read_file","arguments":{"file_path":"package.json"}}'
        )
        tools_text.append(
            "Do not put tool parameters directly at the top level."
        )
        tools_text.append("")
        tools_text.append(
            "When you have enough information, you MUST return a final_answer."
        )
        tools_text.append(
            "The final response MUST contain the field type with the exact value "
            "final_answer and the field content containing the answer."
        )
        tools_text.append(
            'The ONLY valid final response format is: '
            '{"type":"final_answer","content":"YOUR ANSWER"}'
        )
        tools_text.append(
            'Do not use any other JSON structure such as '
            '{"framework":"..."}'
        )
        tools_text.append("")
        tools_text.append(
            "Do not return plain text."
        )
        tools_text.append(
            "Do not use Markdown code fences."
        )
        tools_text.append(
            "Do not add text before or after the JSON."
        )

        return "\n\n".join([
            conversation_text,
            "\n".join(tools_text)
        ])

    def clear_conversation(self):
        self.conversation.clear()
