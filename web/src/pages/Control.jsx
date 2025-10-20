import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { sensoresAPI, ledsAPI, pulsadoresAPI, eventosAPI } from '../services/api'
import { Lightbulb, Radio, Activity, Clock } from 'lucide-react'

export default function Control() {
  const { user } = useAuth()
  const [leds, setLeds] = useState([])
  const [pulsadores, setPulsadores] = useState([])
  const [sensores, setSensores] = useState([])
  const [eventos, setEventos] = useState([])
  const [ultimaLectura, setUltimaLectura] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
    const interval = setInterval(loadData, 2000)
    return () => clearInterval(interval)
  }, [])

  const loadData = async () => {
    try {
      const [ledsRes, pulsRes, sensoresRes, eventosRes] = await Promise.all([
        ledsAPI.getAll(),
        pulsadoresAPI.getAll(),
        sensoresAPI.getAll(20),
        eventosAPI.getAll(15),
      ])

      setLeds(ledsRes.data)
      setPulsadores(pulsRes.data)
      setSensores(sensoresRes.data)
      setEventos(eventosRes.data)

      if (sensoresRes.data.length > 0) {
        setUltimaLectura(sensoresRes.data[0])
      }

      setLoading(false)
    } catch (error) {
      console.error('Error cargando datos:', error)
    }
  }

  const toggleLed = async (ledId) => {
    try {
      const led = leds.find((l) => l.id === ledId)
      const nuevoEstado = !led.estado
      await ledsAPI.update(ledId, nuevoEstado, user.username, 'WEB')
      loadData()
    } catch (error) {
      console.error('Error al cambiar LED:', error)
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
      <div className="bg-white rounded-lg shadow-md p-6">
        <h1 className="text-2xl font-bold text-gray-800 mb-2">
          Control de Dispositivos
        </h1>
        <p className="text-gray-600">
          Controla los LEDs y monitorea el estado de los sensores en tiempo real
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center space-x-2 mb-6">
            <Radio className="w-6 h-6 text-blue-600" />
            <h2 className="text-xl font-bold text-gray-800">
              Sensor HC-SR05
            </h2>
          </div>

          <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg p-8 text-white text-center mb-4">
            <div className="text-6xl font-bold mb-2">
              {ultimaLectura
                ? parseFloat(ultimaLectura.valor).toFixed(1)
                : '0.0'}
            </div>
            <div className="text-2xl">centímetros</div>
            {ultimaLectura && (
              <div className="text-sm mt-4 text-blue-100">
                Última actualización:{' '}
                {new Date(ultimaLectura.fecha).toLocaleTimeString('es-MX')}
              </div>
            )}
          </div>

          <div className="bg-blue-50 p-4 rounded-lg">
            <h3 className="font-bold text-blue-800 mb-2">Estado</h3>
            <p className="text-blue-700 text-sm">
              {ultimaLectura
                ? parseFloat(ultimaLectura.valor) < 10
                  ? 'OBJETO CERCANO'
                  : 'DETECCIÓN NORMAL'
                : 'Esperando lecturas...'}
            </p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center space-x-2 mb-6">
            <Lightbulb className="w-6 h-6 text-yellow-500" />
            <h2 className="text-xl font-bold text-gray-800">Control de LEDs</h2>
          </div>

          <div className="space-y-4">
            {leds.map((led) => (
              <div
                key={led.id}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition"
              >
                <div className="flex items-center space-x-3">
                  <div
                    className="w-6 h-6 rounded-full shadow-lg"
                    style={{ backgroundColor: led.color }}
                  ></div>
                  <span className="font-medium text-gray-700">{led.nombre}</span>
                </div>

                <button
                  onClick={() => toggleLed(led.id)}
                  className={`px-6 py-2 rounded-lg font-bold transition ${
                    led.estado
                      ? 'bg-green-600 hover:bg-green-700 text-white'
                      : 'bg-gray-300 hover:bg-gray-400 text-gray-700'
                  }`}
                >
                  {led.estado ? 'ON' : 'OFF'}
                </button>
              </div>
            ))}
          </div>

          <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-sm text-yellow-800">
              <strong>Nota:</strong> Los LEDs también pueden ser controlados
              mediante los pulsadores físicos del ESP32
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center space-x-2 mb-4">
            <Activity className="w-6 h-6 text-green-600" />
            <h2 className="text-xl font-bold text-gray-800">
              Historial del Sensor
            </h2>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2 px-2 text-gray-600">Fecha</th>
                  <th className="text-right py-2 px-2 text-gray-600">Valor</th>
                </tr>
              </thead>
              <tbody>
                {sensores.slice(0, 10).map((sensor) => (
                  <tr key={sensor.id} className="border-b hover:bg-gray-50">
                    <td className="py-2 px-2 text-gray-700">
                      {new Date(sensor.fecha).toLocaleString('es-MX')}
                    </td>
                    <td className="py-2 px-2 text-right font-bold text-blue-600">
                      {parseFloat(sensor.valor).toFixed(1)} cm
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center space-x-2 mb-4">
            <Clock className="w-6 h-6 text-purple-600" />
            <h2 className="text-xl font-bold text-gray-800">Eventos Recientes</h2>
          </div>

          <div className="space-y-2 max-h-96 overflow-y-auto">
            {eventos.map((evento) => (
              <div
                key={evento.id}
                className="p-3 bg-gray-50 rounded-lg border-l-4 border-purple-500"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-medium text-gray-800">{evento.accion}</p>
                    <p className="text-sm text-gray-600">{evento.detalles}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      Usuario: {evento.usuario}
                    </p>
                  </div>
                  <span className="text-xs text-gray-500">
                    {new Date(evento.fecha).toLocaleTimeString('es-MX')}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
