import { useState } from 'react'
import { useAuth } from '../../context/AuthContext'
import { updateCustomer } from '../../lib/api'

export default function CustomerProfile() {
  const { user, login } = useAuth()
  const [saving,  setSaving]  = useState(false)
  const [error,   setError]   = useState('')
  const [success, setSuccess] = useState('')

  const [form, setForm] = useState({
    name:        user.name,
    email:       user.email,
    phoneNumber: user.phoneNumber || '',
    password:    '',
  })

  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.password) { setError('Enter your new (or current) password to save.'); return }
    setError(''); setSuccess(''); setSaving(true)
    try {
      const updated = await updateCustomer(user.email, {
        email: form.email,
        name: form.name,
        phoneNumber: form.phoneNumber || null,
        password: form.password,
      })
      login({ ...updated, type: 'customer' })
      setForm(f => ({ ...f, password: '' }))
      setSuccess('Profile updated successfully.')
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
        <p>Update your account information.</p>
      </div>

      {error   && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      <div className="card" style={{ maxWidth: 480 }}>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Full Name</label>
            <input value={form.name} onChange={set('name')} required />
          </div>
          <div className="form-group">
            <label>Email</label>
            <input type="email" value={form.email} onChange={set('email')} required />
          </div>
          <div className="form-group">
            <label>Phone <span style={{ color: 'var(--ink-3)', fontWeight: 400 }}>(optional)</span></label>
            <input value={form.phoneNumber} onChange={set('phoneNumber')} placeholder="403-000-0000" />
          </div>
          <div className="form-group">
            <label>New Password <span style={{ color: 'var(--ink-3)', fontWeight: 400 }}>(required to save)</span></label>
            <input type="password" value={form.password} onChange={set('password')} placeholder="Enter new or current password" minLength={6} />
          </div>
          <button type="submit" className="btn btn-primary" disabled={saving}>
            {saving ? <span className="spinner" /> : 'Save changes'}
          </button>
        </form>
      </div>
    </>
  )
}