import { useEffect, useRef } from 'react'

function Terminal({ messages, inputValue, setInputValue, handleSend, showDataInTerminal, setShowDataInTerminal }) {
  const textareaRef = useRef(null)

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.scrollTop = textareaRef.current.scrollHeight
    }
  }, [messages])

  return (
    <div style={{ padding: '20px', height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
        <h2 style={{ margin: 0 }}>Terminal</h2>
        <label style={{ display: 'flex', alignItems: 'center', gap: '5px', cursor: 'pointer' }}>
          <input 
            type="checkbox" 
            checked={showDataInTerminal}
            onChange={(e) => setShowDataInTerminal(e.target.checked)}
          />
          <span>Show data in terminal</span>
        </label>
      </div>
      <textarea 
        ref={textareaRef}
        value={messages.join('\n')} 
        readOnly 
        rows={10} 
        style={{ flex: 1, width: '100%', fontFamily: 'monospace', resize: 'none' }}
      />
      <div style={{ marginTop: '10px' }}>
        <input 
          type="text" 
          value={inputValue} 
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          style={{ width: 'calc(100% - 200px)', padding: '5px' }}
        />
        <button onClick={handleSend} style={{ marginLeft: '10px', padding: '5px 15px' }}>Send</button>
      </div>
    </div>
  )
}

export default Terminal
