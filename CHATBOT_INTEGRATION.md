# Crittr Backend with Integrated Chatbot

The Crittr backend now includes an integrated AI-powered chatbot that can answer questions about Crittr's features using OpenAI's GPT-4o-mini model.

## New Chatbot Features

### `/query` Endpoint
- **Method**: POST
- **Description**: AI-powered chatbot for answering questions about Crittr features
- **Request Body**: `{"query": "Your question about Crittr"}`
- **Response**: `{"response": "AI-generated response", "model_used": "gpt-4o-mini"}`

### Updated Homepage (`/`)
The homepage now includes information about the chatbot endpoint and usage examples.

## Setup

### Prerequisites
- OpenAI API key
- All existing Crittr backend dependencies

### Environment Variables
Add your OpenAI API key to your `.env` file:
```bash
OPENAI_API_KEY=your-openai-api-key-here
```

### Running the Backend
The chatbot is integrated into the main backend, so no separate setup is needed:

```bash
# Using Docker Compose (recommended)
docker-compose up --build

# Or run locally
python main.py
```

## Testing the Chatbot

Run the test script to verify the chatbot functionality:
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

## Integration Benefits

- ✅ Single container deployment
- ✅ Shared authentication and middleware
- ✅ Unified API documentation
- ✅ Consistent logging and error handling
- ✅ No additional port management needed
- ✅ Simplified maintenance and updates
