# Security

Never commit:
- Google OAuth client secrets
- Earth Engine service-account private keys
- user passwords
- session secrets
- production .env files

Use .env for local secrets and a managed secret store in production.
Each user's Earth Engine authorization must remain tied to that user's Google account.
