// lib/api.js
// FIX LOG:
//  - loginStaff now sends { employeeID, password } correctly (was already correct)
//  - getTable / updateTable / deleteTable path order was (section, num) but backend
//    route is /{section_name}/{table_number} — verified match, no change needed
//  - getLoyalty / createLoyalty / updateLoyalty / deleteLoyalty paths verified

const BASE = 'http://localhost:8000';

async function req(method, path, body) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' },
  };
  if (body !== undefined) opts.body = JSON.stringify(body);

  const res = await fetch(`${BASE}${path}`, opts);

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const err = await res.json();
      // FastAPI validation errors return { detail: [ {loc, msg, type} ] }
      if (Array.isArray(err.detail)) {
        detail = err.detail.map(d => d.msg).join('; ');
      } else {
        detail = err.detail || detail;
      }
    } catch {
      // response body not JSON — keep statusText
    }
    throw new Error(detail);
  }

  if (res.status === 204) return null;
  return res.json();
}

const get  = (path)       => req('GET',    path);
const post = (path, body) => req('POST',   path, body);
const put  = (path, body) => req('PUT',    path, body);
const del  = (path)       => req('DELETE', path);

// ── Auth ──────────────────────────────────────────────────────────────────────
export const loginCustomer    = (data) => post('/customers/login', data);
export const loginStaff       = (data) => post('/staff/login', data);
export const registerCustomer = (data) => post('/customers/', data);
export const registerStaff    = (data) => post('/staff/', data);

// ── Customers ─────────────────────────────────────────────────────────────────
export const getCustomer    = (email)       => get(`/customers/${encodeURIComponent(email)}`);
export const updateCustomer = (email, data) => put(`/customers/${encodeURIComponent(email)}`, data);

// ── Staff ─────────────────────────────────────────────────────────────────────
export const getStaff    = (id)       => get(`/staff/${id}`);
export const updateStaff = (id, data) => put(`/staff/${id}`, data);

// ── Loyalty ───────────────────────────────────────────────────────────────────
export const getLoyalty    = (email)        => get(`/loyalty/${encodeURIComponent(email)}`);
export const createLoyalty = (data)         => post('/loyalty/', data);
export const updateLoyalty = (email, points) =>
  put(`/loyalty/${encodeURIComponent(email)}`, { pointsBalance: points });
export const deleteLoyalty = (email) => del(`/loyalty/${encodeURIComponent(email)}`);

// ── Reservations ──────────────────────────────────────────────────────────────
export const getReservation    = (email)       => get(`/reservation/${encodeURIComponent(email)}`);
export const createReservation = (data)        => post('/reservation/', data);
export const updateReservation = (email, data) => put(`/reservation/${encodeURIComponent(email)}`, data);
export const deleteReservation = (email)       => del(`/reservation/${encodeURIComponent(email)}`);

// ── Waitlist ──────────────────────────────────────────────────────────────────
export const getWaitlist    = (email)       => get(`/waitlist/${encodeURIComponent(email)}`);
export const createWaitlist = (data)        => post('/waitlist/', data);
export const updateWaitlist = (email, data) => put(`/waitlist/${encodeURIComponent(email)}`, data);
export const deleteWaitlist = (email)       => del(`/waitlist/${encodeURIComponent(email)}`);

// ── Sections ──────────────────────────────────────────────────────────────────
export const getSection    = (name)        => get(`/sections/${encodeURIComponent(name)}`);
export const createSection = (data)        => post('/sections/', data);
export const updateSection = (name, data)  => put(`/sections/${encodeURIComponent(name)}`, data);
export const deleteSection = (name)        => del(`/sections/${encodeURIComponent(name)}`);

// ── Tables ────────────────────────────────────────────────────────────────────
// Backend route: GET /tables/{section_name}/{table_number}
export const getTable    = (section, num)        => get(`/tables/${encodeURIComponent(section)}/${num}`);
export const createTable = (data)                => post('/tables/', data);
export const updateTable = (section, num, data)  => put(`/tables/${encodeURIComponent(section)}/${num}`, data);
export const deleteTable = (section, num)        => del(`/tables/${encodeURIComponent(section)}/${num}`);

// ── Seating Assignments ───────────────────────────────────────────────────────
export const getAssignment    = (id)        => get(`/seating-assignments/${id}`);
export const createAssignment = (data)      => post('/seating-assignments/', data);
export const updateAssignment = (id, data)  => put(`/seating-assignments/${id}`, data);
export const deleteAssignment = (id)        => del(`/seating-assignments/${id}`);

// ── Menu Items ────────────────────────────────────────────────────────────────
export const getMenuItem    = (id)        => get(`/menu-items/${id}`);
export const createMenuItem = (data)      => post('/menu-items/', data);
export const updateMenuItem = (id, data)  => put(`/menu-items/${id}`, data);
export const deleteMenuItem = (id)        => del(`/menu-items/${id}`);

// ── Promotions ────────────────────────────────────────────────────────────────
export const getPromotion    = (id)        => get(`/promotions/${id}`);
export const createPromotion = (data)      => post('/promotions/', data);
export const updatePromotion = (id, data)  => put(`/promotions/${id}`, data);
export const deletePromotion = (id)        => del(`/promotions/${id}`);

// ── Bills ─────────────────────────────────────────────────────────────────────
export const getBill    = (id)        => get(`/bills/${id}`);
export const createBill = (data)      => post('/bills/', data);
export const updateBill = (id, data)  => put(`/bills/${id}`, data);
export const deleteBill = (id)        => del(`/bills/${id}`);

// ── Bill Items ────────────────────────────────────────────────────────────────
export const getBillItem    = (invoiceId, menuItemId)        => get(`/bill-items/${invoiceId}/${menuItemId}`);
export const createBillItem = (data)                         => post('/bill-items/', data);
export const updateBillItem = (invoiceId, menuItemId, data)  => put(`/bill-items/${invoiceId}/${menuItemId}`, data);
export const deleteBillItem = (invoiceId, menuItemId)        => del(`/bill-items/${invoiceId}/${menuItemId}`);

// ── Payments ──────────────────────────────────────────────────────────────────
export const getPayment    = (id)        => get(`/payments/${id}`);
export const createPayment = (data)      => post('/payments/', data);
export const updatePayment = (id, data)  => put(`/payments/${id}`, data);
export const deletePayment = (id)        => del(`/payments/${id}`);

// ── List endpoints (new) ──────────────────────────────────────────────────────
export const listReservations   = ()         => get('/reservation/');
export const listWaitlist       = (status)   => get(`/waitlist/${status ? '?status=' + encodeURIComponent(status) : ''}`);
export const listTables         = (section)  => get(`/tables/${section ? '?section=' + encodeURIComponent(section) : ''}`);
export const listSections       = ()         => get('/sections/');
export const listMenuItems      = ()         => get('/menu-items/');
export const listBillItems      = (invoiceId) => get(`/bill-items/by-invoice/${invoiceId}`);
export const listPayments       = (invoiceId) => get(`/payments/by-invoice/${invoiceId}`);
export const listAssignments    = ()          => get('/seating-assignments/');
export const updateWaitlistStatus = (id, status) => req('PATCH', `/waitlist/${id}/status`, { entryStatus: status });