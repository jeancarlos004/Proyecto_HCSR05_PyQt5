import { useEffect, useState } from 'react'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { sensoresAPI, historialAPI } from '../services/api'
import { Activity, TrendingUp, Clock, Zap } from 'lucide-react'

const COLORS = ['#e74c3c', '#2ecc71', '#3498db', '#f39c12', '#9b59b6']

export default function Tablero() {
  const [stats, setStats] = useState({ total: 0, promedio: 0, minimo: 0, maximo: 0 })
  const [sensores, setSensores] = useState([])
  const [ledHist, setLedHist] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
    const interval = setInterval(loadData, 5000)
    return () => clearInterval(interval)
  }, [])

  const loadData = async () => {
    try {
      const [statsRes, sensoresRes, ledHistRes] = await Promise.all([
        sensoresAPI.getEstadisticas(),
        sensoresAPI.getAll(50),
        historialAPI.getLedHist(100),
      ])

      setStats(statsRes.data)
      setSensores(sensoresRes.data)
      setLedHist(ledHistRes.data)
      setLoading(false)
    } catch (error) {
      console.error('Error cargando datos:', error)
    }
  }

  const chartData = sensores
    .slice(0, 20)
    .reverse()
    .map((s, index) => ({
      nombre: `#${index + 1}`,
      distancia: parseFloat(s.valor),
      fecha: new Date(s.fecha).toLocaleTimeString('es-MX', {
        hour: '2-digit',
        minute: '2-digit',
      }),
    }))

  const ledStats = ledHist.reduce((acc, curr) => {
    const ledId = curr.led_id
    if (!acc[ledId]) {
      acc[ledId] = { nombre: `LED ${ledId}`, on: 0, off: 0 }
    }
    if (curr.estado) {
      acc[ledId].on++
    } else {
      acc[ledId].off++
    }
    return acc
  }, {})

  const ledPieData = Object.values(ledStats)

  const rangoDistancias = [
    { rango: '0-10 cm', cantidad: 0 },
    { rango: '10-30 cm', cantidad: 0 },
    { rango: '30-50 cm', cantidad: 0 },
    { rango: '50-100 cm', cantidad: 0 },
    { rango: '>100 cm', cantidad: 0 },
  ]

  sensores.forEach((s) => {
    const val = parseFloat(s.valor)
    if (val < 10) rangoDistancias[0].cantidad++
    else if (val < 30) rangoDistancias[1].cantidad++
    else if (val < 50) rangoDistancias[2].cantidad++
    else if (val < 100) rangoDistancias[3].cantidad++
    else rangoDistancias[4].cantidad++
  })

  const fuenteData = ledHist.reduce((acc, curr) => {
    const fuente = curr.fuente
    if (!acc[fuente]) {
      acc[fuente] = { nombre: fuente, cantidad: 0 }
    }
    acc[fuente].cantidad++
    return acc
  }, {})

  const fuentePieData = Object.values(fuenteData)

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h1 className="text-2xl font-bold text-gray-800 mb-2">
          Tablero de Indicadores
        </h1>
        <p className="text-gray-600">
          Visualización de datos del sistema con gráficos e indicadores
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg shadow-lg p-6 text-white">
          <div className="flex items-center justify-between mb-2">
            <Activity className="w-8 h-8" />
            <span className="text-3xl font-bold">{stats.total}</span>
          </div>
          <p className="text-blue-100 text-sm">Total de Lecturas</p>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg shadow-lg p-6 text-white">
          <div className="flex items-center justify-between mb-2">
            <TrendingUp className="w-8 h-8" />
            <span className="text-3xl font-bold">{stats.promedio.toFixed(1)}</span>
          </div>
          <p className="text-green-100 text-sm">Promedio (cm)</p>
        </div>

        <div className="bg-gradient-to-br from-yellow-500 to-yellow-600 rounded-lg shadow-lg p-6 text-white">
          <div className="flex items-center justify-between mb-2">
            <Clock className="w-8 h-8" />
            <span className="text-3xl font-bold">{stats.minimo.toFixed(1)}</span>
          </div>
          <p className="text-yellow-100 text-sm">Mínimo (cm)</p>
        </div>

        <div className="bg-gradient-to-br from-red-500 to-red-600 rounded-lg shadow-lg p-6 text-white">
          <div className="flex items-center justify-between mb-2">
            <Zap className="w-8 h-8" />
            <span className="text-3xl font-bold">{stats.maximo.toFixed(1)}</span>
          </div>
          <p className="text-red-100 text-sm">Máximo (cm)</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-lg font-bold text-gray-800 mb-4">
            Historial de Distancias (Últimas 20 lecturas)
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="nombre" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="distancia"
                stroke="#3498db"
                strokeWidth={2}
                name="Distancia (cm)"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-lg font-bold text-gray-800 mb-4">
            Distribución por Rangos de Distancia
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={rangoDistancias}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="rango" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="cantidad" fill="#2ecc71" name="Cantidad" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-lg font-bold text-gray-800 mb-4">
            Tendencia de Distancias (Área)
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="nombre" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Area
                type="monotone"
                dataKey="distancia"
                stroke="#9b59b6"
                fill="#9b59b6"
                fillOpacity={0.6}
                name="Distancia (cm)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-lg font-bold text-gray-800 mb-4">
            Cambios de LEDs por Fuente
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={fuentePieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={(entry) => `${entry.nombre}: ${entry.cantidad}`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="cantidad"
              >
                {fuentePieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-lg font-bold text-gray-800 mb-4">
          Actividad de LEDs (ON vs OFF)
        </h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={ledPieData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="nombre" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="on" fill="#2ecc71" name="Encendido" />
            <Bar dataKey="off" fill="#e74c3c" name="Apagado" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
