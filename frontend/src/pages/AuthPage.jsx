import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { loginCustomer, loginStaff, registerCustomer } from '../lib/api'

export default function AuthPage() {
  const { login } = useAuth()
  const navigate  = useNavigate()

  const [portal, setPortal] = useState('customer') // 'customer' | 'staff'
  const [mode,   setMode]   = useState('login')    // 'login' | 'register'
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState('')

  // Customer login
  const [custEmail, setCustEmail] = useState('')
  const [custPass,  setCustPass]  = useState('')

  // Customer register
  const [regName,  setRegName]  = useState('')
  const [regEmail, setRegEmail] = useState('')
  const [regPhone, setRegPhone] = useState('')
  const [regPass,  setRegPass]  = useState('')

  // Staff login
  const [staffId,   setStaffId]   = useState('')
  const [staffPass, setStaffPass] = useState('')

  const handleCustomerLogin = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const data = await loginCustomer({ email: custEmail, password: custPass })
      login({ ...data, type: 'customer' })
      navigate('/portal')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleCustomerRegister = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await registerCustomer({ email: regEmail, name: regName, phoneNumber: regPhone || null, password: regPass })
      const data = await loginCustomer({ email: regEmail, password: regPass })
      login({ ...data, type: 'customer' })
      navigate('/portal')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleStaffLogin = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const data = await loginStaff({ employeeID: parseInt(staffId), password: staffPass })
      login({ ...data, type: 'staff' })
      navigate('/staff')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-shell">
      <div className="auth-brand">
        <div>
          <div className="auth-brand-logo">White<br />Lobster</div>
          <p className="auth-brand-desc">
            Restaurant management platform. Reservations, waitlists, seating,
            billing — all in one place.
          </p>
        </div>
      </div>

      <div className="auth-panel">
        <div className="auth-form-wrap">
          {/* Portal toggle */}
          <div className="auth-tabs" style={{ marginBottom: 24 }}>
            <button
              className={`auth-tab${portal === 'customer' ? ' active' : ''}`}
              onClick={() => { setPortal('customer'); setMode('login'); setError('') }}
            >Guest</button>
            <button
              className={`auth-tab${portal === 'staff' ? ' active' : ''}`}
              onClick={() => { setPortal('staff'); setMode('login'); setError('') }}
            >Staff</button>
          </div>

          {/* ── Customer ── */}
          {portal === 'customer' && (
            <>
              <div className="auth-tabs">
                <button
                  className={`auth-tab${mode === 'login' ? ' active' : ''}`}
                  onClick={() => { setMode('login'); setError('') }}
                >Sign in</button>
                <button
                  className={`auth-tab${mode === 'register' ? ' active' : ''}`}
                  onClick={() => { setMode('register'); setError('') }}
                >Create account</button>
              </div>

              {error && <div className="alert alert-error">{error}</div>}

              {mode === 'login' ? (
                <form onSubmit={handleCustomerLogin}>
                  <div className="form-group">
                    <label>Email</label>
                    <input type="email" value={custEmail} onChange={e => setCustEmail(e.target.value)} required autoFocus />
                  </div>
                  <div className="form-group">
                    <label>Password</label>
                    <input type="password" value={custPass} onChange={e => setCustPass(e.target.value)} required />
                  </div>
                  <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
                    {loading ? <span className="spinner" /> : 'Sign in'}
                  </button>
                </form>
              ) : (
                <form onSubmit={handleCustomerRegister}>
                  <div className="form-group">
                    <label>Full name</label>
                    <input value={regName} onChange={e => setRegName(e.target.value)} required />
                  </div>
                  <div className="form-group">
                    <label>Email</label>
                    <input type="email" value={regEmail} onChange={e => setRegEmail(e.target.value)} required />
                  </div>
                  <div className="form-group">
                    <label>Phone <span style={{ color: 'var(--ink-3)', fontWeight: 400 }}>(optional)</span></label>
                    <input value={regPhone} onChange={e => setRegPhone(e.target.value)} />
                  </div>
                  <div className="form-group">
                    <label>Password</label>
                    <input type="password" value={regPass} onChange={e => setRegPass(e.target.value)} required minLength={6} />
                  </div>
                  <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
                    {loading ? <span className="spinner" /> : 'Create account'}
                  </button>
                </form>
              )}
            </>
          )}

          {/* ── Staff ── */}
          {portal === 'staff' && (
            <>
              <h2 style={{ marginBottom: 6 }}>Staff Sign In</h2>
              <p className="sub">Use your employee ID and password.</p>

              {error && <div className="alert alert-error">{error}</div>}

              <form onSubmit={handleStaffLogin}>
                <div className="form-group">
                  <label>Employee ID</label>
                  <input
                    type="number"
                    value={staffId}
                    onChange={e => setStaffId(e.target.value)}
                    required
                    autoFocus
                  />
                </div>
                <div className="form-group">
                  <label>Password</label>
                  <input
                    type="password"
                    value={staffPass}
                    onChange={e => setStaffPass(e.target.value)}
                    required
                  />
                </div>
                <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
                  {loading ? <span className="spinner" /> : 'Sign in'}
                </button>
              </form>
            </>
          )}
        </div>
      </div>
    </div>
  )
}