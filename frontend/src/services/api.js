import axios from 'axios'

const BASE =
  import.meta.env.VITE_API_BASE_URL ??
  'https://legal-aid-ai-4.onrender.com'
const api = axios.create({ baseURL: BASE, timeout: 45000 })

api.interceptors.response.use(
  (r) => r,
  (err) => {
    const msg =
      err.response?.data?.detail ??
      (err.code === 'ECONNABORTED' ? 'Request timed out — please try again.' : 'Network error.')
    return Promise.reject(new Error(msg))
  }
)

export const sendMessage = (payload) => api.post('/chat/', payload).then((r) => r.data)
export const transcribeAudio = (payload) => api.post('/chat/transcribe', payload).then((r) => r.data)
export const fetchDomains = () => api.get('/legal/domains').then((r) => r.data)
export const fetchHealth = () => api.get('/health').then((r) => r.data)
export const fetchNearbyCenters = (lat, lon) =>
  api.get('/location/centers', { params: { lat, lon } }).then((r) => r.data)
export const searchLegal = (payload) => api.post('/legal/search', payload).then((r) => r.data)
export const uploadLaw = (formData) =>
  api.post('/admin/upload-law', formData, { headers: { 'Content-Type': 'multipart/form-data' }, timeout: 120000 }).then((r) => r.data)
