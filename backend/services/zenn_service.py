import re
import subprocess
from pathlib import Path
from typing import List
from dataclasses import dataclass
from backend.core.settings import Settings
from backend.services.file_service import FileService
from fastapi import HTTPException

settings: Settings = Settings()
ROOT_DIR: Path = Path("./")
ARTICLES_DIR: Path = Path(settings.ARTICLE_DIR)


class GenerateService:
    def __init__(self) -> None:
        self.file_service = FileService()

    def generate_article(
        self, title: str, emoji: str, content: str, type: str, slug: str | None = None
    ):
        """
        Zenn CLIで新規記事を作成し
        自動生成された slug の md ファイルを特定して中身を書き換える
        """

        # CLI実行前ファイル一覧
        before_files = set(ARTICLES_DIR.glob("*.md"))

        # 新規記事作成
        if slug:
            cmd = [
                "npx",
                "zenn",
                "new:article",
                "--slug",
                slug,
                "--title",
                title,
                "--type",
                type,
                "--emoji",
                emoji,
                "--published",
                "false",
            ]
        else:
            cmd = [
                "npx",
                "zenn",
                "new:article",
                "--title",
                title,
                "--type",
                "tech",
                "--emoji",
                emoji,
                "--published",
                "false",
            ]

        subprocess.run(cmd, cwd=str(ROOT_DIR), check=True)

        # CLI実行後ファイル一覧
        after_files = set(ARTICLES_DIR.glob("*.md"))

        # 新しく作られたファイルを特定
        new_files = list(after_files - before_files)
        if not new_files:
            raise FileNotFoundError("Failed to detect created Zenn article markdown file.")

        article_path = new_files[0]  # 1つだけのはずなので確定

        # ファイル内容を読み込み
        with article_path.open("r") as f:
            original = f.read()

        # フロントマター部分（--- ... ---）を抽出
        if original.startswith("---"):
            parts = original.split("---", 2)
            # parts = ["", frontmatter, rest]
            front_matter = f"---{parts[1]}---\n\n"
        else:
            raise ValueError("Frontmatter not found")

        # 本文部分をLLMの内容で上書き
        new_content = front_matter + content.strip() + "\n"

        with article_path.open("w") as f:
            f.write(new_content)

        article_slug: str = self.file_service.get_article_slug(article_path=article_path)

        return article_slug

    def add_topics(
        self, article_slug: str, topic: str
    ) -> str:  # ToDo: topicは複数登録できるのうに改良
        article_path = self.file_service.get_article_path(article_slug=article_slug)

        with Path(article_path).open("r") as f:
            content = f.read()

        if content.startswith("---"):
            parts = content.split("---", 2)
            front_matter = parts[1]
            body = parts[2]

            match = re.search(r"topics:\s*\[(.*?)\]", front_matter)

            if match:
                topic_list_str = match.group(1).strip()

                if topic_list_str:
                    topics: List[str] = [
                        t.strip().strip('"').strip("'") for t in topic_list_str.split(",")
                    ]
                else:
                    topics = []

                if topic not in topics:
                    topics.append(topic)

                new_topic_str = ",".join([f'"{t}"' for t in topics])
                new_front_matter = re.sub(
                    r"topics:\s*\[.*?\]",
                    f"topics: [{new_topic_str}]",
                    front_matter,
                )

                new_content = f"---{new_front_matter}---{body}"

                with Path(article_path).open("w") as f:
                    f.write(new_content)

                slug: str = self.file_service.get_article_slug(article_path=article_path)

                return slug
            else:
                raise ValueError("topics: の行が見つかりません")

        else:
            raise ValueError("front matter が存在しません")


@dataclass
class PublishResult:
    result: bool
    slug: str


class PublishService:
    def __init__(self, root_dir: Path = ROOT_DIR) -> None:
        self.file_service = FileService()
        self.root_dir = root_dir

    def publish_article(self, slug: str) -> PublishResult:
        settings.create_netrc()

        # 対象ファイルを検索
        md_files = list(ARTICLES_DIR.glob(f"*{slug}*.md"))
        if not md_files:
            raise FileNotFoundError(f"記事が見つかりません: slug={slug}")

        article_path = md_files[0]

        # Frontmatter 書き換え
        with open(article_path, "r") as file:
            content = file.read()

        new_content = re.sub(r"published:\s*false", "published: true", content)
        match_title = re.search(r'title:\s*"(.+?)"', content)

        if match_title:
            article_title = match_title.group(1)
        else:
            article_title = "Untitled"

        with open(article_path, "w") as file:
            file.write(new_content)

        article_slug: str = self.file_service.get_article_slug(article_path=article_path)

        # Git 連携
        try:
            subprocess.run(
                ["git", "add", "."],
                cwd=str(self.root_dir),
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "commit", "-m", f"publish {article_title}"],
                cwd=str(self.root_dir),
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "push"], cwd=str(self.root_dir), check=True, capture_output=True, text=True
            )

        except subprocess.CalledProcessError as e:
            if "could not read Username" in e.stderr:
                raise HTTPException(
                    status_code=500, detail="GitHub credential missing. Configure PAT or SSH key."
                )
            else:
                print(f"git_result: {e}\nstdout: {e.stdout}\nstderr: {e.stderr}")

            return PublishResult(False, article_slug)

        return PublishResult(True, article_slug)
