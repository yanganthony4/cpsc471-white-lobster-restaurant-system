import { useState, useEffect } from 'react'
import { useAuth } from '../../context/AuthContext'
import { getLoyalty, createLoyalty, deleteLoyalty } from '../../lib/api'

export default function CustomerLoyalty() {
  const { user } = useAuth()
  const [loyalty, setLoyalty] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving,  setSaving]  = useState(false)
  const [error,   setError]   = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    getLoyalty(user.email)
      .then(setLoyalty)
      .catch(() => setLoyalty(null))
      .finally(() => setLoading(false))
  }, [user.email])

  const handleEnroll = async () => {
    setError(''); setSaving(true)
    try {
      const data = await createLoyalty({ email: user.email, pointsBalance: 0 })
      setLoyalty(data)
      setSuccess('Welcome to the loyalty program!')
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  const handleLeave = async () => {
    if (!confirm('Leave the loyalty program? Your points will be lost.')) return
    setError(''); setSaving(true)
    try {
      await deleteLoyalty(user.email)
      setLoyalty(null)
      setSuccess('You have left the loyalty program.')
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <div className="loading-center"><span className="spinner" /></div>

  const tier = (pts) => {
    if (pts >= 1000) return { name: 'Gold', color: '#c8a96e' }
    if (pts >= 500)  return { name: 'Silver', color: '#8a9ba8' }
    return { name: 'Bronze', color: '#b0896a' }
  }

  return (
    <>
      <div className="page-header">
        <h1>Loyalty Program</h1>
        <p>Earn points with every visit and redeem them for exclusive offers.</p>
      </div>

      {error   && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      {loyalty ? (
        <>
          <div className="card" style={{ maxWidth: 480, marginBottom: 20 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 24 }}>
              <div>
                <div style={{ fontFamily: 'var(--font-display)', fontSize: '3rem', fontWeight: 400, lineHeight: 1 }}>
                  {loyalty.pointsBalance.toLocaleString()}
                </div>
                <div style={{ fontSize: 13, color: 'var(--ink-3)', marginTop: 4 }}>points balance</div>
              </div>
              <div style={{
                background: tier(loyalty.pointsBalance).color,
                color: '#fff',
                padding: '4px 14px',
                borderRadius: 20,
                fontSize: 12,
                fontWeight: 600,
                letterSpacing: '0.04em',
                textTransform: 'uppercase',
              }}>
                {tier(loyalty.pointsBalance).name}
              </div>
            </div>

            <div style={{ background: 'var(--cream)', borderRadius: 'var(--r)', padding: '14px 16px', marginBottom: 16 }}>
              <div style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--ink-3)', marginBottom: 8 }}>Tier progress</div>
              {loyalty.pointsBalance < 500 ? (
                <>
                  <ProgressBar value={loyalty.pointsBalance} max={500} />
                  <div style={{ fontSize: 12, color: 'var(--ink-3)', marginTop: 6 }}>{500 - loyalty.pointsBalance} pts until Silver</div>
                </>
              ) : loyalty.pointsBalance < 1000 ? (
                <>
                  <ProgressBar value={loyalty.pointsBalance - 500} max={500} />
                  <div style={{ fontSize: 12, color: 'var(--ink-3)', marginTop: 6 }}>{1000 - loyalty.pointsBalance} pts until Gold</div>
                </>
              ) : (
                <div style={{ fontSize: 13, color: 'var(--gold)', fontWeight: 500 }}>You've reached Gold status 🎉</div>
              )}
            </div>

            <div style={{ fontSize: 13, color: 'var(--ink-3)', marginBottom: 16 }}>
              Points are added to your account by staff after each visit. Redemptions are applied by our team at checkout.
            </div>

            <button className="btn btn-danger btn-sm" onClick={handleLeave} disabled={saving}>
              {saving ? <span className="spinner" /> : 'Leave loyalty program'}
            </button>
          </div>

          <div className="card" style={{ maxWidth: 480 }}>
            <div className="card-title">Tier Benefits</div>
            <TierRow name="Bronze" range="0–499 pts"  perks="Priority waitlist consideration, birthday bonus" color="#b0896a" />
            <TierRow name="Silver" range="500–999 pts" perks="5% discount on bills, early reservation access" color="#8a9ba8" />
            <TierRow name="Gold"   range="1000+ pts"  perks="10% discount, complimentary dessert, VIP seating" color="#c8a96e" />
          </div>
        </>
      ) : (
        <div className="card" style={{ maxWidth: 480 }}>
          <div className="card-title">Join the Loyalty Program</div>
          <div style={{ marginBottom: 24 }}>
            {[
              ['Earn points', 'Get points credited after each visit.'],
              ['Unlock tiers', 'Bronze → Silver → Gold with increasing perks.'],
              ['Redeem rewards', 'Discounts, complimentary items, and more.'],
            ].map(([title, desc]) => (
              <div key={title} style={{ display: 'flex', gap: 12, marginBottom: 16, alignItems: 'flex-start' }}>
                <div style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--terracotta)', marginTop: 6, flexShrink: 0 }} />
                <div>
                  <div style={{ fontWeight: 500, marginBottom: 2 }}>{title}</div>
                  <div style={{ fontSize: 13, color: 'var(--ink-3)' }}>{desc}</div>
                </div>
              </div>
            ))}
          </div>
          <button className="btn btn-primary" onClick={handleEnroll} disabled={saving}>
            {saving ? <span className="spinner" /> : 'Enroll — it\'s free'}
          </button>
        </div>
      )}
    </>
  )
}

function ProgressBar({ value, max }) {
  const pct = Math.min(100, Math.round((value / max) * 100))
  return (
    <div style={{ background: 'var(--border)', borderRadius: 4, height: 6, overflow: 'hidden' }}>
      <div style={{ width: `${pct}%`, height: '100%', background: 'var(--terracotta)', borderRadius: 4, transition: 'width 0.4s ease' }} />
    </div>
  )
}

function TierRow({ name, range, perks, color }) {
  return (
    <div style={{ display: 'flex', gap: 14, padding: '12px 0', borderBottom: '1px solid var(--border)', alignItems: 'flex-start' }}>
      <div style={{ width: 12, height: 12, borderRadius: '50%', background: color, marginTop: 4, flexShrink: 0 }} />
      <div>
        <div style={{ fontWeight: 500, marginBottom: 2 }}>{name} <span style={{ color: 'var(--ink-3)', fontSize: 12, fontWeight: 400 }}>({range})</span></div>
        <div style={{ fontSize: 13, color: 'var(--ink-3)' }}>{perks}</div>
      </div>
    </div>
  )
}