import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { pedidosApi } from '@/api'
import { Spinner, Alert, Badge } from '@/components/UI'

const fmt = (n, dec = 2) =>
    Number(n).toLocaleString('es-CL', { minimumFractionDigits: dec, maximumFractionDigits: dec })

const SIGUIENTE = { pendiente: 'en_bodega', en_bodega: 'enviado' }
const ETIQUETA = { en_bodega: '📥 Marcar en bodega', enviado: '✈️ Marcar como enviado' }

export default function DetallePedido() {
    const { id } = useParams()
    const nav = useNavigate()
    const [pedido, setPedido] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')
    const [updating, setUpdating] = useState(false)

    const cargar = async () => {
        setLoading(true)
        try { const r = await pedidosApi.obtener(id); setPedido(r.data) }
        catch (e) { setError(e.message) }
        finally { setLoading(false) }
    }

    useEffect(() => { cargar() }, [id])

    const avanzar = async () => {
        const next = SIGUIENTE[pedido.estado]
        if (!next) return
        setUpdating(true)
        try { await pedidosApi.actualizarEstado(id, next); cargar() }
        catch (e) { setError(e.message) }
        finally { setUpdating(false) }
    }

    if (loading) return <Spinner />
    if (!pedido) return <Alert type="error">{error || 'Pedido no encontrado'}</Alert>

    const nextEstado = SIGUIENTE[pedido.estado]

    return (
        <div>
            <div className="page-header">
                <div>
                    <h1 className="page-title">🔍 Detalle del pedido</h1>
                    <p className="page-subtitle" style={{ fontFamily: 'monospace', fontSize: '.8rem' }}>{pedido.id}</p>
                </div>
                <div style={{ display: 'flex', gap: '.75rem', alignItems: 'center' }}>
                    {nextEstado && (
                        <button className="btn btn-primary" onClick={avanzar} disabled={updating}>
                            {updating ? 'Actualizando…' : ETIQUETA[nextEstado]}
                        </button>
                    )}
                    <button className="btn btn-ghost" onClick={() => nav('/pedidos')}>← Volver</button>
                </div>
            </div>

            {error && <Alert type="error" style={{ marginBottom: '1rem' }}>{error}</Alert>}

            {/* Info general */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.25rem' }}>
                <div className="card">
                    <h3 style={{ fontSize: '.85rem', fontWeight: 700, color: 'var(--clr-text-muted)', marginBottom: '.85rem', textTransform: 'uppercase', letterSpacing: '.05em' }}>
                        Información general
                    </h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '.6rem' }}>
                        {[
                            ['Estado', <Badge estado={pedido.estado} />],
                            ['Tipo de cambio', `$${fmt(pedido.valor_dolar)} CLP/USD`],
                            ['Fecha', new Date(pedido.created_at).toLocaleString('es-CL')],
                        ].map(([k, v]) => (
                            <div key={k} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '.875rem' }}>
                                <span style={{ color: 'var(--clr-text-muted)' }}>{k}</span>
                                <span style={{ fontWeight: 600 }}>{v}</span>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="card">
                    <h3 style={{ fontSize: '.85rem', fontWeight: 700, color: 'var(--clr-text-muted)', marginBottom: '.85rem', textTransform: 'uppercase', letterSpacing: '.05em' }}>
                        Totales
                    </h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '.6rem' }}>
                        {[
                            ['Subtotal USD', `$${fmt(pedido.subtotal_usd)}`],
                            ['Total USD', `$${fmt(pedido.total_usd)}`],
                            ['Total CLP', `$${fmt(pedido.total_clp, 0)}`],
                        ].map(([k, v], idx) => (
                            <div key={k} style={{ display: 'flex', justifyContent: 'space-between', fontSize: idx === 2 ? '1rem' : '.875rem' }}>
                                <span style={{ color: 'var(--clr-text-muted)' }}>{k}</span>
                                <span style={{ fontWeight: 700, color: idx === 2 ? 'var(--clr-accent)' : idx === 1 ? 'var(--clr-primary)' : 'var(--clr-text)' }}>{v}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Tabla de detalles */}
            <div className="card" style={{ padding: 0 }}>
                <div style={{ padding: '1.25rem 1.5rem', borderBottom: '1px solid var(--clr-border)' }}>
                    <h2 style={{ fontSize: '1rem', fontWeight: 700 }}>
                        🛒 Productos ({pedido.detalles?.length || 0})
                    </h2>
                </div>
                <div className="table-wrap" style={{ borderRadius: 0, border: 'none' }}>
                    <table>
                        <thead>
                            <tr>
                                <th>Producto</th>
                                <th>Cant.</th>
                                <th>Precio base</th>
                                <th>Tax %</th>
                                <th>Tax USD</th>
                                <th>Com. %</th>
                                <th>Com. USD</th>
                                <th>Precio final</th>
                                <th>Subtotal</th>
                            </tr>
                        </thead>
                        <tbody>
                            {pedido.detalles?.map(d => (
                                <tr key={d.id}>
                                    <td style={{ fontWeight: 600, maxWidth: '200px' }}>{d.nombre_producto}</td>
                                    <td style={{ textAlign: 'center' }}>{d.cantidad}</td>
                                    <td>${fmt(d.precio_base_usd)}</td>
                                    <td style={{ color: 'var(--clr-text-muted)' }}>{fmt(d.porcentaje_tax)}%</td>
                                    <td>${fmt(d.tax_usd)}</td>
                                    <td style={{ color: 'var(--clr-text-muted)' }}>{fmt(d.porcentaje_comision)}%</td>
                                    <td>${fmt(d.comision_usd)}</td>
                                    <td style={{ color: 'var(--clr-primary)', fontWeight: 600 }}>${fmt(d.precio_final_usd)}</td>
                                    <td style={{ color: 'var(--clr-accent)', fontWeight: 700 }}>${fmt(d.subtotal_usd)}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    )
}
