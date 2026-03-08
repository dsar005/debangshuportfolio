from http.server import BaseHTTPRequestHandler
import json
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

GMAIL_USER = os.environ.get("GMAIL_USER", "")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL", GMAIL_USER)


class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length).decode("utf-8"))

            name = body.get("name", "").strip()
            email = body.get("email", "").strip()
            message = body.get("message", "").strip()

            if not name or not email or not message:
                return self._respond(400, {"detail": "All fields are required."})

            if not GMAIL_USER or not GMAIL_APP_PASSWORD:
                return self._respond(500, {"detail": "Email service not configured."})

            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"Portfolio Contact from {name}"
            msg["From"] = GMAIL_USER
            msg["To"] = RECIPIENT_EMAIL
            msg["Reply-To"] = email

            plain = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
            html = f"""<html><body style="font-family:sans-serif;color:#333">
<h2 style="color:#00C9A7">New Portfolio Contact</h2>
<p><strong>Name:</strong> {name}</p>
<p><strong>Email:</strong> <a href="mailto:{email}">{email}</a></p>
<p><strong>Message:</strong></p>
<p style="background:#f5f5f5;padding:12px;border-radius:6px">{message.replace(chr(10), "<br>")}</p>
</body></html>"""

            msg.attach(MIMEText(plain, "plain"))
            msg.attach(MIMEText(html, "html"))

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
                server.sendmail(GMAIL_USER, RECIPIENT_EMAIL, msg.as_string())

            self._respond(200, {"status": "Message sent successfully."})

        except json.JSONDecodeError:
            self._respond(400, {"detail": "Invalid request."})
        except smtplib.SMTPAuthenticationError:
            self._respond(500, {"detail": "Email configuration error. Please try again later."})
        except Exception:
            self._respond(500, {"detail": "Something went wrong. Please try again."})

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _respond(self, status, data):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self._cors()
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))
