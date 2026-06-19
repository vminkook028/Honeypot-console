import socket
import threading
import datetime

log_callback = None
_servers = {}
_running = {}

def set_log_callback(cb):
    global log_callback
    log_callback = cb

def log(msg):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    full_msg = f"[{timestamp}] [SSH] {msg}"
    print(full_msg)
    if log_callback:
        log_callback("SSH", full_msg)

def handle_client(conn, addr):
    ip, port = addr
    log(f"New connection from {ip}:{port}")
    try:
        conn.sendall(b"SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.6\r\n")
        conn.settimeout(5.0)
        buffer = b""
        while True:
            try:
                data = conn.recv(1024)
            except socket.timeout:
                break
            if not data:
                break
            buffer += data
            try:
                text = buffer.decode(errors="ignore")
                for line in text.split("\n"):
                    line = line.strip()
                    if line:
                        printable = "".join(c if 32 <= ord(c) < 127 else "." for c in line)
                        if printable.strip("."):
                            log(f"DATA from {ip} >> {printable[:100]}")
            except:
                pass
            if len(buffer) > 16:
                log(f"*** AUTH PROBE *** From={ip}:{port} bytes={len(buffer)}")
                try:
                    conn.sendall(b"Permission denied (publickey,password).\r\n")
                except:
                    pass
                break
    except Exception as e:
        log(f"Error [{ip}]: {e}")
    finally:
        try:
            conn.close()
        except:
            pass
        log(f"Connection closed: {ip}:{port}")

def start(host="0.0.0.0", port=2222, instance_id=None):
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
    log(f"SSH stopped on port {port}")

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
    log("SSH instance stopped")