import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { sensoresAPI, ledsAPI, pulsadoresAPI } from '../services/api'
import { Activity, Lightbulb, Radio, TrendingUp } from 'lucide-react'

export default function Dashboard() {
  const { user } = useAuth()
  const [stats, setStats] = useState({ total: 0, promedio: 0, minimo: 0, maximo: 0 })
  const [leds, setLeds] = useState([])
  const [sensores, setSensores] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
    const interval = setInterval(loadData, 3000)
    return () => clearInterval(interval)
  }, [])

  const loadData = async () => {
    try {
      const [statsRes, ledsRes, sensoresRes] = await Promise.all([
        sensoresAPI.getEstadisticas(),
        ledsAPI.getAll(),
        sensoresAPI.getAll(10),
      ])

      setStats(statsRes.data)
      setLeds(ledsRes.data)
      setSensores(sensoresRes.data)
      setLoading(false)
    } catch (error) {
      console.error('Error cargando datos:', error)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-lg p-6 text-white">
        <h1 className="text-3xl font-bold mb-2">
          Bienvenido, {user?.username}
        </h1>
        <p className="text-blue-100">
          Panel de control del sistema HC-SR05 con LEDs y sensores
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm font-medium">Total Lecturas</p>
              <p className="text-3xl font-bold text-gray-800 mt-2">
                {stats.total}
              </p>
            </div>
            <div className="bg-blue-100 rounded-full p-3">
              <Activity className="w-8 h-8 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm font-medium">Promedio</p>
              <p className="text-3xl font-bold text-gray-800 mt-2">
                {stats.promedio.toFixed(1)} cm
              </p>
            </div>
            <div className="bg-green-100 rounded-full p-3">
              <TrendingUp className="w-8 h-8 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm font-medium">Mínimo</p>
              <p className="text-3xl font-bold text-gray-800 mt-2">
                {stats.minimo.toFixed(1)} cm
              </p>
            </div>
            <div className="bg-yellow-100 rounded-full p-3">
              <Radio className="w-8 h-8 text-yellow-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm font-medium">Máximo</p>
              <p className="text-3xl font-bold text-gray-800 mt-2">
                {stats.maximo.toFixed(1)} cm
              </p>
            </div>
            <div className="bg-red-100 rounded-full p-3">
              <Radio className="w-8 h-8 text-red-600" />
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center space-x-2 mb-4">
            <Lightbulb className="w-6 h-6 text-yellow-500" />
            <h2 className="text-xl font-bold text-gray-800">Estado de LEDs</h2>
          </div>

          <div className="space-y-3">
            {leds.map((led) => (
              <div
                key={led.id}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
              >
                <div className="flex items-center space-x-3">
                  <div
                    className="w-4 h-4 rounded-full"
                    style={{ backgroundColor: led.color }}
                  ></div>
                  <span className="font-medium text-gray-700">{led.nombre}</span>
                </div>
                <span
                  className={`px-3 py-1 rounded-full text-sm font-medium ${
                    led.estado
                      ? 'bg-green-100 text-green-700'
                      : 'bg-gray-200 text-gray-600'
                  }`}
                >
                  {led.estado ? 'ON' : 'OFF'}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center space-x-2 mb-4">
            <Activity className="w-6 h-6 text-blue-600" />
            <h2 className="text-xl font-bold text-gray-800">
              Últimas Lecturas del Sensor
            </h2>
          </div>

          <div className="space-y-2">
            {sensores.map((sensor, index) => (
              <div
                key={sensor.id}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <span className="text-sm text-gray-600">
                  {new Date(sensor.fecha).toLocaleString('es-MX')}
                </span>
                <span className="font-bold text-blue-600">
                  {parseFloat(sensor.valor).toFixed(1)} cm
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
        <h3 className="font-bold text-blue-800 mb-2">Funcionalidades</h3>
        <ul className="text-blue-700 space-y-1 text-sm">
          <li>• Monitoreo en tiempo real del sensor HC-SR05</li>
          <li>• Control de 3 LEDs mediante pulsadores físicos o interfaz web</li>
          <li>• Historial completo de eventos y cambios de estado</li>
          <li>• Generación de reportes en PDF y Excel</li>
          <li>• Tablero de indicadores y gráficos estadísticos</li>
        </ul>
      </div>
    </div>
  )
}
