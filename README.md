# Locales Monorepo

Monorepo for localization management with React + TypeScript frontend and Python + FastAPI backend.

## Project Structure

```
locales/
├── frontend/          # React + TypeScript + Vite
├── backend/           # Python + FastAPI
├── docker-compose.yml # Docker configuration
├── package.json       # Root scripts
└── README.md
```

## Technologies

### Frontend
- **React 18** - UI library
- **TypeScript** - type system
- **Vite** - build tool and dev server
- **Axios** - HTTP client
- **React Router** - routing

### Backend
- **FastAPI** - web framework
- **SQLAlchemy** - ORM
- **PostgreSQL** - database
- **Alembic** - migrations
- **Pydantic** - data validation

### Infrastructure
- **Docker** - containerization
- **Docker Compose** - orchestration

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- Docker and Docker Compose

### Installation

1. **Clone the repository and install dependencies:**
```bash
git clone <repository-url>
cd locales
npm run install:all
```

2. **Run the project with Docker:**
```bash
docker-compose up --build
```

Or run locally:

3. **Start PostgreSQL:**
```bash
docker-compose up postgres -d
```

4. **Start backend:**
```bash
cd backend
pip install -r requirements.txt
python main.py
```

5. **Start frontend:**
```bash
cd frontend
npm run dev
```

## Available Services

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432

## API Endpoints

### Localizations

- `GET /api/v1/locales/` - Get list of localizations
- `GET /api/v1/locales/{id}` - Get localization by ID
- `POST /api/v1/locales/` - Create new localization
- `PUT /api/v1/locales/{id}` - Update localization
- `DELETE /api/v1/locales/{id}` - Delete localization
- `GET /api/v1/locales/export/{language}` - Export localizations

### Query Parameters

- `skip` - number of records to skip (pagination)
- `limit` - maximum number of records (default 100)
- `language` - filter by language (e.g.: 'ru', 'en')
- `namespace` - filter by namespace

## Development

### Scripts

```bash
# Install all dependencies
npm run install:all

# Run all services in development mode
npm run dev

# Run only frontend
npm run dev:frontend

# Run only backend
npm run dev:backend

# Build frontend for production
npm run build

# Clean node_modules
npm run clean
```

### Database Structure

`locales` table:
- `id` - unique identifier
- `key` - localization key
- `value` - localization value
- `language` - language (ru, en, etc.)
- `namespace` - namespace (default, admin, etc.)
- `is_active` - whether localization is active
- `created_at` - creation date
- `updated_at` - update date

### Environment Variables

Create `.env` file in `backend/` folder based on `env.example`:

```bash
cp backend/env.example backend/.env
```

## Docker

### Build and Run
```bash
# Build all services
docker-compose build

# Run all services
docker-compose up

# Run in background
docker-compose up -d

# Stop services
docker-compose down

# Stop with volume removal
docker-compose down -v
```

### Logs
```bash
# View logs for all services
docker-compose logs

# View logs for specific service
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres
```

## License

MIT