/*
  # Schema Inicial del Sistema HC-SR05

  1. Tablas Nuevas
    - `usuarios`
      - `id` (uuid, primary key)
      - `username` (text, unique, not null)
      - `email` (text, unique, not null)
      - `password_hash` (text, not null)
      - `created_at` (timestamp with timezone, default now())
    
    - `sensores`
      - `id` (bigint, primary key, auto-increment)
      - `usuario_id` (uuid, foreign key to usuarios)
      - `tipo` (text, not null, default 'HC-SR05')
      - `valor` (numeric, not null)
      - `fecha` (timestamp with timezone, default now())
    
    - `leds`
      - `id` (integer, primary key)
      - `nombre` (text, not null)
      - `estado` (boolean, default false)
      - `color` (text)
    
    - `pulsadores`
      - `id` (integer, primary key)
      - `nombre` (text, not null)
      - `estado` (boolean, default false)
    
    - `eventos`
      - `id` (bigint, primary key, auto-increment)
      - `usuario` (text, not null)
      - `accion` (text, not null)
      - `detalles` (text)
      - `fecha` (timestamp with timezone, default now())
    
    - `led_hist`
      - `id` (bigint, primary key, auto-increment)
      - `usuario` (text, not null)
      - `led_id` (integer, not null)
      - `estado` (boolean, not null)
      - `fuente` (text, not null) -- 'UI' or 'HW'
      - `fecha` (timestamp with timezone, default now())
    
    - `pulsador_hist`
      - `id` (bigint, primary key, auto-increment)
      - `usuario` (text, not null)
      - `pulsador_id` (integer, not null)
      - `estado` (boolean, not null)
      - `fuente` (text, not null) -- 'UI' or 'HW'
      - `fecha` (timestamp with timezone, default now())

  2. Seguridad
    - Habilitar RLS en todas las tablas
    - Políticas para usuarios autenticados
    - Políticas restrictivas para acceso de datos propios

  3. Datos Iniciales
    - Crear 3 LEDs (Rojo, Verde, Azul)
    - Crear 3 Pulsadores
*/

-- Crear tabla usuarios
CREATE TABLE IF NOT EXISTS usuarios (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  username text UNIQUE NOT NULL,
  email text UNIQUE NOT NULL,
  password_hash text NOT NULL,
  created_at timestamptz DEFAULT now()
);

-- Crear tabla sensores
CREATE TABLE IF NOT EXISTS sensores (
  id bigserial PRIMARY KEY,
  usuario_id uuid REFERENCES usuarios(id) ON DELETE SET NULL,
  tipo text NOT NULL DEFAULT 'HC-SR05',
  valor numeric NOT NULL,
  fecha timestamptz DEFAULT now()
);

-- Crear tabla leds
CREATE TABLE IF NOT EXISTS leds (
  id integer PRIMARY KEY,
  nombre text NOT NULL,
  estado boolean DEFAULT false,
  color text
);

-- Crear tabla pulsadores
CREATE TABLE IF NOT EXISTS pulsadores (
  id integer PRIMARY KEY,
  nombre text NOT NULL,
  estado boolean DEFAULT false
);

-- Crear tabla eventos
CREATE TABLE IF NOT EXISTS eventos (
  id bigserial PRIMARY KEY,
  usuario text NOT NULL,
  accion text NOT NULL,
  detalles text,
  fecha timestamptz DEFAULT now()
);

-- Crear tabla led_hist
CREATE TABLE IF NOT EXISTS led_hist (
  id bigserial PRIMARY KEY,
  usuario text NOT NULL,
  led_id integer NOT NULL,
  estado boolean NOT NULL,
  fuente text NOT NULL,
  fecha timestamptz DEFAULT now()
);

-- Crear tabla pulsador_hist
CREATE TABLE IF NOT EXISTS pulsador_hist (
  id bigserial PRIMARY KEY,
  usuario text NOT NULL,
  pulsador_id integer NOT NULL,
  estado boolean NOT NULL,
  fuente text NOT NULL,
  fecha timestamptz DEFAULT now()
);

-- Crear índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_sensores_fecha ON sensores(fecha DESC);
CREATE INDEX IF NOT EXISTS idx_sensores_usuario ON sensores(usuario_id);
CREATE INDEX IF NOT EXISTS idx_eventos_fecha ON eventos(fecha DESC);
CREATE INDEX IF NOT EXISTS idx_led_hist_fecha ON led_hist(fecha DESC);
CREATE INDEX IF NOT EXISTS idx_pulsador_hist_fecha ON pulsador_hist(fecha DESC);

-- Insertar datos iniciales LEDs
INSERT INTO leds (id, nombre, estado, color) VALUES
  (1, 'LED Rojo', false, '#e74c3c'),
  (2, 'LED Verde', false, '#2ecc71'),
  (3, 'LED Azul', false, '#3498db')
ON CONFLICT (id) DO NOTHING;

-- Insertar datos iniciales Pulsadores
INSERT INTO pulsadores (id, nombre, estado) VALUES
  (1, 'Pulsador 1', false),
  (2, 'Pulsador 2', false),
  (3, 'Pulsador 3', false)
ON CONFLICT (id) DO NOTHING;

-- Habilitar RLS en todas las tablas
ALTER TABLE usuarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE sensores ENABLE ROW LEVEL SECURITY;
ALTER TABLE leds ENABLE ROW LEVEL SECURITY;
ALTER TABLE pulsadores ENABLE ROW LEVEL SECURITY;
ALTER TABLE eventos ENABLE ROW LEVEL SECURITY;
ALTER TABLE led_hist ENABLE ROW LEVEL SECURITY;
ALTER TABLE pulsador_hist ENABLE ROW LEVEL SECURITY;

-- Políticas para usuarios
CREATE POLICY "Users can read own data"
  ON usuarios FOR SELECT
  TO authenticated
  USING (auth.uid() = id);

CREATE POLICY "Users can update own data"
  ON usuarios FOR UPDATE
  TO authenticated
  USING (auth.uid() = id)
  WITH CHECK (auth.uid() = id);

-- Políticas para sensores
CREATE POLICY "Authenticated users can read all sensors"
  ON sensores FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Authenticated users can insert sensors"
  ON sensores FOR INSERT
  TO authenticated
  WITH CHECK (true);

-- Políticas para leds (lectura/escritura pública para ESP32)
CREATE POLICY "Anyone can read leds"
  ON leds FOR SELECT
  USING (true);

CREATE POLICY "Authenticated users can update leds"
  ON leds FOR UPDATE
  TO authenticated
  USING (true)
  WITH CHECK (true);

-- Políticas para pulsadores (lectura/escritura pública para ESP32)
CREATE POLICY "Anyone can read pulsadores"
  ON pulsadores FOR SELECT
  USING (true);

CREATE POLICY "Authenticated users can update pulsadores"
  ON pulsadores FOR UPDATE
  TO authenticated
  USING (true)
  WITH CHECK (true);

-- Políticas para eventos
CREATE POLICY "Authenticated users can read all eventos"
  ON eventos FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Authenticated users can insert eventos"
  ON eventos FOR INSERT
  TO authenticated
  WITH CHECK (true);

-- Políticas para led_hist
CREATE POLICY "Authenticated users can read all led_hist"
  ON led_hist FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Authenticated users can insert led_hist"
  ON led_hist FOR INSERT
  TO authenticated
  WITH CHECK (true);

-- Políticas para pulsador_hist
CREATE POLICY "Authenticated users can read all pulsador_hist"
  ON pulsador_hist FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Authenticated users can insert pulsador_hist"
  ON pulsador_hist FOR INSERT
  TO authenticated
  WITH CHECK (true);