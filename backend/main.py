from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List
import logging
from datetime import datetime
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="WebSocket Learning Backend", version="1.0.0")


# =============================================================================
# CONNECTION MANAGER
# =============================================================================
# The ConnectionManager class is a crucial pattern in WebSocket applications.
# It manages all active WebSocket connections in one place, making it easy to:
# - Track connected clients
# - Send messages to specific clients
# - Broadcast messages to all clients
# - Handle client disconnections
#
# Why use a manager?
# - Clean separation of connection handling logic
# - Reusable across different endpoints
# - Makes broadcasting simple

class ConnectionManager:
    """
    Manages WebSocket connections and message routing.
    
    Key responsibilities:
    1. Track all active connections
    2. Add new connections (connect)
    3. Remove disconnected clients (disconnect)
    4. Send messages to specific clients
    5. Broadcast to all clients
    
    Data structure:
    - active_connections: List storing all connected WebSocket objects
    - Each WebSocket represents one client connection
    
    Thread safety notes:
    - In production, use asyncio.Lock for thread-safe operations
    - For learning, simple list operations are fine
    """
    
    def __init__(self):
        # List to store all active WebSocket connections
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """
        Accept and register a new WebSocket connection.
        
        WebSocket handshake process:
        ┌─────────────────────────────────────────────────────────────┐
        │ 1. Client initiates WebSocket upgrade request           │
        │    (HTTP GET request with Upgrade header)                │
        │                                                             │
        │ 2. Server accepts with websocket.accept()               │
        │    - This sends 101 Switching Protocols response        │
        │    - Upgrades connection from HTTP to WebSocket           │
        │                                                             │
        │ 3. Connection established!                               │
        │    - Now full-duplex communication is possible           │
        │    - Both sides can send messages anytime                 │
        └─────────────────────────────────────────────────────────────┘
        
        Args:
            websocket: The WebSocket object representing the client connection
            
        Returns:
            None (modifies active_connections list in place)
        """
        # accept() performs the WebSocket handshake
        # This upgrades the HTTP connection to WebSocket
        # Must be called before any other WebSocket operations
        await websocket.accept()
        
        # Add to our list of active connections
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """
        Remove a WebSocket connection from the manager.
        
        When is disconnect() called?
        - Client sends close frame
        - Client closes the browser/tab
        - Network connection lost
        - Server explicitly closes connection
        
        Important: This method is SYNCHRONOUS (no await)
        because we're just removing from a list.
        Exception handling is done in the endpoint.
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """
        Send a message to a specific WebSocket client.
        
        Use cases:
        - Direct responses to a client's request
        - Private messages in chat applications
        - User-specific notifications
        
        Args:
            message: Text string to send to the client
            websocket: Target WebSocket connection
            
        How it works:
        - Uses websocket.send_text() to send string data
        - Message goes only to the specified client
        - Other clients don't receive this message
        """
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        """
        Send a message to ALL connected WebSocket clients.
        
        Use cases:
        - Chat room messages to all members
        - Server-wide announcements
        - Real-time updates (stock prices, sports scores)
        - System notifications
        
        How it works:
        - Iterates through all active_connections
        - Sends the same message to each
        - If one fails, continue with others
        
        ┌─────────────────────────────────────────────────────────────┐
        │ Example: Broadcasting a message                          │
        │                                                             │
        │ Client A ──message──► Server ──broadcast──► Client B     │
        │                              │              ──broadcast──► Client C
        │                              │              ──broadcast──► Client D
        └─────────────────────────────────────────────────────────────┘
        """
        for connection in self.active_connections:
            await connection.send_text(message)


# Create a global instance of ConnectionManager
# This single instance is shared across all WebSocket connections
# In production, you might use dependency injection
manager = ConnectionManager()


# =============================================================================
# REST API ENDPOINTS
# =============================================================================
# These are standard HTTP endpoints (not WebSocket)
# They serve the frontend and provide app info

@app.get("/")
async def get_root():
    """Root endpoint - returns app info"""
    return {
        "name": "WebSocket Learning Backend",
        "version": "1.0.0",
        "websocket_endpoint": "/ws",
        "docs": "/docs"
    }


# =============================================================================
# WEBSOCKET ENDPOINT
# =============================================================================
# This is the main WebSocket endpoint where clients connect
# and exchange messages with the server

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint - handles real-time communication.
    
    URL: ws://localhost:8000/ws
    
    Connection lifecycle:
    ┌─────────────────────────────────────────────────────────────┐
    │ 1. CONNECT: Client calls new WebSocket(url)                 │
    │            Client sends HTTP GET with Upgrade header        │
    │                                                             │
    │ 2. HANDSHAKE: Server calls websocket.accept()               │
    │              Connection upgraded to WebSocket               │
    │                                                             │
    │ 3. COMMUNICATE: Loop receiving and sending messages         │
    │              - receive_text(): Wait for client message      │
    │              - send_text(): Send message to client          │
    │                                                             │
    │ 4. DISCONNECT: Exception raised (WebSocketDisconnect)       │
    │              Client closed browser/tab or connection        │
    └─────────────────────────────────────────────────────────────┘
    
    WebSocket object methods:
    - accept(): Complete the WebSocket handshake
    - receive_text(): Wait for and get text message from client
    - receive_json(): Wait for and parse JSON message
    - receive_bytes(): Wait for binary data
    - send_text(): Send text message to client
    - send_json(): Send JSON data to client
    - send_bytes(): Send binary data
    - close(): Close the WebSocket connection
    
    Exception handling:
    - WebSocketDisconnect: Raised when client disconnects
    - Happens automatically when:
      * Client closes connection
      * Client browser tab closed
      * Network failure
    """
    # Step 1: Accept the connection
    await manager.connect(websocket)
    
    # Step 2: Enter message loop
    try:
        while True:
            """
            receive_text() - Blocking call that waits for client message
            
            This is the key to WebSocket's real-time nature:
            - Code execution pauses here until message arrives
            - No need for polling!
            - Server can process other requests while waiting
            
            Message flow:
            Client sends ──► receive_text() returns ──► Process ──► Respond
            
            Other receive methods:
            - receive_json(): Returns parsed JSON dict
            - receive_bytes(): Returns bytes (for binary data)
            """
            client_message = await websocket.receive_text()
            logger.info(f"Received message: {client_message}")
            
            # Step 3: Process the message and get response
            response = process_message(client_message)
            
            # Step 4: Send response back to THIS client only
            # To broadcast to all clients, use:
            # await manager.broadcast(response)
            await manager.send_personal_message(response, websocket)
            
    except WebSocketDisconnect:
        """
        WebSocketDisconnect exception
        
        Raised when:
        - Client closes the WebSocket connection
        - Client closes browser/tab
        - Network connection lost
        - Client sends close frame
        
        What to do:
        - Clean up the connection from manager
        - Optionally notify other clients
        """
        manager.disconnect(websocket)
        logger.info("Client disconnected")


# =============================================================================
# MESSAGE PROCESSING
# =============================================================================
# This function processes incoming messages and generates responses
# It's designed to demonstrate different WebSocket interactions

def process_message(message: str) -> str:
    """
    Process client messages and generate appropriate responses.
    
    This demonstrates various response patterns in WebSocket apps.
    
    Args:
        message: The raw text message from the client
        
    Returns:
        Response string to send back to the client
        
    Commands demonstrated:
    - ping: Simple echo/response pattern
    - get_time: Server-generated data
    - get_random: Random data generation
    - broadcast: Message that should go to all clients
    - default: Echo pattern
    """
    # Normalize the message (lowercase, strip whitespace)
    message = message.lower().strip()
    
    # ================================================================
    # COMMAND: ping
    # Pattern: Request-Response (like HTTP but over WebSocket)
    # Use case: Keep-alive, latency measurement, connection test
    # ================================================================
    if message == "ping":
        return "pong"
    
    # ================================================================
    # COMMAND: get_time
    # Pattern: Server-push data (server generates and sends)
    # Use case: Time sync, live data updates
    # ================================================================
    elif message == "get_time":
        return f"Server time: {datetime.now().strftime('%H:%M:%S')}"
    
    # ================================================================
    # COMMAND: get_random
    # Pattern: Server-generated dynamic content
    # Use case: Games, random quotes, dynamic content
    # ================================================================
    elif message == "get_random":
        number = random.randint(1, 100)
        return f"Random number (1-100): {number}"
    
    # ================================================================
    # COMMAND: hello
    # Pattern: Greeting/welcome message
    # Use case: User authentication, welcome screens
    # ================================================================
    elif message == "hello":
        return "Hello! Welcome to the WebSocket server!"
    
    # ================================================================
    # COMMAND: echo:<message>
    # Pattern: Echo (reflect back to client)
    # Use case: Testing, message verification
    # ================================================================
    elif message.startswith("echo:"):
        # Return the message as-is (echo)
        return message
    
    # ================================================================
    # DEFAULT: Echo with prefix
    # Pattern: Default handling for unknown commands
    # ================================================================
    else:
        return f"Server received: '{message}'. Try: ping, get_time, get_random, hello, echo:<message>"


# =============================================================================
# RUNNING THE APPLICATION
# =============================================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)