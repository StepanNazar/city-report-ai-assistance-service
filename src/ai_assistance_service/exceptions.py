from uuid import UUID


class PromptNotFoundError(Exception):
    def __init__(self, locality_id: UUID) -> None:
        super().__init__(f"Prompt not found for locality {locality_id}")
        self.locality_id = locality_id


class PromptAlreadyExistsError(Exception):
    def __init__(self, locality_id: UUID) -> None:
        super().__init__(f"Prompt already exists for locality {locality_id}")
        self.locality_id = locality_id


class SuggestionNotFoundError(Exception):
    def __init__(self, suggestion_id: UUID) -> None:
        super().__init__(f"Prompt suggestion not found {suggestion_id}")
        self.suggestion_id = suggestion_id


class PromptInjectionError(Exception):
    def __init__(self, ai_request_id: UUID) -> None:
        super().__init__(f"Prompt injection detected for request {ai_request_id}")
        self.ai_request_id = ai_request_id
