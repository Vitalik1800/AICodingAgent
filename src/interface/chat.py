import threading

import customtkinter as ctk

from ..agent.agent import Agent
from ..ai.ollama_client import OllamaClient
from .theme import Theme


class Chat(ctk.CTkFrame):
    def __init__(
        self,
        master,
        on_status_change=None,
        project_path="."
    ):
        super().__init__(
            master,
            corner_radius=0,
            fg_color=Theme.BACKGROUND
        )

        self.on_status_change = on_status_change
        self.project_path = project_path

        self.agent = Agent(
            OllamaClient(),
            project_path
        )

        self._create_widgets()

    def _create_widgets(self):
        title_label = ctk.CTkLabel(
            self,
            text="AI Chat",
            font=ctk.CTkFont(
                size=16,
                weight="bold"
            )
        )
        title_label.pack(
            padx=20,
            pady=(16, 10),
            anchor="w"
        )

        self.chat_history = ctk.CTkTextbox(
            self,
            wrap="word",
            state="disabled",
            font=ctk.CTkFont(size=13),
            fg_color=Theme.BACKGROUND,
            border_width=0
        )
        self.chat_history.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 12)
        )

        commands_label = ctk.CTkLabel(
            self,
            text=(
                "Commands:  "
                "/list — list files   "
                "/read <file> — read file   "
                "/search <query> — search code"
            ),
            text_color=Theme.SECONDARY_TEXT,
            font=ctk.CTkFont(size=11)
        )
        commands_label.pack(
            padx=20,
            pady=(0, 8),
            anchor="w"
        )

        input_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        input_frame.pack(
            fill="x",
            padx=20,
            pady=(0, 16)
        )

        self.message_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Ask AI...",
            height=38,
            font=ctk.CTkFont(size=13),
            fg_color=Theme.INPUT_BACKGROUND,
            border_color=Theme.BORDER
        )
        self.message_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 10)
        )

        self.message_entry.bind(
            "<Return>",
            self._on_enter
        )

        send_button = ctk.CTkButton(
            input_frame,
            text="Send",
            width=90,
            height=38,
            command=self._send_message
        )
        send_button.pack(
            side="right"
        )

        clear_button = ctk.CTkButton(
            input_frame,
            text="Clear",
            width=90,
            height=38,
            fg_color=Theme.STATUS_BACKGROUND,
            hover_color=Theme.BORDER,
            command=self._clear_chat
        )
        clear_button.pack(
            side="left"
        )

    def _on_enter(self, event):
        self._send_message()

    def _clear_chat(self):
        self.agent.clear_conversation()

        self.chat_history.configure(
            state="normal"
        )

        self.chat_history.delete(
            "1.0",
            "end"
        )

        self.chat_history.configure(
            state="disabled"
        )

        if self.on_status_change:
            self.on_status_change("Chat cleared")

    def set_project_path(self, project_path):
        self.project_path = project_path

        self.agent = Agent(
            OllamaClient(),
            project_path
        )

    def _send_message(self):
        message = self.message_entry.get().strip()

        if not message:
            return

        if self.on_status_change:
            self.on_status_change("Thinking...")

        self._append_message(
            "You",
            message
        )

        self.message_entry.delete(
            0,
            "end"
        )

        thread = threading.Thread(
            target=self._generate_response,
            args=(message,),
            daemon=True
        )

        thread.start()

    def _generate_response(self, message):
        try:
            if message == "/list":
                result = self.agent.list_files()
                response = self._format_tool_result(result)

            elif message.startswith("/read "):
                file_path = message[6:].strip()

                if not file_path:
                    response = "Usage: /read <file_path>"
                else:
                    result = self.agent.read_file(file_path)
                    response = self._format_tool_result(result)

            elif message.startswith("/search "):
                query = message[8:].strip()

                if not query:
                    response = "Usage: /search <query>"
                else:
                    result = self.agent.search_code(query)
                    response = self._format_tool_result(result)

            else:
                response = self._generate_ai_response(message)

            self.after(
                0,
                self._handle_response,
                response
            )

        except Exception as error:
            self.after(
                0,
                self._handle_error,
                error
            )

    def _generate_ai_response(self, message):
        structure = self.agent.get_project_structure()

        project_context = "\n".join(
            f"{item.item_type}: {item.path}"
            for item in structure
        )

        prompt = (
            "PROJECT_STRUCTURE:\n"
            f"{project_context}\n\n"
            f"USER REQUEST:\n{message}"
        )

        return self.agent.ask(prompt)

    def _format_tool_result(self, tool_result):
        if not tool_result.success:
            return (
                f"Tool: {tool_result.tool}\n"
                f"Status: error\n"
                f"Error: {tool_result.error}"
            )

        return (
            f"Tool: {tool_result.tool}\n"
            f"Status: success\n"
            f"Result:\n{tool_result.result}"
        )

    def _handle_response(self, response):
        self._append_message(
            "AI",
            response
        )

        if self.on_status_change:
            self.on_status_change("Ready")

    def _handle_error(self, error):
        self._append_message(
            "Error",
            str(error)
        )

        if self.on_status_change:
            self.on_status_change("Error")

    def _append_message(self, sender, message):
        self.chat_history.configure(
            state="normal"
        )

        self.chat_history.insert(
            "end",
            f"{sender}:\n{message}\n\n"
        )

        self.chat_history.configure(
            state="disabled"
        )

        self.chat_history.see("end")
