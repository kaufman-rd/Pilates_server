import { memo } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const SensorGraphs = memo(function SensorGraphs({ positionData, velocityData, weightData }) {
  return (
    <div style={{ padding: '20px' }}>
      <h1>Sensor Data Visualization</h1>
      
      <div style={{ marginBottom: '30px' }}>
        <h2>Position</h2>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={positionData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="index" hide />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="value" stroke="#8884d8" strokeWidth={4} dot={false} name="Position" isAnimationActive={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div style={{ marginBottom: '30px' }}>
        <h2>Velocity</h2>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={velocityData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="index" hide />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="value" stroke="#82ca9d" strokeWidth={4} dot={false} name="Velocity" isAnimationActive={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div style={{ marginBottom: '30px' }}>
        <h2>Weight</h2>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={weightData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="index" hide />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="value" stroke="#ffc658" strokeWidth={4} dot={false} name="Weight" isAnimationActive={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
})

export default SensorGraphs
