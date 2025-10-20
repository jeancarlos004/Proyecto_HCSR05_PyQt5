import { useState, useEffect } from 'react'
import { sensoresAPI, historialAPI } from '../services/api'
import { jsPDF } from 'jspdf'
import * as XLSX from 'xlsx'
import { FileText, Download, Calendar, Filter } from 'lucide-react'

export default function Reportes() {
  const [sensores, setSensores] = useState([])
  const [ledHist, setLedHist] = useState([])
  const [fechaInicio, setFechaInicio] = useState('')
  const [fechaFin, setFechaFin] = useState('')
  const [tipoReporte, setTipoReporte] = useState('sensores')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const hoy = new Date()
    const hace7Dias = new Date()
    hace7Dias.setDate(hoy.getDate() - 7)

    setFechaInicio(hace7Dias.toISOString().split('T')[0])
    setFechaFin(hoy.toISOString().split('T')[0])

    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const [sensoresRes, ledHistRes] = await Promise.all([
        sensoresAPI.getAll(1000),
        historialAPI.getLedHist(1000),
      ])

      setSensores(sensoresRes.data)
      setLedHist(ledHistRes.data)
    } catch (error) {
      console.error('Error cargando datos:', error)
    }
    setLoading(false)
  }

  const filtrarPorFecha = (datos) => {
    if (!fechaInicio || !fechaFin) return datos

    const inicio = new Date(fechaInicio)
    const fin = new Date(fechaFin)
    fin.setHours(23, 59, 59, 999)

    return datos.filter((item) => {
      const fecha = new Date(item.fecha)
      return fecha >= inicio && fecha <= fin
    })
  }

  const generarPDF = () => {
    const doc = new jsPDF()
    const datos = tipoReporte === 'sensores' ? sensores : ledHist
    const datosFiltrados = filtrarPorFecha(datos)

    doc.setFontSize(20)
    doc.text('Reporte del Sistema HC-SR05', 20, 20)

    doc.setFontSize(12)
    doc.text(`Tipo: ${tipoReporte === 'sensores' ? 'Sensores' : 'LEDs'}`, 20, 35)
    doc.text(`Fecha: ${fechaInicio} a ${fechaFin}`, 20, 42)
    doc.text(`Total de registros: ${datosFiltrados.length}`, 20, 49)

    let y = 60

    if (tipoReporte === 'sensores') {
      doc.setFontSize(10)
      doc.text('Fecha', 20, y)
      doc.text('Valor (cm)', 100, y)
      doc.text('Tipo', 150, y)
      y += 7

      datosFiltrados.slice(0, 30).forEach((sensor) => {
        if (y > 270) {
          doc.addPage()
          y = 20
        }
        const fecha = new Date(sensor.fecha).toLocaleString('es-MX')
        doc.text(fecha, 20, y)
        doc.text(parseFloat(sensor.valor).toFixed(2), 100, y)
        doc.text(sensor.tipo, 150, y)
        y += 7
      })

      if (datosFiltrados.length > 0) {
        const valores = datosFiltrados.map((s) => parseFloat(s.valor))
        const promedio = valores.reduce((a, b) => a + b, 0) / valores.length
        const minimo = Math.min(...valores)
        const maximo = Math.max(...valores)

        y += 10
        doc.setFontSize(12)
        doc.text(`Estadísticas:`, 20, y)
        y += 7
        doc.setFontSize(10)
        doc.text(`Promedio: ${promedio.toFixed(2)} cm`, 20, y)
        y += 7
        doc.text(`Mínimo: ${minimo.toFixed(2)} cm`, 20, y)
        y += 7
        doc.text(`Máximo: ${maximo.toFixed(2)} cm`, 20, y)
      }
    } else {
      doc.setFontSize(10)
      doc.text('Fecha', 20, y)
      doc.text('Usuario', 70, y)
      doc.text('LED', 110, y)
      doc.text('Estado', 140, y)
      doc.text('Fuente', 170, y)
      y += 7

      datosFiltrados.slice(0, 30).forEach((led) => {
        if (y > 270) {
          doc.addPage()
          y = 20
        }
        const fecha = new Date(led.fecha).toLocaleString('es-MX')
        doc.text(fecha, 20, y)
        doc.text(led.usuario, 70, y)
        doc.text(`LED ${led.led_id}`, 110, y)
        doc.text(led.estado ? 'ON' : 'OFF', 140, y)
        doc.text(led.fuente, 170, y)
        y += 7
      })
    }

    doc.save(`reporte_${tipoReporte}_${Date.now()}.pdf`)
  }

  const generarExcel = () => {
    const datos = tipoReporte === 'sensores' ? sensores : ledHist
    const datosFiltrados = filtrarPorFecha(datos)

    let datosExcel
    if (tipoReporte === 'sensores') {
      datosExcel = datosFiltrados.map((s) => ({
        Fecha: new Date(s.fecha).toLocaleString('es-MX'),
        Tipo: s.tipo,
        'Valor (cm)': parseFloat(s.valor).toFixed(2),
      }))
    } else {
      datosExcel = datosFiltrados.map((l) => ({
        Fecha: new Date(l.fecha).toLocaleString('es-MX'),
        Usuario: l.usuario,
        LED: `LED ${l.led_id}`,
        Estado: l.estado ? 'ON' : 'OFF',
        Fuente: l.fuente,
      }))
    }

    const worksheet = XLSX.utils.json_to_sheet(datosExcel)
    const workbook = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Reporte')

    XLSX.writeFile(workbook, `reporte_${tipoReporte}_${Date.now()}.xlsx`)
  }

  const datosMostrar = tipoReporte === 'sensores' ? sensores : ledHist
  const datosFiltrados = filtrarPorFecha(datosMostrar)

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h1 className="text-2xl font-bold text-gray-800 mb-2">
          Generación de Reportes
        </h1>
        <p className="text-gray-600">
          Exporta los datos del sistema en formato PDF o Excel
        </p>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Filter className="inline w-4 h-4 mr-1" />
              Tipo de Reporte
            </label>
            <select
              value={tipoReporte}
              onChange={(e) => setTipoReporte(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
            >
              <option value="sensores">Sensores HC-SR05</option>
              <option value="leds">Historial de LEDs</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Calendar className="inline w-4 h-4 mr-1" />
              Fecha Inicio
            </label>
            <input
              type="date"
              value={fechaInicio}
              onChange={(e) => setFechaInicio(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Calendar className="inline w-4 h-4 mr-1" />
              Fecha Fin
            </label>
            <input
              type="date"
              value={fechaFin}
              onChange={(e) => setFechaFin(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
            />
          </div>

          <div className="flex items-end">
            <button
              onClick={loadData}
              disabled={loading}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
            >
              {loading ? 'Cargando...' : 'Actualizar'}
            </button>
          </div>
        </div>

        <div className="mt-6 flex gap-4">
          <button
            onClick={generarPDF}
            className="flex items-center space-x-2 px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition font-medium"
          >
            <FileText className="w-5 h-5" />
            <span>Exportar PDF</span>
          </button>

          <button
            onClick={generarExcel}
            className="flex items-center space-x-2 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition font-medium"
          >
            <Download className="w-5 h-5" />
            <span>Exportar Excel</span>
          </button>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-800">
            Vista Previa de Datos
          </h2>
          <span className="text-sm text-gray-600">
            {datosFiltrados.length} registros encontrados
          </span>
        </div>

        <div className="overflow-x-auto">
          {tipoReporte === 'sensores' ? (
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-100 border-b">
                  <th className="text-left py-3 px-4 font-medium text-gray-700">
                    Fecha
                  </th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">
                    Tipo
                  </th>
                  <th className="text-right py-3 px-4 font-medium text-gray-700">
                    Valor (cm)
                  </th>
                </tr>
              </thead>
              <tbody>
                {datosFiltrados.slice(0, 50).map((sensor) => (
                  <tr key={sensor.id} className="border-b hover:bg-gray-50">
                    <td className="py-3 px-4 text-gray-700">
                      {new Date(sensor.fecha).toLocaleString('es-MX')}
                    </td>
                    <td className="py-3 px-4 text-gray-700">{sensor.tipo}</td>
                    <td className="py-3 px-4 text-right font-bold text-blue-600">
                      {parseFloat(sensor.valor).toFixed(2)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-100 border-b">
                  <th className="text-left py-3 px-4 font-medium text-gray-700">
                    Fecha
                  </th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">
                    Usuario
                  </th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">
                    LED
                  </th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">
                    Estado
                  </th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">
                    Fuente
                  </th>
                </tr>
              </thead>
              <tbody>
                {datosFiltrados.slice(0, 50).map((led) => (
                  <tr key={led.id} className="border-b hover:bg-gray-50">
                    <td className="py-3 px-4 text-gray-700">
                      {new Date(led.fecha).toLocaleString('es-MX')}
                    </td>
                    <td className="py-3 px-4 text-gray-700">{led.usuario}</td>
                    <td className="py-3 px-4 text-gray-700">LED {led.led_id}</td>
                    <td className="py-3 px-4">
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-medium ${
                          led.estado
                            ? 'bg-green-100 text-green-700'
                            : 'bg-gray-200 text-gray-600'
                        }`}
                      >
                        {led.estado ? 'ON' : 'OFF'}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-medium ${
                          led.fuente === 'HW'
                            ? 'bg-blue-100 text-blue-700'
                            : 'bg-purple-100 text-purple-700'
                        }`}
                      >
                        {led.fuente}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  )
}
