from .modification import Modification


class ModificationCollection:
    def __init__(self, modifications=None):
        self._modifications = []

        if modifications is not None:
            for modification in modifications:
                self.add(modification)

    def add(self, modification):
        if not isinstance(modification, Modification):
            raise TypeError("Only Modification objects can be added.")

        for existing in self._modifications:
            if existing.file_path == modification.file_path:
                raise ValueError(
                    f"Modification for file already exists: "
                    f"{modification.file_path}"
                )

        self._modifications.append(modification)

    def remove(self, modification):
        self._modifications.remove(modification)

    def clear(self):
        self._modifications.clear()

    def get_all(self):
        return self._modifications.copy()

    def get_by_file(self, file_path):
        for modification in self._modifications:
            if modification.file_path == file_path:
                return modification

            return None

    def __len__(self):
        return len(self._modifications)

    @property
    def is_empty(self):
        return len(self._modifications) == 0
