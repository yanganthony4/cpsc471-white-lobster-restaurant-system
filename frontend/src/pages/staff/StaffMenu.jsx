import { useState } from 'react'
import Modal from '../../components/Modal'
import { getMenuItem, createMenuItem, updateMenuItem, deleteMenuItem } from '../../lib/api'

const emptyForm = () => ({ name: '', description: '', currentPrice: '' })

export default function StaffMenu() {
  const [lookupId,  setLookupId]  = useState('')
  const [item,      setItem]      = useState(null)
  const [error,     setError]     = useState('')
  const [loading,   setLoading]   = useState(false)
  const [success,   setSuccess]   = useState('')

  const [showCreate, setShowCreate] = useState(false)
  const [showEdit,   setShowEdit]   = useState(false)
  const [form,       setForm]       = useState(emptyForm())
  const [saving,     setSaving]     = useState(false)
  const [modalError, setModalError] = useState('')

  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  const handleLookup = async (e) => {
    e.preventDefault(); setError(''); setSuccess(''); setLoading(true); setItem(null)
    try { setItem(await getMenuItem(parseInt(lookupId))) } catch (err) { setError(err.message) } finally { setLoading(false) }
  }

  const handleCreate = async (e) => {
    e.preventDefault(); setModalError(''); setSaving(true)
    try {
      const i = await createMenuItem({ name: form.name, description: form.description || null, currentPrice: parseFloat(form.currentPrice) })
      setItem(i); setShowCreate(false); setForm(emptyForm()); setSuccess(`"${i.name}" added to menu.`)
    } catch (err) { setModalError(err.message) } finally { setSaving(false) }
  }

  const handleUpdate = async (e) => {
    e.preventDefault(); setModalError(''); setSaving(true)
    try {
      const i = await updateMenuItem(item.menuItemID, { name: form.name, description: form.description || null, currentPrice: parseFloat(form.currentPrice) })
      setItem(i); setShowEdit(false); setSuccess('Menu item updated.')
    } catch (err) { setModalError(err.message) } finally { setSaving(false) }
  }

  const handleDelete = async () => {
    if (!confirm(`Delete "${item.name}"?`)) return
    setLoading(true)
    try { await deleteMenuItem(item.menuItemID); setItem(null); setSuccess('Menu item deleted.') }
    catch (err) { setError(err.message) } finally { setLoading(false) }
  }

  const openEdit = () => {
    setForm({ name: item.name, description: item.description || '', currentPrice: item.currentPrice })
    setModalError('')
    setShowEdit(true)
  }

  return (
    <>
      <div className="page-header">
        <h1>Menu Items</h1>
        <p>Look up menu items by ID, or add new ones.</p>
      </div>

      <div className="toolbar">
        <form onSubmit={handleLookup} style={{ display: 'flex', gap: 10, alignItems: 'flex-end' }}>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label>Menu Item ID</label>
            <input type="number" min={1} value={lookupId} onChange={e => setLookupId(e.target.value)} required placeholder="601" style={{ width: 120 }} />
          </div>
          <button type="submit" className="btn btn-secondary" disabled={loading}>
            {loading ? <span className="spinner" /> : 'Look up'}
          </button>
        </form>
        <button className="btn btn-primary" onClick={() => { setForm(emptyForm()); setModalError(''); setShowCreate(true) }}>
          + Add item
        </button>
      </div>

      {error   && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      {item && (
        <div className="card" style={{ maxWidth: 480 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 12 }}>
            <div className="card-title" style={{ marginBottom: 0, paddingBottom: 0, border: 'none' }}>{item.name}</div>
            <div style={{ fontFamily: 'var(--font-display)', fontSize: '1.5rem', color: 'var(--terracotta)' }}>
              ${Number(item.currentPrice).toFixed(2)}
            </div>
          </div>
          <div style={{ borderBottom: '1px solid var(--border)', marginBottom: 12 }} />
          <div className="info-row"><span className="label">ID</span><span className="value">#{item.menuItemID}</span></div>
          <div className="info-row">
            <span className="label">Description</span>
            <span className="value">{item.description || <span style={{ color: 'var(--ink-3)' }}>No description</span>}</span>
          </div>
          <div style={{ display: 'flex', gap: 10, marginTop: 20 }}>
            <button className="btn btn-secondary" onClick={openEdit}>Edit</button>
            <button className="btn btn-danger" onClick={handleDelete}>Delete</button>
          </div>
        </div>
      )}

      {showCreate && (
        <Modal title="Add Menu Item" onClose={() => setShowCreate(false)}
          footer={<>
            <button className="btn btn-ghost" onClick={() => setShowCreate(false)}>Cancel</button>
            <button className="btn btn-primary" form="create-menu-form" type="submit" disabled={saving}>
              {saving ? <span className="spinner" /> : 'Add item'}
            </button>
          </>}
        >
          {modalError && <div className="alert alert-error">{modalError}</div>}
          <form id="create-menu-form" onSubmit={handleCreate}>
            <MenuItemForm form={form} set={set} />
          </form>
        </Modal>
      )}

      {showEdit && (
        <Modal title="Edit Menu Item" onClose={() => setShowEdit(false)}
          footer={<>
            <button className="btn btn-ghost" onClick={() => setShowEdit(false)}>Cancel</button>
            <button className="btn btn-primary" form="edit-menu-form" type="submit" disabled={saving}>
              {saving ? <span className="spinner" /> : 'Save'}
            </button>
          </>}
        >
          {modalError && <div className="alert alert-error">{modalError}</div>}
          <form id="edit-menu-form" onSubmit={handleUpdate}>
            <MenuItemForm form={form} set={set} />
          </form>
        </Modal>
      )}
    </>
  )
}

function MenuItemForm({ form, set }) {
  return (
    <>
      <div className="form-group">
        <label>Name</label>
        <input value={form.name} onChange={set('name')} required maxLength={100} />
      </div>
      <div className="form-group">
        <label>Price ($)</label>
        <input type="number" step="0.01" min="0" value={form.currentPrice} onChange={set('currentPrice')} required />
      </div>
      <div className="form-group">
        <label>Description <span style={{ color: 'var(--ink-3)', fontWeight: 400 }}>(optional)</span></label>
        <textarea value={form.description} onChange={set('description')} rows={2} />
      </div>
    </>
  )
}