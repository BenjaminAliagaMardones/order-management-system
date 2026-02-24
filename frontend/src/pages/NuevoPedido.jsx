import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { pedidosApi, clientesApi } from '@/api'
import { Alert } from '@/components/UI'

const EMPTY_ITEM = () => ({
    nombre_producto: '',
    cantidad: 1,
    precio_base_usd: '',
    porcentaje_tax: '10',
    porcentaje_comision: '5',
})

const fmt = (n) =>
    Number(n).toLocaleString('es-CL', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

function calcItem(item) {
    const base = Number(item.precio_base_usd) || 0
    const tax = parseFloat(item.porcentaje_tax) || 0
    const com = parseFloat(item.porcentaje_comision) || 0
    const qty = parseInt(item.cantidad) || 1
    const taxUSD = base * tax / 100
    const comUSD = (base + taxUSD) * com / 100
    const finalUSD = base + taxUSD + comUSD
    const subtotal = finalUSD * qty
    return { taxUSD, comUSD, finalUSD, subtotal }
}

export default function NuevoPedido() {
    const nav = useNavigate()
    const [clientes, setClientes] = useState([])
    const [clienteId, setClienteId] = useState('')
    const [valorDolar, setValorDolar] = useState('')
    const [items, setItems] = useState([EMPTY_ITEM()])
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)

    useEffect(() => {
        clientesApi.listar({ limit: 200 }).then(r => {
            setClientes(r.data)
            if (r.data.length > 0) setClienteId(r.data[0].id)
        })
    }, [])

    const setItem = (i, key) => (e) =>
        setItems(it => it.map((x, idx) => idx === i ? { ...x, [key]: e.target.value } : x))

    const addItem = () => setItems(it => [...it, EMPTY_ITEM()])
    const removeItem = (i) => setItems(it => it.filter((_, idx) => idx !== i))

    const totalUSD = items.reduce((s, it) => s + calcItem(it).subtotal, 0)
    const totalCLP = totalUSD * (Number(valorDolar) || 0)

    const submit = async (e) => {
        e.preventDefault()
        setError(''); setLoading(true)
        try {
            const payload = {
                cliente_id: clienteId,
                valor_dolar: Number(valorDolar),
                detalles: items.map(it => ({
                    nombre_producto: it.nombre_producto,
                    cantidad: Number(it.cantidad),
                    precio_base_usd: Number(it.precio_base_usd),
                    porcentaje_tax: Number(it.porcentaje_tax),
                    porcentaje_comision: Number(it.porcentaje_comision),
                })),
            }
            const r = await pedidosApi.crear(payload)
            nav(`/pedidos/${r.data.id}`)
        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div>
            <div className="page-header">
                <div>
                    <h1 className="page-title">➕ Nuevo pedido</h1>
                    <p className="page-subtitle">Completa los datos del pedido</p>
                </div>
                <button className="btn btn-ghost" onClick={() => nav('/pedidos')}>← Volver</button>
            </div>

            {error && <Alert type="error" style={{ marginBottom: '1rem' }}>{error}</Alert>}

            <form onSubmit={submit}>
                {/* Datos generales */}
                <div className="card" style={{ marginBottom: '1.25rem' }}>
                    <h2 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '1rem' }}>📋 Datos generales</h2>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                        <div className="form-group">
                            <label className="form-label">Cliente *</label>
                            <select
                                className="form-input"
                                value={clienteId}
                                onChange={e => setClienteId(e.target.value)}
                                required
                            >
                                {clientes.map(c => (
                                    <option key={c.id} value={c.id}>{c.nombre} · {c.telefono}</option>
                                ))}
                            </select>
                        </div>
                        <div className="form-group">
                            <label className="form-label">Tipo de cambio (USD→CLP) *</label>
                            <input
                                className="form-input"
                                type="number"
                                step="0.01"
                                min="1"
                                value={valorDolar}
                                onChange={e => setValorDolar(e.target.value)}
                                required
                                placeholder="ej: 970.50"
                            />
                        </div>
                    </div>
                </div>

                {/* Productos */}
                <div className="card" style={{ marginBottom: '1.25rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                        <h2 style={{ fontSize: '1rem', fontWeight: 700 }}>🛒 Productos</h2>
                        <button type="button" className="btn btn-ghost btn-sm" onClick={addItem}>+ Agregar</button>
                    </div>

                    {items.map((item, i) => {
                        const calc = calcItem(item)
                        return (
                            <div key={i} style={{
                                background: 'var(--clr-surface-2)',
                                border: '1px solid var(--clr-border)',
                                borderRadius: 'var(--radius-md)',
                                padding: '1rem',
                                marginBottom: '.75rem',
                            }}>
                                <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr 1fr 1fr auto', gap: '.75rem', alignItems: 'end' }}>
                                    <div className="form-group">
                                        <label className="form-label">Producto *</label>
                                        <input className="form-input" value={item.nombre_producto} onChange={setItem(i, 'nombre_producto')} required placeholder="iPhone 15 Pro..." />
                                    </div>
                                    <div className="form-group">
                                        <label className="form-label">Cantidad</label>
                                        <input className="form-input" type="number" min="1" value={item.cantidad} onChange={setItem(i, 'cantidad')} required />
                                    </div>
                                    <div className="form-group">
                                        <label className="form-label">Precio base USD</label>
                                        <input className="form-input" type="number" step="0.01" min="0.01" value={item.precio_base_usd} onChange={setItem(i, 'precio_base_usd')} required placeholder="0.00" />
                                    </div>
                                    <div className="form-group">
                                        <label className="form-label">Tax %</label>
                                        <input className="form-input" type="number" step="0.01" min="0" max="100" value={item.porcentaje_tax} onChange={setItem(i, 'porcentaje_tax')} />
                                    </div>
                                    <div className="form-group">
                                        <label className="form-label">Comisión %</label>
                                        <input className="form-input" type="number" step="0.01" min="0" max="100" value={item.porcentaje_comision} onChange={setItem(i, 'porcentaje_comision')} />
                                    </div>
                                    <button
                                        type="button"
                                        className="btn btn-danger btn-sm"
                                        onClick={() => removeItem(i)}
                                        disabled={items.length === 1}
                                        style={{ marginBottom: '0' }}
                                    >✕</button>
                                </div>
                                {/* Preview calculado */}
                                {item.precio_base_usd > 0 && (
                                    <div style={{ marginTop: '.75rem', display: 'flex', gap: '1.5rem', fontSize: '.78rem', color: 'var(--clr-text-muted)' }}>
                                        <span>Tax: <strong style={{ color: 'var(--clr-text)' }}>${fmt(calc.taxUSD)}</strong></span>
                                        <span>Comisión: <strong style={{ color: 'var(--clr-text)' }}>${fmt(calc.comUSD)}</strong></span>
                                        <span>Precio final: <strong style={{ color: 'var(--clr-text)' }}>${fmt(calc.finalUSD)}</strong></span>
                                        <span>Subtotal: <strong style={{ color: 'var(--clr-accent)' }}>${fmt(calc.subtotal)}</strong></span>
                                    </div>
                                )}
                            </div>
                        )
                    })}
                </div>

                {/* Resumen totales */}
                <div className="card" style={{ marginBottom: '1.5rem' }}>
                    <h2 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '1rem' }}>💰 Resumen</h2>
                    <div style={{ display: 'flex', gap: '2.5rem' }}>
                        <div>
                            <div style={{ fontSize: '.75rem', color: 'var(--clr-text-muted)', textTransform: 'uppercase', letterSpacing: '.05em' }}>Total USD</div>
                            <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--clr-primary)' }}>${fmt(totalUSD)}</div>
                        </div>
                        <div>
                            <div style={{ fontSize: '.75rem', color: 'var(--clr-text-muted)', textTransform: 'uppercase', letterSpacing: '.05em' }}>Total CLP</div>
                            <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--clr-accent)' }}>
                                {valorDolar ? `$${Number(totalCLP).toLocaleString('es-CL', { maximumFractionDigits: 0 })}` : '—'}
                            </div>
                        </div>
                    </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '.75rem' }}>
                    <button type="button" className="btn btn-ghost" onClick={() => nav('/pedidos')}>Cancelar</button>
                    <button type="submit" className="btn btn-primary" disabled={loading}>
                        {loading ? 'Creando pedido…' : '✅ Crear pedido'}
                    </button>
                </div>
            </form>
        </div>
    )
}
