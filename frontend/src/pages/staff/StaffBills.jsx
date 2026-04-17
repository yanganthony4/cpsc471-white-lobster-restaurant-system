import { useState } from 'react'
import Modal from '../../components/Modal'
import {
  getBill, createBill, updateBill, deleteBill,
  createBillItem, deleteBillItem,
  createPayment,
  getMenuItem,
} from '../../lib/api'

const PAYMENT_METHODS = ['Cash', 'Debit', 'Credit', 'Gift Card', 'Online']

export default function StaffBills() {
  const [lookupId,  setLookupId]  = useState('')
  const [bill,      setBill]      = useState(null)
  const [error,     setError]     = useState('')
  const [loading,   setLoading]   = useState(false)
  const [success,   setSuccess]   = useState('')

  // Create bill
  const [showCreate,  setShowCreate]  = useState(false)
  const [createForm,  setCreateForm]  = useState({ assignmentID: '', totalAmount: '', taxesAndFees: '', promoID: '' })
  const [saving,      setSaving]      = useState(false)
  const [modalError,  setModalError]  = useState('')

  // Add item
  const [showAddItem, setShowAddItem] = useState(false)
  const [itemForm,    setItemForm]    = useState({ menuItemID: '', quantity: 1, priceAtOrder: '' })
  const [itemLookup,  setItemLookup]  = useState(null)

  // Payment
  const [showPayment, setShowPayment] = useState(false)
  const [payForm,     setPayForm]     = useState({ paymentMethod: 'Cash', amount: '' })

  // Settle
  const [showSettle,  setShowSettle]  = useState(false)

  const setC = (k) => (e) => setCreateForm(f => ({ ...f, [k]: e.target.value }))
  const setI = (k) => (e) => setItemForm(f => ({ ...f, [k]: e.target.value }))
  const setP = (k) => (e) => setPayForm(f => ({ ...f, [k]: e.target.value }))

  const handleLookup = async (e) => {
  e.preventDefault(); setError(''); setSuccess(''); setLoading(true); setBill(null)
  setBillItems([]); setBillPayments([])
  try {
    const b = await getBill(parseInt(lookupId))
    setBill(b)
    // FIX: also load items and payments
    const [items, pays] = await Promise.allSettled([
      listBillItems(b.invoiceID),
      listPayments(b.invoiceID),
    ])
    if (items.status === 'fulfilled') setBillItems(items.value)
    if (pays.status  === 'fulfilled') setBillPayments(pays.value)
  } catch (err) { setError(err.message) }
  finally { setLoading(false) }
}

  const handleCreate = async (e) => {
    e.preventDefault(); setModalError(''); setSaving(true)
    try {
      const b = await createBill({
        assignmentID: parseInt(createForm.assignmentID),
        totalAmount: parseFloat(createForm.totalAmount),
        taxesAndFees: parseFloat(createForm.taxesAndFees),
        promoID: createForm.promoID ? parseInt(createForm.promoID) : null,
        isSettled: false,
      })
      setBill(b); setShowCreate(false); setSuccess(`Bill #${b.invoiceID} created.`)
      setCreateForm({ assignmentID: '', totalAmount: '', taxesAndFees: '', promoID: '' })
    } catch (err) { setModalError(err.message) } finally { setSaving(false) }
  }

  const handleLookupMenuItem = async () => {
    if (!itemForm.menuItemID) return
    try {
      const item = await getMenuItem(parseInt(itemForm.menuItemID))
      setItemLookup(item)
      setItemForm(f => ({ ...f, priceAtOrder: item.currentPrice }))
    } catch {
      setItemLookup(null)
    }
  }

  const handleAddItem = async (e) => {
    e.preventDefault(); setModalError(''); setSaving(true)
    try {
      await createBillItem({
        invoiceID: bill.invoiceID,
        menuItemID: parseInt(itemForm.menuItemID),
        quantity: parseInt(itemForm.quantity),
        priceAtOrder: parseFloat(itemForm.priceAtOrder),
      })
      setShowAddItem(false)
      setItemForm({ menuItemID: '', quantity: 1, priceAtOrder: '' })
      setItemLookup(null)
      setSuccess('Item added to bill.')
    } catch (err) { setModalError(err.message) } finally { setSaving(false) }
  }

  const handlePayment = async (e) => {
    e.preventDefault(); setModalError(''); setSaving(true)
    try {
      await createPayment({
        invoiceID: bill.invoiceID,
        paymentMethod: payForm.paymentMethod,
        amount: parseFloat(payForm.amount),
      })
      setShowPayment(false)
      setPayForm({ paymentMethod: 'Cash', amount: '' })
      setSuccess('Payment recorded.')
    } catch (err) { setModalError(err.message) } finally { setSaving(false) }
  }

  const reloadBillDetails = async () => {
  if (!bill) return
  const [items, pays] = await Promise.allSettled([
    listBillItems(bill.invoiceID),
    listPayments(bill.invoiceID),
  ])
  if (items.status === 'fulfilled') setBillItems(items.value)
  if (pays.status  === 'fulfilled') setBillPayments(pays.value)
  // Also refresh the bill itself (to pick up isSettled changes)
  const b = await getBill(bill.invoiceID)
  setBill(b)
}

  const handleSettle = async () => {
    setSaving(true)
    try {
      const b = await updateBill(bill.invoiceID, {
        promoID: bill.promoID,
        totalAmount: bill.totalAmount,
        taxesAndFees: bill.taxesAndFees,
        isSettled: true,
      })
      setBill(b); setShowSettle(false); setSuccess('Bill marked as settled.')
    } catch (err) { setError(err.message) } finally { setSaving(false) }
  }

  const handleDelete = async () => {
    if (!confirm('Delete this bill? This cannot be undone.')) return
    setLoading(true)
    try { await deleteBill(bill.invoiceID); setBill(null); setSuccess('Bill deleted.') }
    catch (err) { setError(err.message) } finally { setLoading(false) }
  }

  const fmtMoney = (v) => `$${Number(v).toFixed(2)}`

  return (
    <>
      <div className="page-header">
        <h1>Bills</h1>
        <p>Look up a bill by invoice ID, or create one for a seating assignment.</p>
      </div>

      <div className="toolbar">
        <form onSubmit={handleLookup} style={{ display: 'flex', gap: 10, alignItems: 'flex-end' }}>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label>Invoice ID</label>
            <input type="number" min={1} value={lookupId} onChange={e => setLookupId(e.target.value)} required placeholder="701" style={{ width: 120 }} />
          </div>
          <button type="submit" className="btn btn-secondary" disabled={loading}>
            {loading ? <span className="spinner" /> : 'Look up'}
          </button>
        </form>
        <button className="btn btn-primary" onClick={() => { setCreateForm({ assignmentID: '', totalAmount: '', taxesAndFees: '', promoID: '' }); setModalError(''); setShowCreate(true) }}>
          + Create bill
        </button>
      </div>

      {error   && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      {bill && (
        <div style={{ maxWidth: 560 }}>
          <div className="card" style={{ marginBottom: 16 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
              <div className="card-title" style={{ margin: 0, padding: 0, border: 'none' }}>Invoice #{bill.invoiceID}</div>
              <span className={`badge ${bill.isSettled ? 'badge-green' : 'badge-amber'}`}>
                {bill.isSettled ? 'Settled' : 'Unpaid'}
              </span>
            </div>
            <div style={{ borderBottom: '1px solid var(--border)', marginBottom: 12 }} />
            <div className="info-row"><span className="label">Assignment</span><span className="value">#{bill.assignmentID}</span></div>
            <div className="info-row"><span className="label">Promo</span><span className="value">{bill.promoID ? `#${bill.promoID}` : '—'}</span></div>
            <div className="info-row"><span className="label">Subtotal</span><span className="value">{fmtMoney(bill.totalAmount)}</span></div>
            <div className="info-row"><span className="label">Tax & Fees</span><span className="value">{fmtMoney(bill.taxesAndFees)}</span></div>
            <div className="info-row">
              <span className="label" style={{ fontWeight: 700 }}>Total</span>
              <span className="value" style={{ fontFamily: 'var(--font-display)', fontSize: '1.3rem', color: 'var(--terracotta)' }}>
                {fmtMoney(Number(bill.totalAmount) + Number(bill.taxesAndFees))}
              </span>
            </div>

            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginTop: 20 }}>
              <button className="btn btn-secondary btn-sm" onClick={() => { setItemForm({ menuItemID: '', quantity: 1, priceAtOrder: '' }); setItemLookup(null); setModalError(''); setShowAddItem(true) }}>
                + Add item
              </button>
              <button className="btn btn-secondary btn-sm" onClick={() => { setPayForm({ paymentMethod: 'Cash', amount: '' }); setModalError(''); setShowPayment(true) }}>
                Record payment
              </button>
              {!bill.isSettled && (
                <button className="btn btn-primary btn-sm" onClick={() => setShowSettle(true)}>
                  Mark settled
                </button>
              )}
              <button className="btn btn-danger btn-sm" onClick={handleDelete}>Delete bill</button>
            </div>
          </div>
        </div>
      )}

      {/* Create bill modal */}
      {showCreate && (
        <Modal title="Create Bill" onClose={() => setShowCreate(false)}
          footer={<>
            <button className="btn btn-ghost" onClick={() => setShowCreate(false)}>Cancel</button>
            <button className="btn btn-primary" form="create-bill-form" type="submit" disabled={saving}>
              {saving ? <span className="spinner" /> : 'Create'}
            </button>
          </>}
        >
          {modalError && <div className="alert alert-error">{modalError}</div>}
          <form id="create-bill-form" onSubmit={handleCreate}>
            <div className="form-group">
              <label>Assignment ID</label>
              <input type="number" min={1} value={createForm.assignmentID} onChange={setC('assignmentID')} required />
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Subtotal ($)</label>
                <input type="number" step="0.01" min="0" value={createForm.totalAmount} onChange={setC('totalAmount')} required />
              </div>
              <div className="form-group">
                <label>Tax & Fees ($)</label>
                <input type="number" step="0.01" min="0" value={createForm.taxesAndFees} onChange={setC('taxesAndFees')} required />
              </div>
            </div>
            <div className="form-group">
              <label>Promo ID <span style={{ color: 'var(--ink-3)', fontWeight: 400 }}>(optional)</span></label>
              <input type="number" min={1} value={createForm.promoID} onChange={setC('promoID')} />
            </div>
          </form>
        </Modal>
      )}

      {/* Add item modal */}
      {showAddItem && (
        <Modal title="Add Item to Bill" onClose={() => setShowAddItem(false)}
          footer={<>
            <button className="btn btn-ghost" onClick={() => setShowAddItem(false)}>Cancel</button>
            <button className="btn btn-primary" form="add-item-form" type="submit" disabled={saving}>
              {saving ? <span className="spinner" /> : 'Add item'}
            </button>
          </>}
        >
          {modalError && <div className="alert alert-error">{modalError}</div>}
          <form id="add-item-form" onSubmit={handleAddItem}>
            <div style={{ display: 'flex', gap: 8, alignItems: 'flex-end' }}>
              <div className="form-group" style={{ flex: 1, marginBottom: 0 }}>
                <label>Menu Item ID</label>
                <input type="number" min={1} value={itemForm.menuItemID} onChange={setI('menuItemID')} required />
              </div>
              <button type="button" className="btn btn-secondary btn-sm" style={{ marginBottom: 1 }} onClick={handleLookupMenuItem}>
                Lookup
              </button>
            </div>
            {itemLookup && (
              <div className="alert alert-info" style={{ marginTop: 8, marginBottom: 0 }}>
                {itemLookup.name} — ${Number(itemLookup.currentPrice).toFixed(2)}
              </div>
            )}
            <div className="form-row" style={{ marginTop: 12 }}>
              <div className="form-group">
                <label>Quantity</label>
                <input type="number" min={1} value={itemForm.quantity} onChange={setI('quantity')} required />
              </div>
              <div className="form-group">
                <label>Price at Order ($)</label>
                <input type="number" step="0.01" min="0" value={itemForm.priceAtOrder} onChange={setI('priceAtOrder')} required />
              </div>
            </div>
          </form>
        </Modal>
      )}

      {/* Payment modal */}
      {showPayment && (
        <Modal title="Record Payment" onClose={() => setShowPayment(false)}
          footer={<>
            <button className="btn btn-ghost" onClick={() => setShowPayment(false)}>Cancel</button>
            <button className="btn btn-primary" form="payment-form" type="submit" disabled={saving}>
              {saving ? <span className="spinner" /> : 'Record payment'}
            </button>
          </>}
        >
          {modalError && <div className="alert alert-error">{modalError}</div>}
          <div className="alert alert-info" style={{ marginBottom: 16 }}>
            Invoice #{bill.invoiceID} · Total: {fmtMoney(Number(bill.totalAmount) + Number(bill.taxesAndFees))}
          </div>
          <form id="payment-form" onSubmit={handlePayment}>
            <div className="form-group">
              <label>Payment Method</label>
              <select value={payForm.paymentMethod} onChange={setP('paymentMethod')}>
                {PAYMENT_METHODS.map(m => <option key={m}>{m}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Amount ($)</label>
              <input type="number" step="0.01" min="0.01" value={payForm.amount} onChange={setP('amount')} required />
            </div>
          </form>
        </Modal>
      )}

      {/* Settle confirmation */}
      {showSettle && (
        <Modal title="Mark as Settled?" onClose={() => setShowSettle(false)}
          footer={<>
            <button className="btn btn-ghost" onClick={() => setShowSettle(false)}>Cancel</button>
            <button className="btn btn-primary" onClick={handleSettle} disabled={saving}>
              {saving ? <span className="spinner" /> : 'Confirm'}
            </button>
          </>}
        >
          <p style={{ fontSize: 13, color: 'var(--ink-2)' }}>
            This will mark invoice #{bill.invoiceID} as settled. This action cannot be easily undone.
          </p>
        </Modal>
      )}
    </>
  )
}