from backend.exceptions.exceptions import PublishException
from fastapi import APIRouter, HTTPException
from backend.zenn.zenn_article_schemas import PublishRequest, PublishResponse
from backend.zenn.publish_service import PublishService

router = APIRouter(prefix="/publish", tags=["Publish"])
publisher: PublishService = PublishService()


@router.post("/")
def publish(req: PublishRequest) -> PublishResponse:
    """
    Publish an article to Kenn_Zenn service

    :param req: Publish request containing slug to publish
    :type req: PublishRequest
    :return: {"status": ["published!" or "failed"], "slug": str}
    :rtype: PublishResponse
    :raises HTTPException: If the Kenn_Zenn API request fails
    """

    try:
        publish_response: PublishResponse = publisher.publish_article(req=req)
        return publish_response
    except PublishException as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail={
                "error": "Kenn_Zenn API Error",
                "message": e.message,
                "endpoint": e.endpoint,
            },
        ) from e
