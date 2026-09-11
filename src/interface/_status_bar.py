import customtkinter as ctk

from .theme import Theme


class StatusBar(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(
            master,
            height=30,
            corner_radius=0,
            fg_color=Theme.STATUS_BACKGROUND
        )

        self._create_widgets()

    def _create_widgets(self):
        self.status_label = ctk.CTkLabel(
            self,
            text="Ready",
            anchor="w",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(
            side="left",
            padx=12,
            pady=4
        )

    def set_status(self, status):
        self.status_label.configure(
            text=status
        )
