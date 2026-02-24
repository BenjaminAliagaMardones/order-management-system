import { NavLink, useLocation } from 'react-router-dom'

const NAV = [
    { to: '/', icon: '📊', label: 'Dashboard' },
    { to: '/clientes', icon: '👥', label: 'Clientes' },
    { to: '/pedidos', icon: '📦', label: 'Pedidos' },
]

export default function Sidebar() {
    return (
        <aside style={{
            width: '220px',
            minHeight: '100vh',
            background: 'var(--clr-surface)',
            borderRight: '1px solid var(--clr-border)',
            display: 'flex',
            flexDirection: 'column',
            padding: '0',
            flexShrink: 0,
        }}>
            {/* Logo */}
            <div style={{
                padding: '1.75rem 1.5rem 1.25rem',
                borderBottom: '1px solid var(--clr-border)',
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '.6rem' }}>
                    <span style={{
                        fontSize: '1.4rem',
                        background: 'var(--clr-primary)',
                        borderRadius: '10px',
                        width: '36px', height: '36px',
                        display: 'grid', placeItems: 'center',
                        flexShrink: 0,
                        boxShadow: '0 0 16px rgba(108,99,255,.4)',
                    }}>🛍️</span>
                    <div>
                        <div style={{ fontWeight: 700, fontSize: '.95rem', lineHeight: 1.1 }}>ShopManager</div>
                        <div style={{ fontSize: '.7rem', color: 'var(--clr-text-muted)' }}>Gestión de pedidos</div>
                    </div>
                </div>
            </div>

            {/* Nav */}
            <nav style={{ padding: '1rem .75rem', flex: 1 }}>
                {NAV.map(({ to, icon, label }) => (
                    <NavLink
                        key={to}
                        to={to}
                        end={to === '/'}
                        style={({ isActive }) => ({
                            display: 'flex',
                            alignItems: 'center',
                            gap: '.65rem',
                            padding: '.65rem .9rem',
                            borderRadius: 'var(--radius-md)',
                            marginBottom: '.25rem',
                            fontSize: '.875rem',
                            fontWeight: isActive ? 600 : 400,
                            color: isActive ? '#fff' : 'var(--clr-text-muted)',
                            background: isActive ? 'var(--clr-primary)' : 'transparent',
                            boxShadow: isActive ? '0 0 12px rgba(108,99,255,.3)' : 'none',
                            transition: 'var(--transition)',
                            textDecoration: 'none',
                        })}
                    >
                        <span>{icon}</span>
                        {label}
                    </NavLink>
                ))}
            </nav>

            {/* Footer */}
            <div style={{
                padding: '1rem 1.5rem',
                borderTop: '1px solid var(--clr-border)',
                fontSize: '.72rem',
                color: 'var(--clr-text-dim)',
            }}>
                v0.1.0 · USA→Chile
            </div>
        </aside>
    )
}
