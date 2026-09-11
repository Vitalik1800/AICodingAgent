import customtkinter as ctk

from .theme import Theme


class ProjectExplorer(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(
            master,
            corner_radius=0,
            fg_color=Theme.EXPLORER_BACKGROUND
        )

        self._create_widgets()

    def _create_widgets(self):
        title_label = ctk.CTkLabel(
            self,
            text="Project Explorer",
            font=ctk.CTkFont(
                size=16,
                weight="bold"
            )
        )
        title_label.pack(
            padx=16,
            pady=(16, 10),
            anchor="w"
        )

        placeholder_label = ctk.CTkLabel(
            self,
            text="No project opened",
            text_color="gray",
            font=ctk.CTkFont(size=13)
        )
        placeholder_label.pack(
            padx=16,
            pady=10,
            anchor="w"
        )
