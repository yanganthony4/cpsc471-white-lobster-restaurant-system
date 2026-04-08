import { useAuth } from '../../context/AuthContext'

export default function StaffDash() {
  const { user } = useAuth()
  const greeting = new Date().getHours() < 12 ? 'Good morning' : new Date().getHours() < 17 ? 'Good afternoon' : 'Good evening'

  const quickLinks = {
    Host:    [
      { label: 'Manage tables',      to: '/staff/tables' },
      { label: 'View reservations',  to: '/staff/reservations' },
      { label: 'View waitlist',      to: '/staff/waitlist' },
      { label: 'Create seating',     to: '/staff/seating' },
    ],
    Server:  [
      { label: 'My seating',  to: '/staff/seating' },
      { label: 'View bills',  to: '/staff/bills' },
    ],
    Cashier: [
      { label: 'Process bills', to: '/staff/bills' },
    ],
    Manager: [
      { label: 'Tables & sections', to: '/staff/tables' },
      { label: 'Reservations',      to: '/staff/reservations' },
      { label: 'Waitlist',          to: '/staff/waitlist' },
      { label: 'Menu items',        to: '/staff/menu' },
      { label: 'Promotions',        to: '/staff/promotions' },
      { label: 'Bills',             to: '/staff/bills' },
    ],
  }

  const links = quickLinks[user.role] || []

  return (
    <>
      <div className="page-header">
        <h1>{greeting}, {user.name.split(' ')[0]}</h1>
        <p>
          Logged in as <strong>{user.role}</strong> · Employee #{user.employeeID}
        </p>
      </div>

      <div style={{ marginBottom: 32 }}>
        <div style={{ fontFamily: 'var(--font-display)', fontSize: '1.1rem', fontWeight: 500, marginBottom: 16 }}>
          Quick access
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10 }}>
          {links.map(l => (
            <a key={l.to} href={l.to} className="btn btn-secondary">
              {l.label} →
            </a>
          ))}
        </div>
      </div>

      <div className="card" style={{ maxWidth: 480 }}>
        <div className="card-title">Your account</div>
        <div className="info-row"><span className="label">Name</span><span className="value">{user.name}</span></div>
        <div className="info-row"><span className="label">Role</span><span className="value">{user.role}</span></div>
        <div className="info-row"><span className="label">Employee ID</span><span className="value">#{user.employeeID}</span></div>
      </div>
    </>
  )
}