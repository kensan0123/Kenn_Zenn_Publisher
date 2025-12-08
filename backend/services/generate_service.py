import requests
from core.logger import logger
from core.settings import Settings
from exceptions.api_exception import KennZennAPIError
from requests.exceptions import ConnectionError, HTTPError, Timeout
from schemas.generate_schema import GeneratedResponse, GenerateRequest

settings: Settings = Settings()
KENN_ZENN_URL: str = settings.KENN_ZENN_URL


def generate_article(req: GenerateRequest) -> GeneratedResponse:
    """
    Docstring for generate_article

    :param req: Description
    :type req: GenerateRequest
    :return: Description
    :rtype: GeneratedResponse
    """
    try:
        logger.info(f"Generating article with theme: {req.title}")
        response = requests.post(f"{KENN_ZENN_URL}/generate", json=req.model_dump(), timeout=20)
        logger.info("Article generation request completed")
        logger.info(f"Response body: {response.text}")
        response.raise_for_status()
    except Timeout as e:
        logger.error("Request to Kenn_Zenn API timed out at /generate endpoint")
        raise KennZennAPIError("timeout error", endpoint="/generate") from e
    except ConnectionError as e:
        logger.error(
            f"Failed to connect to Kenn_Zenn API at {KENN_ZENN_URL}. Check network connection"
        )
        raise KennZennAPIError("networks error", endpoint="/generate") from e
    except HTTPError as e:
        if 500 <= e.response.status_code < 600:
            logger.error(f"Server error occurred: status_code={e.response.status_code}")
            raise KennZennAPIError(
                "server error", endpoint="/generate", status_code=e.response.status_code
            ) from e
        else:
            logger.error(f"Client error occurred: status_code={e.response.status_code}")
            raise KennZennAPIError(
                "client error", endpoint="/generate", status_code=e.response.status_code
            ) from e
    except requests.exceptions.RequestException as e:
        logger.error(f"Unknown request error occurred: {str(e)}")
        raise KennZennAPIError("unknown error", endpoint="/generate") from e

    try:
        response_json = response.json()
    except ValueError as e:
        logger.error("Invalid JSON response from Kenn_Zenn API")
        raise KennZennAPIError(
            message="Invalid JSON response from Kenn_Zenn API",
            endpoint="/generate",
            status_code=response.status_code,
        ) from e

    generate_response: GeneratedResponse = GeneratedResponse(
        status=response_json.get("status"), slug=response_json.get("slug")
    )

    logger.info(
        f"Article generated successfully."
        f"slug: {generate_response.slug},"
        f"status: {generate_response.status}"
    )

    return generate_response
