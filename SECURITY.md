# Security

LatentTraceRAG is local first. It does not call external APIs by default, and `ALLOW_EXTERNAL_APIS=false` is the default configuration.

The backend exposes application routes only; it does not expose raw SQL endpoints. SQLite access is still file access, so protect the database path and do not place it in a shared writable directory.

Do not expose the backend publicly without authentication, rate limiting, TLS, and deployment review. Review generated outputs before relying on them for operational, legal, medical, or financial decisions. Users are responsible for securing their own deployments and any modifications that add network services or cloud APIs.
