from pathlib import Path
from backend.core.settings import Settings

settings: Settings = Settings()
ARTICLES_DIR: Path = Path(settings.ARTICLE_DIR)


class FileService:
    def save_markdown(self, slug: str, content: str) -> str:
        ARTICLES_DIR.mkdir(parents=True, exist_ok=True)

        file_path = ARTICLES_DIR / f"{slug}.md"

        with open(file_path, "w") as f:
            f.write(content)

        return str(file_path)

    def get_article_path(self, article_slug: str) -> Path:
        exact_path = ARTICLES_DIR / f"{article_slug}.md"
        if exact_path.exists():
            return exact_path

        candidates = list(ARTICLES_DIR.glob(f"*{article_slug}*.md"))
        if not candidates:
            raise FileNotFoundError(f"Article not found for slug: {article_slug}")
        return candidates[0]

    def get_article_slug(self, article_path: str | Path) -> str:
        article_slug: str = Path(article_path).stem
        return article_slug
