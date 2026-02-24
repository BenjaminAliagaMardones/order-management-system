import axios from 'axios'

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
    headers: { 'Content-Type': 'application/json' },
    timeout: 15000,
})

// Interceptor: extrae el mensaje de error de FastAPI
api.interceptors.response.use(
    (res) => res,
    (err) => {
        const msg =
            err.response?.data?.detail ||
            err.response?.data?.message ||
            err.message ||
            'Error desconocido'
        return Promise.reject(new Error(typeof msg === 'string' ? msg : JSON.stringify(msg)))
    }
)

/* ── Clientes ─────────────────────────────────────────────── */
export const clientesApi = {
    listar: (params = {}) => api.get('/clientes/', { params }),
    obtener: (id) => api.get(`/clientes/${id}`),
    crear: (data) => api.post('/clientes/', data),
    actualizar: (id, data) => api.patch(`/clientes/${id}`, data),
    eliminar: (id) => api.delete(`/clientes/${id}`),
}

/* ── Pedidos ──────────────────────────────────────────────── */
export const pedidosApi = {
    listar: (params = {}) => api.get('/pedidos/', { params }),
    obtener: (id) => api.get(`/pedidos/${id}`),
    crear: (data) => api.post('/pedidos/', data),
    actualizarEstado: (id, estado) => api.patch(`/pedidos/${id}/estado`, { estado }),
    eliminar: (id) => api.delete(`/pedidos/${id}`),
}

export default api
