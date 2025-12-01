# EnMS Chatbot

Rasa-powered conversational AI assistant for EnMS.

## Architecture

```
Portal → Nginx → Chatbot Backend (Express:5006) → Rasa Server (5005)
```

## Requirements

- **Rasa Server**: Must be running separately (not included in Docker)
- **Node.js 20+**: For the Express backend

## Setup

### Option 1: External Rasa Server (Recommended)

1. Install Rasa on your host machine:
   ```bash
   pip install rasa
   ```

2. Extract and run the model:
   ```bash
   cd chatbot/models
   tar -xzf 20251126-090737-matte-nailer.tar.gz
   rasa run --enable-api --cors "*" --port 5005
   ```

3. Set environment variables in `.env`:
   ```
   RASA_HOST=host.docker.internal  # or your host IP
   RASA_PORT=5005
   ```

4. Start EnMS:
   ```bash
   docker-compose up -d
   ```

### Option 2: Run Chatbot Locally (Development)

1. Install dependencies:
   ```bash
   cd chatbot
   npm install
   ```

2. Start Rasa (in another terminal):
   ```bash
   cd models
   tar -xzf *.tar.gz
   rasa run --enable-api --cors "*" --port 5005
   ```

3. Run the chatbot:
   ```bash
   npm run dev
   ```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/rasa/webhook` | POST | Send message to Rasa |

### Send Message Example

```bash
curl -X POST http://localhost:5006/api/rasa/webhook \
  -H "Content-Type: application/json" \
  -d '{"sender": "user123", "message": "Merhaba"}'
```

## Widget Integration

The chatbot widget is automatically included in the EnMS portal at `/js/chatbot-widget.js`.

To add to other pages:
```html
<script src="/js/chatbot-widget.js"></script>
```

## Troubleshooting

### "Rasa server not available"

1. Check if Rasa is running: `curl http://localhost:5005/webhooks/rest/webhook -X POST -d '{}'`
2. Verify `RASA_HOST` and `RASA_PORT` in `.env`
3. Check firewall/network connectivity

### Widget not appearing

1. Check browser console for errors
2. Verify chatbot service is running: `docker-compose ps chatbot`
3. Check nginx logs: `docker-compose logs nginx`
