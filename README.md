# White Lobster Restaurant System
University of Calgary
CPSC 471 Project

A full-stack restaurant management system for White Lobster built with:

- Frontend: React
- Backend: FastAPI
- Database: MySQL

## Project Structure

```text
restaurant-system/
├── frontend/
├── backend/
├── database/
├── docs/
├── .gitignore
└── README.md

## Install/Run
Setup .env in backend

mysql -u root -p
SOURCE database/schema/create_database.sql;
SOURCE database/schema/create_tables.sql;
SOURCE database/seed/seed_database.sql;
exit;

cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python generate_seed_hashes.py | mysql -u root -p wl_restaurant_system

cd frontend
npm install
npm run dev

Post inital setup: 
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload
cd frontend
npm run dev