import { Info, User, Mail, Github, Cpu, Database, Globe } from 'lucide-react'

export default function Acerca() {
  const tecnologias = [
    { nombre: 'React', descripcion: 'Framework de interfaz de usuario', icono: Globe },
    { nombre: 'Flask', descripcion: 'API REST en Python', icono: Cpu },
    { nombre: 'Supabase', descripcion: 'Base de datos PostgreSQL', icono: Database },
    { nombre: 'ESP32', descripcion: 'Microcontrolador IoT', icono: Cpu },
  ]

  const creadores = [
    {
      nombre: 'Tu Nombre',
      rol: 'Desarrollador Full Stack',
      email: 'tu.email@ejemplo.com',
      github: 'tu-usuario',
    },
  ]

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center space-x-3 mb-4">
          <Info className="w-8 h-8 text-blue-600" />
          <h1 className="text-2xl font-bold text-gray-800">
            Acerca del Sistema
          </h1>
        </div>
        <p className="text-gray-600">
          Sistema de monitoreo y control basado en ESP32 con sensor HC-SR05
        </p>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold text-gray-800 mb-4">
          Descripción del Proyecto
        </h2>
        <div className="prose text-gray-700">
          <p className="mb-4">
            Este proyecto integra hardware y software para crear un sistema completo
            de monitoreo y control IoT. El sistema utiliza un sensor ultrasónico
            HC-SR05 para medir distancias, 3 LEDs controlables y 3 pulsadores,
            todo conectado a un ESP32 que se comunica con una API REST.
          </p>

          <h3 className="font-bold text-lg mb-2">Características Principales:</h3>
          <ul className="list-disc list-inside space-y-2 mb-4">
            <li>Monitoreo en tiempo real del sensor HC-SR05</li>
            <li>Control de 3 LEDs mediante pulsadores físicos o interfaz web</li>
            <li>Teclado matricial 4x4 para control local</li>
            <li>Display LCD I2C para visualización de estados</li>
            <li>Sistema de autenticación con JWT</li>
            <li>Base de datos relacional con 3+ tablas relacionadas</li>
            <li>Generación de reportes en PDF y Excel</li>
            <li>Tablero de indicadores con 4 KPIs y 5 gráficos</li>
            <li>Historial completo de eventos y cambios de estado</li>
          </ul>

          <h3 className="font-bold text-lg mb-2">Módulos del Sistema:</h3>
          <ul className="list-disc list-inside space-y-2">
            <li><strong>Principal:</strong> Dashboard con resumen de estadísticas</li>
            <li><strong>Control:</strong> Gestión de LEDs y visualización de sensores</li>
            <li><strong>Tablero:</strong> Gráficos e indicadores de rendimiento</li>
            <li><strong>Reportes:</strong> Exportación de datos a PDF/Excel</li>
            <li><strong>Acerca de:</strong> Información del proyecto y equipo</li>
          </ul>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold text-gray-800 mb-4">
          Tecnologías Utilizadas
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {tecnologias.map((tech) => (
            <div
              key={tech.nombre}
              className="flex items-start space-x-4 p-4 bg-gray-50 rounded-lg"
            >
              <div className="bg-blue-100 rounded-full p-3">
                <tech.icono className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h3 className="font-bold text-gray-800">{tech.nombre}</h3>
                <p className="text-sm text-gray-600">{tech.descripcion}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold text-gray-800 mb-4">
          Creadores del Proyecto
        </h2>
        <div className="space-y-4">
          {creadores.map((creador) => (
            <div
              key={creador.nombre}
              className="flex items-start space-x-4 p-6 bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg"
            >
              <div className="bg-blue-600 rounded-full p-4">
                <User className="w-8 h-8 text-white" />
              </div>
              <div className="flex-1">
                <h3 className="text-xl font-bold text-gray-800">
                  {creador.nombre}
                </h3>
                <p className="text-blue-600 font-medium mb-3">{creador.rol}</p>
                <div className="space-y-2">
                  <div className="flex items-center space-x-2 text-gray-700">
                    <Mail className="w-4 h-4" />
                    <span className="text-sm">{creador.email}</span>
                  </div>
                  <div className="flex items-center space-x-2 text-gray-700">
                    <Github className="w-4 h-4" />
                    <span className="text-sm">github.com/{creador.github}</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-lg shadow-lg p-6 text-white">
        <h2 className="text-xl font-bold mb-2">Hardware del Proyecto</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
          <div className="bg-white bg-opacity-20 rounded-lg p-4">
            <h3 className="font-bold mb-2">Sensor HC-SR05</h3>
            <p className="text-sm text-blue-100">
              TRIG: GPIO 5 | ECHO: GPIO 18
            </p>
          </div>
          <div className="bg-white bg-opacity-20 rounded-lg p-4">
            <h3 className="font-bold mb-2">LCD I2C</h3>
            <p className="text-sm text-blue-100">
              SDA: GPIO 21 | SCL: GPIO 22
            </p>
          </div>
          <div className="bg-white bg-opacity-20 rounded-lg p-4">
            <h3 className="font-bold mb-2">LEDs</h3>
            <p className="text-sm text-blue-100">
              GPIO 23, 19, 4 (con resistencias 220Ω)
            </p>
          </div>
          <div className="bg-white bg-opacity-20 rounded-lg p-4">
            <h3 className="font-bold mb-2">Pulsadores</h3>
            <p className="text-sm text-blue-100">
              GPIO 15, 2, 13 (pull-down 10kΩ)
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
