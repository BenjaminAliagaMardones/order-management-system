import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { pedidosApi, clientesApi } from '@/api'
import { Spinner, Alert, EmptyState, ConfirmModal, Badge } from '@/components/UI'

const fmt = (n, dec = 2) =>
    Number(n).toLocaleString('es-CL', { minimumFractionDigits: dec, maximumFractionDigits: dec })

const ESTADOS = ['pendiente', 'en_bodega', 'enviado']

export default function Pedidos() {
    const nav = useNavigate()
    const [pedidos, setPedidos] = useState([])
    const [clientes, setClientes] = useState({})
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')
    const [filtroEstado, setFiltroEstado] = useState('')
    const [confirm, setConfirm] = useState(null)
    const [deleting, setDeleting] = useState(false)

    const cargar = async () => {
        setLoading(true); setError('')
        try {
            const params = { limit: 200 }
            if (filtroEstado) params.estado = filtroEstado
            const [rp, rc] = await Promise.all([
                pedidosApi.listar(params),
                clientesApi.listar({ limit: 200 }),
            ])
            setPedidos(rp.data)
            // mapa id → nombre
            const mapa = {}
            rc.data.forEach(c => { mapa[c.id] = c.nombre })
            setClientes(mapa)
        } catch (e) {
            setError(e.message)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => { cargar() }, [filtroEstado])

    const eliminar = async () => {
        setDeleting(true)
        try { await pedidosApi.eliminar(confirm.id); setConfirm(null); cargar() }
        catch (e) { setError(e.message); setConfirm(null) }
        finally { setDeleting(false) }
    }

    const avanzarEstado = async (pedido) => {
        const siguiente = { pendiente: 'en_bodega', en_bodega: 'enviado' }
        const next = siguiente[pedido.estado]
        if (!next) return
        try { await pedidosApi.actualizarEstado(pedido.id, next); cargar() }
        catch (e) { setError(e.message) }
    }

    return (
        <div>
            <div className="page-header">
                <div>
                    <h1 className="page-title">📦 Pedidos</h1>
                    <p className="page-subtitle">{pedidos.length} pedido{pedidos.length !== 1 ? 's' : ''}</p>
                </div>
                <div style={{ display: 'flex', gap: '.75rem', alignItems: 'center' }}>
                    <select
                        className="form-input"
                        style={{ width: 'auto' }}
                        value={filtroEstado}
                        onChange={e => setFiltroEstado(e.target.value)}
                    >
                        <option value="">Todos los estados</option>
                        {ESTADOS.map(e => <option key={e} value={e}>{e.replace('_', ' ')}</option>)}
                    </select>
                    <button className="btn btn-primary" onClick={() => nav('/pedidos/nuevo')}>
                        + Nuevo pedido
                    </button>
                </div>
            </div>

            {error && <Alert type="error" style={{ marginBottom: '1rem' }}>{error}</Alert>}

            {loading ? <Spinner /> : pedidos.length === 0 ? (
                <EmptyState icon="📦" message="No hay pedidos. ¡Crea el primero!" />
            ) : (
                <div className="card" style={{ padding: 0 }}>
                    <div className="table-wrap">
                        <table>
                            <thead>
                                <tr>
                                    <th>Cliente</th>
                                    <th>Estado</th>
                                    <th>Total USD</th>
                                    <th>Total CLP</th>
                                    <th>TC USD</th>
                                    <th>Fecha</th>
                                    <th style={{ width: '140px' }}>Acciones</th>
                                </tr>
                            </thead>
                            <tbody>
                                {pedidos.map(p => (
                                    <tr key={p.id} style={{ cursor: 'pointer' }}>
                                        <td style={{ fontWeight: 600 }}>
                                            {clientes[p.cliente_id] || p.cliente_id.slice(0, 8) + '…'}
                                        </td>
                                        <td><Badge estado={p.estado} /></td>
                                        <td>${fmt(p.total_usd)}</td>
                                        <td>${fmt(p.total_clp, 0)}</td>
                                        <td style={{ color: 'var(--clr-text-muted)', fontSize: '.8rem' }}>
                                            ${fmt(p.valor_dolar)}
                                        </td>
                                        <td style={{ color: 'var(--clr-text-muted)', fontSize: '.8rem' }}>
                                            {new Date(p.created_at).toLocaleDateString('es-CL')}
                                        </td>
                                        <td>
                                            <div style={{ display: 'flex', gap: '.4rem' }}>
                                                <button
                                                    className="btn btn-ghost btn-sm"
                                                    onClick={() => nav(`/pedidos/${p.id}`)}
                                                    title="Ver detalle"
                                                >🔍</button>
                                                {p.estado !== 'enviado' && (
                                                    <button
                                                        className="btn btn-ghost btn-sm"
                                                        onClick={() => avanzarEstado(p)}
                                                        title={`Avanzar a ${p.estado === 'pendiente' ? 'en bodega' : 'enviado'}`}
                                                    >⏭️</button>
                                                )}
                                                {p.estado === 'pendiente' && (
                                                    <button
                                                        className="btn btn-danger btn-sm"
                                                        onClick={() => setConfirm(p)}
                                                        title="Eliminar pedido"
                                                    >🗑️</button>
                                                )}
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {confirm && (
                <ConfirmModal
                    title="Eliminar pedido"
                    message="¿Eliminar este pedido? Se eliminarán también todos sus productos. Esta acción no se puede deshacer."
                    onConfirm={eliminar}
                    onCancel={() => setConfirm(null)}
                    loading={deleting}
                />
            )}
        </div>
    )
}
