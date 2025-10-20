# Sistema HC-SR05 Web - Instrucciones de Instalación y Uso

## Descripción General

Sistema completo de monitoreo y control IoT con:
- ESP32 + Sensor HC-SR05 + LEDs + Pulsadores + Teclado Matricial + LCD I2C
- API REST en Python (Flask) con Supabase
- Aplicación Web en React con Vite

---

## 1. BASE DE DATOS (Supabase)

La base de datos ya está creada con las siguientes tablas:
- `usuarios` - Autenticación de usuarios
- `sensores` - Lecturas del HC-SR05
- `leds` - Estado de los 3 LEDs
- `pulsadores` - Estado de los 3 pulsadores
- `eventos` - Log de eventos del sistema
- `led_hist` - Historial de cambios de LEDs
- `pulsador_hist` - Historial de cambios de pulsadores

**Crear usuario de prueba:**
```sql
-- Ejecutar en Supabase SQL Editor
INSERT INTO usuarios (username, email, password_hash)
VALUES ('admin', 'admin@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5eoWy7TBzhO8S');
-- Contraseña: admin123
```

---

## 2. API REST (Python Flask)

### Instalación:

```bash
cd api
pip install -r requirements.txt
```

### Configuración:

Editar `api/app.py` líneas 9-11 para usar las credenciales de Supabase correctas.

### Ejecutar API:

```bash
cd api
python app.py
```

La API estará disponible en: `http://localhost:5000`

### Endpoints principales:

- `POST /api/auth/login` - Inicio de sesión
- `POST /api/auth/register` - Registro de usuario
- `GET /api/sensores` - Obtener lecturas del sensor
- `POST /api/sensores` - Crear nueva lectura
- `GET /api/leds` - Obtener estado de LEDs
- `PUT /api/leds/{id}` - Actualizar estado de LED
- `GET /api/eventos` - Obtener eventos
- `GET /api/led_hist` - Historial de LEDs

---

## 3. APLICACIÓN WEB (React)

### Instalación:

```bash
cd web
npm install
```

### Configuración:

El archivo `.env` ya tiene las credenciales de Supabase.

### Ejecutar aplicación:

```bash
cd web
npm run dev
```

La aplicación estará disponible en: `http://localhost:5173`

### Credenciales de prueba:
- Usuario: `admin`
- Contraseña: `admin123`

### Módulos:

1. **Login** - Autenticación con JWT
2. **Dashboard** - Panel principal con estadísticas
3. **Control** - Control de LEDs y visualización de sensor
4. **Tablero** - 4 indicadores + 5 gráficos
5. **Reportes** - Exportar datos a PDF/Excel
6. **Acerca de** - Información del proyecto

---

## 4. ESP32

### Hardware necesario:

- ESP32
- Sensor HC-SR05
- LCD I2C (16x2)
- 3 LEDs con resistencias 220Ω
- 3 Pulsadores con resistencias 10kΩ (pull-down)
- Teclado Matricial 4x4

### Conexiones:

```
HC-SR05:
- VCC → 5V
- GND → GND
- TRIG → GPIO 5
- ECHO → GPIO 18

LCD I2C:
- VCC → 5V
- GND → GND
- SDA → GPIO 21
- SCL → GPIO 22

LEDs:
- LED1 → GPIO 23 (con resistencia 220Ω)
- LED2 → GPIO 19 (con resistencia 220Ω)
- LED3 → GPIO 4 (con resistencia 220Ω)

Pulsadores (pull-down con resistencia 10kΩ):
- BTN1 → GPIO 15
- BTN2 → GPIO 2
- BTN3 → GPIO 13

Teclado Matricial 4x4:
- Filas: GPIO 32, 33, 25, 26
- Columnas: GPIO 27, 14, 12, 13
```

### Configuración:

Editar `esp32/esp32_hcsr05_matricial.ino`:

```cpp
const char* ssid = "TU_WIFI_SSID";           // Línea 7
const char* password = "TU_WIFI_PASSWORD";    // Línea 8
const char* apiUrl = "http://TU_IP:5000/api"; // Línea 9 (IP de tu PC donde corre la API)
```

### Librerías necesarias (Arduino IDE):

1. WiFi (incluida)
2. HTTPClient (incluida)
3. ArduinoJson (by Benoit Blanchon)
4. LiquidCrystal_I2C (by Frank de Brabander)

### Funcionalidad del Teclado Matricial:

**Menú Principal:**
- `1` - Control LED
- `2` - Control Sensor
- `3` - Estadísticas BD
- `*` - Volver al menú

**Submenú LED:**
- `1` - Encender LED
- `2` - Apagar LED
- `3` - Ver estado
- `*` - Volver

**Características:**
- Los pulsadores físicos también conmutan los LEDs
- El LCD muestra el nombre del usuario cuando alguien inicia sesión en la web
- Cada 2 segundos envía lectura del sensor a la API
- Todos los cambios se registran en la base de datos

---

## 5. FLUJO DE TRABAJO

1. **Iniciar API:** `python api/app.py`
2. **Iniciar Web:** `npm run dev` (en carpeta web)
3. **Configurar y cargar código ESP32**
4. **Acceder a:** `http://localhost:5173`
5. **Login con:** admin / admin123
6. **El ESP32 se conecta automáticamente a la API**

---

## 6. CARACTERÍSTICAS IMPLEMENTADAS

### ✅ API Python
- CRUD completo para todas las tablas
- CORS configurado para ESP32 y Web
- JWT para autenticación
- Conexión a Supabase

### ✅ Aplicación Web
- Inicio de sesión con JWT y sesiones
- Módulo principal con navegación
- Módulo control de sensor y LEDs
- Tablero con 4 indicadores y 5 gráficos:
  1. Total lecturas
  2. Promedio distancia
  3. Mínimo distancia
  4. Máximo distancia
  5. Gráfico de línea (historial)
  6. Gráfico de barras (rangos)
  7. Gráfico de área (tendencia)
  8. Gráfico circular (fuentes)
  9. Gráfico de barras (LED ON/OFF)
- Módulo reportes PDF/Excel con filtros de fecha
- Módulo acerca de con información del equipo

### ✅ ESP32
- Sensor HC-SR05 envía datos cada 2 segundos
- 3 LEDs controlables por pulsadores, teclado o web
- Teclado matricial 4x4 con menús
- LCD I2C muestra estados y login de usuario
- Todo se refleja en la base de datos

---

## 7. TROUBLESHOOTING

### API no conecta a Supabase:
- Verificar credenciales en `api/app.py`
- Verificar que las tablas existen en Supabase

### Web no carga datos:
- Verificar que la API esté corriendo en puerto 5000
- Verificar URL en `web/src/services/api.js` línea 3

### ESP32 no conecta:
- Verificar WiFi SSID y password
- Verificar IP de la API (debe ser IP local de tu PC, no localhost)
- Verificar que el ESP32 y la PC estén en la misma red

---

## 8. TECNOLOGÍAS UTILIZADAS

- **Frontend:** React 19, Vite, TailwindCSS, Recharts, Axios, jsPDF, XLSX
- **Backend:** Python 3, Flask, Flask-CORS, PyJWT, bcrypt
- **Base de Datos:** Supabase (PostgreSQL)
- **Hardware:** ESP32, HC-SR05, LCD I2C, LEDs, Pulsadores, Teclado Matricial
- **Librerías ESP32:** WiFi, HTTPClient, ArduinoJson, LiquidCrystal_I2C

---

## 9. PRÓXIMOS PASOS

1. Cambiar contraseñas y JWT_SECRET en producción
2. Personalizar información en módulo "Acerca de"
3. Ajustar colores y diseño según preferencias
4. Agregar más sensores o actuadores
5. Implementar notificaciones push
