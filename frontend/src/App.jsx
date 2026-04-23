import React, { useState, useEffect, useRef, useCallback } from 'react'

const WS_URL = window.WS_URL || 'ws://localhost:8000/ws'

function App() {
  const [status, setStatus] = useState('disconnected')
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const wsRef = useRef(null)
  const reconnectAttempts = useRef(0)
  const maxReconnectAttempts = 5

  /**
   * =====================================================================
   * WEBSOCKET CONNECTION
   * =====================================================================
   * The WebSocket class is built into browsers and provides a simple API
   * to connect to WebSocket servers.
   * 
   * WebSocket URL formats:
   * - ws://host:port/path - Unencrypted (development)
   * - wss://host:port/path - SSL encrypted (production)
   */

  const connect = useCallback(() => {
    /**
     * Create new WebSocket connection
     * 
     * When called:
     * 1. Browser sends HTTP GET request with Upgrade header
     * 2. Server responds with 101 Switching Protocols
     * 3. Connection upgraded to WebSocket
     * 4. This triggers onopen event
     */
    wsRef.current = new WebSocket(WS_URL)

    /**
     * =====================================================================
     * onopen - Connection established
     * =====================================================================
     * Called when WebSocket handshake completes successfully.
     * At this point, readyState is OPEN (1).
     * You can now send messages with ws.send()
     */
    wsRef.current.onopen = () => {
      setStatus('connected')
      reconnectAttempts.current = 0
      addMessage('✓ Connected to WebSocket server!', 'system')
    }

    /**
     * =====================================================================
     * onmessage - Message received from server
     * =====================================================================
     * Called when a message is received from the server.
     * event.data contains the message text (string).
     * For binary data, use event.data.arrayBuffer()
     */
    wsRef.current.onmessage = (event) => {
      addMessage('← Server: ' + event.data, 'received')
    }

    /**
     * =====================================================================
     * onclose - Connection closed
     * =====================================================================
     * Called when:
     * - Server closes connection
     * - Client calls ws.close()
     * - Network error/timeout
     * - Browser closes the tab
     * 
     * The connection can no longer be used after this.
     */
    wsRef.current.onclose = (event) => {
      setStatus('disconnected')
      addMessage('✗ Disconnected', 'system')

      // Auto-reconnect logic
      if (reconnectAttempts.current < maxReconnectAttempts) {
        reconnectAttempts.current++
        addMessage(`↻ Reconnecting... (attempt ${reconnectAttempts.current})`, 'system')
        setTimeout(connect, 2000)
      }
    }

    /**
     * =====================================================================
     * onerror - Error occurred
     * =====================================================================
     * Called when a WebSocket error occurs.
     * Usually followed by onclose.
     */
    wsRef.current.onerror = (error) => {
      console.error('WebSocket error:', error)
      addMessage('⚠ Error occurred', 'error')
    }
  }, [])

  /**
   * =====================================================================
   * SEND MESSAGE
   * =====================================================================
   * ws.send() - Send message to server
   * 
   * Only works if WebSocket is connected (readyState === 1)
   * Message must be a string (or ArrayBuffer for binary)
   */
  const sendMessage = useCallback((message) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(message)
      addMessage('→ You: ' + message, 'sent')
    } else {
      addMessage('⚠ Not connected', 'error')
    }
  }, [])

  const handleSend = useCallback(() => {
    if (inputMessage.trim()) {
      sendMessage(inputMessage)
      setInputMessage('')
    }
  }, [inputMessage, sendMessage])

  const addMessage = useCallback((text, type) => {
    setMessages(prev => [...prev, { text, type, time: new Date().toLocaleTimeString() }])
  }, [])

  useEffect(() => {
    connect()
    return () => {
      wsRef.current?.close()
    }
  }, [connect])

  return (
    <div className="container">
      <header>
        <h1>WebSocket Learning - Test Client</h1>
        <p className="subtitle">Interactive client to learn WebSocket communication</p>
      </header>

      <div className={`status-bar ${status}`}>
        <span className="status-dot"></span>
        <span>{status.charAt(0).toUpperCase() + status.slice(1)}</span>
      </div>

      <div className="connection-info">
        <h3>WebSocket Connection</h3>
        <div className="connection-url">{WS_URL}</div>
      </div>

      <div className="main-grid">
        <div className="panel">
          <h2>Messages</h2>
          <div className="messages">
            {messages.map((msg, i) => (
              <div key={i} className={`message ${msg.type}`}>
                {msg.text}
                <span className="time">{msg.time}</span>
              </div>
            ))}
          </div>

          <div className="input-group">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Type a message... (Press Enter)"
              disabled={status !== 'connected'}
            />
            <button onClick={handleSend} disabled={status !== 'connected'}>
              Send
            </button>
          </div>

          <div className="quick-actions">
            <button onClick={() => sendMessage('Hello!')}>Say Hello</button>
            <button onClick={() => sendMessage('ping')}>Ping</button>
            <button onClick={() => sendMessage('get_time')}>Get Time</button>
            <button onClick={() => sendMessage('get_random')}>Get Random</button>
            <button onClick={() => sendMessage('echo:test')}>Echo Test</button>
          </div>
        </div>

        <div className="panel">
          <h2>WebSocket Guide</h2>

          <h3>Connection</h3>
          <pre><code>{`const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => console.log('Connected');
ws.onmessage = (e) => console.log(e.data);
ws.onclose = () => console.log('Disconnected');
ws.onerror = (e) => console.error(e);

ws.send('Hello server!');`}</code></pre>

          <h3>WebSocket States</h3>
          <table>
            <tbody>
              <tr><th>Value</th><th>State</th><th>Description</th></tr>
              <tr><td>0</td><td>CONNECTING</td><td>Connection being established</td></tr>
              <tr><td>1</td><td>OPEN</td><td>Connected, ready to communicate</td></tr>
              <tr><td>2</td><td>CLOSING</td><td>Connection closing</td></tr>
              <tr><td>3</td><td>CLOSED</td><td>Connection closed</td></tr>
            </tbody>
          </table>

          <h3>Server Commands</h3>
          <table>
            <tbody>
              <tr><th>Command</th><th>Response</th></tr>
              <tr><td><code>ping</code></td><td>"pong"</td></tr>
              <tr><td><code>get_time</code></td><td>Server time</td></tr>
              <tr><td><code>get_random</code></td><td>Random number</td></tr>
              <tr><td><code>Hello!</code></td><td>Welcome</td></tr>
            </tbody>
          </table>
        </div>
      </div>

      <div className="docs-section">
        <h2>Learn WebSocket</h2>

        <div className="docs-grid">
          <div className="concept-card">
            <h3>What is WebSocket?</h3>
            <p>Full-duplex (two-way) communication over a single TCP connection. Both client and server can send messages anytime, unlike HTTP where client must always request.</p>
          </div>

          <div className="concept-card">
            <h3>Connection Lifecycle</h3>
            <ol>
              <li>Client creates new WebSocket(url)</li>
              <li>Server accepts with accept()</li>
              <li>Both send/receive messages</li>
              <li>Either side closes</li>
            </ol>
          </div>

          <div className="concept-card">
            <h3>WebSocket vs HTTP</h3>
            <table>
              <tbody>
                <tr><th>Aspect</th><th>WebSocket</th><th>HTTP</th></tr>
                <tr><td>Connection</td><td>Persistent</td><td>Request-Response</td></tr>
                <tr><td>Server → Client</td><td>Anytime</td><td>Must request</td></tr>
                <tr><td>Real-time</td><td>Yes</td><td>No (polling)</td></tr>
                <tr><td>Overhead</td><td>Low</td><td>High</td></tr>
              </tbody>
            </table>
          </div>

          <div className="concept-card">
            <h3>Use Cases</h3>
            <ul>
              <li><strong>Chat apps</strong> - Real-time messaging</li>
              <li><strong>Live updates</strong> - Stocks, scores</li>
              <li><strong>Gaming</strong> - Game state</li>
              <li><strong>IoT</strong> - Sensor streams</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App