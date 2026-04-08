import { useState } from 'react'
import { getWaitlist, deleteWaitlist } from '../../lib/api'

const STATUS_CLASS = { Waiting: 'badge-amber', Seated: 'badge-green', Cancelled: 'badge-red', Removed: 'badge-gray' }

export default function StaffWaitlist() {
  const [email,   setEmail]   = useState('')
  const [entry,   setEntry]   = useState(null)
  const [error,   setError]   = useState('')
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState('')

  const handleLookup = async (e) => {
    e.preventDefault(); setError(''); setSuccess(''); setLoading(true); setEntry(null)
    try { setEntry(await getWaitlist(email)) } catch (err) { setError(err.message) } finally { setLoading(false) }
  }

  const handleRemove = async () => {
    if (!confirm('Remove this customer from the waitlist?')) return
    setError(''); setLoading(true)
    try {
      await deleteWaitlist(entry.email)
      setEntry(null)
      setSuccess('Customer removed from waitlist.')
    } catch (err) { setError(err.message) } finally { setLoading(false) }
  }

  return (
    <>
      <div className="page-header">
        <h1>Waitlist</h1>
        <p>Look up a customer's queue position by email.</p>
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

      {entry && (
        <div className="card" style={{ maxWidth: 480 }}>
          <div className="card-title">Waitlist Entry #{entry.waitlistID}</div>
          <div className="info-row">
            <span className="label">Status</span>
            <span className="value"><span className={`badge ${STATUS_CLASS[entry.entryStatus] || 'badge-gray'}`}>{entry.entryStatus}</span></span>
          </div>
          <div className="info-row"><span className="label">Customer</span><span className="value">{entry.email}</span></div>
          <div className="info-row"><span className="label">Party Size</span><span className="value">{entry.partySize}</span></div>
          <div className="info-row"><span className="label">Est. Wait</span><span className="value">{entry.estimatedWaitTime} min</span></div>
          {entry.specialRequests && (
            <div className="info-row"><span className="label">Requests</span><span className="value">{entry.specialRequests}</span></div>
          )}
          {entry.entryStatus === 'Waiting' && (
            <div style={{ marginTop: 20 }}>
              <button className="btn btn-danger" onClick={handleRemove} disabled={loading}>Remove from waitlist</button>
            </div>
          )}
        </div>
      )}
    </>
  )
}