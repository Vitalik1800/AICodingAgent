from difflib import unified_diff

from .modification import Modification
from .modification_collection import ModificationCollection
from .patch import Patch


class PatchGenerator:
    def generate(self, modification):
        if not isinstance(modification, Modification):
            raise TypeError("Only Modification objects can be converted to patches.")

        original_lines = modification.original_content.splitlines(keepends=True)
        new_lines = modification.new_content.splitlines(keepends=True)

        file_path = modification.file_path.as_posix()

        if modification.modification_type == "create":
            from_file = "/dev/null"
            to_file = f"b/{file_path}"
        elif modification.modification_type == "delete":
            from_file = f"a/{file_path}"
            to_file = "/dev/null"
        else:
            from_file = f"a/{file_path}"
            to_file = f"b/{file_path}"

        diff = unified_diff(
            original_lines,
            new_lines,
            fromfile=from_file,
            tofile=to_file,
            lineterm="\n"
        )

        return Patch(
            file_path=modification.file_path,
            content="".join(diff),
            modification_type=modification.modification_type
        )

    def generate_combined(self, modifications):
        patches = self.generate_all(modifications)
        return "\n".join(
            patch.content.rstrip("\n")
            for patch in patches
            if not patch.is_empty
        )

    def generate_all(self, modifications):

        if not isinstance(modifications, ModificationCollection):
            raise TypeError("Only ModificationCollection can be converted to patches.")

        return [
            self.generate(modification)
            for modification in modifications.get_all()
        ]
