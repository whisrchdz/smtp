from flask import Flask, request, jsonify
import re
import smtplib
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

app = Flask(__name__)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@app.post("/api/send")
def send():

    data = request.get_json(silent=True) or {}

    smtp_host = (data.get("smtp_host") or "").strip()
    smtp_port = int(data.get("smtp_port", 587))
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    sender_name = (data.get("sender_name") or "").strip()
    sender_email = (data.get("sender_email") or "").strip() or username
    recipient = (data.get("recipient") or "").strip()
    subject = (data.get("subject") or "SMTP Test").strip()
    html_body = data.get("html") or "<h2>SMTP Test</h2>"

    if not EMAIL_RE.match(username):
        return jsonify(error="Invalid username"), 400

    if not EMAIL_RE.match(recipient):
        return jsonify(error="Invalid recipient"), 400

    msg = MIMEMultipart()
    msg["From"] = formataddr((sender_name, sender_email))
    msg["To"] = recipient
    msg["Subject"] = subject

    msg.attach(MIMEText(html_body, "html"))

    server = None

    try:

        server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
        server.ehlo()

        if server.has_extn("STARTTLS"):
            server.starttls()
            server.ehlo()

        server.login(username, password)

        server.sendmail(
            sender_email,
            [recipient],
            msg.as_string()
        )

        return jsonify(success=True)

    except smtplib.SMTPAuthenticationError:
        return jsonify(error="Authentication failed"), 401

    except socket.timeout:
        return jsonify(error="Connection timeout"), 504

    except Exception as e:
        return jsonify(error=str(e)), 500

    finally:
        if server:
            try:
                server.quit()
            except:
                pass


@app.get("/")
def home():
    return "SMTP Tester API"
