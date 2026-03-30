# Backups (production)

- **PostgreSQL**: schedule `pg_dump` (encrypted) to off-site storage; test restores quarterly.
- **CV files**: backup the volume/directory configured as `CV_STORAGE_DIR` together with DB dumps so file paths stay consistent.
- **Secrets**: store `SECRET_KEY`, `PII_ENCRYPTION_KEY`, DB credentials in a secret manager; never commit `.env`.
