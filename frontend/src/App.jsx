import { useEffect, useState, useRef, useMemo, useCallback } from 'react'
import io from 'socket.io-client'
import Terminal from './Terminal'
import SensorGraphs from './SensorGraphs'

function App() {
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [showDataInTerminal, setShowDataInTerminal] = useState(false)
  const [graphData, setGraphData] = useState({
    position: Array(200).fill(0).map((_, i) => ({ index: i, value: 0 })),
    velocity: Array(200).fill(0).map((_, i) => ({ index: i, value: 0 })),
    weight: Array(200).fill(0).map((_, i) => ({ index: i, value: 0 }))
  })
  const socketRef = useRef(null)
  const dataIndexRef = useRef(0)
  const showDataInTerminalRef = useRef(showDataInTerminal)

  // Keep ref in sync with state
  useEffect(() => {
    showDataInTerminalRef.current = showDataInTerminal
  }, [showDataInTerminal])

  useEffect(() => {
    const socket = io('http://localhost:8000', {
      transports: ['websocket', 'polling']
    })
    socketRef.current = socket
    
    socket.on('connect', () => {
      setMessages(prev => {
        const newMessages = [...prev, 'Connected to WebSocket']
        return newMessages.slice(-100) // Keep only last 100 messages
      })
    })
    
    socket.on('sensor_data', (data) => {
      setMessages(prev => {
        const newMessages = [...prev, `sensor_data: ${JSON.stringify(data)}`]
        return newMessages.slice(-100) // Keep only last 100 messages
      })
    })
    
    socket.on('message', (data) => {
      if (showDataInTerminalRef.current) {
        setMessages(prev => {
          const newMessages = [...prev, `message: ${JSON.stringify(data)}`]
          return newMessages.slice(-100) // Keep only last 100 messages
        })
      }
      
      // Extract position, velocity, and weight from the data
      if (data.position !== undefined && data.velocity !== undefined && data.total_weight !== undefined) {
        const position = parseFloat(data.position)
        const velocity = parseFloat(data.velocity)
        const weight = parseFloat(data.total_weight)
        
        const currentIndex = dataIndexRef.current
        
        // Batch update all three graphs in a single state update
        setGraphData(prev => ({
          position: [...prev.position.slice(1), { index: currentIndex, value: position }],
          velocity: [...prev.velocity.slice(1), { index: currentIndex, value: velocity }],
          weight: [...prev.weight.slice(1), { index: currentIndex, value: weight }]
        }))
        
        dataIndexRef.current += 1
      }
    })
    
    socket.on('disconnect', () => {
      setMessages(prev => {
        const newMessages = [...prev, 'Disconnected from WebSocket']
        return newMessages.slice(-100) // Keep only last 100 messages
      })
    })
    
    return () => {
      socket.disconnect()
    }
  }, [])

  const handleSend = useCallback(() => {
    if (inputValue.trim() && socketRef.current) {
      socketRef.current.emit('message', inputValue)
      setMessages(prev => {
        const newMessages = [...prev, `Sent: ${inputValue}`]
        return newMessages.slice(-100) // Keep only last 100 messages
      })
      setInputValue('')
    }
  }, [inputValue])

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      <div style={{ width: '60%', borderRight: '1px solid #ccc', overflow: 'auto' }}>
        <Terminal 
          messages={messages}
          inputValue={inputValue}
          setInputValue={setInputValue}
          handleSend={handleSend}
          showDataInTerminal={showDataInTerminal}
          setShowDataInTerminal={setShowDataInTerminal}
        />
      </div>
      <div style={{ width: '40%', overflow: 'auto' }}>
        <SensorGraphs 
          positionData={graphData.position}
          velocityData={graphData.velocity}
          weightData={graphData.weight}
        />
      </div>
    </div>
  )
}

export default App
