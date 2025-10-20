from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import bcrypt
from datetime import datetime, timedelta
from functools import wraps
import os
from supabase import create_client, Client

app = Flask(__name__)
CORS(app)

SUPABASE_URL = os.getenv('VITE_SUPABASE_URL', 'https://wnbikudxwxjawbqlqcyc.supabase.co')
SUPABASE_KEY = os.getenv('VITE_SUPABASE_SUPABASE_ANON_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InduYmlrdWR4d3hqYXdicWxxY3ljIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA5MDAzNjksImV4cCI6MjA3NjQ3NjM2OX0.gtmb1rxgwa7qVe9eERYkrrJnAs38MkV-yDKHZwECsTM')
JWT_SECRET = 'tu_clave_secreta_super_segura_cambiar_en_produccion'

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token requerido'}), 401
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            request.user_data = data
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token inválido'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return jsonify({'error': 'Faltan datos requeridos'}), 400

        existing = supabase.table('usuarios').select('*').eq('username', username).execute()
        if existing.data:
            return jsonify({'error': 'Usuario ya existe'}), 400

        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        result = supabase.table('usuarios').insert({
            'username': username,
            'email': email,
            'password_hash': password_hash
        }).execute()

        return jsonify({'message': 'Usuario registrado exitosamente', 'user': result.data[0]}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': 'Usuario y contraseña requeridos'}), 400

        result = supabase.table('usuarios').select('*').eq('username', username).execute()

        if not result.data:
            return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401

        user = result.data[0]

        if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401

        supabase.table('eventos').insert({
            'usuario': username,
            'accion': 'login',
            'detalles': 'Inicio de sesión desde web',
            'fecha': datetime.now().isoformat()
        }).execute()

        token = jwt.encode({
            'user_id': user['id'],
            'username': username,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, JWT_SECRET, algorithm='HS256')

        return jsonify({
            'token': token,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email']
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sensores', methods=['GET'])
def get_sensores():
    try:
        limit = request.args.get('limit', 100)
        result = supabase.table('sensores').select('*').order('fecha', desc=True).limit(limit).execute()
        return jsonify(result.data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sensores', methods=['POST'])
def create_sensor():
    try:
        data = request.json
        tipo = data.get('tipo', 'HC-SR05')
        valor = data.get('valor')
        usuario_id = data.get('usuario_id')

        if valor is None:
            return jsonify({'error': 'Valor requerido'}), 400

        result = supabase.table('sensores').insert({
            'tipo': tipo,
            'valor': valor,
            'usuario_id': usuario_id,
            'fecha': datetime.now().isoformat()
        }).execute()

        return jsonify(result.data[0]), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sensores/estadisticas', methods=['GET'])
def get_estadisticas():
    try:
        result = supabase.table('sensores').select('*').order('fecha', desc=True).limit(1000).execute()

        if not result.data:
            return jsonify({
                'total': 0,
                'promedio': 0,
                'minimo': 0,
                'maximo': 0
            }), 200

        valores = [float(s['valor']) for s in result.data]

        return jsonify({
            'total': len(valores),
            'promedio': sum(valores) / len(valores),
            'minimo': min(valores),
            'maximo': max(valores)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/leds', methods=['GET'])
def get_leds():
    try:
        result = supabase.table('leds').select('*').order('id').execute()
        return jsonify(result.data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/leds/<int:led_id>', methods=['PUT'])
def update_led(led_id):
    try:
        data = request.json
        estado = data.get('estado')
        usuario = data.get('usuario', 'API')
        fuente = data.get('fuente', 'WEB')

        result = supabase.table('leds').update({
            'estado': estado
        }).eq('id', led_id).execute()

        supabase.table('led_hist').insert({
            'usuario': usuario,
            'led_id': led_id,
            'estado': estado,
            'fuente': fuente,
            'fecha': datetime.now().isoformat()
        }).execute()

        supabase.table('eventos').insert({
            'usuario': usuario,
            'accion': 'led_toggle',
            'detalles': f'LED {led_id} -> {"ON" if estado else "OFF"} ({fuente})',
            'fecha': datetime.now().isoformat()
        }).execute()

        return jsonify(result.data[0]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pulsadores', methods=['GET'])
def get_pulsadores():
    try:
        result = supabase.table('pulsadores').select('*').order('id').execute()
        return jsonify(result.data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pulsadores/<int:pulsador_id>', methods=['PUT'])
def update_pulsador(pulsador_id):
    try:
        data = request.json
        estado = data.get('estado')
        usuario = data.get('usuario', 'API')
        fuente = data.get('fuente', 'WEB')

        result = supabase.table('pulsadores').update({
            'estado': estado
        }).eq('id', pulsador_id).execute()

        supabase.table('pulsador_hist').insert({
            'usuario': usuario,
            'pulsador_id': pulsador_id,
            'estado': estado,
            'fuente': fuente,
            'fecha': datetime.now().isoformat()
        }).execute()

        return jsonify(result.data[0]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/eventos', methods=['GET'])
def get_eventos():
    try:
        limit = request.args.get('limit', 50)
        result = supabase.table('eventos').select('*').order('fecha', desc=True).limit(limit).execute()
        return jsonify(result.data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/led_hist', methods=['GET'])
def get_led_hist():
    try:
        limit = request.args.get('limit', 100)
        result = supabase.table('led_hist').select('*').order('fecha', desc=True).limit(limit).execute()
        return jsonify(result.data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pulsador_hist', methods=['GET'])
def get_pulsador_hist():
    try:
        limit = request.args.get('limit', 100)
        result = supabase.table('pulsador_hist').select('*').order('fecha', desc=True).limit(limit).execute()
        return jsonify(result.data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'OK', 'message': 'API funcionando correctamente'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
