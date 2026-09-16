import threading
import traceback

import customtkinter as ctk

from ..agent.agent import Agent
from ..agent.message import Message
from ..agent.project_context_builder import ProjectContextBuilder
from ..ai.ollama_client import OllamaClient
from .theme import Theme


class Chat(ctk.CTkFrame):
    def __init__(
        self,
        master,
        on_status_change=None,
        on_patch_preview=None,
        on_generation_state_change=None,
        project_path=".",
        chat_history_storage=None,
        chat_history_manager=None
    ):
        super().__init__(
            master,
            corner_radius=0,
            fg_color=Theme.BACKGROUND
        )

        self.on_status_change = on_status_change
        self.on_patch_preview = on_patch_preview
        self.on_generation_state_change = on_generation_state_change
        self.project_path = project_path
        self.active_chat = None
        self.is_generating = False
        self.generation_id = 0
        self.chat_history_storage = chat_history_storage
        self.chat_history_manager = chat_history_manager

        self.context_builder = ProjectContextBuilder()
        self.agent = self._create_agent()

        self._create_widgets()

    def _create_agent(self):
        self.project_context = self.context_builder.build(
            self.project_path
        )

        return Agent(
            OllamaClient(),
            self.project_path,
            self.project_context
        )

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

    def set_active_chat(self, chat_history):
        self.active_chat = chat_history

    def load_chat_history(self, chat_history):
        self.active_chat = chat_history

        self.chat_history.configure(
            state="normal"
        )

        self.chat_history.delete(
            "1.0",
            "end"
        )

        self.agent.clear_conversation()

        for message in chat_history.messages:
            if message.role == "user":
                self.chat_history.insert(
                    "end",
                    f"You: \n{message.content}\n\n"
                )
            elif message.role == "assistant":
                self.chat_history.insert(
                    "end",
                    f"AI: \n{message.content}\n\n"
                )
            elif message.role == "tool":
                self.chat_history.insert(
                    "end",
                    f"Tool: \n{message.content}\n\n"
                )

            self.agent.conversation.add_message(
                message.role,
                message.content
            )

        self.chat_history.configure(
            state="disabled"
        )

        self.chat_history.see("end")

    def _on_enter(self, _event):
        self._send_message()

    def _clear_chat(self):
        self.agent.clear_conversation()

        if self.active_chat is not None:
            self.active_chat.messages.clear()

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
        self.agent = self._create_agent()

    def _send_message(self):
        if self.is_generating:
            return

        message = self.message_entry.get().strip()

        if not message:
            return

        self.is_generating = True
        self.generation_id += 1
        generation_id = self.generation_id

        if self.on_generation_state_change:
            self.on_generation_state_change(True)

        if self.on_patch_preview:
            self.on_patch_preview([])

        if self.on_status_change:
            self.on_status_change("Thinking...")

        self._append_message(
            "You",
            message
        )

        if self.active_chat is not None:
            self.active_chat.messages.append(
                Message(
                    role="user",
                    content=message
                )
            )

        if (
                self.active_chat is not None
                and self.chat_history_storage is not None
                and self.chat_history_manager is not None
        ):
            self.chat_history_storage.save(
                self.chat_history_manager.get_all_chats()
            )

        self.message_entry.delete(
            0,
            "end"
        )

        generation_agent = self.agent
        generation_chat = self.active_chat

        thread = threading.Thread(
            target=self._generate_response,
            args=(
                message,
                generation_id,
                generation_agent,
                generation_chat
            ),
            daemon=True
        )

        thread.start()

    def list_files(self):
        return self.agent.list_files()

    def read_file(self, file_path):
        return self.agent.read_file(file_path)

    def search_code(self, query):
        return self.agent.search_code(query)

    def apply_pending_modifications(self):
        modifications = self.agent.get_pending_modifications()

        if modifications is None:
            raise ValueError(
                "No pending modifications to apply."
            )

        results = self.agent.apply_modifications(
            modifications
        )

        failed_results = [
            result
            for result in results
            if result.is_failure
        ]

        if failed_results:
            error_messages = "\n".join(
                f"{result.file_path}: {result.message}"
                for result in failed_results
            )

            if self.on_status_change:
                self.on_status_change(
                    f"Apply failed:\n{error_messages}"
                )

        self.agent.pending_modifications = None

        return results

    def reject_pending_modifications(self):
        self.agent.pending_modifications = None

    def _update_patch_preview(self):
        if self.on_patch_preview is None:
            print("[CHAT] Patch preview callback is not configured.")
            return

        previews = self.agent.get_patch_previews()

        print(
            f"[CHAT] Patch previews received: {len(previews)}"
        )

        for preview in previews:
            print(
                f"[CHAT] Preview: "
                f"{preview.file_path} | "
                f"{preview.modification_type} | "
                f"content_length={len(preview.patch_content)}"
            )

        self.after(
            0,
            self.on_patch_preview,
            previews
        )

    def _generate_response(
            self,
            message,
            generation_id,
            generation_agent,
            generation_chat
    ):
        try:
            if message == "/list":
                result = generation_agent.list_files()
                response = self._format_tool_result(result)

            elif message.startswith("/read "):
                file_path = message[6:].strip()

                if not file_path:
                    response = "Usage: /read <file_path>"
                else:
                    result = generation_agent.read_file(file_path)
                    response = self._format_tool_result(result)

            elif message.startswith("/search "):
                query = message[8:].strip()

                if not query:
                    response = "Usage: /search <query>"
                else:
                    result = generation_agent.search_code(query)
                    response = self._format_tool_result(result)

            else:
                response = generation_agent.run_tool_loop(message)

            if generation_id != self.generation_id:
                return

            self.after(
                0,
                self._update_patch_preview_for_generation,
                generation_agent
            )

            self.after(
                0,
                self._handle_response,
                response,
                generation_chat
            )

        except Exception as error:

            error_traceback = traceback.format_exc()

            self.after(

                0,

                self._handle_error,

                error,

                error_traceback

            )

    def _update_patch_preview_for_generation(self, generation_agent):
        if self.on_patch_preview is None:
            print("[CHAT] Patch preview callback is not configured.")
            return

        previews = generation_agent.get_patch_previews()

        for preview in previews:
            print(
                f"[CHAT] Preview: "
                f"{preview.file_path} | "
                f"{preview.modification_type} | "
                f"content_length={len(preview.patch_content)}"
            )

        self.on_patch_preview(previews)

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

    def _handle_response(self, response, generation_chat):
        if generation_chat is not None:
            generation_chat.messages.append(
                Message(
                    role="assistant",
                    content=response
                )
            )

        if (
                generation_chat is not None
                and self.chat_history_storage is not None
                and self.chat_history_manager is not None
        ):
            self.chat_history_storage.save(
                self.chat_history_manager.get_all_chats()
            )

        if generation_chat is self.active_chat:
            self._append_message(
                "AI",
                response
            )

        self.is_generating = False

        if self.on_generation_state_change:
            self.on_generation_state_change(False)

        if self.on_status_change:
            self.on_status_change("Ready")

    def _handle_error(self, error, error_traceback):
        print("[CHAT] ERROR TRACEBACK:")
        print(error_traceback)

        self._append_message(
            "Error",
            str(error)
        )

        self.is_generating = False

        if self.on_patch_preview:
            self.on_patch_preview([])

        if self.on_generation_state_change:
            self.on_generation_state_change(False)

        if self.on_status_change:
            self.on_status_change(
                f"Error: {error}"
            )

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
