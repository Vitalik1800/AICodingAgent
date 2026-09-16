
import customtkinter as ctk

from src.core.patch_preview import PatchPreview
from .theme import Theme


class PatchPreviewPanel(ctk.CTkFrame):
    def __init__(self, master, on_apply=None, on_reject=None):
        super().__init__(
            master,
            fg_color=Theme.EXPLORER_BACKGROUND,
            corner_radius=0
        )

        self.on_apply = on_apply
        self.on_reject = on_reject
        self.has_preview = False
        self.is_busy = False

        self._create_widgets()

    def _create_widgets(self):
        self.grid_rowconfigure(3, weight=1)
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
            pady=(12, 4),
            sticky="ew"
        )

        self.file_label = ctk.CTkLabel(
            self,
            text="File: —",
            anchor="w",
            text_color=Theme.TEXT
        )

        self.file_label.grid(
            row=1,
            column=0,
            padx=12,
            pady=(0, 2),
            sticky="ew"
        )

        self.type_label = ctk.CTkLabel(
            self,
            text="Type: —",
            anchor="w",
            text_color=Theme.TEXT
        )

        self.type_label.grid(
            row=2,
            column=0,
            padx=12,
            pady=(0, 8),
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
            row=3,
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
            row=4,
            column=0,
            padx=12,
            pady=(0, 12),
            sticky="ew"
        )

        self.reject_button = ctk.CTkButton(
            self,
            text="Reject Changes",
            height=36,
            corner_radius=6,
            command=self._reject_changes
        )

        self.reject_button.grid(
            row=5,
            column=0,
            padx=12,
            pady=(0, 12),
            sticky="ew"
        )

        self.clear()

    def _apply_changes(self):
        if self.on_apply is not None:
            self.on_apply()

    def _reject_changes(self):
        if self.on_reject is not None:
            self.on_reject()

    def _format_preview(self, preview):
        sections = [
            f"File: {preview.file_path.as_posix()}",
            f"Type: {preview.modification_type}",
            "",
            "=" * 60,
            "OLD CODE",
            "=" * 60,
            preview.original_content,
            "",
            "=" * 60,
            "NEW CODE",
            "=" * 60,
            preview.new_content
        ]

        return "\n".join(sections)

    def show_preview(self, preview):
        if not isinstance(preview, PatchPreview):
            raise TypeError(
                "Only PatchPreview objects can be displayed."
            )

        self.file_label.configure(
            text=f"File: {preview.file_path.as_posix()}"
        )

        self.type_label.configure(
            text=f"Type: {preview.modification_type}"
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
            self._format_preview(preview)
        )

        self.preview_text.configure(
            state="disabled"
        )

        self.has_preview = Theme
        self._update_button_states()

    def show_previews(self, previews):
        previews = list(previews)

        for preview in previews:
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

        if previews:
            self.file_label.configure(
                text=f"Files: {len(previews)}"
            )

            self.type_label.configure(
                text="Type: Multiple modifications"
            )
        else:
            self.file_label.configure(
                text="File: —"
            )

            self.type_label.configure(
                text="Type: —"
            )

        for index, preview in enumerate(previews):
            if index > 0:
                self.preview_text.insert(
                    "end",
                    "\n\n"
                )

            self.preview_text.insert(
                "end",
                self._format_preview(preview)
            )

        self.preview_text.configure(
            state="disabled"
        )

        self.has_preview = bool(previews)
        self._update_button_states()

    def set_busy(self, is_busy):
        self.is_busy = is_busy
        self._update_button_states()

    def _update_button_states(self):
        if self.is_busy:
            state = "disabled"
        elif self.has_preview:
            state = "normal"
        else:
            state = "disabled"

        self.apply_button.configure(
            state=state
        )

        self.reject_button.configure(
            state=state
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

        self.file_label.configure(
            text="File: —"
        )

        self.type_label.configure(
            text="Type: —"
        )

        self.has_preview = False
        self._update_button_states()
