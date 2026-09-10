import customtkinter as ctk

from .chat import Chat
from .project_explorer import ProjectExplorer
from ._status_bar import StatusBar


class App:
    def __init__(self):
        self.root = ctk.CTk()

        self.root.title("AI Coding Agent")
        self.root.geometry("1000x650")
        self.root.minsize(800, 500)

        self._configure_appearance()
        self._configure_fonts()
        self._create_layout()

    def _configure_appearance(self):
        ctk.set_appearance_mode("System")
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
            weight=1,
            minsize=500
        )

        self.root.grid_rowconfigure(
            0,
            weight=1
        )
        self.root.grid_rowconfigure(
            1,
            weight=0
        )

        self.project_explorer = ProjectExplorer(self.root)
        self.project_explorer.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        self.chat = Chat(
            self.root,
            on_status_change=self._handle_status_change
        )
        self.chat.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

        self.status_bar = StatusBar(
            self.root
        )
        self.status_bar.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="ew"
        )

    def _handle_status_change(self, status):
        self.status_bar.set_status(status)

    def run(self):
        self.root.mainloop()
