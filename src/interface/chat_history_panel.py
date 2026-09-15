import customtkinter as ctk
from tkinter import messagebox, simpledialog

from .theme import Theme


class ChatHistoryPanel(ctk.CTkFrame):
    def __init__(self, master, on_chat_select=None):
        super().__init__(
            master,
            fg_color=Theme.EXPLORER_BACKGROUND,
            corner_radius=0
        )

        self.on_chat_select = on_chat_select
        self._chat_buttons = {}

        self._create_widgets()

    def _create_widgets(self):
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(
            self,
            text="Chat History",
            anchor="w",
            text_color=Theme.TEXT,
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.title_label.grid(
            row=0,
            column=0,
            padx=12,
            pady=(12, 8),
            sticky="ew"
        )

        self.new_chat_button = ctk.CTkButton(
            self,
            text="+ New Chat",
            height=34,
            corner_radius=6,
            command=self._create_new_chat
        )
        self.new_chat_button.grid(
            row=1,
            column=0,
            padx=12,
            pady=(0, 8),
            sticky="ew"
        )

        self.chat_list = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )
        self.chat_list.grid(
            row=2,
            column=0,
            padx=6,
            pady=(0, 6),
            sticky="nsew"
        )

    def _create_new_chat(self):
        if self.on_chat_select is not None:
            self.on_chat_select("__new_chat__")

    def set_chats(self, chats):
        for widget in self.chat_list.winfo_children():
            widget.destroy()

        self._chat_buttons.clear()

        for chat in chats:
            self._add_chat_button(chat)

    def _add_chat_button(self, chat):
        button = ctk.CTkButton(
            self.chat_list,
            text=chat.name,
            anchor="w",
            fg_color="transparent",
            hover_color=Theme.BORDER,
            text_color=Theme.TEXT,
            corner_radius=6,
            height=36,
            command=lambda chat_id=chat.id: self._select_chat(chat_id)
        )

        button.pack(
            fill="x",
            padx=4,
            pady=2
        )

        button.bind(
            "<Button-3>",
            lambda event, chat_id=chat.id: self._show_context_menu(
                event,
                chat_id
            )
        )

        self._chat_buttons[chat.id] = button

    def _show_context_menu(self, event, chat_id):
        menu = ctk.CTkToplevel(self)
        menu.title("Chat")
        menu.geometry(
            f"180x90+{event.x_root}+{event.y_root}"
        )
        menu.resizable(False, False)

        rename_button = ctk.CTkButton(
            menu,
            text="Rename Chat",
            height=32,
            command=lambda: self._rename_chat(
                menu,
                chat_id
            )
        )
        rename_button.pack(
            fill="x",
            padx=8,
            pady=(8, 4)
        )

        delete_button = ctk.CTkButton(
            menu,
            text="Delete Chat",
            height=32,
            command=lambda: self._delete_chat(
                menu,
                chat_id
            )
        )
        delete_button.pack(
            fill="x",
            padx=8,
            pady=(4, 8)
        )

    def _rename_chat(self, menu, chat_id):
        menu.destroy()

        if self.on_chat_select is None:
            return

        new_name = simpledialog.askstring(
            "Rename Chat",
            "Enter new chat name:"
        )

        if new_name is None:
            return

        self.on_chat_select(
            chat_id,
            new_name
        )

    def _delete_chat(self, menu, chat_id):
        menu.destroy()

        if self.on_chat_select is None:
            return

        confirmed = messagebox.askyesno(
            "Delete Chat",
            "Are you sure you want to delete this chat?"
        )

        if not confirmed:
            return

        self.on_chat_select(
            chat_id,
            "__delete_chat__"
        )

    def _select_chat(self, chat_id):
        if self.on_chat_select is not None:
            self.on_chat_select(chat_id)
