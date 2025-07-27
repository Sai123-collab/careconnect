from flask import Flask, render_template, request, redirect, url_for, session, flash
from random import randint
import sqlite3
import os
import random
from dotenv import load_dotenv
from twilio.rest import Client

# Load environment variables from .env
load_dotenv()

# Fetch Twilio credentials from environment
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
phone = os.getenv("TWILIO_PHONE_NUMBER")

# Initialize Twilio client
client = Client(account_sid, auth_token)
import sqlite3

def get_db_connection():
    conn = sqlite3.connect('careconnect.db')  # change 'database.db' to your DB name if different
    conn.row_factory = sqlite3.Row
    return conn
import sqlite3

conn = sqlite3.connect('careconnect.db')
cursor = conn.cursor()

# Example: Update phone number for a patient
cursor.execute("UPDATE patients SET phone = ? WHERE aadhaar = ?", ("9876543210", "123456789012"))


# --- TEMP FIX FOR RENDER DB MIGRATION ---
try:
    cursor.execute("ALTER TABLE patients ADD COLUMN phone TEXT")
    conn.commit()
    print("✅ Added 'phone' column to 'patients' table")
except sqlite3.OperationalError:
    print("ℹ️ 'phone' column already exists.")
conn.commit()
conn.close()
# ----------------------------------------






app = Flask(__name__)
app.secret_key = 'your_secret_key'

# ---------- Database Initialization ----------
def init_db():
    conn = sqlite3.connect('careconnect.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS doctors (
            doctor_id TEXT PRIMARY KEY,
            name TEXT,
            phone TEXT,
            password TEXT
        )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS patients (
        aadhaar TEXT PRIMARY KEY,
        name TEXT,
        age INTEGER,
        gender TEXT,
        phone TEXT
    )
''')




    cursor.execute('''
        CREATE TABLE IF NOT EXISTS checkups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aadhaar TEXT,
            doctor_id TEXT,
            date TEXT,
            symptoms TEXT,
            diagnosis TEXT,
            prescription TEXT,
            FOREIGN KEY (aadhaar) REFERENCES patients(aadhaar),
            FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
        )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        aadhaar TEXT,
        doctor_id TEXT,
        filename TEXT,
        upload_date TEXT,
        FOREIGN KEY (aadhaar) REFERENCES patients(aadhaar),
        FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
    )
''')


    conn.commit()
    conn.close()

# ---------- Routes ----------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        doctor_id = request.form['doctor_id']
        phone = request.form['phone']
        password = request.form['password']

        conn = sqlite3.connect('careconnect.db')
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO doctors VALUES (?, ?, ?, ?)", (doctor_id, name, phone, password))
            conn.commit()
            flash("Doctor registered successfully", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Doctor ID already exists", "danger")
        finally:
            conn.close()
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        doctor_id = request.form['doctor_id']
        password = request.form['password']

        conn = sqlite3.connect('careconnect.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM doctors WHERE doctor_id = ? AND password = ?", (doctor_id, password))
        doctor = cursor.fetchone()
        conn.close()

        if doctor:
            session['doctor_id'] = doctor_id
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid login credentials", "danger")
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'doctor_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        aadhaar = request.form['aadhaar']
        otp = str(random.randint(1000, 9999))
        session['aadhaar'] = aadhaar
        session['otp'] = otp

        conn = sqlite3.connect('careconnect.db')
        cursor = conn.cursor()
        cursor.execute("SELECT phone FROM patients WHERE aadhaar = ?", (aadhaar,))
        patient_phone = cursor.fetchone()
        conn.close()

        if patient_phone and patient_phone[0]:
            try:
                to_number = patient_phone[0]
                if not to_number.startswith('+'):
                    to_number = '+91' + to_number

                # Send OTP via Twilio
                client.messages.create(
                    body=f"Your OTP for CareConnect is: {otp}",
                    from_=phone,
                    to=to_number
                )
                flash("✅ OTP has been sent to the registered number.", "success")

            except Exception as e:
                print(f"[⚠️ Twilio Error] {e}")
                flash("⚠️ Unable to send OTP. Using backup OTP instead.", "warning")
                flash(f"🔑 Backup OTP: {otp}", "info")
        else:
            flash("❌ Phone number not found for this Aadhaar.", "danger")

        # ✅ Redirect to verify_otp page
        return redirect(url_for('verify_otp'))

    return render_template('dashboard.html')



    # Always generate a backup code (new for every GET request)
    session["backup_code"] = str(randint(100000, 999999))
    return render_template('verify_otp.html', backup_code=session["backup_code"])
@app.route("/register_patient", methods=["GET", "POST"])
def register_patient():
    if "doctor_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        aadhaar = request.form["aadhaar"]
        name = request.form["name"]
        age = request.form["age"]
        gender = request.form["gender"]
        phone = request.form["phone"]

        conn = sqlite3.connect("careconnect.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM patients WHERE aadhaar = ?", (aadhaar,))
        existing = cursor.fetchone()
        if existing:
            flash("Patient already exists.", "warning")
            conn.close()
            return redirect(url_for("register_patient"))

        cursor.execute("INSERT INTO patients (aadhaar, name, age, gender, phone) VALUES (?, ?, ?, ?, ?)",
                       (aadhaar, name, age, gender, phone))
        conn.commit()
        conn.close()

        flash("Patient registered successfully.", "success")
        return redirect(url_for("dashboard"))  # ✅ REDIRECT AFTER REGISTRATION

    return render_template("register_patient.html")



@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if 'otp' not in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        entered_otp = request.form['otp']
        if entered_otp == session.get('otp'):
            flash("✅ OTP verified successfully!", "success")
            return redirect(url_for('patient_details'))
        else:
            flash("❌ Incorrect OTP. Try again.", "danger")

    return render_template('verify_otp.html', backup_code=session.get('otp'))  # or backup_code=session["backup_code"]


@app.route('/resend_otp')
def resend_otp():
    if 'doctor_phone' in session:
        phone = session['doctor_phone']
        otp = str(random.randint(1000, 9999))
        session['otp'] = otp
        try:
            message = client.messages.create(
                body=f"Your OTP for Care Connect is {otp}",
                from_=twilio_number,
                to=phone
            )
            return '', 200
        except Exception as e:
            print("Failed to resend OTP:", e)
            return '', 500
    return '', 401



@app.route('/patient_details')
def patient_details():
    if 'doctor_id' not in session or 'aadhaar' not in session:
        return redirect(url_for('login'))

    aadhaar = session['aadhaar']
    conn = sqlite3.connect('careconnect.db')
    cursor = conn.cursor()

    # ✅ INSERT DEFAULT PATIENT if Aadhaar not found
    cursor.execute("SELECT * FROM patients WHERE aadhaar = ?", (aadhaar,))
    patient = cursor.fetchone()

    if not patient:
        # Create new patient with NULL name, age, gender
        cursor.execute("INSERT INTO patients (aadhaar) VALUES (?)", (aadhaar,))
        conn.commit()
        cursor.execute("SELECT * FROM patients WHERE aadhaar = ?", (aadhaar,))
        patient = cursor.fetchone()

    # ✅ Fetch checkups and reports
    cursor.execute("SELECT * FROM checkups WHERE aadhaar = ?", (aadhaar,))
    checkups = cursor.fetchall()
    cursor.execute("SELECT id, filename, upload_date FROM reports WHERE aadhaar = ?", (aadhaar,))
    reports = cursor.fetchall()

    conn.close()

    return render_template('patient_details.html', patient=patient, checkups=checkups, reports=reports, aadhaar=aadhaar)


@app.route('/delete_checkup/<int:checkup_id>', methods=['POST'])
def delete_checkup(checkup_id):
    if 'doctor_name' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('careconnect.db')
    cursor = conn.cursor()

    # Fetch report_file
    cursor.execute('SELECT report_file FROM checkups WHERE id = ?', (checkup_id,))
    
    result = cursor.fetchone()

    if result and result[0]:
        report_file = result[0]
        report_path = os.path.join(app.root_path, 'static', 'reports', report_file)
        print("Trying to delete:", report_path)  # Debug

        if os.path.exists(report_path):
            os.remove(report_path)
            print("Deleted:", report_path)
        else:
            print("File does not exist:", report_path)

    # Delete DB record
    cursor.execute('DELETE FROM checkups WHERE id = ?', (checkup_id,))
    
    conn.commit()
    conn.close()

    flash('Checkup and report deleted.', 'success')
    return redirect(url_for('patient_details'))



@app.route('/add_checkup', methods=['GET', 'POST'])
def add_checkup():
    if 'doctor_id' not in session or 'aadhaar' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form.get('name')
        age = request.form.get('age')
        gender = request.form.get('gender')
        symptoms = request.form.get('symptoms')
        diagnosis = request.form.get('diagnosis')
        prescription = request.form.get('prescription')
        date = request.form.get('date')

        if not all([name, age, gender, symptoms, diagnosis, prescription, date]):
            flash("Please fill all fields", "danger")
            return render_template('add_checkup.html')

        aadhaar = session['aadhaar']
        doctor_id = session['doctor_id']

        conn = sqlite3.connect('careconnect.db')
        cursor = conn.cursor()

        # Insert patient info if not already present
        cursor.execute("INSERT OR IGNORE INTO patients VALUES (?, ?, ?, ?)", (aadhaar, name, age, gender))

        # Insert new checkup linked to this Aadhaar
        cursor.execute(
            "INSERT INTO checkups (aadhaar, doctor_id, date, symptoms, diagnosis, prescription) VALUES (?, ?, ?, ?, ?, ?)",
            (aadhaar, doctor_id, date, symptoms, diagnosis, prescription)
        )

        conn.commit()
        conn.close()

        flash("Checkup details added successfully", "success")
        return redirect(url_for('patient_details'))

    return render_template('add_checkup.html')

import os
from werkzeug.utils import secure_filename
from datetime import datetime

UPLOAD_FOLDER = 'static/reports'
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_report', methods=['GET', 'POST'])
def upload_report():
    if 'doctor_id' not in session or 'aadhaar' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        if 'report' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)

        file = request.files['report']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            aadhaar = session['aadhaar']
            doctor_id = session['doctor_id']
            upload_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            conn = sqlite3.connect('careconnect.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO reports (aadhaar, doctor_id, filename, upload_date) VALUES (?, ?, ?, ?)",
                           (aadhaar, doctor_id, filename, upload_date))
            conn.commit()
            conn.close()

            flash('Report uploaded successfully', 'success')
            return redirect(url_for('patient_details'))

    return render_template('upload_report.html')


@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully", "success")
    return redirect(url_for('index'))

# ---------- Run ----------
@app.route('/delete_report/<filename>', methods=['POST'])
def delete_report(filename):
    if 'doctor_id' not in session:
        return redirect(url_for('login'))

    aadhaar = request.args.get('aadhaar')

    # Delete file
    file_path = os.path.join('static/reports', filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    # Delete DB record
    conn = sqlite3.connect('careconnect.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reports WHERE filename = ?", (filename,))
    conn.commit()
    conn.close()

    flash('Report removed successfully.', 'success')
    return redirect(url_for('patient_details'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
