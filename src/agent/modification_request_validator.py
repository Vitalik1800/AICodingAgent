from .modification import Modification


class ModificationRequestValidator:
    VALID_OPERATIONS = {"create", "update", "delete"}

    def validate(self, user_message, modifications):
        if not isinstance(user_message, str):
            raise TypeError("User message must be a string.")

        if not hasattr(modifications, "get_all"):
            raise TypeError("Modifications must provide get_all().")

        modification_items = modifications.get_all()

        if not isinstance(modification_items, list):
            raise TypeError("Modifications get_all() must return a list.")

        requested_operation = self._detect_requested_operation(
            user_message
        )

        if requested_operation is None:
            return True

        for modification in modification_items:
            if not isinstance(modification, Modification):
                raise TypeError(
                    "All items must be Modification objects."
                )

            if modification.modification_type != requested_operation:
                raise ValueError(
                    "Modification operation does not match the "
                    f"user request. Expected '{requested_operation}', "
                    f"got '{modification.modification_type}'."
                )

        return True

    def _detect_requested_operation(self, user_message):
        message = user_message.lower().strip()

        delete_phrases = (
            "видали",
            "видалити",
            "видаляй",
            "видалення",
            "delete",
            "remove"
        )

        create_phrases = (
            "створи",
            "створити",
            "створюй",
            "створення",
            "create"
        )

        update_phrases = (
            "зміни",
            "змінити",
            "змінюй",
            "онови",
            "оновити",
            "update",
            "modify"
        )

        if any(phrase in message for phrase in delete_phrases):
            return "delete"

        if any(phrase in message for phrase in create_phrases):
            return "create"

        if any(phrase in message for phrase in update_phrases):
            return "update"

        return None
