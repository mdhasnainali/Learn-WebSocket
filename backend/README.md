# WebSocket Learning Backend

FastAPI WebSocket server with detailed inline documentation for learning how WebSocket communication works.

## Quick Start

### With Docker
```bash
docker-compose up --build
```

### Local Development
```bash
cd backend
pip install -r requirements.txt
python main.py
```

## Access

- **WebSocket Endpoint:** `ws://localhost:8000/ws`
- **API Info:** `http://localhost:8000/`

## Architecture

### ConnectionManager Pattern

The `ConnectionManager` class is a core pattern in WebSocket applications:

```python
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket):    # Accept & register connection
    def disconnect(self, websocket): # Remove connection
    async def send_personal_message(message, websocket): # Send to one client
    async def broadcast(message):      # Send to all clients
```

### WebSocket Endpoint Lifecycle

```
Client                              Server
  |                                    |
  |-- WebSocket(url) ------------------->|
  |    (HTTP GET + Upgrade header)       |
  |                                    |
  |<-- accept() -----------------------|
  |    (101 Switching Protocols)       |
  |                                    |
  |==== Real-time messages ========     |
  |                                    |
  |==== Connection closes ==========     |
  |    (WebSocketDisconnect)         |
```

## Key Concepts

### 1. WebSocket Handshake
- Client sends HTTP GET with `Upgrade` header
- Server responds with `101 Switching Protocols`
- Connection upgraded from HTTP to WebSocket

### 2. Full-Duplex Communication
- Both client and server can send messages anytime
- No need for polling
- Lower overhead than HTTP

### 3. Message Loop
```python
while True:
    message = await websocket.receive_text()  # Wait for message
    response = process_message(message)
    await websocket.send_text(response)         # Send response
```

## API Methods

| Method | Description |
|--------|-------------|
| `websocket.accept()` | Accept WebSocket upgrade |
| `websocket.receive_text()` | Wait for text message |
| `websocket.receive_json()` | Wait for JSON message |
| `websocket.receive_bytes()` | Wait for binary data |
| `websocket.send_text(message)` | Send text to client |
| `websocket.send_json(data)` | Send JSON to client |
| `websocket.send_bytes(data)` | Send binary to client |
| `websocket.close()` | Close connection |

## Server Commands

Send these messages to test:

| Command | Response |
|---------|----------|
| `ping` | "pong" |
| `get_time` | Current server time |
| `get_random` | Random number (1-100) |
| `Hello!` | Welcome message |
| `echo:message` | Echoes back |
| Any other text | Instructions |

## Learning Points

### When to Use WebSocket
- Real-time messaging (chat)
- Live updates (stocks, scores)
- Push notifications
- Gaming (game state sync)
- IoT (sensor streams)

### When NOT to Use WebSocket
- Simple one-time requests (use HTTP)
- Low-frequency updates (use REST)
- Behind restrictive proxies (use HTTP long-polling)

### Security Considerations
- Use `wss://` (WebSocket Secure) in production
- Validate all incoming messages
- Implement authentication before upgrade
- Set connection limits
- Handle timeouts