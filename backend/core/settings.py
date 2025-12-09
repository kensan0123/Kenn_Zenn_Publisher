from pydantic import Field
from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    def __init__(self):
        self.OPENAI_API_KEY: str = Field(pattern=r"^sk-.+")
        self.ARTICLE_DIR: str = Field(default="./articles")
        self.GITHUB_USER: str
        self.GITHUB_PAT: str

    def create_netrc(self):
        home = os.path.expanduser("~")
        netrc_path = os.path.join(home, ".netrc")

        content = "\n".join(
            [
                "machine github.com",
                f"login {self.GITHUB_USER}",
                f"password {self.GITHUB_PAT}",
            ]
        )

        with open(netrc_path, "w") as f:
            f.write(content)

        os.chmod(netrc_path, 0o600)
