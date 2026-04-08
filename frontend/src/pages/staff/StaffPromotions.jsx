import { useState } from 'react'
import Modal from '../../components/Modal'
import { getPromotion, createPromotion, updatePromotion, deletePromotion } from '../../lib/api'

const today = () => new Date().toISOString().slice(0, 10)
const emptyForm = () => ({ startDate: today(), endDate: today(), discountAmount: '', eligibilityRules: '' })

export default function StaffPromotions() {
  const [lookupId,  setLookupId]  = useState('')
  const [promo,     setPromo]     = useState(null)
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
    e.preventDefault(); setError(''); setSuccess(''); setLoading(true); setPromo(null)
    try { setPromo(await getPromotion(parseInt(lookupId))) } catch (err) { setError(err.message) } finally { setLoading(false) }
  }

  const buildPayload = () => ({
    startDate: form.startDate,
    endDate: form.endDate,
    discountAmount: parseFloat(form.discountAmount),
    eligibilityRules: form.eligibilityRules || null,
  })

  const handleCreate = async (e) => {
    e.preventDefault(); setModalError(''); setSaving(true)
    try {
      const p = await createPromotion(buildPayload())
      setPromo(p); setShowCreate(false); setForm(emptyForm()); setSuccess(`Promotion #${p.promoID} created.`)
    } catch (err) { setModalError(err.message) } finally { setSaving(false) }
  }

  const handleUpdate = async (e) => {
    e.preventDefault(); setModalError(''); setSaving(true)
    try {
      const p = await updatePromotion(promo.promoID, buildPayload())
      setPromo(p); setShowEdit(false); setSuccess('Promotion updated.')
    } catch (err) { setModalError(err.message) } finally { setSaving(false) }
  }

  const handleDelete = async () => {
    if (!confirm(`Delete promotion #${promo.promoID}?`)) return
    setLoading(true)
    try { await deletePromotion(promo.promoID); setPromo(null); setSuccess('Promotion deleted.') }
    catch (err) { setError(err.message) } finally { setLoading(false) }
  }

  const openEdit = () => {
    setForm({ startDate: promo.startDate, endDate: promo.endDate, discountAmount: promo.discountAmount, eligibilityRules: promo.eligibilityRules || '' })
    setModalError(''); setShowEdit(true)
  }

  const isActive = (p) => {
    const now = today()
    return p.startDate <= now && now <= p.endDate
  }

  return (
    <>
      <div className="page-header">
        <h1>Promotions</h1>
        <p>Look up and manage discount promotions by ID.</p>
      </div>

      <div className="toolbar">
        <form onSubmit={handleLookup} style={{ display: 'flex', gap: 10, alignItems: 'flex-end' }}>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label>Promotion ID</label>
            <input type="number" min={1} value={lookupId} onChange={e => setLookupId(e.target.value)} required placeholder="501" style={{ width: 120 }} />
          </div>
          <button type="submit" className="btn btn-secondary" disabled={loading}>
            {loading ? <span className="spinner" /> : 'Look up'}
          </button>
        </form>
        <button className="btn btn-primary" onClick={() => { setForm(emptyForm()); setModalError(''); setShowCreate(true) }}>
          + New promotion
        </button>
      </div>

      {error   && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      {promo && (
        <div className="card" style={{ maxWidth: 480 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
            <div style={{ fontFamily: 'var(--font-display)', fontSize: '1.1rem', fontWeight: 500 }}>
              Promotion #{promo.promoID}
            </div>
            <span className={`badge ${isActive(promo) ? 'badge-green' : 'badge-gray'}`}>
              {isActive(promo) ? 'Active' : 'Inactive'}
            </span>
          </div>
          <div style={{ borderBottom: '1px solid var(--border)', marginBottom: 12 }} />
          <div className="info-row">
            <span className="label">Discount</span>
            <span className="value" style={{ color: 'var(--terracotta)', fontWeight: 600 }}>
              ${Number(promo.discountAmount).toFixed(2)} off
            </span>
          </div>
          <div className="info-row"><span className="label">Valid From</span><span className="value">{promo.startDate}</span></div>
          <div className="info-row"><span className="label">Valid Until</span><span className="value">{promo.endDate}</span></div>
          <div className="info-row">
            <span className="label">Eligibility</span>
            <span className="value">{promo.eligibilityRules || <span style={{ color: 'var(--ink-3)' }}>No restrictions</span>}</span>
          </div>
          <div style={{ display: 'flex', gap: 10, marginTop: 20 }}>
            <button className="btn btn-secondary" onClick={openEdit}>Edit</button>
            <button className="btn btn-danger" onClick={handleDelete}>Delete</button>
          </div>
        </div>
      )}

      {showCreate && (
        <Modal title="New Promotion" onClose={() => setShowCreate(false)}
          footer={<>
            <button className="btn btn-ghost" onClick={() => setShowCreate(false)}>Cancel</button>
            <button className="btn btn-primary" form="create-promo-form" type="submit" disabled={saving}>
              {saving ? <span className="spinner" /> : 'Create'}
            </button>
          </>}
        >
          {modalError && <div className="alert alert-error">{modalError}</div>}
          <form id="create-promo-form" onSubmit={handleCreate}>
            <PromotionForm form={form} set={set} />
          </form>
        </Modal>
      )}

      {showEdit && (
        <Modal title={`Edit Promotion #${promo.promoID}`} onClose={() => setShowEdit(false)}
          footer={<>
            <button className="btn btn-ghost" onClick={() => setShowEdit(false)}>Cancel</button>
            <button className="btn btn-primary" form="edit-promo-form" type="submit" disabled={saving}>
              {saving ? <span className="spinner" /> : 'Save'}
            </button>
          </>}
        >
          {modalError && <div className="alert alert-error">{modalError}</div>}
          <form id="edit-promo-form" onSubmit={handleUpdate}>
            <PromotionForm form={form} set={set} />
          </form>
        </Modal>
      )}
    </>
  )
}

function PromotionForm({ form, set }) {
  return (
    <>
      <div className="form-group">
        <label>Discount Amount ($)</label>
        <input type="number" step="0.01" min="0" value={form.discountAmount} onChange={set('discountAmount')} required />
      </div>
      <div className="form-row">
        <div className="form-group">
          <label>Start Date</label>
          <input type="date" value={form.startDate} onChange={set('startDate')} required />
        </div>
        <div className="form-group">
          <label>End Date</label>
          <input type="date" value={form.endDate} onChange={set('endDate')} required />
        </div>
      </div>
      <div className="form-group">
        <label>Eligibility Rules <span style={{ color: 'var(--ink-3)', fontWeight: 400 }}>(optional)</span></label>
        <textarea value={form.eligibilityRules} onChange={set('eligibilityRules')} rows={2} placeholder="e.g. Loyalty members only, bills over $30…" />
      </div>
    </>
  )
}