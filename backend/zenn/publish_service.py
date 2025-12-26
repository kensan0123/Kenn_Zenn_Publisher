from backend.core.logger import get_logger
from backend.exceptions.exceptions import PublishException
from requests.exceptions import Timeout
from backend.zenn.zenn_article_schemas import PublishRequest, PublishResponse
from backend.zenn.zenn_service import ZennService

logger = get_logger(__name__)


class PublishService:
    def __init__(self):
        self._zenn_srevice: ZennService = ZennService()

    def publish_article(self, req: PublishRequest) -> PublishResponse:
        """
        Publish an article to Zenn service

        :param req: Publish request containing slug
        :type req: PublishRequest
        :return: Publish response with status and slug
        :rtype: PublishResponse
        :raises KennZennAPIError: If API request fails or returns invalid response
        """
        logger.info(f"Publishing article with slug: {req.slug}")

        try:
            article_response: PublishResponse = self._zenn_srevice.publish_article(slug=req.slug)

        except Timeout:
            logger.error(f"Request to Kenn_Zenn API timed out for slug: {req.slug}")
            raise PublishException(
                message="Request to Kenn_Zenn API timed out",
                endpoint="/publish",
            )

        except ValueError:
            logger.error("Invalid JSON response from Kenn_Zenn API")
            raise PublishException(
                message="Invalid JSON response from Kenn_Zenn API",
                endpoint="/publish",
            )

        publish_article: PublishResponse = PublishResponse(
            status=article_response.status, slug=article_response.slug
        )

        logger.info(
            f"Article published successfully."
            f"slug: {publish_article.slug},"
            f"status: {publish_article.status}"
        )

        return publish_article
