import { useEffect, useState } from 'react'
import { pedidosApi, clientesApi } from '@/api'
import { Spinner } from '@/components/UI'

function StatCard({ label, value, sub, color = 'var(--clr-primary)' }) {
    return (
        <div className="stat-card">
            <div className="stat-label">{label}</div>
            <div className="stat-value" style={{ color }}>{value}</div>
            {sub && <div className="stat-sub">{sub}</div>}
        </div>
    )
}

const fmt = (n, dec = 2) =>
    Number(n).toLocaleString('es-CL', { minimumFractionDigits: dec, maximumFractionDigits: dec })

export default function Dashboard() {
    const [pedidos, setPedidos] = useState([])
    const [clientes, setClientes] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        Promise.all([
            pedidosApi.listar({ limit: 200 }),
            clientesApi.listar({ limit: 200 }),
        ]).then(([p, c]) => {
            setPedidos(p.data)
            setClientes(c.data)
        }).finally(() => setLoading(false))
    }, [])

    if (loading) return <Spinner />

    const totalUSD = pedidos.reduce((s, p) => s + Number(p.total_usd), 0)
    const totalCLP = pedidos.reduce((s, p) => s + Number(p.total_clp), 0)
    const pendiente = pedidos.filter(p => p.estado === 'pendiente').length
    const en_bodega = pedidos.filter(p => p.estado === 'en_bodega').length
    const enviado = pedidos.filter(p => p.estado === 'enviado').length

    return (
        <div>
            <div className="page-header">
                <div>
                    <h1 className="page-title">📊 Dashboard</h1>
                    <p className="page-subtitle">Resumen general del negocio</p>
                </div>
            </div>

            {/* KPIs */}
            <div className="stats-grid">
                <StatCard label="Total vendido" value={`$${fmt(totalUSD)}`} sub="USD acumulado" color="var(--clr-primary)" />
                <StatCard label="Total en CLP" value={`$${fmt(totalCLP, 0)}`} sub="Pesos chilenos" color="var(--clr-accent)" />
                <StatCard label="Pedidos totales" value={pedidos.length} sub={`${clientes.length} clientes`} />
                <StatCard label="Pendientes" value={pendiente} color="var(--clr-warning)" />
                <StatCard label="En bodega" value={en_bodega} color="var(--clr-primary)" />
                <StatCard label="Enviados" value={enviado} color="var(--clr-accent)" />
            </div>

            {/* Últimos pedidos */}
            <div className="card">
                <h2 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '1rem' }}>
                    🕐 Últimos 10 pedidos
                </h2>
                {pedidos.length === 0 ? (
                    <p style={{ color: 'var(--clr-text-muted)', fontSize: '.875rem' }}>Sin pedidos aún.</p>
                ) : (
                    <div className="table-wrap">
                        <table>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Estado</th>
                                    <th>Total USD</th>
                                    <th>Total CLP</th>
                                    <th>Fecha</th>
                                </tr>
                            </thead>
                            <tbody>
                                {pedidos.slice(0, 10).map(p => (
                                    <tr key={p.id}>
                                        <td style={{ fontFamily: 'monospace', fontSize: '.78rem', color: 'var(--clr-text-muted)' }}>
                                            {p.id.slice(0, 8)}…
                                        </td>
                                        <td><span className={`badge badge-${p.estado}`}>{p.estado.replace('_', ' ')}</span></td>
                                        <td>${fmt(p.total_usd)}</td>
                                        <td>${fmt(p.total_clp, 0)}</td>
                                        <td style={{ color: 'var(--clr-text-muted)', fontSize: '.8rem' }}>
                                            {new Date(p.created_at).toLocaleDateString('es-CL')}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    )
}
