

# Care Connect

Care Connect is a web-based healthcare platform that integrates patient details using Aadhaar number and facilitates secure access to medical history for verified doctors. The platform uses OTP-based Aadhaar verification and allows doctors to view, update, and maintain patient records efficiently.

## 🔧 Features

- 👨‍⚕️ **Doctor Registration & Login**
  - Register using Doctor ID, Name, Phone Number, and Password.
  - Secure login system with session management.

- 🆔 **Aadhaar-Based Patient Verification**
  - Doctors can enter the patient’s Aadhaar number.
  - OTP is sent via Twilio to verify identity before accessing records.

- 📁 **Patient Records Management**
  - View previous check-up details.
  - Add new check-up notes and medical files.
  - Upload reports and prescriptions for future reference.

- 🔐 **Security**
  - Twilio-based OTP verification.
  - Sessions ensure only logged-in doctors can access patient data.

## 🖥️ Tech Stack

- **Frontend:** HTML, CSS, Bootstrap
- **Backend:** Python (Flask)
- **Database:** SQLite
- **Third-party API:** Twilio (OTP Verification)

## 📂 Project Structure

```

careconnect/
│
├── app.py                  # Main Flask backend
├── templates/              # HTML Templates (register.html, login.html, dashboard.html, etc.)
├── static/                 # CSS, JS, etc.
├── database.db             # SQLite database
├── .env                    # Environment variables (Twilio SID, Auth Token, etc.)
└── README.md

````

## 🚀 Getting Started

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Sai123-collab/careconnect.git
   cd careconnect
````

2. **Create `.env` file:**

   ```
   TWILIO_ACCOUNT_SID=your_account_sid
   TWILIO_AUTH_TOKEN=your_auth_token
   TWILIO_PHONE_NUMBER=your_twilio_number
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app:**

   ```bash
   python app.py
   ```

5. **Visit the app in your browser:**

   ```
   http://127.0.0.1:5000/
   ```

## 📝 License

This project is for academic and demonstration purposes only.

---

### 🙌 Project Contributors

* **Sai Balaji** – Team Lead & Developer
* **Sameena**-Team Member & Developer
* **Sai Jaswanth** -Team Member & Developer

---

> 💡 *If you like this project, feel free to ⭐️ the repo!*

