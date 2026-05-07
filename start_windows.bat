@echo off
echo [1/3] Arrancando PostgreSQL...
docker compose up -d db

echo [2/3] Instalando base de datos digitux y modulo digitux_web...
docker compose --profile init run --rm odoo-init

echo [3/3] Arrancando Odoo...
docker compose up -d odoo

echo.
echo Listo: http://localhost:8069
echo Base de datos: digitux
echo Si quieres empezar de cero: docker compose down -v
pause
