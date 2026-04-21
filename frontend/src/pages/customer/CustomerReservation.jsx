import { useState, useEffect } from 'react'
import { useAuth } from '../../context/AuthContext'
import { getReservation, createReservation, updateReservation, deleteReservation } from '../../lib/api'

function toLocalDatetimeInput(dt) {
  const d = new Date(dt)
  const pad = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`
}

function minDatetime() {
  const d = new Date(Date.now() + 60 * 60 * 1000)
  return toLocalDatetimeInput(d)
}

export default function CustomerReservation() {
  const { user } = useAuth()
  const [res,     setRes]     = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving,  setSaving]  = useState(false)
  const [error,   setError]   = useState('')
  const [success, setSuccess] = useState('')
  const [editing, setEditing] = useState(false)

  const [form, setForm] = useState({
    partySize: 2,
    reservationDateTime: minDatetime(),
    specialRequests: '',
  })

  useEffect(() => {
    getReservation(user.email)
      .then(data => { setRes(data); setEditing(false) })
      .catch(() => setRes(null))
      .finally(() => setLoading(false))
  }, [user.email])

  const handleCreate = async (e) => {
    e.preventDefault()
    setError(''); setSuccess(''); setSaving(true)
    try {
      const data = await createReservation({
        email: user.email,
        partySize: parseInt(form.partySize),
        reservationDateTime: new Date(form.reservationDateTime).toISOString(),
        specialRequests: form.specialRequests || null,
      })
      setRes(data)
      setSuccess('Reservation confirmed!')
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
      const data = await updateReservation(user.email, {
        partySize: parseInt(form.partySize),
        reservationDateTime: new Date(form.reservationDateTime).toISOString(),
        specialRequests: form.specialRequests || null,
      })
      setRes(data)
      setEditing(false)
      setSuccess('Reservation updated.')
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  const handleCancel = async () => {
    if (!confirm('Cancel this reservation?')) return
    setError(''); setSaving(true)
    try {
      await deleteReservation(user.email)
      setRes(null)
      setSuccess('Reservation cancelled.')
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  const startEdit = () => {
    setForm({
      partySize: res.partySize,
      reservationDateTime: toLocalDatetimeInput(res.reservationDateTime),
      specialRequests: res.specialRequests || '',
    })
    setEditing(true)
  }

  const fmt = (dt) => new Date(dt).toLocaleString('en-CA', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })

  if (loading) return <div className="loading-center"><span className="spinner" /></div>

  return (
    <>
      <div className="page-header">
        <h1>Reservation</h1>
        <p>Book a table in advance. One active reservation per account.</p>
      </div>

      {error   && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      {/* ── Has reservation, not editing ── */}
      {res && !editing && (
        <div className="card" style={{ maxWidth: 520 }}>
          <div className="card-title">Current Reservation</div>
          <div className="info-row">
            <span className="label">Date & Time</span>
            <span className="value">{fmt(res.reservationDateTime)}</span>
          </div>
          <div className="info-row">
            <span className="label">Party Size</span>
            <span className="value">{res.partySize} {res.partySize === 1 ? 'guest' : 'guests'}</span>
          </div>
          <div className="info-row">
            <span className="label">Special Requests</span>
            <span className="value">{res.specialRequests || <span style={{ color: 'var(--ink-3)' }}>None</span>}</span>
          </div>
          <div style={{ display: 'flex', gap: 10, marginTop: 20 }}>
            <button className="btn btn-secondary" onClick={startEdit}>Edit</button>
            <button className="btn btn-danger" onClick={handleCancel} disabled={saving}>
              {saving ? <span className="spinner" /> : 'Cancel reservation'}
            </button>
          </div>
        </div>
      )}

      {/* ── Editing existing ── */}
      {res && editing && (
        <div className="card" style={{ maxWidth: 520 }}>
          <div className="card-title">Edit Reservation</div>
          <form onSubmit={handleUpdate}>
            <ReservationForm form={form} setForm={setForm} />
            <div style={{ display: 'flex', gap: 10, marginTop: 8 }}>
              <button type="submit" className="btn btn-primary" disabled={saving}>
                {saving ? <span className="spinner" /> : 'Save changes'}
              </button>
              <button type="button" className="btn btn-ghost" onClick={() => setEditing(false)}>Cancel</button>
            </div>
          </form>
        </div>
      )}

      {/* ── No reservation ── */}
      {!res && (
        <div className="card" style={{ maxWidth: 520 }}>
          <div className="card-title">Book a Table</div>
          <form onSubmit={handleCreate}>
            <ReservationForm form={form} setForm={setForm} />
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? <span className="spinner" /> : 'Confirm reservation'}
            </button>
          </form>
        </div>
      )}
    </>
  )
}

function ReservationForm({ form, setForm }) {
  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))
  return (
    <>
      <div className="form-row">
        <div className="form-group">
          <label>Party Size</label>
          <input type="number" min={1} max={20} value={form.partySize} onChange={set('partySize')} required />
        </div>
        <div className="form-group">
          <label>Date & Time</label>
          <input type="datetime-local" value={form.reservationDateTime} onChange={set('reservationDateTime')} min={minDatetime()} required />
        </div>
      </div>
      <div className="form-group">
        <label>Special Requests <span style={{ color: 'var(--ink-3)', fontWeight: 400 }}>(optional)</span></label>
        <textarea value={form.specialRequests} onChange={set('specialRequests')} rows={2} placeholder="Allergies, seating preferences, occasion…" />
      </div>
    </>
  )
}