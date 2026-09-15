import customtkinter as ctk
from tkinter import filedialog
from pathlib import Path

from ..agent.chat_history_manager import ChatHistoryManager
from ..agent.chat_history_storage import ChatHistoryStorage
from .chat import Chat
from .chat_history_panel import ChatHistoryPanel
from .project_explorer import ProjectExplorer
from .patch_preview_panel import PatchPreviewPanel
from ._status_bar import StatusBar


class App:
    def __init__(self):
        self.root = ctk.CTk()

        self.root.title("AI Coding Agent")
        self.root.geometry("1500x700")
        self.root.minsize(1200, 500)

        self.project_path = None
        self.active_chat_id = None

        self.chat_history_manager = ChatHistoryManager()
        self.chat_history_storage = ChatHistoryStorage()

        self._configure_appearance()
        self._configure_fonts()
        self._create_layout()
        self._load_chat_history()

    def _configure_appearance(self):
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

    def _configure_fonts(self):
        self.title_font = ctk.CTkFont(
            size=16,
            weight="bold"
        )

        self.body_font = ctk.CTkFont(
            size=13
        )

        self.small_font = ctk.CTkFont(
            size=12
        )

    def _create_layout(self):
        self.root.grid_columnconfigure(
            0,
            weight=0,
            minsize=220
        )

        self.root.grid_columnconfigure(
            1,
            weight=0,
            minsize=220
        )

        self.root.grid_columnconfigure(
            2,
            weight=1,
            minsize=500
        )

        self.root.grid_columnconfigure(
            3,
            weight=1,
            minsize=400
        )

        self.root.grid_rowconfigure(
            0,
            weight=1
        )

        self.root.grid_rowconfigure(
            1,
            weight=0
        )

        self.chat_history_panel = ChatHistoryPanel(
            self.root,
            on_chat_select=self._select_chat
        )

        self.chat_history_panel.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        self.project_explorer = ProjectExplorer(
            self.root,
            on_project_select=self._select_project
        )

        self.project_explorer.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

        self.chat = Chat(
            self.root,
            on_status_change=self._handle_status_change,
            on_patch_preview=self._handle_patch_preview,
            project_path=".",
            chat_history_storage=self.chat_history_storage,
            chat_history_manager=self.chat_history_manager
        )

        self.chat.grid(
            row=0,
            column=2,
            sticky="nsew"
        )

        self.patch_preview_panel = PatchPreviewPanel(
            self.root,
            on_apply=self._apply_patch_changes
        )

        self.patch_preview_panel.grid(
            row=0,
            column=3,
            sticky="nsew"
        )

        self.status_bar = StatusBar(
            self.root
        )

        self.status_bar.grid(
            row=1,
            column=0,
            columnspan=4,
            sticky="ew"
        )

    def _load_chat_history(self):
        try:
            chats = self.chat_history_storage.load()

        except ValueError as error:
            self.chat_history_panel.set_chats([])

            self._handle_status_change(
                f"Chat history error: {error}"
            )

            return

        except OSError as error:
            self.chat_history_panel.set_chats([])

            self._handle_status_change(
                f"Unable to load chat history: {error}"
            )

            return

        for chat in chats:
            self.chat_history_manager._chats[chat.id] = chat

        self.chat_history_panel.set_chats(
            self.chat_history_manager.get_all_chats()
        )

        if not chats:
            return

        chat = chats[0]

        self.active_chat_id = chat.id
        self.chat.set_active_chat(chat)

        if chat.project_path is not None:
            project_path = Path(chat.project_path)

            if project_path.exists() and project_path.is_dir():
                self.project_path = str(project_path)

                self.project_explorer.set_project_path(
                    self.project_path
                )

                self.chat.set_project_path(
                    self.project_path
                )
            else:
                self.project_path = None

        self.chat.load_chat_history(chat)

        self._handle_status_change(
            f"Chat restored: {chat.name}"
        )

    def _select_chat(self, chat_id, new_name=None):
        if new_name == "__delete_chat__":
            chat = self.chat_history_manager.get_chat(chat_id)

            if chat is None:
                return

            was_active = self.chat.active_chat is chat

            self.chat_history_manager.delete_chat(chat_id)

            self.chat_history_storage.save(
                self.chat_history_manager.get_all_chats()
            )

            self.chat_history_panel.set_chats(
                self.chat_history_manager.get_all_chats()
            )

            if was_active:
                self.chat.active_chat = None
                self.chat.agent.clear_conversation()

                self.chat.chat_history.configure(
                    state="normal"
                )
                self.chat.chat_history.delete(
                    "1.0",
                    "end"
                )
                self.chat.chat_history.configure(
                    state="disabled"
                )

                if not self.chat.is_generating:
                    self._handle_status_change(
                        "Chat deleted"
                    )
            else:
                if not self.chat.is_generating:
                    self._handle_status_change(
                        "Chat deleted"
                    )

            return

        if new_name is not None:
            chat = self.chat_history_manager.rename_chat(
                chat_id,
                new_name
            )

            self.chat_history_storage.save(
                self.chat_history_manager.get_all_chats()
            )

            self.chat_history_panel.set_chats(
                self.chat_history_manager.get_all_chats()
            )

            if not self.chat.is_generating:
                self._handle_status_change(
                    f"Chat renamed: {chat.name}"
                )

            return

        if chat_id == "__new_chat__":
            chat = self.chat_history_manager.create_chat(
                name="New Chat",
                project_path=self.project_path
            )

            self.chat_history_storage.save(
                self.chat_history_manager.get_all_chats()
            )

            self.chat_history_panel.set_chats(
                self.chat_history_manager.get_all_chats()
            )

            self.active_chat_id = chat.id

            if chat.project_path is not None:
                self.project_path = str(chat.project_path)

                self.project_explorer.set_project_path(
                    self.project_path
                )

                self.chat.set_project_path(
                    self.project_path
                )

            self.chat.load_chat_history(chat)

            self._handle_status_change(
                f"New chat selected: {chat.name}"
            )
            return

        chat = self.chat_history_manager.get_chat(chat_id)

        if chat is None:
            self._handle_status_change(
                f"Chat not found: {chat_id}"
            )
            return

        self.active_chat_id = chat.id

        self.chat.load_chat_history(chat)

        self._handle_status_change(
            f"Chat selected: {chat.name}"
        )

    def _select_project(self):
        selected_path = filedialog.askdirectory(
            title="Select Project"
        )

        if not selected_path:
            return

        self.project_path = selected_path

        self.project_explorer.set_project_path(
            selected_path
        )

        self.chat.set_project_path(
            selected_path
        )

        if not self.chat.is_generating:
            self._handle_status_change(
                f"Project selected: {selected_path}"
            )

    def _handle_status_change(self, status):
        self.status_bar.set_status(status)

    def _handle_patch_preview(self, previews):
        if not previews:
            self.patch_preview_panel.clear()
            return

        self.patch_preview_panel.show_previews(
            previews
        )

    def _apply_patch_changes(self):
        try:
            results = self.chat.apply_pending_modifications()

            success_count = sum(
                1
                for result in results
                if result.is_success
            )

            failed_results = [
                result
                for result in results
                if result.is_failure
            ]

            self.patch_preview_panel.clear()

            if failed_results:
                error_lines = []

                for result in failed_results:
                    try:
                        relative_path = result.file_path.relative_to(
                            self.chat.agent.apply_patch_service.safety.project_root
                        )
                        relative_path = relative_path.as_posix()
                    except ValueError:
                        relative_path = result.file_path.as_posix()

                    error_lines.append(
                        f"• {relative_path}\n"
                        f"  {result.message}"
                    )

                self._handle_status_change(
                    f"Changes applied: {success_count}/{len(results)}\n\n"
                    "Failed:\n"
                    + "\n".join(error_lines)
                )
            else:
                self._handle_status_change(
                    f"Changes applied: {success_count}/{len(results)}"
                )

        except Exception as error:
            self._handle_status_change(
                f"Apply error: {error}"
            )

    def run(self):
        self.root.mainloop()
