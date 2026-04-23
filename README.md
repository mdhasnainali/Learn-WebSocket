# WebSocket Learning Application

A comprehensive WebSocket learning solution split into two Docker containers with detailed documentation for learning how WebSocket communication works.

## Project Structure

```
learn-websocket/
├── backend/              # FastAPI WebSocket server
│   ├── main.py          # Server with detailed inline docs
│   ├── requirements.txt
│   ├── Dockerfile
│   └── README.md       # Backend-specific docs
│
├── frontend/            # Static HTML client
│   ├── index.html     # Interactive client with learning content
│   ├── server.py     # Simple HTTP server
│   ├── Dockerfile
│   └── README.md     # Frontend-specific docs
│
├── docker-compose.yml   # Run both services
└── README.md          # This file
```

## Quick Start

### Prerequisites
- Docker
- Docker Compose

### Run with Docker
```bash
cd learn-websocket/main
docker-compose up --build
```

### Access the Application

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:8080 | Interactive test client |
| Backend | http://localhost:8000 | API info endpoint |
| WebSocket | ws://localhost:8000/ws | WebSocket endpoint |

## What You'll Learn

### Backend (FastAPI)
- WebSocket endpoint definition
- Connection management patterns
- Broadcasting vs personal messages
- Message handling
- Disconnection handling

### Frontend (JavaScript)
- WebSocket JavaScript API
- Event handlers (onopen, onmessage, onclose, onerror)
- Connection lifecycle
- Reconnection patterns
- Message sending/receiving

### Key WebSocket Concepts
- Full-duplex communication
- Persistent connections
- Server-push capability
- Real-time messaging
- Connection lifecycle

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker Network                          │
│                                                             │
│  ┌──────────────┐           ┌──────────────┐              │
│  │  Frontend    │           │   Backend     │              │
│  │  (Port 8080) │ ────────► │  (Port 8000) │              │
│  │  Nginx       │           │  FastAPI      │              │
│  │              │           │  /ws endpoint│              │
│  └──────────────┘           └──────────────┘              │
│                                                             │
│  Browser ───────────────────────────► WebSocket Server     │
│  http://localhost:8080              ws://localhost:8000/ws    │
└─────────────────────────────────────────────────────────────┘
```

## Testing WebSocket

1. Open http://localhost:8080 in your browser
2. Connection should auto-establish (status shows "Connected")
3. Use quick action buttons to test commands
4. Watch messages appear in real-time
5. Open multiple browser tabs to see message flow

## Server Commands

Send these from the frontend client:

| Command | Response |
|---------|----------|
| `ping` | "pong" |
| `get_time` | Current server time |
| `get_random` | Random number (1-100) |
| `Hello!` | Welcome message |
| `echo:test` | Echoes back |

## Documentation

- [Backend Documentation](backend/README.md) - FastAPI server details
- [Frontend Documentation](frontend/README.md) - JavaScript client details

## Stopping the Application

```bash
docker-compose down
```

## Development

### Backend Only
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Frontend Only (requires running backend)
```bash
cd frontend
WS_URL=ws://localhost:8000/ws python server.py
```