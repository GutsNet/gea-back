"""
Custom exception handler for DRF.

Formato de respuesta consistente para todos los errores de la API.
"""

from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    Wraps DRF's default exception handler to return a consistent error format:

    {
        "error": true,
        "message": "...",
        "details": { ... }  // optional
    }
    """
    response = exception_handler(exc, context)

    if response is not None:
        custom_data = {
            "error": True,
            "message": _get_error_message(response),
        }

        # Include field-level errors as details
        if isinstance(response.data, dict) and any(
            key not in ("detail", "non_field_errors") for key in response.data
        ):
            custom_data["details"] = response.data
        elif isinstance(response.data, list):
            custom_data["details"] = response.data

        response.data = custom_data

    return response


def _get_error_message(response):
    """Extract a human-readable message from the DRF response."""
    data = response.data

    if isinstance(data, dict):
        if "detail" in data:
            return str(data["detail"])
        if "non_field_errors" in data:
            errors = data["non_field_errors"]
            return str(errors[0]) if errors else "Error de validación."
    elif isinstance(data, list) and data:
        return str(data[0])

    return "Error de validación."
