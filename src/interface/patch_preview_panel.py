import customtkinter as ctk

from ..agent.patch_preview import PatchPreview
from .theme import Theme


class PatchPreviewPanel(ctk.CTkFrame):
    def __init__(self, master, on_apply=None):
        super().__init__(
            master,
            fg_color=Theme.EXPLORER_BACKGROUND,
            corner_radius=0
        )

        self.on_apply = on_apply

        self._create_widgets()

    def _create_widgets(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(
            self,
            text="Patch Preview",
            anchor="w",
            text_color=Theme.TEXT,
            font=ctk.CTkFont(
                size=15,
                weight="bold"
            )
        )

        self.title_label.grid(
            row=0,
            column=0,
            padx=12,
            pady=(12, 8),
            sticky="ew"
        )

        self.preview_text = ctk.CTkTextbox(
            self,
            wrap="none",
            fg_color=Theme.INPUT_BACKGROUND,
            text_color=Theme.TEXT,
            border_width=1,
            border_color=Theme.BORDER
        )

        self.preview_text.grid(
            row=1,
            column=0,
            padx=12,
            pady=(0, 12),
            sticky="nsew"
        )

        self.apply_button = ctk.CTkButton(
            self,
            text="Apply Changes",
            height=36,
            corner_radius=6,
            command=self._apply_changes
        )

        self.apply_button.grid(
            row=2,
            column=0,
            padx=12,
            pady=(0, 12),
            sticky="ew"
        )

        self.clear()

    def _apply_changes(self):
        if self.on_apply is not None:
            self.on_apply()

    def show_preview(self, preview):
        if not isinstance(preview, PatchPreview):
            raise TypeError(
                "Only PatchPreview objects can be displayed."
            )

        self.preview_text.configure(
            state="normal"
        )

        self.preview_text.delete(
            "1.0",
            "end"
        )

        self.preview_text.insert(
            "1.0",
            preview.patch_content
        )

        self.preview_text.configure(
            state="disabled"
        )

        self.apply_button.configure(
            state="normal"
        )

    def show_previews(self, previews):
        self.preview_text.configure(
            state="normal"
        )

        self.preview_text.delete(
            "1.0",
            "end"
        )

        for index, preview in enumerate(previews):
            if not isinstance(preview, PatchPreview):
                raise TypeError(
                    "Only PatchPreview objects can be displayed."
                )

            if index > 0:
                self.preview_text.insert(
                    "end",
                    "\n\n"
                )

            self.preview_text.insert(
                "end",
                f"File: {preview.file_path.as_posix()}\n"
            )

            self.preview_text.insert(
                "end",
                f"Type: {preview.modification_type}\n\n"
            )

            self.preview_text.insert(
                "end",
                preview.patch_content
            )

        self.preview_text.configure(
            state="disabled"
        )

        self.apply_button.configure(
            state="normal" if previews else "disabled"
        )

    def clear(self):
        self.preview_text.configure(
            state="normal"
        )

        self.preview_text.delete(
            "1.0",
            "end"
        )

        self.preview_text.configure(
            state="disabled"
        )

        self.apply_button.configure(
            state="disabled"
        )
