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
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS wl_restaurant_system;"
mysql -u root -p wl_restaurant_system < database/schema/create_tables.sql
mysql -u root -p wl_restaurant_system < database/seed/seed_database.sql

cd backend
pip install -r requirements.txt
python generate_seed_hashes.py | mysql -u root -p wl_restaurant_system
# Customer password: password123
# Staff password: staffpass1

cd backend
uvicorn app.main:app --reload --port 8000

cd frontend
npm install
npm run dev 