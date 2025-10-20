import axios from 'axios'

const API_BASE_URL = 'http://localhost:5000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const authAPI = {
  login: (username, password) => api.post('/auth/login', { username, password }),
  register: (username, email, password) => api.post('/auth/register', { username, email, password }),
}

export const sensoresAPI = {
  getAll: (limit = 100) => api.get(`/sensores?limit=${limit}`),
  create: (data) => api.post('/sensores', data),
  getEstadisticas: () => api.get('/sensores/estadisticas'),
}

export const ledsAPI = {
  getAll: () => api.get('/leds'),
  update: (id, estado, usuario, fuente = 'WEB') =>
    api.put(`/leds/${id}`, { estado, usuario, fuente }),
}

export const pulsadoresAPI = {
  getAll: () => api.get('/pulsadores'),
  update: (id, estado, usuario, fuente = 'WEB') =>
    api.put(`/pulsadores/${id}`, { estado, usuario, fuente }),
}

export const eventosAPI = {
  getAll: (limit = 50) => api.get(`/eventos?limit=${limit}`),
}

export const historialAPI = {
  getLedHist: (limit = 100) => api.get(`/led_hist?limit=${limit}`),
  getPulsadorHist: (limit = 100) => api.get(`/pulsador_hist?limit=${limit}`),
}

export default api
