import { useState, useEffect } from 'react'
import { useAuth } from '../../context/AuthContext'
import { getWaitlist, createWaitlist, updateWaitlist, deleteWaitlist } from '../../lib/api'

const STATUS_CLASS = { Waiting: 'badge-amber', Seated: 'badge-green', Cancelled: 'badge-red', Removed: 'badge-gray' }

export default function CustomerWaitlist() {
  const { user } = useAuth()
  const [entry,   setEntry]   = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving,  setSaving]  = useState(false)
  const [error,   setError]   = useState('')
  const [success, setSuccess] = useState('')
  const [editing, setEditing] = useState(false)

  const [form, setForm] = useState({ partySize: 2, specialRequests: '' })

  useEffect(() => {
    getWaitlist(user.email)
      .then(data => { setEntry(data); setEditing(false) })
      .catch(() => setEntry(null))
      .finally(() => setLoading(false))
  }, [user.email])

  const handleJoin = async (e) => {
    e.preventDefault()
    setError(''); setSuccess(''); setSaving(true)
    try {
      const data = await createWaitlist({
        email: user.email,
        partySize: parseInt(form.partySize),
        specialRequests: form.specialRequests || null,
      })
      setEntry(data)
      setSuccess("You've been added to the waitlist.")
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  const handleUpdate = async (e) => {
    e.preventDefault()
    setError(''); setSuccess(''); setSaving(true)
    try {
      const data = await updateWaitlist(user.email, {
        partySize: parseInt(form.partySize),
        specialRequests: form.specialRequests || null,
      })
      setEntry(data)
      setEditing(false)
      setSuccess('Waitlist entry updated.')
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  const handleLeave = async () => {
    if (!confirm('Leave the waitlist?')) return
    setError(''); setSaving(true)
    try {
      await deleteWaitlist(user.email)
      setEntry(null)
      setSuccess('You have left the waitlist.')
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  const startEdit = () => {
    setForm({ partySize: entry.partySize, specialRequests: entry.specialRequests || '' })
    setEditing(true)
  }

  if (loading) return <div className="loading-center"><span className="spinner" /></div>

  return (
    <>
      <div className="page-header">
        <h1>Waitlist</h1>
        <p>Walk in and join the queue. We'll seat you when a table opens up.</p>
      </div>

      {error   && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      {entry && !editing && (
        <div className="card" style={{ maxWidth: 480 }}>
          <div className="card-title">Your Queue Position</div>
          <div className="info-row">
            <span className="label">Status</span>
            <span className="value">
              <span className={`badge ${STATUS_CLASS[entry.entryStatus] || 'badge-gray'}`}>{entry.entryStatus}</span>
            </span>
          </div>
          <div className="info-row">
            <span className="label">Est. Wait</span>
            <span className="value">{entry.estimatedWaitTime} minutes</span>
          </div>
          <div className="info-row">
            <span className="label">Party Size</span>
            <span className="value">{entry.partySize} {entry.partySize === 1 ? 'guest' : 'guests'}</span>
          </div>
          {entry.specialRequests && (
            <div className="info-row">
              <span className="label">Requests</span>
              <span className="value">{entry.specialRequests}</span>
            </div>
          )}
          {entry.entryStatus === 'Waiting' && (
            <div style={{ display: 'flex', gap: 10, marginTop: 20 }}>
              <button className="btn btn-secondary" onClick={startEdit}>Edit</button>
              <button className="btn btn-danger" onClick={handleLeave} disabled={saving}>
                {saving ? <span className="spinner" /> : 'Leave queue'}
              </button>
            </div>
          )}
        </div>
      )}

      {entry && editing && (
        <div className="card" style={{ maxWidth: 480 }}>
          <div className="card-title">Update Queue Entry</div>
          <form onSubmit={handleUpdate}>
            <WaitlistForm form={form} setForm={setForm} />
            <div style={{ display: 'flex', gap: 10 }}>
              <button type="submit" className="btn btn-primary" disabled={saving}>
                {saving ? <span className="spinner" /> : 'Save'}
              </button>
              <button type="button" className="btn btn-ghost" onClick={() => setEditing(false)}>Cancel</button>
            </div>
          </form>
        </div>
      )}

      {!entry && (
        <div className="card" style={{ maxWidth: 480 }}>
          <div className="card-title">Join the Waitlist</div>
          <p style={{ color: 'var(--ink-3)', fontSize: 13, marginBottom: 20 }}>
            You'll be added to the end of the queue. Our host will seat you when a table becomes available.
          </p>
          <form onSubmit={handleJoin}>
            <WaitlistForm form={form} setForm={setForm} />
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? <span className="spinner" /> : 'Join queue'}
            </button>
          </form>
        </div>
      )}
    </>
  )
}

function WaitlistForm({ form, setForm }) {
  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))
  return (
    <>
      <div className="form-group">
        <label>Party Size</label>
        <input type="number" min={1} max={20} value={form.partySize} onChange={set('partySize')} required />
      </div>
      <div className="form-group">
        <label>Special Requests <span style={{ color: 'var(--ink-3)', fontWeight: 400 }}>(optional)</span></label>
        <textarea value={form.specialRequests} onChange={set('specialRequests')} rows={2} placeholder="Seating preferences, accessibility needs…" />
      </div>
    </>
  )
}