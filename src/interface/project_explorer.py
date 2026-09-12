from pathlib import Path
from tkinter import ttk

import customtkinter as ctk

from ..tools.project_scanner import ProjectScanner
from .theme import Theme


class ProjectExplorer(ctk.CTkFrame):
    def __init__(self, master, on_project_select=None):
        super().__init__(
            master,
            corner_radius=0,
            fg_color=Theme.EXPLORER_BACKGROUND
        )

        self.on_project_select = on_project_select
        self.project_path = None
        self.project_scanner = None

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

        select_button = ctk.CTkButton(
            self,
            text="Select Project",
            command=self._handle_project_select
        )
        select_button.pack(
            padx=16,
            pady=(0, 10),
            fill="x"
        )

        self.project_label = ctk.CTkLabel(
            self,
            text="No project opened",
            text_color=Theme.SECONDARY_TEXT,
            font=ctk.CTkFont(size=13)
        )
        self.project_label.pack(
            padx=16,
            pady=10,
            anchor="w"
        )

        self.tree_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        self.tree_frame.pack(
            padx=16,
            pady=10,
            fill="both",
            expand=True
        )

        self._create_treeview()

    def _create_treeview(self):
        style = ttk.Style()

        style.configure(
            "ProjectExplorer.Treeview",
            background=Theme.EXPLORER_BACKGROUND,
            foreground=Theme.TEXT,
            fieldbackground=Theme.EXPLORER_BACKGROUND,
            borderwidth=0,
            font=("Segoe UI", 10)
        )

        style.map(
            "ProjectExplorer.Treeview",
            background=[
                ("selected", Theme.ACCENT)
            ],
            foreground=[
                ("selected", Theme.TEXT)
            ]
        )

        self.tree = ttk.Treeview(
            self.tree_frame,
            show="tree",
            style="ProjectExplorer.Treeview"
        )

        self.tree.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.tree_scrollbar = ttk.Scrollbar(
            self.tree_frame,
            orient="vertical",
            command=self.tree.yview
        )

        self.tree_scrollbar.pack(
            side="right",
            fill="y"
        )

        self.tree.configure(
            yscrollcommand=self.tree_scrollbar.set
        )

    def _handle_project_select(self):
        if self.on_project_select is not None:
            self.on_project_select()

    def set_project_path(self, project_path):
        self.project_path = Path(project_path)
        self.project_scanner = ProjectScanner(project_path)

        self.project_label.configure(
            text=self.project_path.name
        )

        self._display_structure()

    def _display_structure(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        if self.project_scanner is None:
            return

        tree_structure = self.project_scanner.get_tree_structure()

        for node in tree_structure:
            self._insert_node(
                parent="",
                node=node
            )

    def _insert_node(self, parent, node):
        prefix = (
            "📁"
            if node.item_type == "directory"
            else "📄"
        )

        tree_item = self.tree.insert(
            parent,
            "end",
            text=f"{prefix} {node.path.name}",
            open=False
        )

        for child in node.children:
            self._insert_node(
                parent=tree_item,
                node=child
            )
