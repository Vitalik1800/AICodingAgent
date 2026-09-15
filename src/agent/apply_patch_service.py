from .apply_result import ApplyResult
from .modification import Modification
from .modification_safety import ModificationSafety
from .patch_applier import PatchApplier


class ApplyPatchService:
    def __init__(self, project_root="."):
        self.safety = ModificationSafety(project_root)
        self.applier = PatchApplier(project_root)

    def _prepare_modification(self, modification):
        if not isinstance(modification, Modification):
            raise TypeError("Only Modification objects can be prepared.")

        if modification.modification_type == "create":
            return modification

        if modification.modification_type not in {"update", "delete"}:
            raise ValueError(
                f"Unsupported modification type: "
                f"{modification.modification_type}"
            )

        if modification.original_content:
            return modification

        file_path = self.applier._resolve_safe_path(
            modification.file_path
        )

        if not file_path.exists():
            raise FileNotFoundError(
                f"File does not exist: {file_path}"
            )

        if not file_path.is_file():
            raise IsADirectoryError(
                f"Path is not a file: {file_path}"
            )

        current_content = file_path.read_text(
            encoding="utf-8"
        )

        return Modification(
            file_path=modification.file_path,
            original_content=current_content,
            new_content=modification.new_content,
            description=modification.description,
            modification_type=modification.modification_type
        )

    def apply(self, modification):
        if not isinstance(modification, Modification):
            raise TypeError(
                "Only Modification objects can be applied."
            )

        try:
            self.safety.validate(modification)

            modification = self._prepare_modification(
                modification
            )

            self.safety.validate(modification)

            if modification.modification_type == "create":
                return self.applier.create_file(
                    modification.file_path,
                    modification.new_content
                )

            if modification.modification_type == "update":
                return self.applier.update_file(
                    modification.file_path,
                    modification.original_content,
                    modification.new_content
                )

            if modification.modification_type == "delete":
                return self.applier.delete_file(
                    modification.file_path,
                    modification.original_content
                )

            raise ValueError(
                f"Unsupported modification type: "
                f"{modification.modification_type}"
            )

        except (
            FileNotFoundError,
            FileExistsError,
            IsADirectoryError,
            PermissionError,
            ValueError
        ) as error:
            return ApplyResult(
                file_path=modification.file_path,
                modification_type=modification.modification_type,
                success=False,
                message=str(error)
            )

    def apply_all(self, modifications):
        if not hasattr(modifications, "get_all"):
            raise TypeError(
                "Modifications must provide get_all()."
            )

        modification_items = modifications.get_all()

        if not isinstance(modification_items, list):
            raise TypeError(
                "Modifications get_all() must return a list."
            )

        results = []

        for modification in modification_items:
            if not isinstance(modification, Modification):
                raise TypeError(
                    "All items must be Modification objects."
                )

            result = self.apply(modification)
            results.append(result)

        return results
