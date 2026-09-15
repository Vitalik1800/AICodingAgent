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
from .context_formatter import ContextFormatter
from .modification_pipeline import ModificationPipeline
from .modification_response_parser import ModificationResponseParser
from copy import deepcopy
from .apply_patch_service import ApplyPatchService
from .modification_request_validator import ModificationRequestValidator


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
        self.modification_pipeline = ModificationPipeline(project_path)
        self.modification_response_parser = ModificationResponseParser(project_path)
        self.apply_patch_service = ApplyPatchService(project_path)
        self.modification_request_validator = ModificationRequestValidator()
        self.patch_previews = []
        self.pending_modifications = None

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

    def preview_modification(self, modification):
        preview = self.modification_pipeline.process_preview(
            modification
        )

        self.patch_previews = [preview]

        return preview

    def preview_modifications(self, modifications):
        previews = self.modification_pipeline.process_previews(
            modifications
        )

        self.patch_previews = previews.copy()

        return previews

    def get_patch_previews(self):
        return deepcopy(self.patch_previews)

    def get_pending_modifications(self):
        if self.pending_modifications is None:
            return None

        return deepcopy(self.pending_modifications)

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

    def _process_modification_response(self, response):
        modification_response = (
            self.modification_response_parser.parse(
                response
            )
        )

        self.pending_modifications = modification_response

        previews = self.preview_modifications(
            modification_response
        )

        print(
            f"[AGENT] Generated {len(previews)} "
            f"patch preview(s)."
        )

        return previews

    def _is_modification_request(self, message):
        if not isinstance(message, str):
            return False

        text = message.lower().strip()

        modification_keywords = (
            "створи файл",
            "створити файл",
            "створи новий файл",
            "створити новий файл",
            "зміни файл",
            "змінити файл",
            "відредагуй файл",
            "відредагувати файл",
            "онови файл",
            "оновити файл",
            "видали файл",
            "видалити файл",
            "create file",
            "create a file",
            "create new file",
            "create a new file",
            "update file",
            "update the file",
            "edit file",
            "edit the file",
            "modify file",
            "modify the file",
            "delete file",
            "delete the file",
            "remove file",
            "remove the file",
        )

        return any(
            keyword in text
            for keyword in modification_keywords
        )

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
                tool_call = self.tool_call_parser.parse(
                    response
                )

            except ValueError:
                try:
                    modification_response = (
                        self.modification_response_parser.parse(
                            response
                        )
                    )

                except ValueError:
                    if self._is_modification_request(message):
                        print(
                            "[AGENT] Modification request requires "
                            "a modification response."
                        )

                        correction_message = (
                            "Your previous response was invalid because "
                            "the user requested a project file modification. "
                            "You MUST NOT return a final_answer. "
                            "Return ONLY a valid modification response "
                            "containing the complete file modification. "
                            "Use the correct modification_type: "
                            "create, update, or delete. "
                            "Do not explain the change. "
                            "Do not use Markdown code fences. "
                            "Return only the JSON object."
                        )

                        self.conversation.add_message(
                            "user",
                            correction_message
                        )

                        continue

                    try:
                        final_answer = self.final_answer_parser.parse(
                            response
                        )

                    except ValueError:
                        print(
                            "[AGENT] Response is neither a tool call, "
                            "modification, nor a final answer."
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

                try:
                    self.modification_request_validator.validate(
                        message,
                        modification_response
                    )

                except ValueError as error:
                    print(
                        "[AGENT] Modification rejected: "
                        f"{error}"
                    )

                    correction_message = (
                        "Your previous modification response was invalid "
                        "because its modification_type does not match the "
                        "operation requested by the user. "
                        "Return ONLY a valid modification response using "
                        "the correct operation: create, update, or delete. "
                        "Do not return a final_answer. "
                        "Do not explain the change. "
                        "Do not use Markdown code fences. "
                        "Return only the JSON object."
                    )

                    self.conversation.add_message(
                        "user",
                        correction_message
                    )

                    continue

                print(
                    "[AGENT] Modification response received."
                )

                self.conversation.add_message(
                    "assistant",
                    response
                )

                self.pending_modifications = modification_response

                previews = self.preview_modifications(
                    modification_response
                )

                print(
                    f"[AGENT] Generated {len(previews)} "
                    f"patch preview(s)."
                )

                return (
                    f"Generated {len(previews)} patch preview(s). "
                    "Review the changes in the Patch Preview panel."
                )

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
        prompt_parts = []

        prompt_parts.append(
            """
    You are an AI coding agent working with a local project.

    GENERAL RULES:
    - Use tools when project information is required.
    - Never claim that you inspected, read, created, updated, or deleted a file
      unless the corresponding tool result confirms it.
    - Work only with relative paths inside the project.
    - Never access paths outside the project.
    - Use read_file when the complete current content of an existing file is required.
    - Use list_files when project structure information is required.
    - Do not repeat a successful tool call when its result already contains the
      required information.
    """
        )

        prompt_parts.append(
            """
    TOOL CALL FORMAT:

    Return ONLY a JSON object.

    For list_files without parameters:
    {"type":"tool_call","tool":"list_files","arguments":{}}

    For read_file:
    {"type":"tool_call","tool":"read_file","arguments":{"file_path":"src/example.py"}}

    Do not use Markdown code fences.
    Do not add explanations before or after the JSON.
    """
        )

        prompt_parts.append(
            """
    MODIFICATION REQUESTS:

    If the user asks to create, update, edit, modify, change, or delete a project
    file, the final result for that request MUST be a modification response.

    A modification response MUST have this structure:

    {
      "type": "modification",
      "modifications": [
        {
          "file_path": "relative/path/to/file",
          "original_content": "...",
          "new_content": "...",
          "description": "...",
          "modification_type": "create"
        }
      ]
    }

    Allowed modification_type values:
    - create
    - update
    - delete

    Return ONLY the JSON object.
    Do not use Markdown code fences.
    Do not return final_answer for a modification request.
    Do not explain the change.
    """
        )

        prompt_parts.append(
            """
    CREATE WORKFLOW:

    When the user requests creation of a file:

    1. Determine whether the requested file exists if necessary.
    2. If the file does not exist, create a modification response.
    3. Use modification_type "create".
    4. file_path MUST be the requested relative project path.
    5. original_content MUST be an empty string.
    6. new_content MUST contain the complete content of the new file.
    7. Do not return final_answer.
    8. Do not claim that the file has already been created.
    9. The agent will create the file only after the modification is approved.
    """
        )

        prompt_parts.append(
            """
    UPDATE WORKFLOW:

    When the user requests an update, edit, or change to an existing file:

    1. If the complete current file content is not already available, use read_file.
    2. When read_file returns STATUS: success, its result contains the current file
       content.
    3. original_content MUST exactly match the complete content returned by
       read_file.
    4. new_content MUST contain the complete updated file content.
    5. modification_type MUST be "update".
    6. Never use an empty original_content for an existing file.
    7. Do not call read_file again for the same file after a successful read.
    8. Do not call list_files after a successful read when the file content is
       already sufficient to create the modification.
    9. The NEXT response after a successful read_file MUST be the modification JSON.
    10. Do not return final_answer.
    11. Do not explain the change.
    """
        )

        prompt_parts.append(
            """
    DELETE WORKFLOW:

    When the user requests deletion of a file:

    1. If the complete current file content is not already available, use read_file.
    2. The purpose of read_file is to obtain the exact current content required for
       the deletion safety check.
    3. When read_file returns STATUS: success, the complete current file content is
       available.
    4. After read_file returns STATUS: success, STOP USING TOOLS.
    5. Do NOT call list_files after a successful read_file.
    6. Do NOT call read_file again for the same file.
    7. Do NOT call any other tool after a successful read_file.
    8. The VERY NEXT response MUST be the modification JSON.
    9. modification_type MUST be "delete".
    10. file_path MUST be the requested relative project path.
    11. original_content MUST exactly equal the complete content returned by
        read_file.
    12. new_content MUST be an empty string.
    13. Do NOT return final_answer.
    14. Do NOT claim that the file has already been deleted.
    15. Do NOT explain the deletion.
    16. The agent will delete the file only after the modification is approved.

    MANDATORY DELETE SEQUENCE:

    read_file SUCCESS
            ↓
    modification JSON
            ↓
    ModificationRequestValidator
            ↓
    Patch Preview

    There must be NO tool call between read_file SUCCESS and modification JSON.
    """
        )

        prompt_parts.append(
            """
    MANDATORY TOOL STOP CONDITION:

    Once a tool has successfully returned all information required to complete the
    user's requested modification, no additional information is needed.

    For UPDATE:
    read_file SUCCESS → modification JSON

    For DELETE:
    read_file SUCCESS → modification JSON

    Do not call list_files.
    Do not call read_file again.
    Do not call another tool.
    Do not return final_answer.
    Do not explain the change.

    Immediately return the modification JSON.
    """
        )

        prompt_parts.append(
            """
    MODIFICATION SAFETY:

    For update:
    - original_content must exactly match the complete current file content.
    - new_content must be the complete resulting file content.
    - Never generate a partial file as new_content.

    For delete:
    - original_content must exactly match the complete current file content.
    - new_content must be empty.
    - Never use an empty original_content for an existing file.

    For create:
    - original_content must be empty.
    - new_content must contain the complete file content.

    Use only relative project paths.
    Never modify files outside the project.
    """
        )

        prompt_parts.append(
            """
    FINAL ANSWER:

    A final_answer is allowed ONLY when the user's request is not a project file
    modification request.

    For a normal informational request, return:

    {
      "type": "final_answer",
      "content": "..."
    }

    Return ONLY the JSON object.
    Do not use Markdown code fences.
    """
        )

        prompt_parts.append(
            """
    FINAL DECISION RULE:

    Before responding, determine whether the user's request requires a project
    file modification.

    If YES:
    - create/update/delete the requested file through a modification response.
    - Never return final_answer.

    If NO:
    - answer normally through final_answer.

    If a successful read_file result already provides the complete content needed
    for an update or deletion, immediately return the modification JSON.
    """
        )

        if self.project_context is not None:
            prompt_parts.append(
                "PROJECT CONTEXT:\n"
                + self.project_context.formatted_structure
            )

        messages = self.conversation.get_messages()

        return self.prompt_builder.build(
            messages,
            project_context=None
        )

    def apply_modification(self, modification):
        result = self.apply_patch_service.apply(
            modification
        )

        self.patch_previews.clear()

        return result

    def apply_modifications(self, modifications):
        results = self.apply_patch_service.apply_all(
            modifications
        )

        self.patch_previews.clear()

        return results

    def clear_conversation(self):
        self.conversation.clear()
        self.patch_previews.clear()
        self.pending_modifications = None
