import socket
import threading
import datetime
import base64

log_callback = None
_servers = {}
_running = {}

FAKE_LOGIN_HTML = """\
HTTP/1.1 200 OK\r
Content-Type: text/html\r
Server: Apache/2.4.54 (Ubuntu)\r
X-Powered-By: PHP/8.1.2\r
\r
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Admin Panel - Login</title>
<style>
  body{background:#1a1a2e;display:flex;align-items:center;justify-content:center;height:100vh;margin:0;font-family:Arial,sans-serif}
  .box{background:#16213e;padding:40px;border-radius:8px;width:320px;box-shadow:0 4px 20px rgba(0,0,0,.5)}
  h2{color:#e94560;margin:0 0 24px;text-align:center}
  input{width:100%;padding:10px;margin:8px 0;background:#0f3460;border:1px solid #e94560;border-radius:4px;color:#fff;box-sizing:border-box}
  button{width:100%;padding:12px;background:#e94560;color:#fff;border:none;border-radius:4px;cursor:pointer;font-size:15px;margin-top:10px}
  button:hover{background:#c73652}
  .logo{text-align:center;color:#aaa;font-size:12px;margin-top:16px}
</style></head>
<body>
<div class="box">
  <h2>&#128274; Admin Login</h2>
  <form method="POST" action="/login">
    <input type="text" name="username" placeholder="Username" required>
    <input type="password" name="password" placeholder="Password" required>
    <button type="submit">Sign In</button>
  </form>
  <div class="logo">Secure Admin Panel v2.1</div>
</div>
</body></html>
"""

FAKE_401 = b"HTTP/1.1 401 Unauthorized\r\nContent-Type: text/plain\r\nWWW-Authenticate: Basic realm=\"Admin Panel\"\r\n\r\nAccess Denied: Invalid credentials."
FAKE_404 = b"HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n<h1>404 Not Found</h1><p>The requested URL was not found.</p>"
FAKE_403 = b"HTTP/1.1 403 Forbidden\r\nContent-Type: text/html\r\n\r\n<h1>403 Forbidden</h1>"

SENSITIVE_PATHS = [
    "/admin", "/administrator", "/wp-admin", "/wp-login.php",
    "/phpmyadmin", "/pma", "/.env", "/config", "/backup",
    "/shell", "/cmd", "/console", "/manager", "/panel",
    "/.git", "/api/v1", "/login", "/signin", "/auth"
]

def set_log_callback(cb):
    global log_callback
    log_callback = cb

def log(msg):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    full_msg = f"[{timestamp}] [HTTP] {msg}"
    print(full_msg)
    if log_callback:
        log_callback("HTTP", full_msg)

def parse_post_body(body):
    creds = {}
    try:
        for pair in body.split("&"):
            if "=" in pair:
                k, v = pair.split("=", 1)
                creds[k.strip()] = v.strip().replace("+", " ")
    except:
        pass
    return creds

def handle_client(conn, addr):
    ip, src_port = addr
    log(f"New connection from {ip}:{src_port}")
    try:
        conn.settimeout(5.0)
        data = conn.recv(8192)
        if not data:
            return
        raw = data.decode(errors="ignore")
        lines = raw.split("\r\n")
        request_line = lines[0] if lines else ""

        method, path, proto = "", "/", "HTTP/1.1"
        if request_line:
            parts = request_line.split(" ")
            method = parts[0] if len(parts) > 0 else "GET"
            path   = parts[1] if len(parts) > 1 else "/"
            proto  = parts[2] if len(parts) > 2 else "HTTP/1.1"

        log(f"{ip} >> {method} {path}")

        user_agent = ""
        for line in lines[1:]:
            if line.lower().startswith("user-agent:"):
                user_agent = line[11:].strip()
                log(f"{ip} User-Agent: {user_agent}")
            if line.lower().startswith("authorization:"):
                log(f"{ip} Auth header detected: {line}")

        # Basic Auth decode
        for line in lines:
            if line.startswith("Authorization: Basic"):
                encoded = line.split(" ")[-1].strip()
                try:
                    decoded = base64.b64decode(encoded).decode()
                    log(f"*** LOGIN ATTEMPT *** BasicAuth={decoded} From={ip}")
                except:
                    log(f"*** LOGIN ATTEMPT *** BasicAuth(raw)={encoded} From={ip}")

        # POST credentials
        if method == "POST":
            body_part = raw.split("\r\n\r\n", 1)[-1] if "\r\n\r\n" in raw else ""
            creds = parse_post_body(body_part)
            user = creds.get("username", creds.get("user", creds.get("email", "?")))
            pwd  = creds.get("password", creds.get("pass", creds.get("pwd", "?")))
            log(f"*** LOGIN ATTEMPT *** User='{user}' Pass='{pwd}' Path={path} From={ip}")
            conn.sendall(FAKE_401)
            return

        path_clean = path.split("?")[0].rstrip("/") or "/"

        if path_clean in ("", "/", "/index.html", "/index.php"):
            conn.sendall(FAKE_LOGIN_HTML.encode())
        elif any(path_clean.lower().startswith(s) for s in SENSITIVE_PATHS):
            log(f"*** PROBE *** Sensitive path '{path_clean}' accessed from {ip}")
            conn.sendall(FAKE_LOGIN_HTML.encode())
        else:
            log(f"PROBE: unknown path '{path_clean}' from {ip}")
            conn.sendall(FAKE_404)

    except socket.timeout:
        pass
    except Exception as e:
        log(f"Error [{ip}]: {e}")
    finally:
        try:
            conn.close()
        except:
            pass
        log(f"Connection closed: {ip}:{src_port}")

def start(host="0.0.0.0", port=8080, instance_id=None):
    key = instance_id or port
    _running[key] = True
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        srv.bind((host, port))
    except OSError as e:
        log(f"BIND ERROR on port {port}: {e}")
        _running[key] = False
        return
    srv.listen(20)
    srv.settimeout(1.0)
    _servers[key] = srv
    log(f"Listening on {host}:{port} [instance={key}]")
    while _running.get(key, False):
        try:
            conn, addr = srv.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()
        except socket.timeout:
            continue
        except Exception:
            break
    try:
        srv.close()
    except:
        pass
    log(f"HTTP stopped on port {port}")

def stop(instance_id=None, port=None):
    key = instance_id or port
    if key is not None:
        _running[key] = False
        if key in _servers:
            try:
                _servers[key].close()
            except:
                pass
    else:
        for k in list(_running.keys()):
            _running[k] = False
        for k, s in list(_servers.items()):
            try:
                s.close()
            except:
                pass
    log("HTTP instance stopped")