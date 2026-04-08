import { useState } from 'react'
import { useAuth } from '../../context/AuthContext'
import { updateStaff } from '../../lib/api'

const ROLES = ['Host', 'Server', 'Manager', 'Cashier']

export default function StaffProfile() {
  const { user, login } = useAuth()
  const [saving,  setSaving]  = useState(false)
  const [error,   setError]   = useState('')
  const [success, setSuccess] = useState('')

  const [form, setForm] = useState({
    name:     user.name,
    role:     user.role,
    password: '',
  })

  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.password) { setError('Enter your new (or current) password to save.'); return }
    setError(''); setSuccess(''); setSaving(true)
    try {
      const updated = await updateStaff(user.employeeID, {
        name: form.name,
        role: form.role,
        password: form.password,
      })
      login({ ...updated, type: 'staff' })
      setForm(f => ({ ...f, password: '' }))
      setSuccess('Profile updated.')
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <>
      <div className="page-header">
        <h1>Profile</h1>
        <p>Update your staff account.</p>
      </div>

      {error   && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      <div className="card" style={{ maxWidth: 420 }}>
        <div className="info-row" style={{ marginBottom: 16 }}>
          <span className="label">Employee ID</span>
          <span className="value">#{user.employeeID}</span>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Full Name</label>
            <input value={form.name} onChange={set('name')} required />
          </div>
          <div className="form-group">
            <label>Role</label>
            <select value={form.role} onChange={set('role')}>
              {ROLES.map(r => <option key={r}>{r}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label>New Password <span style={{ color: 'var(--ink-3)', fontWeight: 400 }}>(required to save)</span></label>
            <input type="password" value={form.password} onChange={set('password')} minLength={8} placeholder="Enter new or current password" />
          </div>
          <button type="submit" className="btn btn-primary" disabled={saving}>
            {saving ? <span className="spinner" /> : 'Save changes'}
          </button>
        </form>
      </div>
    </>
  )
}