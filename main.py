from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="WebSocket Learning App", version="1.0.0")

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>WebSocket Test Client</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            #messages { height: 300px; border: 1px solid #ccc; overflow-y: scroll; margin-bottom: 20px; padding: 10px; }
            .message { padding: 5px; margin: 5px 0; }
            .sent { background: #e3f2fd; text-align: right; }
            .received { background: #f1f8e9; }
            .system { background: #fff3e0; font-style: italic; color: #666; }
            #status { padding: 10px; margin-bottom: 10px; border-radius: 5px; }
            .connected { background: #c8e6c9; color: #2e7d32; }
            .disconnected { background: #ffcdd2; color: #c62828; }
            input, button { padding: 10px; margin: 5px 0; }
            input { width: 70%; }
            button { width: 25%; cursor: pointer; }
            .info { background: #e1f5fe; padding: 10px; margin: 10px 0; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1>WebSocket Learning - Test Client</h1>
        
        <div id="status" class="disconnected">Status: Disconnected</div>
        
        <div class="info">
            <strong>Connection URL:</strong> <code>ws://localhost:8000/ws</code><br>
            <strong>Endpoint:</strong> <code>/ws</code>
        </div>
        
        <h3>Messages</h3>
        <div id="messages"></div>
        
        <input type="text" id="messageInput" placeholder="Type a message..." />
        <button onclick="sendMessage()" id="sendBtn" disabled>Send</button>
        
        <h3>Quick Actions</h3>
        <button onclick="sendQuickMessage('Hello!')">Say Hello</button>
        <button onclick="sendQuickMessage('ping')">Ping</button>
        <button onclick="sendQuickMessage('get_time')">Get Time</button>
        <button onclick="sendQuickMessage('get_random')">Get Random Number</button>

        <script>
            let ws = null;
            let reconnectAttempts = 0;
            const maxReconnectAttempts = 5;

            function connect() {
                ws = new WebSocket('ws://localhost:8000/ws');
                
                ws.onopen = () => {
                    document.getElementById('status').textContent = 'Status: Connected';
                    document.getElementById('status').className = 'connected';
                    document.getElementById('sendBtn').disabled = false;
                    reconnectAttempts = 0;
                    addMessage('Connected to server!', 'system');
                };
                
                ws.onmessage = (event) => {
                    addMessage('Server: ' + event.data, 'received');
                };
                
                ws.onclose = () => {
                    document.getElementById('status').textContent = 'Status: Disconnected';
                    document.getElementById('status').className = 'disconnected';
                    document.getElementById('sendBtn').disabled = true;
                    addMessage('Disconnected from server', 'system');
                    
                    if (reconnectAttempts < maxReconnectAttempts) {
                        reconnectAttempts++;
                        setTimeout(connect, 2000);
                    }
                };
                
                ws.onerror = (error) => {
                    console.error('WebSocket error:', error);
                };
            }

            function sendMessage() {
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                if (message && ws && ws.readyState === WebSocket.OPEN) {
                    ws.send(message);
                    addMessage('You: ' + message, 'sent');
                    input.value = '';
                }
            }

            function sendQuickMessage(message) {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    ws.send(message);
                    addMessage('You: ' + message, 'sent');
                }
            }

            function addMessage(text, type) {
                const messagesDiv = document.getElementById('messages');
                const div = document.createElement('div');
                div.className = 'message ' + type;
                div.textContent = text;
                messagesDiv.appendChild(div);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }

            document.getElementById('messageInput').addEventListener('keypress', (e) => {
                if (e.key === 'Enter') sendMessage();
            });

            connect();
        </script>
    </body>
</html>
"""


class ConnectionManager:
    """
    Manages WebSocket connections.
    
    Key concepts:
    - active_connections: List of all connected WebSocket clients
    - connect(): Add a new client to active connections
    - disconnect(): Remove a client from active connections
    - broadcast(): Send a message to all connected clients
    - send_personal_message(): Send a message to a specific client
    
    Why use a manager class?
    - Keeps track of all connected clients
    - Makes it easy to broadcast messages to everyone
    - Enables sending private messages to specific clients
    """

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """
        Accept a new WebSocket connection and add it to active_connections.
        
        WebSocket handshake:
        1. Client sends a WebSocket upgrade request
        2. Server accepts with await websocket.accept()
        3. Connection is established
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """
        Remove a WebSocket connection from active_connections.
        
        Called when:
        - Client disconnects normally
        - Connection is lost (handled by WebSocketDisconnect exception)
        """
        self.active_connections.remove(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """
        Send a message to a specific WebSocket client.
        
        Args:
            message: The text message to send
            websocket: The target WebSocket connection
        """
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        """
        Send a message to ALL connected WebSocket clients.
        
        Use cases:
        - Chat rooms sending messages to all members
        - Server notifications to all clients
        - Real-time updates (stock prices, notications, etc.)
        """
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.get("/")
async def get():
    """
    Root endpoint - serves the HTML test client.
    
    This is a simple way to test WebSocket without a separate frontend.
    Open http://localhost:8000 in your browser to test.
    """
    return HTMLResponse(html)


@app.get("/docs")
async def documentation():
    """
    Serve detailed documentation about this WebSocket API.
    """
    docs_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>WebSocket API Documentation</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 900px; margin: 50px auto; padding: 20px; line-height: 1.6; }
            h1 { color: #1976d2; }
            h2 { color: #388e3c; margin-top: 30px; }
            h3 { color: #f57c00; }
            code { background: #f5f5f5; padding: 2px 6px; border-radius: 3px; }
            pre { background: #263238; color: #aed581; padding: 15px; border-radius: 5px; overflow-x: auto; }
            .endpoint { background: #e3f2fd; padding: 10px; margin: 10px 0; border-left: 4px solid #1976d2; }
            .concept { background: #fff3e0; padding: 10px; margin: 10px 0; border-left: 4px solid #f57c00; }
        </style>
    </head>
    <body>
        <h1>WebSocket API Documentation</h1>
        
        <h2>What is WebSocket?</h2>
        <div class="concept">
            <strong>WebSocket</strong> is a communication protocol that provides <strong>full-duplex</strong> 
            (two-way) communication over a single TCP connection. Unlike HTTP which is request-response based, 
            WebSocket allows the server to initiate messages to the client.
        </div>
        
        <h2>Key Concepts</h2>
        <ul>
            <li><strong>Full-duplex communication</strong>: Both client and server can send messages anytime</li>
            <li><strong>Persistent connection</strong>: Connection stays open until closed</li>
            <li><strong>Lower overhead</strong>: No need to establish new connections for each message</li>
            <li><strong>Real-time updates</strong>: Server can push updates to clients instantly</li>
        </ul>
        
        <h2>API Endpoints</h2>
        
        <h3>1. WebSocket Endpoint - /ws</h3>
        <div class="endpoint">
            <strong>URL:</strong> <code>ws://localhost:8000/ws</code><br>
            <strong>Method:</strong> GET (WebSocket upgrade)
        </div>
        
        <h4>How to Connect</h4>
        <pre>const ws = new WebSocket('ws://localhost:8000/ws');</pre>
        
        <h4>JavaScript Client Example</h4>
        <pre>// Create connection
const ws = new WebSocket('ws://localhost:8000/ws');

// Connection opened
ws.onopen = () => {
    console.log('Connected!');
    ws.send('Hello server!');
};

// Receive message
ws.onmessage = (event) => {
    console.log('Server says:', event.data);
};

// Connection closed
ws.onclose = () => {
    console.log('Disconnected');
};

// Error occurred
ws.onerror = (error) => {
    console.error('Error:', error);
};</pre>
        
        <h3>2. Test Client - /</h3>
        <div class="endpoint">
            <strong>URL:</strong> <code>http://localhost:8000/</code><br>
            <strong>Purpose:</strong> Browser-based test interface
        </div>
        
        <h2>Server Commands</h2>
        <p>The server responds to these special messages:</p>
        <ul>
            <li><code>ping</code> - Returns "pong"</li>
            <li><code>get_time</code> - Returns current server time</li>
            <li><code>get_random</code> - Returns a random number</li>
            <li>Any other message - Echoes back with prefix</li>
        </ul>
        
        <h2>How WebSocket Works in FastAPI</h2>
        
        <h3>1. Define WebSocket Endpoint</h3>
        <pre>@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Accept connection
    await websocket.accept()
    
    # Receive and send messages in loop
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Echo: {data}")</pre>
        
        <h3>2. Using ConnectionManager</h3>
        <pre>manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)</pre>
        
        <h2>WebSocket vs HTTP</h2>
        <table border="1" cellpadding="10">
            <tr>
                <th>Feature</th>
                <th>WebSocket</th>
                <th>HTTP</th>
            </tr>
            <tr>
                <td>Connection</td>
                <td>Persistent</td>
                <td>Request-Response</td>
            </tr>
            <tr>
                <td>Server → Client</td>
                <td>Yes (anytime)</td>
                <td>No (client must request)</td>
            </tr>
            <tr>
                <td>Real-time</td>
                <td>Yes</td>
                <td>No (polling required)</td>
            </tr>
            <tr>
                <td>Overhead</td>
                <td>Low</td>
                <td>High (headers each request)</td>
            </tr>
        </table>
        
        <h2>Common Use Cases</h2>
        <ul>
            <li><strong>Chat applications</strong> - Real-time messaging</li>
            <li><strong>Live updates</strong> - Stock prices, sports scores</li>
            <li><strong>Notifications</strong> - Push notifications to clients</li>
            <li><strong>Collaborative editing</strong> - Multiple users editing together</li>
            <li><strong>Gaming</strong> - Real-time game state sync</li>
            <li><strong>IoT data</strong> - Receiving sensor data</li>
        </ul>
        
        <h2>Running the Application</h2>
        <pre>uvicorn main:app --reload --host 0.0.0.0 --port 8000</pre>
        
        <h2>Testing</h2>
        <ol>
            <li>Start the server: <code>uvicorn main:app --reload</code></li>
            <li>Open browser: <code>http://localhost:8000</code></li>
            <li>Open multiple browser tabs to test broadcasting</li>
            <li>Test the /docs endpoint for detailed docs</li>
        </ol>
    </body>
    </html>
    """
    return HTMLResponse(docs_html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint - handles client connections and messages.
    
    URL: ws://localhost:8000/ws
    
    How it works:
    1. Client connects to /ws endpoint
    2. Server accepts connection via manager.connect()
    3. Enter a loop to receive messages
    4. Process each message and respond
    5. Handle disconnection via WebSocketDisconnect exception
    
    WebSocket methods:
    - websocket.accept(): Accept the WebSocket upgrade
    - websocket.receive_text(): Wait for and receive a text message
    - websocket.send_text(): Send a text message to the client
    - websocket.close(): Close the connection
    
    Exception:
    - WebSocketDisconnect: Raised when client disconnects
    """
    await manager.connect(websocket)
    try:
        while True:
            """
            receive_text() waits until a message is received.
            This is a blocking operation - code waits here until client sends.
            
            Alternative methods:
            - receive_json(): Receive JSON data
            - receive_bytes(): Receive binary data
            """
            client_message = await websocket.receive_text()
            logger.info(f"Received: {client_message}")
            
            response = process_message(client_message)
            await manager.send_personal_message(response, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected")


def process_message(message: str) -> str:
    """
    Process incoming messages and generate responses.
    
    This demonstrates different response types.
    """
    message = message.lower().strip()
    
    if message == "ping":
        return "pong"
    
    elif message == "get_time":
        from datetime import datetime
        return f"Server time: {datetime.now().strftime('%H:%M:%S')}"
    
    elif message == "get_random":
        import random
        return f"Random number: {random.randint(1, 100)}"
    
    elif message == "hello":
        return "Hello! Welcome to the WebSocket server!"
    
    elif message.startswith("echo:"):
        return message
    
    else:
        return f"Server received: '{message}'. Try 'ping', 'get_time', or 'get_random'"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)