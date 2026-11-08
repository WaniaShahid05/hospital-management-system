"""Hospital Management System (command-line)
Manage patients, doctors, appointments and billing, with reports.
Run:  python hospital.py
"""
from datetime import date, datetime
import database as db


# ---------------------------------------------------------------- helpers
def ask_text(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("  This field cannot be empty.")


def ask_int(prompt, low=0, high=10**9):
    while True:
        value = input(prompt).strip()
        if value.isdigit() and low <= int(value) <= high:
            return int(value)
        print(f"  Please enter a number between {low} and {high}.")


def ask_date(prompt):
    while True:
        value = input(prompt).strip()
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return value
        except ValueError:
            print("  Use the format YYYY-MM-DD (example: 2026-12-25).")


def ask_time(prompt):
    while True:
        value = input(prompt).strip()
        try:
            datetime.strptime(value, "%H:%M")
            return value
        except ValueError:
            print("  Use the 24-hour format HH:MM (example: 14:30).")


def print_table(rows):
    """Print database rows as a neat table."""
    if not rows:
        print("  No records found.")
        return
    headers = rows[0].keys()
    widths = [max(len(h), *(len(str(r[h])) for r in rows)) for h in headers]
    line = " | ".join(h.ljust(w) for h, w in zip(headers, widths))
    print("\n" + line)
    print("-" * len(line))
    for r in rows:
        print(" | ".join(str(r[h]).ljust(w) for h, w in zip(headers, widths)))
    print()


# --------------------------------------------------------------- patients
def register_patient():
    print("\n--- Register new patient ---")
    name = ask_text("Name: ")
    age = ask_int("Age: ", 0, 120)
    gender = ask_text("Gender (Male/Female/Other): ")
    phone = input("Phone: ").strip()
    address = input("Address: ").strip()
    pid = db.execute(
        "INSERT INTO patients (name, age, gender, phone, address, reg_date) VALUES (?, ?, ?, ?, ?, ?)",
        (name, age, gender, phone, address, date.today().isoformat()))
    print(f"Patient registered with ID {pid}.")


def view_patients():
    print_table(db.query("SELECT id, name, age, gender, phone, address FROM patients ORDER BY id"))


def search_patient():
    term = ask_text("Search name: ")
    print_table(db.query(
        "SELECT id, name, age, gender, phone FROM patients WHERE name LIKE ?", (f"%{term}%",)))


# ---------------------------------------------------------------- doctors
def add_doctor():
    print("\n--- Add doctor ---")
    name = ask_text("Name: ")
    spec = ask_text("Specialization: ")
    phone = input("Phone: ").strip()
    fee = ask_int("Consultation fee (Rs): ", 0)
    did = db.execute("INSERT INTO doctors (name, specialization, phone, fee) VALUES (?, ?, ?, ?)",
                     (name, spec, phone, fee))
    print(f"Doctor added with ID {did}.")


def view_doctors():
    print_table(db.query("SELECT id, name, specialization, phone, fee FROM doctors ORDER BY id"))


# ----------------------------------------------------------- appointments
def book_appointment():
    print("\n--- Book appointment ---")
    patient_id = ask_int("Patient ID: ", 1)
    if not db.query("SELECT 1 FROM patients WHERE id = ?", (patient_id,)):
        print("  No patient with that ID.")
        return
    doctor_id = ask_int("Doctor ID: ", 1)
    if not db.query("SELECT 1 FROM doctors WHERE id = ?", (doctor_id,)):
        print("  No doctor with that ID.")
        return
    appt_date = ask_date("Date (YYYY-MM-DD): ")
    appt_time = ask_time("Time (HH:MM): ")

    # Prevent double booking of the same doctor at the same time
    clash = db.query("SELECT 1 FROM appointments WHERE doctor_id = ? AND appt_date = ? "
                     "AND appt_time = ? AND status = 'Scheduled'", (doctor_id, appt_date, appt_time))
    if clash:
        print("  That doctor is already booked at this date and time. Choose another slot.")
        return

    reason = input("Reason for visit: ").strip()
    aid = db.execute(
        "INSERT INTO appointments (patient_id, doctor_id, appt_date, appt_time, reason) "
        "VALUES (?, ?, ?, ?, ?)", (patient_id, doctor_id, appt_date, appt_time, reason))
    print(f"Appointment booked with ID {aid}.")


def view_appointments():
    print_table(db.query("""
        SELECT a.id, p.name AS patient, d.name AS doctor, a.appt_date AS date,
               a.appt_time AS time, a.reason, a.status
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN doctors  d ON a.doctor_id  = d.id
        ORDER BY a.appt_date, a.appt_time"""))


def update_appointment_status():
    aid = ask_int("Appointment ID: ", 1)
    if not db.query("SELECT 1 FROM appointments WHERE id = ?", (aid,)):
        print("  No appointment with that ID.")
        return
    choice = ask_int("New status (1 = Completed, 2 = Cancelled): ", 1, 2)
    status = "Completed" if choice == 1 else "Cancelled"
    db.execute("UPDATE appointments SET status = ? WHERE id = ?", (status, aid))
    print(f"Appointment {aid} marked as {status}.")


# ---------------------------------------------------------------- billing
def generate_bill():
    print("\n--- Generate bill ---")
    aid = ask_int("Appointment ID: ", 1)
    rows = db.query("""SELECT a.status, d.fee FROM appointments a
                       JOIN doctors d ON a.doctor_id = d.id WHERE a.id = ?""", (aid,))
    if not rows:
        print("  No appointment with that ID.")
        return
    if rows[0]["status"] == "Cancelled":
        print("  Cannot bill a cancelled appointment.")
        return
    if db.query("SELECT 1 FROM bills WHERE appointment_id = ?", (aid,)):
        print("  A bill already exists for this appointment.")
        return
    extra = ask_int("Extra charges, e.g. medicines or tests (Rs, 0 if none): ", 0)
    total = rows[0]["fee"] + extra
    bid = db.execute("INSERT INTO bills (appointment_id, amount, bill_date) VALUES (?, ?, ?)",
                     (aid, total, date.today().isoformat()))
    print(f"Bill {bid} created. Consultation Rs {rows[0]['fee']} + extra Rs {extra} = Total Rs {total}")


def view_bills():
    print_table(db.query("""
        SELECT b.id, p.name AS patient, b.amount AS amount_rs, b.bill_date AS date,
               CASE b.paid WHEN 1 THEN 'Paid' ELSE 'Unpaid' END AS status
        FROM bills b
        JOIN appointments a ON b.appointment_id = a.id
        JOIN patients p ON a.patient_id = p.id
        ORDER BY b.id"""))
    bid = ask_int("Enter a bill ID to mark as PAID (0 to skip): ", 0)
    if bid:
        if db.query("SELECT 1 FROM bills WHERE id = ?", (bid,)):
            db.execute("UPDATE bills SET paid = 1 WHERE id = ?", (bid,))
            print(f"Bill {bid} marked as paid.")
        else:
            print("  No bill with that ID.")


# ---------------------------------------------------------------- reports
def show_reports():
    print("\n===== HOSPITAL REPORT =====")
    print("Patients registered :", db.query("SELECT COUNT(*) AS n FROM patients")[0]["n"])
    print("Doctors             :", db.query("SELECT COUNT(*) AS n FROM doctors")[0]["n"])

    print("\nAppointments by status:")
    print_table(db.query("SELECT status, COUNT(*) AS total FROM appointments GROUP BY status"))

    print("Appointments per doctor:")
    print_table(db.query("""
        SELECT d.name AS doctor, d.specialization, COUNT(a.id) AS appointments
        FROM doctors d LEFT JOIN appointments a ON d.id = a.doctor_id
        GROUP BY d.id ORDER BY appointments DESC"""))

    money = db.query("""SELECT COALESCE(SUM(CASE WHEN paid = 1 THEN amount END), 0) AS received,
                               COALESCE(SUM(CASE WHEN paid = 0 THEN amount END), 0) AS pending
                        FROM bills""")[0]
    print(f"Revenue received : Rs {money['received']}")
    print(f"Payments pending : Rs {money['pending']}")


# ------------------------------------------------------------------- menu
MENU = """
========== HOSPITAL MANAGEMENT SYSTEM ==========
 1. Register patient          7. View appointments
 2. View all patients         8. Update appointment status
 3. Search patient            9. Generate bill
 4. Add doctor               10. View bills / mark paid
 5. View doctors             11. Reports
 6. Book appointment          0. Exit
================================================"""

ACTIONS = {
    1: register_patient, 2: view_patients, 3: search_patient, 4: add_doctor,
    5: view_doctors, 6: book_appointment, 7: view_appointments,
    8: update_appointment_status, 9: generate_bill, 10: view_bills, 11: show_reports,
}


def main():
    db.init_db()
    if not db.query("SELECT 1 FROM patients LIMIT 1"):
        if input("Database is empty. Load sample demo data? (y/n): ").strip().lower() == "y":
            db.load_sample_data()
            print("Sample data loaded.")

    while True:
        print(MENU)
        choice = ask_int("Choose an option: ", 0, 11)
        if choice == 0:
            print("Goodbye!")
            break
        ACTIONS[choice]()


if __name__ == "__main__":
    main()
