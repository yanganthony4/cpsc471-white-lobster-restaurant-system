import { useState } from 'react'
import { getReservation, deleteReservation } from '../../lib/api'

export default function StaffReservations() {
  const [email,   setEmail]   = useState('')
  const [res,     setRes]     = useState(null)
  const [error,   setError]   = useState('')
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState('')

  const handleLookup = async (e) => {
    e.preventDefault(); setError(''); setSuccess(''); setLoading(true); setRes(null)
    try { setRes(await getReservation(email)) } catch (err) { setError(err.message) } finally { setLoading(false) }
  }

  const handleCancel = async () => {
    if (!confirm('Cancel this reservation?')) return
    setError(''); setLoading(true)
    try {
      await deleteReservation(res.email)
      setRes(null)
      setSuccess('Reservation cancelled successfully.')
    } catch (err) { setError(err.message) } finally { setLoading(false) }
  }

  const fmt = dt => new Date(dt).toLocaleString('en-CA', {
    weekday: 'short', month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })

  return (
    <>
      <div className="page-header">
        <h1>Reservations</h1>
        <p>Look up a customer's reservation by email.</p>
      </div>

      <form onSubmit={handleLookup} style={{ display: 'flex', gap: 10, alignItems: 'flex-end', marginBottom: 24, flexWrap: 'wrap' }}>
        <div className="form-group" style={{ marginBottom: 0, flex: '1 1 260px' }}>
          <label>Customer Email</label>
          <input type="email" value={email} onChange={e => setEmail(e.target.value)} required placeholder="customer@example.com" />
        </div>
        <button type="submit" className="btn btn-secondary" disabled={loading}>
          {loading ? <span className="spinner" /> : 'Look up'}
        </button>
      </form>

      {error   && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      {res && (
        <div className="card" style={{ maxWidth: 520 }}>
          <div className="card-title">Reservation #{res.reservationID}</div>
          <div className="info-row"><span className="label">Customer</span><span className="value">{res.email}</span></div>
          <div className="info-row"><span className="label">Date & Time</span><span className="value">{fmt(res.reservationDateTime)}</span></div>
          <div className="info-row"><span className="label">Party Size</span><span className="value">{res.partySize}</span></div>
          <div className="info-row">
            <span className="label">Special Requests</span>
            <span className="value">{res.specialRequests || <span style={{ color: 'var(--ink-3)' }}>None</span>}</span>
          </div>
          <div style={{ marginTop: 20, display: 'flex', gap: 10 }}>
            <button className="btn btn-danger" onClick={handleCancel} disabled={loading}>
              Cancel reservation
            </button>
          </div>
        </div>
      )}
    </>
  )
}