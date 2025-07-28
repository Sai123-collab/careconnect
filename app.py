from flask import Flask, render_template, request, redirect, url_for, session, flash
from random import randint
import sqlite3
import os
import random
from dotenv import load_dotenv
from twilio.rest import Client
from datetime import datetime


# Load environment variables from .env
load_dotenv()

# Fetch Twilio credentials from environment
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
phone = os.getenv("TWILIO_PHONE_NUMBER")

# Initialize Twilio client
client = Client(account_sid, auth_token)
import os
import os

from dotenv import load_dotenv

load_dotenv()


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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patient_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            aadhaar TEXT UNIQUE,
            phone TEXT,
            password TEXT
        )
    ''')

    # Daily meal logging table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_meals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aadhaar TEXT,
            date TEXT,
            meal TEXT,
            calories INTEGER
        )
    ''')

    # BMI tracking table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bmi_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aadhaar TEXT,
            date TEXT,
            weight REAL,
            height REAL,
            bmi REAL
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Patient tables created successfully.")

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
    # Generate backup code if not already created
    if "backup_code" not in session:
        session["backup_code"] = str(random.randint(100000, 999999))

    if request.method == 'POST':
        entered_otp = request.form['otp']
        correct_otp = session.get('otp')
        backup_code = session.get('backup_code')

        if entered_otp == correct_otp or entered_otp == backup_code:
            flash("✅ OTP verified successfully!", "success")
            return redirect(url_for('patient_details'))
        else:
            flash("❌ Invalid OTP or Backup Code. Please try again.", "danger")

    return render_template('verify_otp.html', backup_code=session["backup_code"])
  # or backup_code=session["backup_code"]


@app.route('/resend_otp')
def resend_otp():
    if 'aadhaar' not in session:
        return "Session expired", 403

    otp = str(random.randint(1000, 9999))
    session['otp'] = otp
    session['backup_code'] = str(random.randint(100000, 999999))  # regenerate backup code

    # Get phone number from DB again
    conn = sqlite3.connect('careconnect.db')
    cursor = conn.cursor()
    cursor.execute("SELECT phone FROM patients WHERE aadhaar = ?", (session['aadhaar'],))
    patient_phone = cursor.fetchone()
    conn.close()

    if patient_phone and patient_phone[0]:
        try:
            to_number = patient_phone[0]
            if not to_number.startswith('+'):
                to_number = '+91' + to_number

            client.messages.create(
                body=f"Your new OTP for CareConnect is: {otp}",
                from_=phone,
                to=to_number
            )
            return "OK", 200
        except Exception as e:
            print(f"Error resending OTP: {e}")
            return "Twilio error", 500
    else:
        return "Phone number not found", 404




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
        cursor.execute("INSERT OR IGNORE INTO patients VALUES (?, ?, ?, ?, ?)", (aadhaar, name, age, gender, phone))


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
# -------------------- PATIENT LOGIN SYSTEM --------------------

@app.route('/patient_register', methods=['GET', 'POST'])
def patient_register():
    if request.method == 'POST':
        name = request.form['name']
        aadhaar = request.form['aadhaar']
        phone = request.form['phone']
        password = request.form['password']

        conn = sqlite3.connect('careconnect.db')
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO patient_users (name, aadhaar, phone, password) VALUES (?, ?, ?, ?)",
                           (name, aadhaar, phone, password))
            conn.commit()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for('patient_login'))
        except sqlite3.IntegrityError:
            flash("Aadhaar already registered.", "danger")
        finally:
            conn.close()

    return render_template('patient_register.html')


@app.route('/patient_login', methods=['GET', 'POST'])
def patient_login():
    if request.method == 'POST':
        aadhaar = request.form.get('aadhaar')
        password = request.form.get('password')

        print(f"Login attempt with Aadhaar: {aadhaar}")  # Debug print

        conn = sqlite3.connect('careconnect.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patient_users WHERE aadhaar = ? AND password = ?", (aadhaar, password))
        patient = cursor.fetchone()
        conn.close()

        if patient:
            session['patient_aadhaar'] = aadhaar
            print("Login successful. Redirecting to dashboard.")
            return redirect(url_for('patient_dashboard'))
        else:
            print("Login failed. Showing error.")
            flash("Invalid Aadhaar or Password", "danger")

    return render_template('patient_login.html')


from flask import Flask, render_template, request, redirect, session, send_file
import sqlite3
import pandas as pd
from fpdf import FPDF
import os



@app.route('/patientsdashboard', methods=['GET', 'POST'])
def patient_dashboard():
    if "patient_aadhaar" not in session:
        return redirect("/patient_login")

    aadhaar = session["patient_aadhaar"]
    conn = sqlite3.connect("careconnect.db")
    cursor = conn.cursor()

    # Fetch BMI records
    cursor.execute("SELECT date, bmi FROM bmi_records WHERE aadhaar = ? ORDER BY date", (aadhaar,))
    records = cursor.fetchall()
    dates = [r[0] for r in records]
    bmis = [float(round(r[1], 2)) for r in records]

    # Fetch recent meals with ID
    cursor.execute("""
        SELECT date, meal, calories, id
        FROM daily_meals
        WHERE aadhaar = ?
        ORDER BY date DESC, id DESC
        LIMIT 10
    """, (aadhaar,))
    meals = cursor.fetchall()

    # Average BMI and Calories
    avg_bmi = round(sum(bmis) / len(bmis), 2) if bmis else 0
    latest_bmi = float(bmis[-1]) if bmis else 0

    cursor.execute("SELECT date, SUM(calories) FROM daily_meals WHERE aadhaar = ? GROUP BY date", (aadhaar,))
    daily_cals = cursor.fetchall()
    cal_vals = [r[1] for r in daily_cals]
    avg_calories = round(sum(cal_vals) / len(cal_vals), 2) if cal_vals else 0
    calorie_dates = [r[0] for r in daily_cals]
    calorie_values = [r[1] for r in daily_cals]


    # Patient name
    cursor.execute("SELECT name FROM patient_users WHERE aadhaar = ?", (aadhaar,))
    name = cursor.fetchone()[0]
        # Doctor Alert based on BMI
    if latest_bmi < 18.5:
        doctor_alert = "⚠️ Underweight - Consider a high-nutrient diet."
    elif 18.5 <= latest_bmi <= 24.9:
        doctor_alert = "✅ Normal weight - Keep up the good work!"
    elif 25 <= latest_bmi <= 29.9:
        doctor_alert = "⚠️ Overweight - Exercise regularly & eat balanced meals."
    else:
        doctor_alert = "❗ Obese - Consult your doctor for a weight management plan."

    conn.close()

    return render_template("patient_dashboard.html",
                       name=name,
                       dates=dates,
                       bmis=bmis,
                       meals=meals,
                       avg_bmi=avg_bmi,
                       avg_calories=avg_calories,
                       latest_bmi=latest_bmi,
                       calorie_dates=calorie_dates,
                       calorie_values=calorie_values,
                       doctor_alert=doctor_alert)




@app.route("/download_bmi_csv")
def download_bmi_csv():
    if "patient_aadhaar" not in session:
        return redirect("/patient_login")

    aadhaar = session["patient_aadhaar"]
    conn = sqlite3.connect("careconnect.db")
    cursor = conn.cursor()
    cursor.execute("SELECT date, weight, height, bmi FROM bmi_records WHERE aadhaar = ? ORDER BY date", (aadhaar,))
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=["Date", "Weight (kg)", "Height (cm)", "BMI"])
    csv_path = "bmi_history.csv"
    df.to_csv(csv_path, index=False)
    conn.close()
    return send_file(csv_path, as_attachment=True)

@app.route("/download_bmi_pdf")
def download_bmi_pdf():
    if "patient_aadhaar" not in session:
        return redirect("/patient_login")

    aadhaar = session["patient_aadhaar"]
    conn = sqlite3.connect("careconnect.db")
    cursor = conn.cursor()
    cursor.execute("SELECT date, weight, height, bmi FROM bmi_records WHERE aadhaar = ? ORDER BY date", (aadhaar,))
    data = cursor.fetchall()
    conn.close()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="BMI History Report", ln=True, align='C')

    pdf.set_font("Arial", size=10)
    pdf.ln(10)
    pdf.cell(40, 10, "Date", 1)
    pdf.cell(40, 10, "Weight (kg)", 1)
    pdf.cell(40, 10, "Height (cm)", 1)
    pdf.cell(40, 10, "BMI", 1)
    pdf.ln()

    for row in data:
        pdf.cell(40, 10, row[0], 1)
        pdf.cell(40, 10, str(row[1]), 1)
        pdf.cell(40, 10, str(row[2]), 1)
        pdf.cell(40, 10, str(round(row[3], 2)), 1)
        pdf.ln()

    filename = f"bmi_report_{aadhaar}.pdf"
    pdf.output(filename)
    return send_file(filename, as_attachment=True)
@app.route('/delete/<int:meal_id>', methods=['POST'])
def delete_meal(meal_id):
    if 'patient_aadhaar' not in session:
        return redirect(url_for('patient_login'))

    meal_id = request.form.get('meal_id')

    if meal_id:
        conn = sqlite3.connect('careconnect.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM daily_meals WHERE id = ?", (meal_id,))
        conn.commit()
        conn.close()
        flash("Meal deleted successfully.", "success")
    else:
        flash("Meal ID missing.", "danger")

    return redirect(url_for('patient_dashboard'))







@app.route('/log_health', methods=['GET', 'POST'])
def log_health():
    if 'patient_aadhaar' not in session:
        return redirect(url_for('patient_login'))

    if request.method == 'POST':
        date = request.form['date']
        weight = float(request.form['weight'])
        height = float(request.form['height']) / 100  # cm to meters
        bmi = round(weight / (height ** 2), 2)

        meals = request.form.getlist('meal')
        calories = request.form.getlist('calories')

        print("DEBUG Meals:", meals)
        print("DEBUG Calories:", calories)
        print("DEBUG Date:", date)

        aadhaar = session['patient_aadhaar']

        if not meals or not calories or len(meals) != len(calories):
            flash("No meals or calories data submitted.", "danger")
            return redirect(url_for('log_health'))

        conn = sqlite3.connect('careconnect.db')
        cursor = conn.cursor()

        # ✅ Insert BMI after meal check
        cursor.execute("INSERT INTO bmi_records (aadhaar, date, weight, height, bmi) VALUES (?, ?, ?, ?, ?)",
                       (aadhaar, date, weight, height * 100, bmi))

        # Insert Meals
        # Insert Meals with validation
        for m, c in zip(meals, calories):
            if not c.strip().isdigit():
                flash(f"Invalid calorie value '{c}' for meal '{m}'. Please enter a valid number.", "danger")
                return redirect(url_for('log_health'))

            cursor.execute("INSERT INTO daily_meals (aadhaar, date, meal, calories) VALUES (?, ?, ?, ?)",
                        (aadhaar, date, m, int(c)))


        conn.commit()
        conn.close()

        flash("Health data logged!", "success")
        print("DEBUG BMI:", bmi)

        return redirect(url_for('patient_dashboard'))

    return render_template('log_health.html')


@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully", "success")
    return redirect(url_for('index'))

# ---------- Run ----------



if __name__ == '__main__':
    init_db()
    app.run(debug=True)
