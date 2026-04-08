import { Outlet, NavLink } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

const ROLE_SECTIONS = {
  Host:    ['tables', 'seating', 'reservations', 'waitlist'],
  Server:  ['seating', 'bills'],
  Cashier: ['bills'],
  Manager: ['tables', 'sections', 'seating', 'reservations', 'waitlist', 'menu', 'bills', 'promotions'],
}

const NAV = [
  { to: '/staff',             label: 'Overview',     icon: '⬚',  end: true },
  { to: '/staff/reservations',label: 'Reservations', icon: '📅', roles: ['Host', 'Manager'] },
  { to: '/staff/waitlist',    label: 'Waitlist',     icon: '⏱',  roles: ['Host', 'Manager'] },
  { to: '/staff/tables',      label: 'Tables',       icon: '◫',  roles: ['Host', 'Manager'] },
  { to: '/staff/sections',    label: 'Sections',     icon: '⊞',  roles: ['Manager'] },
  { to: '/staff/seating',     label: 'Seating',      icon: '↘',  roles: ['Host', 'Server', 'Manager'] },
  { to: '/staff/menu',        label: 'Menu',         icon: '☰',  roles: ['Manager'] },
  { to: '/staff/bills',       label: 'Bills',        icon: '◻',  roles: ['Server', 'Cashier', 'Manager'] },
  { to: '/staff/promotions',  label: 'Promotions',   icon: '⊛',  roles: ['Manager'] },
  { to: '/staff/profile',     label: 'Profile',      icon: '○' },
]

export default function StaffShell() {
  const { user, logout } = useAuth()

  const visibleNav = NAV.filter(n => !n.roles || n.roles.includes(user.role))

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar-logo">
          <div className="wordmark">White Lobster</div>
          <div className="subtitle">Staff Portal</div>
        </div>

        <nav className="sidebar-nav">
          <div className="nav-section-label">Navigation</div>
          {visibleNav.map(n => (
            <NavLink
              key={n.to}
              to={n.to}
              end={n.end}
              className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')}
            >
              <span style={{ fontSize: 14 }}>{n.icon}</span>
              {n.label}
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="sidebar-user">
            <strong>{user.name}</strong>
            {user.role} · #{user.employeeID}
          </div>
          <button className="btn-logout" onClick={logout}>Sign out</button>
        </div>
      </aside>

      <main className="main-content">
        <div className="page">
          <Outlet />
        </div>
      </main>
    </div>
  )
}