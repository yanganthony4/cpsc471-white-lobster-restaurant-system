import { useState } from 'react'
import Modal from '../../components/Modal'
import { getSection, createSection, updateSection, deleteSection } from '../../lib/api'

export default function StaffSections() {
  const [lookupName, setLookupName] = useState('')
  const [section,    setSection]    = useState(null)
  const [error,      setError]      = useState('')
  const [loading,    setLoading]    = useState(false)

  const [showCreate, setShowCreate] = useState(false)
  const [showEdit,   setShowEdit]   = useState(false)
  const [form,       setForm]       = useState({ sectionName: '', employeeID: '' })
  const [editForm,   setEditForm]   = useState({ employeeID: '' })
  const [saving,     setSaving]     = useState(false)
  const [modalError, setModalError] = useState('')

  const handleLookup = async (e) => {
    e.preventDefault(); setError(''); setLoading(true); setSection(null)
    try { setSection(await getSection(lookupName)) } catch (err) { setError(err.message) } finally { setLoading(false) }
  }

  const handleCreate = async (e) => {
    e.preventDefault(); setModalError(''); setSaving(true)
    try {
      const s = await createSection({ sectionName: form.sectionName, employeeID: form.employeeID ? parseInt(form.employeeID) : null })
      setSection(s); setShowCreate(false); setForm({ sectionName: '', employeeID: '' })
    } catch (err) { setModalError(err.message) } finally { setSaving(false) }
  }

  const handleUpdate = async (e) => {
    e.preventDefault(); setModalError(''); setSaving(true)
    try {
      const s = await updateSection(section.sectionName, { employeeID: editForm.employeeID ? parseInt(editForm.employeeID) : null })
      setSection(s); setShowEdit(false)
    } catch (err) { setModalError(err.message) } finally { setSaving(false) }
  }

  const handleDelete = async () => {
    if (!confirm(`Delete section "${section.sectionName}"?`)) return
    setError(''); setLoading(true)
    try { await deleteSection(section.sectionName); setSection(null) } catch (err) { setError(err.message) } finally { setLoading(false) }
  }

  return (
    <>
      <div className="page-header">
        <h1>Sections</h1>
        <p>Manage dining sections and their assigned staff.</p>
      </div>

      <div className="toolbar">
        <form onSubmit={handleLookup} style={{ display: 'flex', gap: 10, alignItems: 'flex-end' }}>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label>Section Name</label>
            <input value={lookupName} onChange={e => setLookupName(e.target.value)} required placeholder="Main Dining" />
          </div>
          <button type="submit" className="btn btn-secondary" disabled={loading}>
            {loading ? <span className="spinner" /> : 'Look up'}
          </button>
        </form>
        <button className="btn btn-primary" onClick={() => { setForm({ sectionName: '', employeeID: '' }); setModalError(''); setShowCreate(true) }}>
          + Add section
        </button>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {section && (
        <div className="card" style={{ maxWidth: 400 }}>
          <div className="card-title">{section.sectionName}</div>
          <div className="info-row">
            <span className="label">Assigned Staff</span>
            <span className="value">{section.employeeID ? `#${section.employeeID}` : <span style={{ color: 'var(--ink-3)' }}>Unassigned</span>}</span>
          </div>
          <div style={{ display: 'flex', gap: 10, marginTop: 20 }}>
            <button className="btn btn-secondary" onClick={() => { setEditForm({ employeeID: section.employeeID || '' }); setModalError(''); setShowEdit(true) }}>
              Reassign staff
            </button>
            <button className="btn btn-danger" onClick={handleDelete}>Delete</button>
          </div>
        </div>
      )}

      {showCreate && (
        <Modal title="Add Section" onClose={() => setShowCreate(false)}
          footer={<>
            <button className="btn btn-ghost" onClick={() => setShowCreate(false)}>Cancel</button>
            <button className="btn btn-primary" form="create-section-form" type="submit" disabled={saving}>
              {saving ? <span className="spinner" /> : 'Add section'}
            </button>
          </>}
        >
          {modalError && <div className="alert alert-error">{modalError}</div>}
          <form id="create-section-form" onSubmit={handleCreate}>
            <div className="form-group">
              <label>Section Name</label>
              <input value={form.sectionName} onChange={e => setForm(f => ({ ...f, sectionName: e.target.value }))} required />
            </div>
            <div className="form-group">
              <label>Assigned Employee ID <span style={{ color: 'var(--ink-3)', fontWeight: 400 }}>(optional)</span></label>
              <input type="number" value={form.employeeID} onChange={e => setForm(f => ({ ...f, employeeID: e.target.value }))} />
            </div>
          </form>
        </Modal>
      )}

      {showEdit && (
        <Modal title={`Reassign: ${section.sectionName}`} onClose={() => setShowEdit(false)}
          footer={<>
            <button className="btn btn-ghost" onClick={() => setShowEdit(false)}>Cancel</button>
            <button className="btn btn-primary" form="edit-section-form" type="submit" disabled={saving}>
              {saving ? <span className="spinner" /> : 'Save'}
            </button>
          </>}
        >
          {modalError && <div className="alert alert-error">{modalError}</div>}
          <form id="edit-section-form" onSubmit={handleUpdate}>
            <div className="form-group">
              <label>Employee ID <span style={{ color: 'var(--ink-3)', fontWeight: 400 }}>(leave blank to unassign)</span></label>
              <input type="number" value={editForm.employeeID} onChange={e => setEditForm({ employeeID: e.target.value })} />
            </div>
          </form>
        </Modal>
      )}
    </>
  )
}