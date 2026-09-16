import ast
import re


class ModificationSemanticValidator:
    def validate(self, modification, requested_function=None):
        if requested_function is None:
            return True

        if not isinstance(requested_function, str):
            raise TypeError(
                "Requested function name must be a string."
            )

        requested_function = requested_function.strip()

        if not requested_function:
            return True

        original_functions = self._get_function_names(
            modification.original_content
        )

        new_functions = self._get_function_names(
            modification.new_content
        )

        if requested_function not in original_functions:
            raise ValueError(
                f"Requested function '{requested_function}' "
                "does not exist in the original content."
            )

        if requested_function not in new_functions:
            raise ValueError(
                f"Requested function '{requested_function}' "
                "is missing from the new content."
            )

        return True

    def _get_function_names(self, content):
        if not isinstance(content, str):
            raise TypeError("Code content must be a string.")

        try:
            tree = ast.parse(content)
        except SyntaxError as error:
            raise ValueError(
                f"Unable to parse Python code: {error}"
            ) from error

        return {
            node.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }

    def validate_all(self, modifications, requested_function=None):
        if not hasattr(modifications, "get_all"):
            raise TypeError(
                "Modifications must provide get_all()."
            )

        for modification in modifications.get_all():
            self.validate(
                modification,
                requested_function=requested_function
            )

        return True

    def extract_requested_function(self, user_message):
        if not isinstance(user_message, str):
            raise TypeError(
                "User message must be a string."
            )

        patterns = [
            r"функці[юї]\s+([A-Za-z_]\w*)",
            r"функцію\s+([A-Za-z_]\w*)",
            r"function\s+([A-Za-z_]\w*)",
        ]

        for pattern in patterns:
            match = re.search(
                pattern,
                user_message,
                re.IGNORECASE
            )

            if match:
                return match.group(1)

        return None
