from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request

WEB3FORMS_KEY = os.environ.get("WEB3FORMS_KEY", "")


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

            if not WEB3FORMS_KEY:
                return self._respond(500, {"detail": "Email service not configured."})

            payload = json.dumps({
                "access_key": WEB3FORMS_KEY,
                "name": name,
                "email": email,
                "message": message,
                "subject": f"Portfolio Contact from {name}"
            }).encode("utf-8")

            req = urllib.request.Request(
                "https://api.web3forms.com/submit",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode("utf-8"))

            if result.get("success"):
                self._respond(200, {"status": "Message sent successfully."})
            else:
                self._respond(500, {"detail": "Failed to send message. Please try again."})

        except json.JSONDecodeError:
            self._respond(400, {"detail": "Invalid request."})
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
