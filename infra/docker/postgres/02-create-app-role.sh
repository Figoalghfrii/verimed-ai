#!/bin/sh
set -eu

if [ -z "${POSTGRES_APP_PASSWORD:-}" ]; then
  echo "POSTGRES_APP_PASSWORD not set; skipping least-privilege role setup."
  exit 0
fi

APP_ROLE="${POSTGRES_APP_USER:-verimed_app}"

psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" --dbname "${POSTGRES_DB}" \
  -v app_role="${APP_ROLE}" -v app_pass="${POSTGRES_APP_PASSWORD}" <<'EOSQL'
SELECT format(
  'CREATE ROLE %I WITH LOGIN PASSWORD %L NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT',
  :'app_role',
  :'app_pass'
)
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = :'app_role')
\gexec

SELECT format(
  'ALTER ROLE %I WITH LOGIN PASSWORD %L NOSUPERUSER NOCREATEDB NOCREATEROLE',
  :'app_role',
  :'app_pass'
)
WHERE EXISTS (SELECT 1 FROM pg_roles WHERE rolname = :'app_role')
\gexec

GRANT USAGE ON SCHEMA public TO :"app_role";
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO :"app_role";
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO :"app_role";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO :"app_role";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO :"app_role";
EOSQL
