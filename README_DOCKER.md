# GeoAnomaly Pro — Docker deployment

GeoAnomaly Pro is a web platform. Docker packages the web/API/scientific runtime;
it does not contain a shared Earth Engine account.

## Local development
Use the project's `.venv` and authenticate the developer machine with:
`python -c "import ee; ee.Authenticate()"`

## Production
Configure Google OAuth client credentials in `.env` and let each user authorize
their own Google/Earth Engine account. Never bake OAuth secrets or user refresh
tokens into the image.

## Start
`docker compose up --build -d`

Open `http://localhost:8080`.
