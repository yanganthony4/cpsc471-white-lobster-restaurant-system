import { Outlet, NavLink } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

export default function CustomerShell() {
  const { user, logout } = useAuth()

  return (
    <div style={{ minHeight: '100vh', background: 'var(--cream)' }}>
      <header className="portal-header">
        <span className="portal-wordmark">White Lobster</span>
        <nav className="portal-nav">
          <NavLink to="/portal"             end  className={({ isActive }) => 'portal-nav-link' + (isActive ? ' active' : '')}>Home</NavLink>
          <NavLink to="/portal/reservation"      className={({ isActive }) => 'portal-nav-link' + (isActive ? ' active' : '')}>Reservation</NavLink>
          <NavLink to="/portal/waitlist"         className={({ isActive }) => 'portal-nav-link' + (isActive ? ' active' : '')}>Waitlist</NavLink>
          <NavLink to="/portal/loyalty"          className={({ isActive }) => 'portal-nav-link' + (isActive ? ' active' : '')}>Loyalty</NavLink>
          <NavLink to="/portal/profile"          className={({ isActive }) => 'portal-nav-link' + (isActive ? ' active' : '')}>Profile</NavLink>
          <button onClick={logout} className="portal-nav-link" style={{ background: 'none', border: 'none', cursor: 'pointer' }}>
            Sign out
          </button>
        </nav>
      </header>
      <div className="portal-body">
        <Outlet />
      </div>
    </div>
  )
}