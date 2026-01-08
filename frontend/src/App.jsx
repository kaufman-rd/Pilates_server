import { useEffect, useState, useRef } from 'react'
import io from 'socket.io-client'

function App() {
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const socketRef = useRef(null)
  const textareaRef = useRef(null)

  useEffect(() => {
    const socket = io('http://localhost:8000', {
      transports: ['websocket', 'polling']
    })
    socketRef.current = socket
    
    socket.on('connect', () => {
      setMessages(prev => [...prev, 'Connected to WebSocket'])
    })
    
    socket.on('sensor_data', (data) => {
      setMessages(prev => [...prev, `sensor_data: ${JSON.stringify(data)}`])
    })
    
    socket.on('message', (data) => {
      setMessages(prev => [...prev, `message: ${JSON.stringify(data)}`])
    })
    
    socket.on('disconnect', () => {
      setMessages(prev => [...prev, 'Disconnected from WebSocket'])
    })
    
    return () => {
      socket.disconnect()
    }
  }, [])

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.scrollTop = textareaRef.current.scrollHeight
    }
  }, [messages])

  const handleSend = () => {
    if (inputValue.trim() && socketRef.current) {
      socketRef.current.emit('message', inputValue)
      setMessages(prev => [...prev, `Sent: ${inputValue}`])
      setInputValue('')
    }
  }

  return (
    <div>
      <h1>Terminal</h1>
      <textarea 
        ref={textareaRef}
        value={messages.join('\n')} 
        readOnly 
        rows={20} 
        cols={80}
      />
      <div>
        <input 
          type="text" 
          value={inputValue} 
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
        />
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  )
}

export default App
