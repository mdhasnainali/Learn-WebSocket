# WebSocket Learning Application

A simple FastAPI application to learn WebSocket communication with an interactive test client.

## Quick Start

```bash
# Install dependencies
pip install fastapi uvicorn

# Run the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Then open:
- **Test Client:** http://localhost:8000
- **Docs:** http://localhost:8000/docs
- **API Docs:** http://localhost:8000/docs (FastAPI auto-generated)

## Project Structure

```
websocket/
├── main.py      # FastAPI WebSocket server
├── index.html   # Separate frontend test client
└── README.md    # This file
```

## What is WebSocket?

WebSocket is a communication protocol providing **full-duplex** (two-way) communication over a single TCP connection.

| Feature | WebSocket | HTTP |
|---------|----------|------|
| Connection | Persistent | Request-Response |
| Server → Client | Yes (anytime) | No (must request) |
| Real-time | Yes | No (polling needed) |
| Overhead | Low | High (headers each request) |

## WebSocket Endpoint

```python
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Echo: {data}")
```

## Key Methods

| Method | Description |
|-------|-------------|
| `websocket.accept()` | Accept WebSocket upgrade |
| `websocket.receive_text()` | Wait for incoming message |
| `websocket.send_text()` | Send message to client |
| `websocket.close()` | Close connection |

## JavaScript Client

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => console.log('Connected');
ws.onmessage = (e) => console.log(e.data);
ws.onclose = () => console.log('Disconnected');

ws.send('Hello!');
```

## Server Commands

Send these messages to test:

- `ping` → Returns "pong"
- `get_time` → Returns server time
- `get_random` → Returns random number
- `Hello!` → Welcome message
- Any other text → Echoes back

## Testing Tips

1. Open multiple browser tabs to see broadcasting
2. Use browser DevTools (F12) to see WebSocket errors
3. Check the `/docs` endpoint for detailed documentation