# Hospital Management System

A command-line **Hospital Management System** built with **Python and SQLite**. It manages the daily work of a small hospital: patients, doctors, appointments and billing, and produces simple reports.

## Features
- **Patients**: register, list and search
- **Doctors**: add and list (with specialization and consultation fee)
- **Appointments**: book, view and update status (Completed / Cancelled), with **double-booking prevention** for doctors
- **Billing**: generate bills (consultation fee + extra charges) and mark them as paid
- **Reports**: appointments by status, appointments per doctor, revenue received and payments pending
- Input validation for numbers, dates and times

## Database design
Four related tables connected with foreign keys:

```
patients (id, name, age, gender, phone, address, reg_date)
doctors (id, name, specialization, phone, fee)
appointments (id, patient_id -> patients, doctor_id -> doctors, appt_date, appt_time, reason, status)
bills (id, appointment_id -> appointments, amount, paid, bill_date)
```

## SQL concepts used
`INSERT` • `SELECT` • `UPDATE` • `JOIN` • `LEFT JOIN` • `GROUP BY` • `COUNT` • `SUM` • `CASE` • foreign keys

## Tools
Python 3 • SQLite (built into Python, nothing to install)

## How to run
```bash
python hospital.py
```
On the first run you can choose to load **sample demo data** to try every feature.

## Files
- `hospital.py`: menus and main program
- `database.py`: database setup and helper functions

## Important
All demo records are **made-up sample data**. No real patient information is used. Do not store real patient data in this demo project.

## What I learned
Relational database design, writing SQL queries from Python, input validation, and structuring a program into separate files.

## Ideas to improve
Add a graphical interface (Tkinter), login for staff, patient medical history, or export reports to Excel/PDF.
