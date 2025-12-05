#!/bin/bash
set -e

echo "🚀 Iniciando despliegue de HOL-CRM..."

# Navegar al directorio del proyecto
cd /var/www/HOL-CRM

# Pull de los últimos cambios
echo "📥 Descargando cambios de GitHub..."
git pull origin main

# Backend
echo "🐍 Actualizando backend..."
cd backend
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
deactivate

# Frontend
echo "⚛️  Actualizando frontend..."
cd ../frontend
npm install
npm run build

# Reiniciar servicios
echo "🔄 Reiniciando servicios..."
sudo supervisorctl restart hol-crm-backend
sudo supervisorctl restart hol-crm-frontend
sudo systemctl reload nginx

echo "✅ Despliegue completado exitosamente!"
