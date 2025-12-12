from core.logger import logger
from core.settings import settings
from backend.exceptions.exceptions import GenerateException
from requests.exceptions import Timeout
from backend.zenn.zenn_article_schemas import GeneratedResponse, GenerateRequest
from backend.zenn.zenn_service import ZennService


class GenerateService:
    def __init__(self) -> None:
        self._settings = settings
        self._zenn_srevice: ZennService = ZennService()

    def generate_article(self, article_info: GenerateRequest) -> GeneratedResponse:
        """
        Docstring for generate_article

        :param req: Description
        :type req: GenerateRequest
        :return: Description
        :rtype: GeneratedResponse
        """
        try:
            logger.info(msg=f"Generating article with theme: {article_info.title}")
            article_response: GeneratedResponse = self._zenn_srevice.generate_article(
                article_info=article_info
            )
            logger.info(msg="Article generation request completed")
            logger.info(msg=f"Response slag: {article_response.slug}")

        except Timeout:
            logger.error(msg="Request to Kenn_Zenn API timed out at /generate endpoint")
            raise GenerateException(
                message="timeout error",
                endpoint="/generate",
            )
        except ValueError:
            raise GenerateException(
                message="value error",
                endpoint="/generate",
            )

        generate_article: GeneratedResponse = GeneratedResponse(
            status=article_response.status, slug=article_response.slug
        )

        logger.info(
            f"Article generated successfully."
            f"slug: {generate_article.slug},"
            f"status: {generate_article.status}"
        )

        return generate_article
