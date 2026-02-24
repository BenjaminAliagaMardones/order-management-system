export function Badge({ estado }) {
    return <span className={`badge badge-${estado}`}>{estado.replace('_', ' ')}</span>
}

export function Spinner() {
    return <div className="loading-wrap"><div className="spinner" /></div>
}

export function Alert({ type = 'error', children }) {
    return <div className={`alert alert-${type}`}>{children}</div>
}

export function EmptyState({ icon = '📭', message }) {
    return (
        <div className="empty-state">
            <div className="empty-state-icon">{icon}</div>
            <p>{message}</p>
        </div>
    )
}

export function ConfirmModal({ title, message, onConfirm, onCancel, loading }) {
    return (
        <div className="modal-overlay" onClick={onCancel}>
            <div className="modal" style={{ maxWidth: '400px' }} onClick={e => e.stopPropagation()}>
                <h3 className="modal-title">⚠️ {title}</h3>
                <p style={{ color: 'var(--clr-text-muted)', fontSize: '.9rem' }}>{message}</p>
                <div className="modal-footer">
                    <button className="btn btn-ghost" onClick={onCancel} disabled={loading}>Cancelar</button>
                    <button className="btn btn-danger" onClick={onConfirm} disabled={loading}>
                        {loading ? 'Eliminando…' : 'Confirmar'}
                    </button>
                </div>
            </div>
        </div>
    )
}
