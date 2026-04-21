import { useState, useEffect, useCallback } from 'react'
import { listReservations, getReservation, deleteReservation } from '../../lib/api'

export default function StaffReservations() {
  const [reservations, setReservations] = useState([])
  const [loading,  setLoading]  = useState(true)
  const [error,    setError]    = useState('')
  const [success,  setSuccess]  = useState('')

  const [email,  setEmail]   = useState('')
  const [res,    setRes]     = useState(null)
  const [lookErr,setLookErr] = useState('')

  const loadList = useCallback(async () => {
    setLoading(true); setError('')
    try { setReservations(await listReservations()) }
    catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }, [])

  useEffect(() => { loadList() }, [loadList])

  const handleLookup = async (e) => {
    e.preventDefault(); setLookErr(''); setRes(null)
    try { setRes(await getReservation(email)) } catch (e) { setLookErr(e.message) }
  }

  const handleCancel = async (emailAddr) => {
    if (!confirm('Cancel this reservation?')) return
    try {
      await deleteReservation(emailAddr)
      setRes(null); setSuccess('Reservation cancelled.')
      loadList()
    } catch (e) { setError(e.message) }
  }

  const fmt = dt => new Date(dt).toLocaleString('en-CA', {
    weekday: 'short', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
  })

  return (
    <>
      <div className="page-header">
        <h1>Reservations</h1>
        <p>View all upcoming reservations or look up by customer email.</p>
      </div>

      <form onSubmit={handleLookup} style={{ display: 'flex', gap: 10, alignItems: 'flex-end', marginBottom: 16, flexWrap: 'wrap' }}>
        <div className="form-group" style={{ marginBottom: 0, flex: '1 1 240px' }}>
          <label>Look up by email</label>
          <input type="email" value={email} onChange={e => setEmail(e.target.value)} required placeholder="customer@example.com" />
        </div>
        <button type="submit" className="btn btn-secondary">Find</button>
        {lookErr && <span style={{ color: 'var(--danger)', fontSize: 13 }}>{lookErr}</span>}
      </form>

      {res && (
        <div className="card" style={{ maxWidth: 520, marginBottom: 20 }}>
          <div className="card-title">Reservation #{res.reservationID}</div>
          <div className="info-row"><span className="label">Customer</span><span className="value">{res.email}</span></div>
          <div className="info-row"><span className="label">Date & Time</span><span className="value">{fmt(res.reservationDateTime)}</span></div>
          <div className="info-row"><span className="label">Party Size</span><span className="value">{res.partySize}</span></div>
          <div className="info-row"><span className="label">Requests</span><span className="value">{res.specialRequests || <span style={{ color: 'var(--ink-3)' }}>None</span>}</span></div>
          <div style={{ marginTop: 16 }}>
            <button className="btn btn-danger btn-sm" onClick={() => handleCancel(res.email)}>Cancel reservation</button>
          </div>
        </div>
      )}

      {error   && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <div style={{ fontFamily: 'var(--font-display)', fontSize: '1rem', fontWeight: 500 }}>All Reservations</div>
        <button className="btn btn-secondary btn-sm" onClick={loadList}>↻ Refresh</button>
      </div>

      {loading ? <div className="loading-center"><span className="spinner" /></div> : (
        reservations.length === 0 ? (
          <p style={{ color: 'var(--ink-3)', fontSize: 13 }}>No reservations on file.</p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {reservations.map(r => (
              <div key={r.reservationID} className="card" style={{ display: 'flex', alignItems: 'center', gap: 16, padding: '14px 18px' }}>
                <div style={{ flex: '0 0 36px', textAlign: 'center' }}>
                  <div style={{ fontFamily: 'var(--font-display)', fontSize: '1.2rem' }}>#{r.reservationID}</div>
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 500, fontSize: 14 }}>{r.email}</div>
                  <div style={{ fontSize: 13, color: 'var(--ink-3)' }}>{fmt(r.reservationDateTime)} · Party of {r.partySize}</div>
                  {r.specialRequests && <div style={{ fontSize: 12, color: 'var(--ink-2)', marginTop: 2 }}>"{r.specialRequests}"</div>}
                </div>
                <button className="btn btn-danger btn-sm" onClick={() => handleCancel(r.email)}>Cancel</button>
              </div>
            ))}
          </div>
        )
      )}
    </>
  )
}