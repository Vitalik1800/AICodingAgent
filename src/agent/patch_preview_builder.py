from .patch import Patch
from .patch_preview import PatchPreview


class PatchPreviewBuilder:
    def build(self, patch):
        if not isinstance(patch, Patch):
            raise TypeError(
                "Only Patch objects can be converted to patch previews."
            )

        return PatchPreview(
            file_path=patch.file_path,
            patch_content=patch.content,
            modification_type=patch.modification_type
        )

    def build_all(self, patches):
        previews = []

        for patch in patches:
            previews.append(self.build(patch))

        return previews
