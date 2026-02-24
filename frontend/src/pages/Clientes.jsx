import { useEffect, useState } from 'react'
import { clientesApi } from '@/api'
import { Spinner, Alert, EmptyState, ConfirmModal } from '@/components/UI'

function ClienteModal({ cliente, onClose, onSaved }) {
    const editing = Boolean(cliente?.id)
    const [form, setForm] = useState({
        nombre: cliente?.nombre || '',
        telefono: cliente?.telefono || '',
        email: cliente?.email || '',
    })
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)

    const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

    const submit = async (e) => {
        e.preventDefault()
        setError(''); setLoading(true)
        try {
            const payload = { ...form, email: form.email || null }
            if (editing) await clientesApi.actualizar(cliente.id, payload)
            else await clientesApi.crear(payload)
            onSaved()
        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal" onClick={e => e.stopPropagation()}>
                <h3 className="modal-title">{editing ? '✏️ Editar cliente' : '➕ Nuevo cliente'}</h3>
                {error && <Alert type="error" style={{ marginBottom: '1rem' }}>{error}</Alert>}
                <form onSubmit={submit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    <div className="form-group">
                        <label className="form-label">Nombre *</label>
                        <input className="form-input" value={form.nombre} onChange={set('nombre')} required placeholder="María González" />
                    </div>
                    <div className="form-group">
                        <label className="form-label">Teléfono *</label>
                        <input className="form-input" value={form.telefono} onChange={set('telefono')} required placeholder="+56912345678" />
                    </div>
                    <div className="form-group">
                        <label className="form-label">Email (opcional)</label>
                        <input className="form-input" type="email" value={form.email} onChange={set('email')} placeholder="maria@gmail.com" />
                    </div>
                    <div className="modal-footer">
                        <button type="button" className="btn btn-ghost" onClick={onClose}>Cancelar</button>
                        <button type="submit" className="btn btn-primary" disabled={loading}>
                            {loading ? 'Guardando…' : editing ? 'Guardar cambios' : 'Crear cliente'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    )
}

export default function Clientes() {
    const [clientes, setClientes] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')
    const [modal, setModal] = useState(null)   // null | {} | clienteObj
    const [confirm, setConfirm] = useState(null)   // null | clienteObj
    const [deleting, setDeleting] = useState(false)

    const cargar = async () => {
        setLoading(true); setError('')
        try { const r = await clientesApi.listar({ limit: 200 }); setClientes(r.data) }
        catch (e) { setError(e.message) }
        finally { setLoading(false) }
    }

    useEffect(() => { cargar() }, [])

    const onSaved = () => { setModal(null); cargar() }

    const eliminar = async () => {
        setDeleting(true)
        try { await clientesApi.eliminar(confirm.id); setConfirm(null); cargar() }
        catch (e) { setError(e.message); setConfirm(null) }
        finally { setDeleting(false) }
    }

    return (
        <div>
            <div className="page-header">
                <div>
                    <h1 className="page-title">👥 Clientes</h1>
                    <p className="page-subtitle">{clientes.length} cliente{clientes.length !== 1 ? 's' : ''} registrados</p>
                </div>
                <button className="btn btn-primary" onClick={() => setModal({})}>+ Nuevo cliente</button>
            </div>

            {error && <Alert type="error" style={{ marginBottom: '1rem' }}>{error}</Alert>}

            {loading ? <Spinner /> : clientes.length === 0 ? (
                <EmptyState icon="👥" message="No hay clientes aún. ¡Crea el primero!" />
            ) : (
                <div className="card" style={{ padding: 0 }}>
                    <div className="table-wrap">
                        <table>
                            <thead>
                                <tr>
                                    <th>Nombre</th>
                                    <th>Teléfono</th>
                                    <th>Email</th>
                                    <th>Registrado</th>
                                    <th style={{ width: '100px' }}>Acciones</th>
                                </tr>
                            </thead>
                            <tbody>
                                {clientes.map(c => (
                                    <tr key={c.id}>
                                        <td style={{ fontWeight: 600 }}>{c.nombre}</td>
                                        <td>{c.telefono}</td>
                                        <td style={{ color: 'var(--clr-text-muted)' }}>{c.email || '—'}</td>
                                        <td style={{ color: 'var(--clr-text-muted)', fontSize: '.8rem' }}>
                                            {new Date(c.created_at).toLocaleDateString('es-CL')}
                                        </td>
                                        <td>
                                            <div style={{ display: 'flex', gap: '.4rem' }}>
                                                <button className="btn btn-ghost btn-sm" onClick={() => setModal(c)}>✏️</button>
                                                <button className="btn btn-danger btn-sm" onClick={() => setConfirm(c)}>🗑️</button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {modal !== null && (
                <ClienteModal
                    cliente={modal?.id ? modal : null}
                    onClose={() => setModal(null)}
                    onSaved={onSaved}
                />
            )}

            {confirm && (
                <ConfirmModal
                    title="Eliminar cliente"
                    message={`¿Eliminar a "${confirm.nombre}"? Esta acción no se puede deshacer.`}
                    onConfirm={eliminar}
                    onCancel={() => setConfirm(null)}
                    loading={deleting}
                />
            )}
        </div>
    )
}
