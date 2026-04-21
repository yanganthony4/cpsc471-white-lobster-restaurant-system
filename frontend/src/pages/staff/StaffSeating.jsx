import { useState } from 'react'
import Modal from '../../components/Modal'
import { getAssignment, createAssignment, updateAssignment, deleteAssignment } from '../../lib/api'
import { useAuth } from '../../context/AuthContext'

const STATUSES = ['Seated', 'Completed', 'Cancelled']
const STATUS_CLASS = { Seated: 'badge-green', Completed: 'badge-blue', Cancelled: 'badge-red' }

export default function StaffSeating() {
  const { user } = useAuth()
  const [lookupId,   setLookupId]   = useState('')
  const [assignment, setAssignment] = useState(null)
  const [error,      setError]      = useState('')
  const [loading,    setLoading]    = useState(false)
  const [success,    setSuccess]    = useState('')

  const [showCreate, setShowCreate] = useState(false)
  const [showEdit,   setShowEdit]   = useState(false)
  const [form,       setForm]       = useState({
    source: 'reservation', // 'reservation' | 'waitlist'
    reservationID: '', waitlistID: '',
    sectionName: '', tableNumber: '', employeeID: user.employeeID,
  })
  const [editStatus, setEditStatus] = useState('Seated')
  const [saving,     setSaving]     = useState(false)
  const [modalError, setModalError] = useState('')

  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  const handleLookup = async (e) => {
    e.preventDefault(); setError(''); setSuccess(''); setLoading(true); setAssignment(null)
    try { setAssignment(await getAssignment(parseInt(lookupId))) } catch (err) { setError(err.message) } finally { setLoading(false) }
  }

  const handleCreate = async (e) => {
    e.preventDefault(); setModalError(''); setSaving(true)
    try {
      const payload = {
        sectionName: form.sectionName,
        tableNumber: parseInt(form.tableNumber),
        employeeID: parseInt(form.employeeID),
        currentStatus: 'Seated',
        reservationID: form.source === 'reservation' ? parseInt(form.reservationID) : null,
        waitlistID: form.source === 'waitlist' ? parseInt(form.waitlistID) : null,
      }
      const a = await createAssignment(payload)
      setAssignment(a)
      setShowCreate(false)
      setSuccess(`Assignment #${a.assignmentID} created.`)
    } catch (err) { setModalError(err.message) } finally { setSaving(false) }
  }

  const handleUpdateStatus = async (e) => {
    e.preventDefault(); setModalError(''); setSaving(true)
    try {
      const a = await updateAssignment(assignment.assignmentID, { currentStatus: editStatus })
      setAssignment(a)
      setShowEdit(false)
      setSuccess('Status updated.')
    } catch (err) { setModalError(err.message) } finally { setSaving(false) }
  }

  const handleDelete = async () => {
    if (!confirm('Delete this seating assignment?')) return
    setLoading(true)
    try { await deleteAssignment(assignment.assignmentID); setAssignment(null); setSuccess('Assignment deleted.') }
    catch (err) { setError(err.message) } finally { setLoading(false) }
  }

  const fmt = dt => new Date(dt).toLocaleString('en-CA', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })

  return (
    <>
      <div className="page-header">
        <h1>Seating Assignments</h1>
        <p>Create or look up a seating assignment by ID.</p>
      </div>

      <div className="toolbar">
        <form onSubmit={handleLookup} style={{ display: 'flex', gap: 10, alignItems: 'flex-end' }}>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label>Assignment ID</label>
            <input type="number" min={1} value={lookupId} onChange={e => setLookupId(e.target.value)} required placeholder="401" style={{ width: 120 }} />
          </div>
          <button type="submit" className="btn btn-secondary" disabled={loading}>
            {loading ? <span className="spinner" /> : 'Look up'}
          </button>
        </form>
        <button className="btn btn-primary" onClick={() => { setForm({ source: 'reservation', reservationID: '', waitlistID: '', sectionName: '', tableNumber: '', employeeID: user.employeeID }); setModalError(''); setShowCreate(true) }}>
          + New assignment
        </button>
      </div>

      {error   && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      {assignment && (
        <div className="card" style={{ maxWidth: 520 }}>
          <div className="card-title">Assignment #{assignment.assignmentID}</div>
          <div className="info-row">
            <span className="label">Status</span>
            <span className="value"><span className={`badge ${STATUS_CLASS[assignment.currentStatus] || 'badge-gray'}`}>{assignment.currentStatus}</span></span>
          </div>
          <div className="info-row"><span className="label">Table</span><span className="value">#{assignment.tableNumber} — {assignment.sectionName}</span></div>
          <div className="info-row"><span className="label">Staff</span><span className="value">Employee #{assignment.employeeID}</span></div>
          <div className="info-row">
            <span className="label">Source</span>
            <span className="value">
              {assignment.reservationID ? `Reservation #${assignment.reservationID}` : `Waitlist #${assignment.waitlistID}`}
            </span>
          </div>
          <div className="info-row"><span className="label">Started</span><span className="value">{fmt(assignment.startTime)}</span></div>
          <div style={{ display: 'flex', gap: 10, marginTop: 20 }}>
            <button className="btn btn-secondary" onClick={() => { setEditStatus(assignment.currentStatus); setModalError(''); setShowEdit(true) }}>
              Update status
            </button>
            <button className="btn btn-danger" onClick={handleDelete}>Delete</button>
          </div>
        </div>
      )}

      {/* Create modal */}
      {showCreate && (
        <Modal title="New Seating Assignment" onClose={() => setShowCreate(false)}
          footer={<>
            <button className="btn btn-ghost" onClick={() => setShowCreate(false)}>Cancel</button>
            <button className="btn btn-primary" form="create-seating-form" type="submit" disabled={saving}>
              {saving ? <span className="spinner" /> : 'Create'}
            </button>
          </>}
        >
          {modalError && <div className="alert alert-error">{modalError}</div>}
          <form id="create-seating-form" onSubmit={handleCreate}>
            <div className="form-group">
              <label>Source</label>
              <select value={form.source} onChange={set('source')}>
                <option value="reservation">Reservation</option>
                <option value="waitlist">Waitlist</option>
              </select>
            </div>
            {form.source === 'reservation' ? (
              <div className="form-group">
                <label>Reservation ID</label>
                <input type="number" min={1} value={form.reservationID} onChange={set('reservationID')} required />
              </div>
            ) : (
              <div className="form-group">
                <label>Waitlist ID</label>
                <input type="number" min={1} value={form.waitlistID} onChange={set('waitlistID')} required />
              </div>
            )}
            <div className="form-row">
              <div className="form-group">
                <label>Section Name</label>
                <input value={form.sectionName} onChange={set('sectionName')} required />
              </div>
              <div className="form-group">
                <label>Table Number</label>
                <input type="number" min={1} value={form.tableNumber} onChange={set('tableNumber')} required />
              </div>
            </div>
            <div className="form-group">
              <label>Employee ID</label>
              <input type="number" min={1} value={form.employeeID} onChange={set('employeeID')} required />
            </div>
          </form>
        </Modal>
      )}

      {/* Status edit modal */}
      {showEdit && (
        <Modal title="Update Status" onClose={() => setShowEdit(false)}
          footer={<>
            <button className="btn btn-ghost" onClick={() => setShowEdit(false)}>Cancel</button>
            <button className="btn btn-primary" form="edit-seating-form" type="submit" disabled={saving}>
              {saving ? <span className="spinner" /> : 'Save'}
            </button>
          </>}
        >
          {modalError && <div className="alert alert-error">{modalError}</div>}
          <form id="edit-seating-form" onSubmit={handleUpdateStatus}>
            <div className="form-group">
              <label>Status</label>
              <select value={editStatus} onChange={e => setEditStatus(e.target.value)}>
                {STATUSES.map(s => <option key={s}>{s}</option>)}
              </select>
            </div>
          </form>
        </Modal>
      )}
    </>
  )
}