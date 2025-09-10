# Crittr Chatbot API

A simple FastAPI-based chatbot for the Crittr pet care application that uses OpenAI's GPT-4o-mini model to answer questions about Crittr's features.

## Features

- 🤖 AI-powered responses using OpenAI GPT-4o-mini
- 📚 Knowledge base with comprehensive Crittr information
- 🚀 Simple REST API with `/query` endpoint
- 🐳 Docker support for easy deployment
- 📖 Interactive API documentation

## Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key
- Docker (optional)

### Environment Setup

1. Create a `.env` file with your OpenAI API key:
```bash
OPENAI_API_KEY=your-openai-api-key-here
```

### Running Locally

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the chatbot:
```bash
python chatbot.py
```

The API will be available at `http://localhost:8000`

### Running with Docker

1. Build and run with Docker Compose:
```bash
docker-compose up --build
```

2. Or build and run manually:
```bash
docker build -f Dockerfile.chatbot -t crittr-chatbot .
docker run -p 8000:8000 --env-file .env crittr-chatbot
```

## API Endpoints

### GET /
Homepage with API information and usage examples.

### POST /query
Send a query about Crittr features.

**Request Body:**
```json
{
  "query": "What features does Crittr offer?"
}
```

**Response:**
```json
{
  "response": "Crittr offers comprehensive pet care tracking including...",
  "model_used": "gpt-4o-mini"
}
```

### GET /health
Health check endpoint.

### GET /docs
Interactive API documentation (Swagger UI).

### GET /redoc
Alternative API documentation.

## Testing

Run the test script to verify the chatbot is working:

```bash
python test_chatbot.py
```

## Example Usage

### Using curl:
```bash
curl -X POST 'http://localhost:8000/query' \
  -H 'Content-Type: application/json' \
  -d '{"query": "What features does Crittr offer?"}'
```

### Using Python:
```python
import requests

response = requests.post(
    'http://localhost:8000/query',
    json={'query': 'How can I track my pet health?'}
)
print(response.json())
```

## Knowledge Base

The chatbot uses a comprehensive knowledge base (`knowledge.txt`) that includes:
- Core purpose and features of Crittr
- Technical architecture details
- Available pages and routes
- Response guidelines for handling feature requests

## Configuration

The chatbot can be configured through environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `ENVIRONMENT`: Set to "development" for debug logging

## Docker Configuration

- **Port**: 8000 (configurable)
- **Health Check**: Available at `/health`
- **Logs**: Mounted to `./logs` directory
- **Restart Policy**: `unless-stopped`
