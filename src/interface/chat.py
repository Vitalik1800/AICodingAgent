import threading

import customtkinter as ctk

from .theme import Theme
from ..ai.ollama_client import OllamaClient


class Chat(ctk.CTkFrame):
    def __init__(self, master, on_status_change=None):
        super().__init__(
            master,
            corner_radius=0,
            fg_color=Theme.BACKGROUND
        )

        self.on_status_change = on_status_change
        self.ollama_client = OllamaClient()

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

    def _send_message(self):
        message = self.message_entry.get().strip()

        if not message:
            return

        if self.on_status_change:
            self.on_status_change("Thinking...")

        self._append_message("You", message)
        self.message_entry.delete(0, "end")

        thread = threading.Thread(
            target=self._generate_response,
            args=(message, ),
            daemon=True
        )

        thread.start()

    def _generate_response(self, message):
        try:
            response = self.ollama_client.generate(message)

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
