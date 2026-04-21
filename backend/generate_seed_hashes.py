"""
Run this script once after installing requirements to produce real Argon2id
hashes for the seed data.

Usage:
    cd backend
    pip install -r requirements.txt
    python generate_seed_hashes.py

Then paste the printed UPDATE statements into MySQL, or run them directly:
    python generate_seed_hashes.py | mysql -u root -p wl_restaurant_system
"""

from pwdlib import PasswordHash # cd backend -> pip install "pwdlib[argon2]"

ph = PasswordHash.recommended()

CUSTOMER_PASSWORD = "password123"
STAFF_PASSWORD    = "staffpass1"

cust_hash  = ph.hash(CUSTOMER_PASSWORD)
staff_hash = ph.hash(STAFF_PASSWORD)

print("-- ============================================")
print("-- Paste these into MySQL after running seed_database.sql")
print("-- Customer password: password123")
print("-- Staff password:    staffpass1")
print("-- ============================================")
print()
print(f"UPDATE CUSTOMER_ACCOUNT SET passwordHash = '{cust_hash}';")
print()
for emp_id in [101, 102, 103, 104]:
    print(f"UPDATE STAFF_USER SET passwordHash = '{staff_hash}' WHERE employeeID = {emp_id};")

print()
print("-- Done. All seed accounts now have valid hashes.")
print(f"-- Customer login: any of alice/bob/carla @example.com  + password123")
print(f"-- Staff login:    employeeID 101-104  + staffpass1")