# Honeypot Console

A multi-protocol honeypot with a desktop GUI (Tkinter) for monitoring and logging unauthorized connection attempts across FTP, SSH, and HTTP services.

> ⚠️ **Research / Educational Use Only**
> This project is intended strictly for cybersecurity research, learning, and lab environments. **Never deploy this on a production network or expose it to the public internet.** Running fake services can attract real attackers and may have legal implications depending on your jurisdiction.

---

## ✨ Features

- 🖥️ **GUI Console** — Dark-themed Tkinter dashboard to control all honeypot services
- 🔌 **Multi-protocol support** — FTP, SSH, and HTTP fake listeners
- 📋 **60+ well-known ports database** — quickly spin up decoys on common service ports (MySQL, RDP, MongoDB, Redis, Docker API, etc.)
- 🔍 **Live log viewer** — filter by service, search keywords, color-coded events (logins, probes, errors)
- 📊 **Connection tracking** — per-port connection counters and active listener panel
- 💾 **Export logs** — save captured activity to a `.txt` file for later analysis

---

## 📦 Requirements

- Python 3.10+
- No external dependencies — uses only Python's standard library (`tkinter`, `threading`, `socket`)

---

## 🚀 Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/vminkook028/honeypot-console.git
   cd honeypot-console
   ```

2. Run the app:
   ```bash
   python main.py
   ```

3. In the GUI:
   - Pick a port from the list and click **START**, or use **START ALL**
   - Watch incoming connection attempts and captured credentials appear in the log panel
   - Use **Export Log** to save captured data

---

## 🗂️ Project Structure

```
honeypot-console/
├── main.py        # Entry point — launches the GUI
├── FTP.py         # Fake FTP service
├── SSH.py         # Fake SSH service
├── HTTP.py        # Fake HTTP service
└── README.md
```

---

## ⚙️ Notes

- Some ports may fail to bind with a `WinError 10013` on Windows — this usually means the port is reserved by Windows/Hyper-V/WSL or already in use by another program, not a bug in this project.
- Default honeypot ports are non-privileged alternates (e.g. `2121` for FTP, `2222` for SSH) so they can run without admin/root privileges.

---

## 🛡️ Disclaimer

This software is provided for **educational and authorized security research purposes only**. The author is not responsible for any misuse of this tool. Always get proper authorization before deploying any honeypot or monitoring tool on a network you do not own.

---

## 📄 License

MIT License (or update based on what you selected when creating the repo)
