import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { getReservation, getWaitlist, getLoyalty } from '../../lib/api'

export default function CustomerDash() {
  const { user } = useAuth()
  const [reservation, setReservation] = useState(null)
  const [waitlist,    setWaitlist]    = useState(null)
  const [loyalty,     setLoyalty]     = useState(null)
  const [loading,     setLoading]     = useState(true)

  useEffect(() => {
    const load = async () => {
      const [res, wl, loy] = await Promise.allSettled([
        getReservation(user.email),
        getWaitlist(user.email),
        getLoyalty(user.email),
      ])
      if (res.status === 'fulfilled') setReservation(res.value)
      if (wl.status  === 'fulfilled') setWaitlist(wl.value)
      if (loy.status === 'fulfilled') setLoyalty(loy.value)
      setLoading(false)
    }
    load()
  }, [user.email])

  if (loading) return <div className="loading-center"><span className="spinner" /></div>

  const fmt = (dt) => {
    const d = new Date(dt)
    return d.toLocaleDateString('en-CA', { weekday: 'short', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
  }

  return (
    <>
      <div className="page-header">
        <h1>Welcome back, {user.name.split(' ')[0]}</h1>
        <p>Manage your reservations, waitlist, and loyalty points below.</p>
      </div>

      <div className="grid-3" style={{ marginBottom: 24 }}>
        <div className="stat-tile">
          <div className="stat-label">Reservation</div>
          <div className="stat-value" style={{ fontSize: '1.2rem', fontFamily: 'var(--font-body)', fontWeight: 500 }}>
            {reservation ? fmt(reservation.reservationDateTime) : '—'}
          </div>
          <div className="stat-meta">{reservation ? `Party of ${reservation.partySize}` : 'None booked'}</div>
        </div>
        <div className="stat-tile">
          <div className="stat-label">Waitlist</div>
          <div className="stat-value" style={{ fontSize: '1.2rem', fontFamily: 'var(--font-body)', fontWeight: 500 }}>
            {waitlist ? waitlist.entryStatus : '—'}
          </div>
          <div className="stat-meta">{waitlist ? `~${waitlist.estimatedWaitTime} min wait` : 'Not queued'}</div>
        </div>
        <div className="stat-tile">
          <div className="stat-label">Loyalty Points</div>
          <div className="stat-value">{loyalty ? loyalty.pointsBalance.toLocaleString() : '—'}</div>
          <div className="stat-meta">{loyalty ? 'Active member' : 'Not enrolled'}</div>
        </div>
      </div>

      <div className="grid-2">
        {reservation ? (
          <div className="card">
            <div className="card-title">Upcoming Reservation</div>
            <div className="info-row"><span className="label">Date & Time</span><span className="value">{fmt(reservation.reservationDateTime)}</span></div>
            <div className="info-row"><span className="label">Party Size</span><span className="value">{reservation.partySize}</span></div>
            {reservation.specialRequests && (
              <div className="info-row"><span className="label">Requests</span><span className="value">{reservation.specialRequests}</span></div>
            )}
            <div style={{ marginTop: 16 }}>
              <Link to="/portal/reservation" className="btn btn-secondary btn-sm">Manage →</Link>
            </div>
          </div>
        ) : (
          <div className="card">
            <div className="card-title">No Reservation</div>
            <p style={{ color: 'var(--ink-3)', fontSize: 13, marginBottom: 16 }}>
              Book a table in advance to guarantee your spot.
            </p>
            <Link to="/portal/reservation" className="btn btn-primary btn-sm">Book a table</Link>
          </div>
        )}

        {waitlist ? (
          <div className="card">
            <div className="card-title">Waitlist Position</div>
            <div className="info-row"><span className="label">Status</span><span className="value"><StatusBadge s={waitlist.entryStatus} /></span></div>
            <div className="info-row"><span className="label">Est. Wait</span><span className="value">{waitlist.estimatedWaitTime} min</span></div>
            <div className="info-row"><span className="label">Party Size</span><span className="value">{waitlist.partySize}</span></div>
            <div style={{ marginTop: 16 }}>
              <Link to="/portal/waitlist" className="btn btn-secondary btn-sm">Manage →</Link>
            </div>
          </div>
        ) : (
          <div className="card">
            <div className="card-title">Walk-in Waitlist</div>
            <p style={{ color: 'var(--ink-3)', fontSize: 13, marginBottom: 16 }}>
              Join the queue and get an estimated wait time.
            </p>
            <Link to="/portal/waitlist" className="btn btn-primary btn-sm">Join waitlist</Link>
          </div>
        )}
      </div>

      {!loyalty && (
        <div className="card section-gap" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
          <div>
            <div style={{ fontFamily: 'var(--font-display)', fontSize: '1.1rem', fontWeight: 500 }}>Join our loyalty program</div>
            <p style={{ color: 'var(--ink-3)', fontSize: 13, marginTop: 4 }}>Earn points with every visit and unlock exclusive offers.</p>
          </div>
          <Link to="/portal/loyalty" className="btn btn-primary">Enroll now →</Link>
        </div>
      )}
    </>
  )
}

function StatusBadge({ s }) {
  const map = { Waiting: 'badge-amber', Seated: 'badge-green', Cancelled: 'badge-red', Removed: 'badge-gray' }
  return <span className={`badge ${map[s] || 'badge-gray'}`}>{s}</span>
}