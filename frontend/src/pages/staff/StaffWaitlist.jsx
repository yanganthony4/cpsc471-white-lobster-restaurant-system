import { useState, useEffect, useCallback } from 'react'
import { listWaitlist, getWaitlist, deleteWaitlist, updateWaitlistStatus } from '../../lib/api'

const STATUS_CLASS = { Waiting: 'badge-amber', Seated: 'badge-green', Cancelled: 'badge-red', Removed: 'badge-gray' }
const STATUSES = ['Waiting', 'Seated', 'Cancelled', 'Removed']

export default function StaffWaitlist() {
  const [entries,  setEntries]  = useState([])
  const [loading,  setLoading]  = useState(true)
  const [error,    setError]    = useState('')
  const [success,  setSuccess]  = useState('')
  const [filter,   setFilter]   = useState('Waiting')

  // Email lookup
  const [email,    setEmail]    = useState('')
  const [entry,    setEntry]    = useState(null)
  const [lookErr,  setLookErr]  = useState('')

  const loadList = useCallback(async () => {
    setLoading(true); setError('')
    try { setEntries(await listWaitlist(filter || '')) }
    catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }, [filter])

  useEffect(() => { loadList() }, [loadList])

  const handleRemove = async (id) => {
    if (!confirm('Remove this entry from the waitlist?')) return
    try {
      await updateWaitlistStatus(id, 'Removed')
      setSuccess('Entry removed.')
      loadList()
    } catch (e) { setError(e.message) }
  }

  const handleSeat = async (id) => {
    try {
      await updateWaitlistStatus(id, 'Seated')
      setSuccess('Customer marked as seated.')
      loadList()
    } catch (e) { setError(e.message) }
  }

  const handleEmailLookup = async (e) => {
    e.preventDefault(); setLookErr(''); setEntry(null)
    try { setEntry(await getWaitlist(email)) } catch (e) { setLookErr(e.message) }
  }

  const fmt = (dt) => new Date(dt).toLocaleTimeString('en-CA', { hour: '2-digit', minute: '2-digit' })

  return (
    <>
      <div className="page-header">
        <h1>Waitlist</h1>
        <p>Manage the walk-in queue. Entries ordered by arrival time.</p>
      </div>

      {/* Email lookup strip */}
      <form onSubmit={handleEmailLookup} style={{ display: 'flex', gap: 10, alignItems: 'flex-end', marginBottom: 16, flexWrap: 'wrap' }}>
        <div className="form-group" style={{ marginBottom: 0, flex: '1 1 240px' }}>
          <label>Look up by email</label>
          <input type="email" value={email} onChange={e => setEmail(e.target.value)} required placeholder="customer@example.com" />
        </div>
        <button type="submit" className="btn btn-secondary">Find</button>
        {lookErr && <span style={{ color: 'var(--danger)', fontSize: 13 }}>{lookErr}</span>}
      </form>

      {entry && (
        <div className="card" style={{ maxWidth: 480, marginBottom: 20 }}>
          <div className="card-title">Entry #{entry.waitlistID}</div>
          <div className="info-row"><span className="label">Email</span><span className="value">{entry.email}</span></div>
          <div className="info-row"><span className="label">Party</span><span className="value">{entry.partySize}</span></div>
          <div className="info-row"><span className="label">Est. Wait</span><span className="value">{entry.estimatedWaitTime} min</span></div>
          <div className="info-row"><span className="label">Status</span><span className="value"><span className={`badge ${STATUS_CLASS[entry.entryStatus]}`}>{entry.entryStatus}</span></span></div>
          {entry.specialRequests && <div className="info-row"><span className="label">Requests</span><span className="value">{entry.specialRequests}</span></div>}
          <div style={{ display: 'flex', gap: 8, marginTop: 14 }}>
            {entry.entryStatus === 'Waiting' && <>
              <button className="btn btn-primary btn-sm" onClick={() => handleSeat(entry.waitlistID)}>Mark Seated</button>
              <button className="btn btn-danger btn-sm" onClick={() => handleRemove(entry.waitlistID)}>Remove</button>
            </>}
          </div>
        </div>
      )}

      {/* Filter tabs */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 16, flexWrap: 'wrap', alignItems: 'center' }}>
        <span style={{ fontSize: 13, color: 'var(--ink-3)' }}>Show:</span>
        {['Waiting', 'Seated', 'Cancelled', 'Removed', ''].map(s => (
          <button key={s} className={`btn btn-sm ${filter === s ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setFilter(s)}>
            {s || 'All'}
          </button>
        ))}
        <button className="btn btn-secondary btn-sm" onClick={loadList} style={{ marginLeft: 'auto' }}>↻ Refresh</button>
      </div>

      {error   && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      {loading ? <div className="loading-center"><span className="spinner" /></div> : (
        entries.length === 0 ? (
          <p style={{ color: 'var(--ink-3)', fontSize: 13 }}>No {filter.toLowerCase()} entries.</p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {entries.map(e => (
              <div key={e.waitlistID} className="card" style={{ display: 'flex', alignItems: 'center', gap: 16, padding: '14px 18px' }}>
                <div style={{ flex: '0 0 48px', textAlign: 'center' }}>
                  <div style={{ fontFamily: 'var(--font-display)', fontSize: '1.4rem' }}>#{e.waitlistID}</div>
                  <div style={{ fontSize: 11, color: 'var(--ink-3)' }}>{fmt(e.joinTime)}</div>
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontWeight: 500, fontSize: 14, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{e.email}</div>
                  <div style={{ fontSize: 13, color: 'var(--ink-3)' }}>Party of {e.partySize} · ~{e.estimatedWaitTime} min</div>
                  {e.specialRequests && <div style={{ fontSize: 12, color: 'var(--ink-2)', marginTop: 2 }}>"{e.specialRequests}"</div>}
                </div>
                <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexShrink: 0 }}>
                  <span className={`badge ${STATUS_CLASS[e.entryStatus] || 'badge-gray'}`}>{e.entryStatus}</span>
                  {e.entryStatus === 'Waiting' && <>
                    <button className="btn btn-primary btn-sm" onClick={() => handleSeat(e.waitlistID)}>Seat</button>
                    <button className="btn btn-danger btn-sm" onClick={() => handleRemove(e.waitlistID)}>Remove</button>
                  </>}
                </div>
              </div>
            ))}
          </div>
        )
      )}
    </>
  )
}