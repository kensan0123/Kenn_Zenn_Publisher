# FreeBird

## OverView

FreeBird is Text Editor with AI Assistant like "Cursor", but this service focuses on Article Writing not Code Writing.

### Background

Many Engineers, Students or Bussines Persons write something to publish (Posts in X, Blog, ...).
I (Kensuke Nakamura - founder of this repo) want to help them easier to write or to improve them.

### How to use

When user push "Suggest" button, AI Assistant read all content in current article and returns Suggestion to improve it (That's all).

## Development (for all contributors)

### Technology Stack

- Frontend

  - Yet decided ...

- Backend

  - Python
  - FastAPI
  - SQLAlchemy
  - Ruff

- Database

  - PostgreSQL

- Infrastructure

  - Docker

### Setup

1. Clone

   `git clone https://github.com/kensan0123/FreeBird.git`

2. Set Enviroment variables

   Open `.env`.

   ```
   OPENAI_API_KEY=sk-your-openai-api-key-here

   GITHUB_PAT=ghp_your-github-personal-access-token
   GITHUB_USER=your-github-username

   USER_NAME=Your Name
   USER_EMAIL=your.email@example.com

   ARTICLE_DIR=/app/articles

   POSTGRES_USER=your-db-user-name
   POSTGRES_PASSWORD=your-db-password
   POSTGRES_DB=your-db-name
   ```

   > note
   > Variables ralated to GitHub is bad influence from old projct.
   > Soon Remove this.

3. Compose up

   `docker-compose up --build`

### Health Check

- Request

  `curl http://localhost:8000/`

- Response

```
    {
      "status": "ok",
      "message": "This is FreeBird App.",
      "version": "1.0.0"
    }
```

## License

MIT License
