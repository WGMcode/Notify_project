# WGM
# Safety and reproducibility checked independetly and verfied on 3 different LLMs
# Date: 2025-10-01
# --- Script to send email notifications on script completion or failure
# Follow these steps to use:
# 1. Set the following environment variables in your system by opening the settings.json file (Ctrl+Shift+P -> Preferences: Open User Settings (JSON)):
#    Paste the following, replacing placeholders with your actual email credentials:
#    {...some existing settings...,
#     "terminal.integrated.env.windows": {
#         "EMAIL_USER": "gmail address you want to send from",
#         "EMAIL_PASS": "app password you generated from gmail (go to google account -> security -> app passwords (need 2-step verification enabled))",
#         "EMAIL_TO": "gmail address you want to send to"
#     }
#    }
# 2. At the top of any Python script you want this functionality to apply to (inside the same folder), add:
#    import notify_on_finish
#    notify_on_finish.setup()
# 3. Close and reopen VSCode to ensure environment variables are loaded.
# 4. Daar vat hy. Run your script as usual. You will receive an email when it finishes or crashes.
# --- EXTRAS ---
# Set line 36 to False if you don't want to save and send the complete terminal output and only want a brief email notification on finish/failure.


import os                               # for environment variables
import smtplib                          # for sending emails
import ssl                              # for secure email connection
import time                             # for tracking script duration
import atexit                           # for registering exit handlers
import sys                              # for redirecting stdout/stderr
import traceback                        # for capturing exception tracebacks
from datetime import datetime           # for timestamping log files
from email.message import EmailMessage  # for constructing email messages with attachments

#--- global state ---
_start = time.time()
_sent = False                    
_failed = False                    

#--- log file settings ---
SAVE_LOG_TO_FILE = True
LOG_FILE = f"script_log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"

#--- file handle for log file ---
_log_file_handle = None

# --- redirect print output to terminal + file ---
if SAVE_LOG_TO_FILE:
    class Tee: # class for duplicating output streams
        """Redirects writes to multiple file-like objects."""
        def __init__(self, *files):
            self.files = files

        def write(self, data):
            for f in self.files:
                f.write(data)
                f.flush()

        def flush(self):
            for f in self.files:
                f.flush()

    _log_file_handle = open(LOG_FILE, "w", encoding="utf-8")
    sys.stdout = sys.stderr = Tee(sys.stdout, _log_file_handle)

#--- email sending function ---
def _send_email(subject, body):
    global _sent
    if _sent:
        return

    user = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")
    to_addrs = os.getenv("EMAIL_TO", user)
    server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    port = int(os.getenv("SMTP_PORT", "465")) # SSL port

    if not user or not password or not to_addrs:
        print("[notify_on_finish] Missing email environment variables.")
        return

    try:
        # flush the log before reading
        if SAVE_LOG_TO_FILE and _log_file_handle:
            _log_file_handle.flush()

        msg = EmailMessage()
        msg["From"] = user
        msg["To"] = to_addrs
        msg["Subject"] = subject
        msg.set_content(body)

        if SAVE_LOG_TO_FILE and os.path.exists(LOG_FILE):
            with open(LOG_FILE, "rb") as f:
                msg.add_attachment(
                    f.read(),
                    maintype="text",
                    subtype="plain",
                    filename=os.path.basename(LOG_FILE)
                )

        ctx = ssl.create_default_context()
        with smtplib.SMTP_SSL(server, port, context=ctx) as smtp:
            smtp.login(user, password)
            smtp.send_message(msg)

        _sent = True
        print(f"[notify_on_finish] Email sent: {subject}")

    except Exception as e:
        print(f"[notify_on_finish] Failed to send email: {e}")

#--- cleanup function ---
def _cleanup_log_file():
    """Close the log file and restore stdout/stderr to original."""
    global _log_file_handle
    if _log_file_handle:
        try:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
            _log_file_handle.close()
        except Exception:
            pass
        _log_file_handle = None

#--- success and failure handlers ---
def _on_success():
    if _failed:
        _cleanup_log_file()
        return

    dur = time.time() - _start
    subject = f"[DONE] {os.path.basename(sys.argv[0])}"
    body = f"Script finished successfully.\nDuration: {dur:.1f} seconds."
    print(body)
    _send_email(subject, body)
    _cleanup_log_file()

#--- exception handler ---
def _on_failure(exc_type, exc, tb):
    global _failed
    _failed = True
    dur = time.time() - _start
    tbtext = "".join(traceback.format_exception(exc_type, exc, tb))
    subject = f"[ERROR] {os.path.basename(sys.argv[0])}: {exc_type.__name__}"
    body = f"Script crashed after {dur:.1f} seconds.\n\n{tbtext}"
    print(body)
    _send_email(subject, body)
    _cleanup_log_file()
    sys.__excepthook__(exc_type, exc, tb)

#--- setup function ---
def setup():
    """Call at the top of your script to enable notifications and logging."""
    sys.excepthook = _on_failure
    atexit.register(_on_success)