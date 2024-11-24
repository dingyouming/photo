# Intelligent Photo Management System

A comprehensive, AI-powered photo organization platform with advanced metadata processing and intelligent search capabilities.

## Features

- Intelligent photo organization
- Advanced metadata processing
- AI-powered image recognition
- Smart search capabilities
- Efficient storage management

## Development Setup

### Prerequisites

- Docker and Docker Compose
- Git
- Python 3.9+ (for local development)

### Quick Start

1. Clone the repository:
```bash
git clone <repository-url>
cd photo_app
```

2. Copy environment file:
```bash
cp .env.example .env
```

3. Start development environment:
```bash
docker-compose -f docker-compose.dev.yml up -d
```

4. Enter development container:
```bash
docker-compose -f docker-compose.dev.yml exec dev bash
```

### Project Structure

```
photo_app/
├── api/                    # FastAPI application
│   ├── endpoints/         # API endpoints
│   ├── models/           # Pydantic models
│   └── dependencies/     # Dependency injection
├── core/                  # Core business logic
│   ├── services/         # Business services
│   ├── models/           # Database models
│   └── utils/            # Utility functions
├── infrastructure/        # Infrastructure layer
│   ├── database/         # Database configurations
│   ├── storage/          # Storage implementations
│   └── messaging/        # Message queue implementations
├── tests/                # Test suite
├── scripts/              # Utility scripts
└── docs/                 # Documentation
```

## Testing

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=app
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests
4. Submit a pull request

## License

MIT License
