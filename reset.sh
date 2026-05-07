#!/usr/bin/env bash
set -euo pipefail

docker compose down -v
echo "Volúmenes borrados. Ahora ejecuta ./start.sh"
