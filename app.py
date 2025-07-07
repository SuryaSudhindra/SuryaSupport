from flask import Flask, render_template, request, redirect, url_for, Response
import csv
from flask import session
import pytz
import json
import os
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

def load_users():
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

# ✅ Load users from JSON file
users = load_users()
print("📂 Loaded users:", users)

def send_email(subject, body):
    sender_email = "centraldesk@gmail.com"  # 🟡 Replace with your Gmail
    sender_password = "Pragathi@242"  # 🔒 App password from Google
    receiver_email = "centraldesk@gmail.com"  # ✅ Set the IT Head's email here

    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    import smtplib

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
            print("📧 Email sent to IT Head.")
    except Exception as e:
        print("❌ Error sending email:", e)
import json
import os

TICKETS_FILE = 'tickets.json'

def load_tickets():
    if os.path.exists(TICKETS_FILE):
        with open(TICKETS_FILE, 'r') as file:
            return json.load(file)
    return []

def save_tickets(tickets):
    print("💾 Saving to JSON...", len(tickets), "tickets")  # ✅ Add this line
    print("📁 Path:", os.path.abspath(TICKETS_FILE))  # ✅ Add this line
    with open(TICKETS_FILE, 'w') as file:
        json.dump(tickets, file, indent=2)

app = Flask(__name__)
app.secret_key = 'surya@148'  # 🔐 You can make this any strong string
tickets = load_tickets()  # This will hold all ticket submissions
ticket_serials = {}  # To track how many tickets raised each day

# Temporary users stored here (just for testing now)
users = load_users()
@app.route('/add-employee', methods=['GET', 'POST'])
def add_employee():
    users = load_users()

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        if username in users:
            return render_template('add_employee.html', message="❌ User already exists.")

        users[username] = {"password": password, "role": role}
        save_users(users)

        return render_template('add_employee.html', message="✅ User added successfully!")

    return render_template('add_employee.html')
@app.route('/remove-employee')
def remove_employee():
    return "Remove Employee Page (Under Construction)"

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users.get(username)
        if user and user['password'] == password:
            session['username'] = username
            role = user['role']
            if role == 'teacher':
                return redirect(url_for('raise_ticket'))
            elif role == 'it':
                return redirect(url_for('it_dashboard'))
            elif role == 'admin':
                return redirect(url_for('admin_dashboard'))  # can build later
            else:
                return "❌ Unknown role. Please check user role value."
        else:
            return "Invalid credentials. Please try again."

    return render_template('login.html')

@app.route('/raise-ticket', methods=['GET', 'POST'])
def raise_ticket():
    if request.method == 'POST':
        Campus = request.form['Campus']
        description = request.form['description']
        raised_by = session.get('username', 'unknown')
        issue_type = request.form['issue_type']
        username = request.form.get('username', 'Unknown')  # default if session not used
        from datetime import datetime
        india_timezone = pytz.timezone("Asia/Kolkata")
        now = datetime.now(india_timezone)
        ticket_date = now.strftime("%d-%m-%Y")
        ticket_time = now.strftime("%H:%M:%S")
        serial_number = len(tickets) + 1
        ticket_id = now.strftime("%d%m") + str(serial_number).zfill(2)

        ticket = {
            "id": ticket_id,
            "Campus": Campus,
            "raised_by": raised_by,
            "description": description,
            "issue_type": issue_type,
            "date": ticket_date,
            "time": ticket_time,
            "status": "Pending"
        }

        tickets.append(ticket)
        save_tickets(tickets)
        return render_template('raise_ticket.html', message="✅ Ticket submitted successfully!")

    return render_template('raise_ticket.html')

@app.route('/it-dashboard')
def it_dashboard():
    return render_template('it_dashboard.html', tickets=tickets)

@app.route('/raise-ticket', methods=['GET', 'POST'])


@app.route('/export')
def export_tickets():
    if not tickets:
        return "No tickets to export."

    import io
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_ALL)

    # ✅ Write correct header (each column once, in right order)
    writer.writerow(["Ticket ID", "Campus", "Raised By", "Issue Type", "Description", "Date", "Time"])

    # ✅ Write aligned data
    for ticket in tickets:
        writer.writerow([
            ticket["id"],
            ticket["Campus"],
            ticket["raised_by"],       # Make sure this matches your data keys!
            ticket["issue_type"],
            ticket["description"],
            ticket["date"],
            ticket["time"]
        ])

    output.seek(0)
    return Response(output, mimetype='text/csv',
                    headers={"Content-Disposition": "attachment;filename=tickets.csv"})

@app.route('/logout')
def logout():
    return redirect(url_for('login'))
@app.route('/routes')
def show_routes():
    return '<br>'.join([str(rule) for rule in app.url_map.iter_rules()])

@app.route('/update_status', methods=['POST'])
def update_status():
    ticket_id = request.form.get('ticket_id')

    for ticket in tickets:
        if ticket['id'] == ticket_id:
            if ticket['status'] == 'Pending':
                ticket['status'] = 'In Progress'
            elif ticket['status'] == 'In Progress':
                ticket['status'] = 'Resolved'
            elif ticket['status'] == 'Resolved':
                ticket['status'] = 'Pending'
            break
    save_tickets(tickets)

    return redirect(url_for('it_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)



