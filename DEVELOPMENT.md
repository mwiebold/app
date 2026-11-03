# Local development

This fork tracks [beestat/app](https://github.com/beestat/app). The initial
baseline is `22db006` (2026-10-23). `origin` is the personal fork and `upstream`
is the original project. Feature work starts on `codex/beestat-setup`.

## Start the backend

Requirements: Docker with Compose, Python 3, and Node.js 22+ for syntax checks.
The containers provide PHP 8.5 with Apache/MySQLi and MySQL 8.4.

```sh
python3 dev/setup.py
docker compose up -d --build --wait
python3 dev/check.py
```

The server listens at `http://localhost:8088`. Source edits are mounted into
the container immediately. The database has a persistent Docker volume and
no published host port. Settings are generated in the already-ignored
`api/cora/setting.php`; setup preserves an existing file.

These are local development services with known development credentials,
bound to loopback. They are not a production deployment. Apache denies access
to Git metadata, development scripts, documentation, and SQL/config files.

The initial database contains the schema and two local API users only. It has
no thermostat records, history, or logged-in user. A working API does **not**
mean the dashboard has data. The root page retains upstream's hard-coded
HTTPS login redirect, so visiting it on this HTTP-only stack will not complete
login. The smoke check exercises the API directly without logging in.

```sh
docker compose logs --tail=100 web db
docker compose stop
docker compose start
```

Schema and seed SQL run only on the first initialization of an empty volume.
Do not reimport `api/beestat.sql` into a populated database: it drops tables.
Use explicit migrations for future schema changes. Preserve the volume when
stopping/recreating services.

## Connect an existing ecobee developer app

Follow the [upstream self-hosting guide](https://beestat.notion.site/Self-Hosting-4b40cf56c0424692a65461a7a6ffdb1e).
An existing ecobee developer app is available for this fork; its settings and
credentials have not been copied into the repository.

Before interactive login, configure an HTTPS hostname/certificate and the
app's registered callback URL. Set `ecobee_client_id`, `ecobee_redirect_uri`,
`beestat_root_uri`, and `force_ssl` in the ignored settings file. Keep
`environment` set to `dev` while working from source. The callback is
`/api/ecobee_initialize.php` under the chosen HTTPS hostname. Any reverse proxy
must correctly communicate the HTTPS scheme to PHP.

The production cron/synchronization configuration also needs the upstream
hosting instructions. No background sync, real thermostat data import, or
external account connection is configured by this development setup.

## Checks and feature workflow

`python3 dev/check.py` checks tracked, non-vendor JavaScript and PHP syntax,
a database-backed API read, denial of an unauthenticated private read, and
the local server's file-access rules. It needs the stack running. It is a
smoke check, not a full application test suite.

To update the upstream tracking branch:

```sh
git fetch upstream
git log --oneline HEAD..upstream/master
```

Review incoming changes before merging them. Keep feature commits separate
from upstream synchronization. See [the initial review](docs/current-state.md)
for the architecture, existing plots, and suggested next steps.
