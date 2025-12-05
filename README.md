# HOL-CRM - Sistema de Gestión de Trámites de Inmigración

Sistema CRM especializado en la gestión de trámites y procedimientos de inmigración.

## 🚀 Tecnologías

- **Backend**: Django 6.0 + Django REST Framework
- **Frontend**: Next.js 16 + React 19 + Mantine UI
- **Base de datos**: PostgreSQL (producción) / SQLite (desarrollo)

## 📋 Requisitos Previos

- Python 3.10+
- Node.js 20.x+
- PostgreSQL 14+ (para producción)

## 🛠️ Instalación Local

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 8001
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

El frontend estará disponible en `http://localhost:3000` y el backend en `http://localhost:8001`.

## 🌐 Despliegue en VPS

Para instrucciones detalladas de despliegue en un VPS, consulta la [Guía de Despliegue](docs/deployment-guide.md).

### Resumen rápido:

1. Configurar servidor con Ubuntu 22.04+
2. Instalar dependencias del sistema
3. Configurar PostgreSQL
4. Clonar repositorio desde GitHub
5. Configurar variables de entorno
6. Ejecutar script de despliegue

```bash
./deploy.sh
```

## 📁 Estructura del Proyecto

```
HOL-CRM/
├── backend/              # Django REST API
│   ├── core/            # Configuración del proyecto
│   ├── crm/             # Aplicación principal
│   ├── requirements.txt # Dependencias Python
│   └── manage.py
├── frontend/            # Next.js aplicación
│   ├── app/            # Páginas y componentes
│   ├── public/         # Archivos estáticos
│   └── package.json
├── .env.example        # Plantilla de variables de entorno
└── deploy.sh          # Script de despliegue
```

## 🔐 Configuración

Copia `.env.example` a `.env` y configura las variables necesarias:

```bash
cp .env.example .env
```

Edita `.env` con tus valores:

- `SECRET_KEY`: Clave secreta de Django
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`: Credenciales de PostgreSQL
- `ALLOWED_HOSTS`: Dominios permitidos
- `CORS_ALLOWED_ORIGINS`: Orígenes CORS permitidos

## 📝 Comandos Útiles

### Backend

```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Recolectar archivos estáticos
python manage.py collectstatic
```

### Frontend

```bash
# Desarrollo
npm run dev

# Producción
npm run build
npm run start

# Linting
npm run lint
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es privado y confidencial.

## 📞 Soporte

Para soporte, contacta al equipo de desarrollo.
