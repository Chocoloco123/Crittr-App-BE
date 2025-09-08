#!/bin/bash

# PetCare Journal Backend Management Scripts

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Build and start development environment
dev_start() {
    print_status "Starting development environment..."
    check_docker
    
    # Create logs directory if it doesn't exist
    mkdir -p logs
    
    # Start services
    docker-compose up --build -d
    
    print_success "Development environment started!"
    print_status "Backend API: http://localhost:8000"
    print_status "API Docs: http://localhost:8000/docs"
    print_status "PostgreSQL: localhost:5432"
    print_status "Redis: localhost:6379"
}

# Start production environment
prod_start() {
    print_status "Starting production environment..."
    check_docker
    
    # Check if .env file exists
    if [ ! -f .env ]; then
        print_warning ".env file not found. Creating from example..."
        cp env.example .env
        print_warning "Please update .env file with your actual values before starting production!"
        exit 1
    fi
    
    # Create logs directory if it doesn't exist
    mkdir -p logs
    
    # Start services
    docker-compose -f docker-compose.prod.yml up --build -d
    
    print_success "Production environment started!"
    print_status "Backend API: http://localhost:8000"
    print_status "Nginx Proxy: http://localhost:80"
}

# Stop all services
stop() {
    print_status "Stopping all services..."
    docker-compose down
    docker-compose -f docker-compose.prod.yml down
    print_success "All services stopped!"
}

# View logs
logs() {
    if [ "$1" = "prod" ]; then
        docker-compose -f docker-compose.prod.yml logs -f
    else
        docker-compose logs -f
    fi
}

# Restart services
restart() {
    print_status "Restarting services..."
    stop
    if [ "$1" = "prod" ]; then
        prod_start
    else
        dev_start
    fi
}

# Clean up Docker resources
clean() {
    print_status "Cleaning up Docker resources..."
    docker-compose down -v
    docker-compose -f docker-compose.prod.yml down -v
    docker system prune -f
    print_success "Docker resources cleaned up!"
}

# Database operations
db_reset() {
    print_warning "This will reset the database and remove all data!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Resetting database..."
        docker-compose down -v
        docker volume rm backend_postgres_data 2>/dev/null || true
        print_success "Database reset complete!"
    else
        print_status "Database reset cancelled."
    fi
}

# Show status
status() {
    print_status "Service Status:"
    echo
    docker-compose ps
    echo
    print_status "Resource Usage:"
    docker stats --no-stream
}

# Show help
help() {
    echo "PetCare Journal Backend Management Script"
    echo
    echo "Usage: $0 [COMMAND]"
    echo
    echo "Commands:"
    echo "  dev-start    Start development environment"
    echo "  prod-start   Start production environment"
    echo "  stop         Stop all services"
    echo "  restart      Restart services (add 'prod' for production)"
    echo "  logs         View logs (add 'prod' for production)"
    echo "  status       Show service status and resource usage"
    echo "  clean        Clean up Docker resources"
    echo "  db-reset     Reset database (removes all data)"
    echo "  help         Show this help message"
    echo
}

# Main script logic
case "$1" in
    "dev-start")
        dev_start
        ;;
    "prod-start")
        prod_start
        ;;
    "stop")
        stop
        ;;
    "restart")
        restart $2
        ;;
    "logs")
        logs $2
        ;;
    "status")
        status
        ;;
    "clean")
        clean
        ;;
    "db-reset")
        db_reset
        ;;
    "help"|"--help"|"-h"|"")
        help
        ;;
    *)
        print_error "Unknown command: $1"
        help
        exit 1
        ;;
esac
