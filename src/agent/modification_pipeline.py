from .modification import Modification
from .modification_safety import ModificationSafety
from .modification_parser import ModificationParser
from .patch_generator import PatchGenerator
from .patch_validator import PatchValidator
from .patch_preview_builder import PatchPreviewBuilder


class ModificationPipeline:
    def __init__(self, project_root=None):
        self.safety = ModificationSafety(project_root)
        self.generator = PatchGenerator()
        self.validator = PatchValidator(project_root)
        self.preview_builder = PatchPreviewBuilder()

    def process(self, modification):
        if not isinstance(modification, Modification):
            raise TypeError(
                "Only Modification objects can be processed."
            )

        self.safety.validate(modification)

        patch = self.generator.generate(modification)

        self.validator.validate(patch)

        return patch

    def process_preview(self, modification):
        patch = self.process(modification)
        return self.preview_builder.build(patch)

    def process_content(self, content):

        parser = ModificationParser(self.safety.project_root)

        modifications = parser.parse(content)

        return self.process_all(modifications)

    def process_all(self, modifications):
        results = []

        for modification in modifications.get_all():
            results.append(self.process(modification))

        return results

    def process_previews(self, modifications):
        patches = self.process_all(modifications)
        return self.preview_builder.build_all(patches)
