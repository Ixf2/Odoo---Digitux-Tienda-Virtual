#!/usr/bin/env bash
set -euo pipefail

docker compose up -d db
docker compose run --rm odoo odoo --config=/etc/odoo/odoo.conf -d digitux -u digitux_web --stop-after-init
docker compose restart odoo
