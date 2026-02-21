# ManFei SPA Backend

FastAPI-based backend for the ManFei Spa Business Web Application with PostgreSQL database, LINE Login OAuth, and role-based access control.

## Tech Stack

- **Framework:** FastAPI (Async)
- **Database:** PostgreSQL with asyncpg
- **ORM:** SQLAlchemy 2.0 (Async)
- **Migrations:** Alembic
- **Authentication:** LINE Login (OAuth 2.0) + JWT
- **Validation:** Pydantic v2

## Project Structure

```
backend/
├── alembic/              # Database migrations
│   ├── versions/         # Migration scripts
│   └── env.py           # Alembic environment config
├── routers/             # API route handlers
│   ├── auth_router.py   # LINE Login & JWT auth
│   ├── admin_router.py  # Admin CMS CRUD
│   ├── staff_router.py  # Staff work logging
│   └── public_router.py # Public content endpoints
├── scripts/             # Utility scripts
│   └── migrate_data.py  # Google Sheets → PostgreSQL migration
├── alembic.ini          # Alembic configuration
├── auth.py              # JWT utilities & role-based dependencies
├── config.py            # Application settings (from .env)
├── database.py          # Database connection & session management
├── main.py              # FastAPI application entry point
├── models.py            # SQLAlchemy models
├── schemas.py           # Pydantic schemas
├── requirements.txt     # Python dependencies
└── Dockerfile           # Docker container definition
```

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required variables:
- `DATABASE_URL`: PostgreSQL connection string
- `LINE_CHANNEL_ID`: From LINE Developers Console
- `LINE_CHANNEL_SECRET`: From LINE Developers Console
- `JWT_SECRET`: Random secret key for JWT signing

### 3. Run Database Migrations

```bash
# Generate initial migration (first time only)
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### 4. Create Admin User

Connect to PostgreSQL and manually insert an admin user:

```sql
INSERT INTO users (line_user_id, display_name, role, is_active)
VALUES ('your_line_user_id', 'Admin Name', 'admin', true);
```

### 5. Start Development Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at: `http://localhost:8000`
- Interactive API docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

## Using Docker

Start all services (PostgreSQL + Backend):

```bash
# From project root
docker-compose up -d

# View logs
docker-compose logs -f backend

# Run migrations inside container
docker-compose exec backend alembic upgrade head
```

## API Endpoints

### Authentication (`/api/auth`)
- `GET /line` - Redirect to LINE Login
- `GET /callback` - LINE OAuth callback handler
- `GET /me` - Get current user info (requires auth)
- `POST /logout` - Logout endpoint

### Public (`/api/public`)
- `GET /news` - List published news
- `GET /services` - List active services
- `GET /services/by-category` - Services grouped by category
- `GET /products` - List in-stock products
- `GET /testimonials` - List testimonials
- `GET /portfolio` - List portfolio items
- `GET /portfolio/by-category` - Portfolio grouped by category

### Staff (`/api/staff`) - Requires Staff or Admin Role
- `GET /menu` - Get active services for task selection
- `POST /logs` - Create work log (date must be today)
- `GET /logs/my` - Get my work logs for today

### Admin (`/api/admin`) - Requires Admin Role
- **News:** `GET, POST /news`, `GET, PUT, DELETE /news/{id}`, `PATCH /news/reorder`
- **Services:** `GET, POST /services`, `GET, PUT, DELETE /services/{id}`, `PATCH /services/reorder`
- **Products:** `GET, POST /products`, `GET, PUT, DELETE /products/{id}`, `PATCH /products/reorder`
- **Testimonials:** `GET, POST /testimonials`, `GET, PUT, DELETE /testimonials/{id}`, `PATCH /testimonials/reorder`
- **Portfolio:** `GET, POST /portfolio`, `GET, PUT, DELETE /portfolio/{id}`, `PATCH /portfolio/reorder`
- **Staff Logs:** `GET /staff/logs` - View all staff work logs with filters

## Database Models

### User
- `line_user_id` (Unique), `display_name`, `role` (admin/staff/customer), `is_active`

### Content Models (with sort_order, created_at, updated_at)
- **News:** `title`, `content` (HTML), `cover_image`, `category`, `date`
- **Service:** `name`, `description`, `price`, `duration_min`, `category`, `image_url`, `is_active`
- **Product:** `name`, `description`, `price`, `spec`, `image_url`, `is_stock`
- **Testimonial:** `customer_name`, `content`, `rating` (1-5), `avatar_url`
- **Portfolio:** `title`, `description`, `image_url`, `category`

### WorkLog
- `user_id` (FK), `date`, `service_id` (FK, nullable), `custom_task_name` (nullable), `hours`
- **Constraint:** Date must be today (enforced in API)
- **Constraint:** Either `service_id` OR `custom_task_name` must be set (not both)

## Role-Based Access Control

- **Public:** Anyone can access `/api/public` endpoints
- **Staff:** Can access `/api/staff` endpoints to log work
- **Admin:** Full access to `/api/admin` CMS and can view all staff logs

## LINE Login Setup

1. Create a LINE Login channel at: https://developers.line.biz/console/
2. Set **Callback URL** to: `http://localhost:8000/api/auth/callback` (or your production URL)
3. Copy **Channel ID** and **Channel Secret** to `.env`
4. Enable **OpenID Connect** and request `profile` and `openid` scopes

## Development Tips

### Generate New Migration
```bash
alembic revision --autogenerate -m "Description of changes"
```

### Rollback Migration
```bash
alembic downgrade -1
```

### Reset Database (Development Only)
```bash
docker-compose down -v
docker-compose up -d postgres
alembic upgrade head
```

### Test Authentication
```bash
# Get access token from LINE Login, then:
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" http://localhost:8000/api/auth/me
```

## Troubleshooting

**Issue:** `asyncpg.exceptions.InvalidCatalogNameError: database "manfei_spa" does not exist`
- **Solution:** Create the database manually: `docker-compose exec postgres createdb -U manfei_user manfei_spa`

**Issue:** `401 Unauthorized` on protected endpoints
- **Solution:** Ensure you're sending `Authorization: Bearer <token>` header

**Issue:** `KeyError: 'sub'` when decoding JWT
- **Solution:** Check `JWT_SECRET` matches between token creation and validation

**Issue:** LINE Login callback fails
- **Solution:** Verify callback URL in LINE Console matches exactly (including protocol and port)

## Production Deployment

1. Set strong `JWT_SECRET` in production `.env`
2. Update `FRONTEND_URL` and `BACKEND_URL` to production domains
3. Set PostgreSQL password to a strong value
4. Enable HTTPS for both frontend and backend
5. Update LINE Login callback URL in LINE Console
6. Consider using Redis for state token storage instead of in-memory dict
7. Set `echo=False` in database engine config (see [database.py](database.py))

## License

Proprietary - ManFei SPA Business
