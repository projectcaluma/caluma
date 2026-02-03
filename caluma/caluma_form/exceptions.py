from rest_framework import exceptions

FORMAT_VALIDATION_FAILED = "format_validation_failed"


class CustomValidationError(exceptions.ValidationError):
    """Custom validation error to carry more information.

    This can carry more information about the error, so the documentValidity
    query can show more useful information.
    """

    def __init__(self, detail, code=None, slugs=None, document_id=None):
        super().__init__(detail, code)

        self.slugs = slugs if slugs else []
        self.document_id = str(document_id) if document_id else None


class CustomFormatValidationError(CustomValidationError):
    default_code = FORMAT_VALIDATION_FAILED
