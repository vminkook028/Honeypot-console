import socket
import threading
import datetime

log_callback = None
_servers = {}
_running = {}
_locks = {}

def set_log_callback(cb):
    global log_callback
    log_callback = cb

def log(msg, service_tag="FTP"):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    full_msg = f"[{timestamp}] [{service_tag}] {msg}"
    print(full_msg)
    if log_callback:
        log_callback("FTP", full_msg)

def handle_client(conn, addr):
    ip, port = addr
    log(f"New connection from {ip}:{port}")
    try:
        conn.sendall(b"220 ProFTPD 1.3.5e Server ready\r\n")
        username = None
        while True:
            data = conn.recv(1024)
            if not data:
                break
            command = data.decode(errors="ignore").strip()
            if not command:
                continue
            log(f"{ip} >> {command}")
            cmd_upper = command.upper()
            if cmd_upper.startswith("USER"):
                username = command[5:].strip()
                conn.sendall(b"331 Password required for " + username.encode() + b"\r\n")
            elif cmd_upper.startswith("PASS"):
                password = command[5:].strip()
                log(f"*** LOGIN ATTEMPT *** User='{username}' Pass='{password}' From={ip}")
                conn.sendall(b"530 Login incorrect.\r\n")
            elif cmd_upper == "QUIT":
                conn.sendall(b"221 Goodbye.\r\n")
                break
            elif cmd_upper.startswith("SYST"):
                conn.sendall(b"215 UNIX Type: L8\r\n")
            elif cmd_upper.startswith("FEAT"):
                conn.sendall(b"211-Features:\r\n AUTH TLS\r\n UTF8\r\n211 End\r\n")
            else:
                conn.sendall(b"530 Please login with USER and PASS.\r\n")
    except Exception as e:
        log(f"Error [{ip}]: {e}")
    finally:
        try:
            conn.close()
        except:
            pass
        log(f"Connection closed: {ip}:{port}")

def start(host="0.0.0.0", port=2121, instance_id=None):
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
    srv.listen(10)
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
    log(f"FTP stopped on port {port}")

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
    log("FTP instance stopped")