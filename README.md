# PetCare Journal Backend

A Python FastAPI backend for the PetCare Journal application, containerized with Docker for easy deployment.

## Features

- 🚀 **FastAPI** - Modern, fast web framework for building APIs
- 🐘 **PostgreSQL** - Robust relational database
- 🔐 **JWT Authentication** - Secure token-based authentication
- 📧 **Magic Link Auth** - Passwordless email authentication
- 🤖 **OpenAI Integration** - AI-powered health insights
- 📊 **Comprehensive API** - Full CRUD operations for all entities
- 🐳 **Docker Ready** - Containerized for easy deployment
- 🔄 **Redis Caching** - Optional caching layer
- 📝 **Structured Logging** - Production-ready logging
- 🛡️ **Security** - CORS, rate limiting, and security headers

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### Development Environment

1. **Clone and navigate to backend directory**
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. **Start development environment**
   ```bash
   ./manage.sh dev-start
   ```

3. **Access the API**
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Database: localhost:5432
   - Redis: localhost:6379

### Production Environment

1. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your actual values
   ```

2. **Start production environment**
   ```bash
   ./manage.sh prod-start
   ```

## Docker Commands

### Using the Management Script

```bash
# Development
./manage.sh dev-start      # Start development environment
./manage.sh stop          # Stop all services
./manage.sh logs          # View logs
./manage.sh status        # Show service status
./manage.sh clean         # Clean up Docker resources

# Production
./manage.sh prod-start    # Start production environment
./manage.sh logs prod     # View production logs
./manage.sh restart prod  # Restart production services
```

### Manual Docker Commands

```bash
# Development
docker-compose up --build -d
docker-compose logs -f
docker-compose down

# Production
docker-compose -f docker-compose.prod.yml up --build -d
docker-compose -f docker-compose.prod.yml logs -f
docker-compose -f docker-compose.prod.yml down
```

## Environment Variables

### Required Variables

```env
# Database
DATABASE_URL=postgresql://user:password@host:port/database

# JWT
SECRET_KEY=your-super-secret-key

# SMTP (for magic links)
SMTP_HOST=smtp.gmail.com
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@petcarejournal.com

# OpenAI
OPENAI_API_KEY=your-openai-api-key

# Frontend
FRONTEND_URL=http://localhost:3000
```

### Optional Variables

```env
# JWT Configuration
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=production

# Redis
REDIS_URL=redis://redis:6379

# Logging
LOG_LEVEL=INFO
LOG_FILE=/app/logs/app.log
```

## API Endpoints

### Authentication
- `POST /users/` - Create user
- `GET /users/me` - Get current user

### Pets
- `POST /pets/` - Create pet
- `GET /pets/` - Get user's pets
- `GET /pets/{pet_id}` - Get specific pet
- `PUT /pets/{pet_id}` - Update pet
- `DELETE /pets/{pet_id}` - Delete pet

### Journal Entries
- `POST /journal-entries/` - Create journal entry
- `GET /journal-entries/` - Get journal entries
- `GET /journal-entries/{entry_id}` - Get specific entry

### Quick Logs
- `POST /quick-logs/` - Create quick log
- `GET /quick-logs/` - Get quick logs

### Health Check
- `GET /health` - Health check endpoint

## Database Schema

The application uses the following main entities:

- **Users** - User accounts and authentication
- **Pets** - Pet profiles and information
- **Journal Entries** - Detailed journal entries
- **Quick Logs** - Quick activity logging
- **Reminders** - Scheduled reminders
- **User Connections** - Social features
- **Magic Links** - Authentication tokens

## Deployment

### Local Development

1. Start the development environment:
   ```bash
   ./manage.sh dev-start
   ```

2. The API will be available at http://localhost:8000

### Production Deployment

1. **Set up environment variables**
   ```bash
   cp env.example .env
   # Update with production values
   ```

2. **Start production environment**
   ```bash
   ./manage.sh prod-start
   ```

3. **Configure reverse proxy** (optional)
   - Update `nginx.conf` with your domain
   - Add SSL certificates to `./ssl/` directory
   - Uncomment HTTPS configuration in nginx.conf

### Cloud Deployment

#### Railway
1. Connect your GitHub repository
2. Set environment variables in Railway dashboard
3. Deploy automatically

#### Heroku
1. Create a new Heroku app
2. Add PostgreSQL addon
3. Set environment variables
4. Deploy using Heroku CLI

#### DigitalOcean App Platform
1. Create a new app
2. Connect your repository
3. Configure environment variables
4. Deploy

## Monitoring and Logging

### Logs
- Application logs are stored in `./logs/` directory
- View logs: `./manage.sh logs` or `docker-compose logs -f`

### Health Checks
- Health endpoint: `GET /health`
- Docker health checks configured for all services

### Metrics
- Container resource usage: `./manage.sh status`
- Database performance monitoring via PostgreSQL logs

## Security

### Implemented Security Features
- CORS configuration
- Rate limiting (via Nginx)
- Security headers
- JWT token authentication
- Input validation with Pydantic
- SQL injection prevention with SQLAlchemy

### Security Best Practices
- Use strong SECRET_KEY in production
- Enable HTTPS in production
- Regular security updates
- Monitor logs for suspicious activity
- Use environment variables for sensitive data

## Troubleshooting

### Common Issues

1. **Database connection errors**
   ```bash
   # Check if PostgreSQL is running
   docker-compose ps
   
   # View database logs
   docker-compose logs postgres
   ```

2. **Port conflicts**
   ```bash
   # Check what's using the port
   lsof -i :8000
   
   # Stop conflicting services
   ./manage.sh stop
   ```

3. **Permission issues**
   ```bash
   # Fix script permissions
   chmod +x manage.sh
   
   # Fix log directory permissions
   sudo chown -R $USER:$USER logs/
   ```

### Debug Mode

Enable debug mode by setting:
```env
ENVIRONMENT=development
```

This will:
- Enable API documentation at `/docs`
- Show detailed error messages
- Enable SQL query logging

## Development

### Adding New Features

1. **Create database models** in `main.py`
2. **Add Pydantic schemas** for request/response validation
3. **Implement API endpoints** with proper error handling
4. **Add tests** for new functionality
5. **Update documentation**

### Code Structure

```
backend/
├── main.py              # Main FastAPI application
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Development environment
├── docker-compose.prod.yml # Production environment
├── nginx.conf          # Nginx configuration
├── manage.sh           # Management script
├── init.sql            # Database initialization
└── logs/               # Application logs
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.
