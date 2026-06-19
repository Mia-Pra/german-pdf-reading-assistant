from fastapi import HTTPException, status

from app.ai_client import AIConfigurationError, AIProviderError, AIResponseError


def ai_error_to_http_exception(error: Exception) -> HTTPException:
    if isinstance(error, AIConfigurationError):
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        )

    if isinstance(error, AIProviderError):
        return HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(error),
        )

    if isinstance(error, AIResponseError):
        return HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(error),
        )

    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Unexpected AI client error.",
    )
