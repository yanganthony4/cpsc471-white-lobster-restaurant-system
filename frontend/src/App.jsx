import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'

import AuthPage      from './pages/AuthPage'
import CustomerShell from './pages/customer/CustomerShell'
import CustomerDash  from './pages/customer/CustomerDash'
import CustomerReservation from './pages/customer/CustomerReservation'
import CustomerWaitlist    from './pages/customer/CustomerWaitlist'
import CustomerProfile     from './pages/customer/CustomerProfile'
import CustomerLoyalty     from './pages/customer/CustomerLoyalty'

import StaffShell      from './pages/staff/StaffShell'
import StaffDash       from './pages/staff/StaffDash'
import StaffTables     from './pages/staff/StaffTables'
import StaffSeating    from './pages/staff/StaffSeating'
import StaffReservations from './pages/staff/StaffReservations'
import StaffWaitlist   from './pages/staff/StaffWaitlist'
import StaffMenu       from './pages/staff/StaffMenu'
import StaffBills      from './pages/staff/StaffBills'
import StaffPromotions from './pages/staff/StaffPromotions'
import StaffSections   from './pages/staff/StaffSections'
import StaffProfile    from './pages/staff/StaffProfile'

function RequireCustomer({ children }) {
  const { user } = useAuth()
  if (!user) return <Navigate to="/" replace />
  if (user.type !== 'customer') return <Navigate to="/staff" replace />
  return children
}

function RequireStaff({ children }) {
  const { user } = useAuth()
  if (!user) return <Navigate to="/" replace />
  if (user.type !== 'staff') return <Navigate to="/portal" replace />
  return children
}

export default function App() {
  const { user } = useAuth()

  return (
    <Routes>
      <Route
        path="/"
        element={
          user
            ? <Navigate to={user.type === 'staff' ? '/staff' : '/portal'} replace />
            : <AuthPage />
        }
      />

      {/* Customer portal */}
      <Route path="/portal" element={<RequireCustomer><CustomerShell /></RequireCustomer>}>
        <Route index element={<CustomerDash />} />
        <Route path="reservation" element={<CustomerReservation />} />
        <Route path="waitlist"    element={<CustomerWaitlist />} />
        <Route path="loyalty"     element={<CustomerLoyalty />} />
        <Route path="profile"     element={<CustomerProfile />} />
      </Route>

      {/* Staff portal */}
      <Route path="/staff" element={<RequireStaff><StaffShell /></RequireStaff>}>
        <Route index           element={<StaffDash />} />
        <Route path="tables"   element={<StaffTables />} />
        <Route path="sections" element={<StaffSections />} />
        <Route path="seating"  element={<StaffSeating />} />
        <Route path="reservations" element={<StaffReservations />} />
        <Route path="waitlist" element={<StaffWaitlist />} />
        <Route path="menu"     element={<StaffMenu />} />
        <Route path="bills"    element={<StaffBills />} />
        <Route path="promotions" element={<StaffPromotions />} />
        <Route path="profile"  element={<StaffProfile />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}