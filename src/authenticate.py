"""One-command Schwab (re-)authentication.

Schwab refresh tokens expire ~every 7 days and can only be renewed by logging in through a
browser — there is no way to automate past that. This makes it painless:

    python -m src.authenticate

opens your browser to Schwab, captures the OAuth redirect with a local HTTPS server, caches a
fresh token to SCHWAB_TOKEN_PATH, then prints every account the token can see so you can confirm
your Roth IRA and individual account are actually included (not just the options account).

Copied from ../trade-log/src/authenticate.py's in-process HTTPS callback approach: schwab-py's
built-in Flask/multiprocess auto-capture is broken on this Windows box (confirmed there), so don't
try it again here — this custom loopback server is the proven-working path.
"""
import datetime as dt
import ipaddress
import json
import os
import ssl
import tempfile
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

from dotenv import load_dotenv
from schwab.auth import client_from_received_url, client_from_token_file, get_auth_context

from src.schwab_client import get_accounts_summary

load_dotenv()

LOGIN_TIMEOUT_SECONDS = 180
_captured = {}


def _self_signed_cert():
    """Generate an ephemeral self-signed cert for the local 127.0.0.1 callback server."""
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "127.0.0.1")])
    cert = (x509.CertificateBuilder()
            .subject_name(name).issuer_name(name)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(dt.datetime.utcnow() - dt.timedelta(days=1))
            .not_valid_after(dt.datetime.utcnow() + dt.timedelta(days=3650))
            .add_extension(x509.SubjectAlternativeName(
                [x509.IPAddress(ipaddress.ip_address("127.0.0.1"))]), critical=False)
            .sign(key, hashes.SHA256()))
    cf = tempfile.NamedTemporaryFile(delete=False, suffix=".pem")
    kf = tempfile.NamedTemporaryFile(delete=False, suffix=".pem")
    cf.write(cert.public_bytes(serialization.Encoding.PEM)); cf.close()
    kf.write(key.private_bytes(serialization.Encoding.PEM,
             serialization.PrivateFormat.TraditionalOpenSSL,
             serialization.NoEncryption())); kf.close()
    return cf.name, kf.name


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        _captured["path"] = self.path
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(b"<h2>Schwab login captured. You can close this tab.</h2>")

    def log_message(self, *args):
        pass


def _capture_via_server(callback_url, auth_url):
    """Open the browser, catch the OAuth redirect locally. Returns full URL or None."""
    parsed = urllib.parse.urlparse(callback_url)
    host, port = parsed.hostname, parsed.port or 443
    certf, keyf = _self_signed_cert()
    httpd = HTTPServer((host, port), _Handler)
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(certf, keyf)
    httpd.socket = ctx.wrap_socket(httpd.socket, server_side=True)
    httpd.timeout = LOGIN_TIMEOUT_SECONDS
    print("Opening your browser to log in to Schwab...")
    print("(Your browser will warn about a self-signed certificate for 127.0.0.1 — "
          "that's expected; choose Advanced -> Proceed.)")
    webbrowser.open(auth_url)
    print(f"If it didn't open, visit:\n  {auth_url}")
    httpd.handle_request()   # blocks until the redirect arrives or timeout
    httpd.server_close()
    if "path" in _captured:
        return urllib.parse.urljoin(callback_url, _captured["path"])
    return None


def _token_writer(token_path):
    def write(token, *args, **kwargs):
        with open(token_path, "w") as f:
            json.dump(token, f)
    return write


def main():
    api_key = os.environ["SCHWAB_APP_KEY"]
    app_secret = os.environ["SCHWAB_APP_SECRET"]
    callback_url = os.environ.get("SCHWAB_CALLBACK_URL", "https://127.0.0.1:8182")
    token_path = os.environ.get("SCHWAB_TOKEN_PATH", ".schwab_token.json")

    ctx = get_auth_context(api_key, callback_url)

    received_url = None
    try:
        received_url = _capture_via_server(callback_url, ctx.authorization_url)
    except Exception as e:
        print(f"Auto-capture unavailable ({e}); using manual fallback.")

    if not received_url:
        print("\nManual fallback — open the URL above, log in, then paste the address "
              "your browser lands on (starts with https://127.0.0.1:8182/?code=...):")
        received_url = input("Paste redirect URL: ").strip()

    client_from_received_url(
        api_key, app_secret, ctx, received_url, _token_writer(token_path))

    # Verify the fresh token actually works, and show what it can see.
    client = client_from_token_file(token_path, api_key, app_secret)
    accounts = get_accounts_summary(client)
    print(f"\nToken refreshed and cached to {token_path}. Good for ~7 days.")
    print(f"Verified: {len(accounts)} account(s) reachable:")
    for acct in accounts:
        print(f"  - {acct['type']} ({acct['account_number_masked']}) "
              f"— {len(acct['positions'])} position(s)")
    print("\nConfirm your Roth IRA and individual account both appear above. If not, see "
          "planning/todo.md #2-#3.")


if __name__ == "__main__":
    main()
