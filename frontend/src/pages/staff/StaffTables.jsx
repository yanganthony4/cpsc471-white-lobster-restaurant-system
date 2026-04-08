import { useState } from 'react'
import Modal from '../../components/Modal'
import { getTable, createTable, updateTable, deleteTable } from '../../lib/api'

const STATUSES = ['Available', 'Occupied', 'Reserved', 'Out of Service']
const STATUS_CLASS = { Available: 'badge-green', Occupied: 'badge-red', Reserved: 'badge-amber', 'Out of Service': 'badge-gray' }

const emptyForm = () => ({ tableNumber: '', sectionName: '', availabilityStatus: 'Available', capacity: 2 })

export default function StaffTables() {
  const [lookup, setLookup] = useState({ section: '', number: '' })
  const [table,  setTable]  = useState(null)
  const [error,  setError]  = useState('')
  const [loading,setLoading]= useState(false)

  const [showCreate, setShowCreate] = useState(false)
  const [showEdit,   setShowEdit]   = useState(false)
  const [form,       setForm]       = useState(emptyForm())
  const [saving,     setSaving]     = useState(false)
  const [modalError, setModalError] = useState('')

  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  const handleLookup = async (e) => {
    e.preventDefault()
    setError(''); setLoading(true); setTable(null)
    try {
      const t = await getTable(lookup.section, parseInt(lookup.number))
      setTable(t)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async (e) => {
    e.preventDefault()
    setModalError(''); setSaving(true)
    try {
      const t = await createTable({
        tableNumber: parseInt(form.tableNumber),
        sectionName: form.sectionName,
        availabilityStatus: form.availabilityStatus,
        capacity: parseInt(form.capacity),
      })
      setTable(t)
      setShowCreate(false)
      setForm(emptyForm())
    } catch (err) {
      setModalError(err.message)
    } finally {
      setSaving(false)
    }
  }

  const handleEdit = async (e) => {
    e.preventDefault()
    setModalError(''); setSaving(true)
    try {
      const t = await updateTable(table.sectionName, table.tableNumber, {
        availabilityStatus: form.availabilityStatus,
        capacity: parseInt(form.capacity),
      })
      setTable(t)
      setShowEdit(false)
    } catch (err) {
      setModalError(err.message)
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async () => {
    if (!confirm(`Delete table ${table.tableNumber} in ${table.sectionName}?`)) return
    setError(''); setLoading(true)
    try {
      await deleteTable(table.sectionName, table.tableNumber)
      setTable(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const openEdit = () => {
    setForm({ ...form, availabilityStatus: table.availabilityStatus, capacity: table.capacity })
    setModalError('')
    setShowEdit(true)
  }

  return (
    <>
      <div className="page-header">
        <h1>Tables</h1>
        <p>Look up a table by section and number to view or update its status.</p>
      </div>

      <div className="toolbar">
        <form onSubmit={handleLookup} style={{ display: 'flex', gap: 10, alignItems: 'flex-end', flexWrap: 'wrap' }}>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label>Section Name</label>
            <input value={lookup.section} onChange={e => setLookup(l => ({ ...l, section: e.target.value }))} required placeholder="Main Dining" />
          </div>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label>Table Number</label>
            <input type="number" min={1} value={lookup.number} onChange={e => setLookup(l => ({ ...l, number: e.target.value }))} required placeholder="1" style={{ width: 100 }} />
          </div>
          <button type="submit" className="btn btn-secondary" disabled={loading}>
            {loading ? <span className="spinner" /> : 'Look up'}
          </button>
        </form>
        <button className="btn btn-primary" onClick={() => { setForm(emptyForm()); setModalError(''); setShowCreate(true) }}>
          + Add table
        </button>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {table && (
        <div className="card" style={{ maxWidth: 480 }}>
          <div className="card-title">Table {table.tableNumber} — {table.sectionName}</div>
          <div className="info-row">
            <span className="label">Status</span>
            <span className="value"><span className={`badge ${STATUS_CLASS[table.availabilityStatus]}`}>{table.availabilityStatus}</span></span>
          </div>
          <div className="info-row">
            <span className="label">Capacity</span>
            <span className="value">{table.capacity} guests</span>
          </div>
          <div style={{ display: 'flex', gap: 10, marginTop: 20 }}>
            <button className="btn btn-secondary" onClick={openEdit}>Update status</button>
            <button className="btn btn-danger" onClick={handleDelete}>Delete</button>
          </div>
        </div>
      )}

      {/* Create modal */}
      {showCreate && (
        <Modal title="Add Table" onClose={() => setShowCreate(false)}
          footer={<>
            <button className="btn btn-ghost" onClick={() => setShowCreate(false)}>Cancel</button>
            <button className="btn btn-primary" form="create-table-form" type="submit" disabled={saving}>
              {saving ? <span className="spinner" /> : 'Add table'}
            </button>
          </>}
        >
          {modalError && <div className="alert alert-error">{modalError}</div>}
          <form id="create-table-form" onSubmit={handleCreate}>
            <div className="form-row">
              <div className="form-group">
                <label>Table Number</label>
                <input type="number" min={1} value={form.tableNumber} onChange={set('tableNumber')} required />
              </div>
              <div className="form-group">
                <label>Capacity</label>
                <input type="number" min={1} value={form.capacity} onChange={set('capacity')} required />
              </div>
            </div>
            <div className="form-group">
              <label>Section Name</label>
              <input value={form.sectionName} onChange={set('sectionName')} required />
            </div>
            <div className="form-group">
              <label>Status</label>
              <select value={form.availabilityStatus} onChange={set('availabilityStatus')}>
                {STATUSES.map(s => <option key={s}>{s}</option>)}
              </select>
            </div>
          </form>
        </Modal>
      )}

      {/* Edit modal */}
      {showEdit && (
        <Modal title={`Update Table ${table.tableNumber}`} onClose={() => setShowEdit(false)}
          footer={<>
            <button className="btn btn-ghost" onClick={() => setShowEdit(false)}>Cancel</button>
            <button className="btn btn-primary" form="edit-table-form" type="submit" disabled={saving}>
              {saving ? <span className="spinner" /> : 'Save'}
            </button>
          </>}
        >
          {modalError && <div className="alert alert-error">{modalError}</div>}
          <form id="edit-table-form" onSubmit={handleEdit}>
            <div className="form-group">
              <label>Status</label>
              <select value={form.availabilityStatus} onChange={set('availabilityStatus')}>
                {STATUSES.map(s => <option key={s}>{s}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Capacity</label>
              <input type="number" min={1} value={form.capacity} onChange={set('capacity')} required />
            </div>
          </form>
        </Modal>
      )}
    </>
  )
}