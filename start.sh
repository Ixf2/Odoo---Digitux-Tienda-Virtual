#!/usr/bin/env bash
set -euo pipefail

echo "[1/3] Arrancando PostgreSQL..."
docker compose up -d db

echo "[2/3] Instalando base de datos digitux y módulo digitux_web..."
docker compose --profile init run --rm odoo-init

echo "[3/3] Arrancando Odoo..."
docker compose up -d odoo

echo ""
echo "Listo: http://localhost:8069"
echo "Base de datos: digitux"
echo "Usuario inicial: créalo en la primera pantalla si Odoo lo pide."
echo "Si ya existe una base anterior y quieres empezar de cero: ./reset.sh"
