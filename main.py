import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import threading
import datetime
import os
import sys
import uuid
import socket

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import FTP, SSH, HTTP

# ── Palette ──────────────────────────────────────────────────────────────────
BG      = "#0d1117"
PANEL   = "#161b22"
PANEL2  = "#1c2128"
BORDER  = "#30363d"
BORDER2 = "#21262d"
FG      = "#e6edf3"
FG2     = "#c9d1d9"
MUTED   = "#8b949e"
GREEN   = "#3fb950"
GREEN_D = "#2ea043"
RED     = "#f85149"
RED_D   = "#da3633"
YELLOW  = "#e3b341"
BLUE    = "#58a6ff"
BLUE_D  = "#1f6feb"
ORANGE  = "#ffa657"
PURPLE  = "#bc8cff"
CYAN    = "#39d353"
PINK    = "#ff7eb6"
TEAL    = "#2dd4bf"

SVC_COLOR  = {"FTP": BLUE, "SSH": GREEN, "HTTP": ORANGE}
SVC_MODULE = {"FTP": FTP,  "SSH": SSH,   "HTTP": HTTP}

# ── All well-known ports database ────────────────────────────────────────────
ALL_PORTS = [
    # (port, service_name, protocol_module, category, description)
    (21,    "FTP",          "FTP",  "File Transfer",   "File Transfer Protocol"),
    (22,    "SSH",          "SSH",  "Remote Access",   "Secure Shell"),
    (23,    "TELNET",       "SSH",  "Remote Access",   "Telnet (unencrypted shell)"),
    (25,    "SMTP",         "HTTP", "Mail",            "Simple Mail Transfer Protocol"),
    (53,    "DNS",          "HTTP", "Network",         "Domain Name System"),
    (69,    "TFTP",         "FTP",  "File Transfer",   "Trivial File Transfer Protocol"),
    (80,    "HTTP",         "HTTP", "Web",             "HyperText Transfer Protocol"),
    (110,   "POP3",         "HTTP", "Mail",            "Post Office Protocol v3"),
    (119,   "NNTP",         "HTTP", "News",            "Network News Transfer Protocol"),
    (123,   "NTP",          "HTTP", "Network",         "Network Time Protocol"),
    (135,   "MSRPC",        "HTTP", "Windows",         "Microsoft RPC"),
    (137,   "NetBIOS-NS",   "HTTP", "Windows",         "NetBIOS Name Service"),
    (138,   "NetBIOS-DGM",  "HTTP", "Windows",         "NetBIOS Datagram Service"),
    (139,   "NetBIOS-SSN",  "HTTP", "Windows",         "NetBIOS Session Service"),
    (143,   "IMAP",         "HTTP", "Mail",            "Internet Message Access Protocol"),
    (161,   "SNMP",         "HTTP", "Network",         "Simple Network Management Protocol"),
    (194,   "IRC",          "HTTP", "Chat",            "Internet Relay Chat"),
    (389,   "LDAP",         "HTTP", "Directory",       "Lightweight Directory Access Protocol"),
    (443,   "HTTPS",        "HTTP", "Web",             "HTTP Secure"),
    (445,   "SMB",          "HTTP", "Windows",         "Server Message Block"),
    (465,   "SMTPS",        "HTTP", "Mail",            "SMTP over SSL"),
    (514,   "Syslog",       "HTTP", "Network",         "System Logging Protocol"),
    (515,   "LPD",          "HTTP", "Print",           "Line Printer Daemon"),
    (587,   "SMTP-Sub",     "HTTP", "Mail",            "SMTP Submission"),
    (631,   "IPP",          "HTTP", "Print",           "Internet Printing Protocol"),
    (993,   "IMAPS",        "HTTP", "Mail",            "IMAP over SSL"),
    (995,   "POP3S",        "HTTP", "Mail",            "POP3 over SSL"),
    (1080,  "SOCKS",        "HTTP", "Proxy",           "SOCKS Proxy"),
    (1194,  "OpenVPN",      "HTTP", "VPN",             "OpenVPN"),
    (1433,  "MSSQL",        "HTTP", "Database",        "Microsoft SQL Server"),
    (1521,  "Oracle",       "HTTP", "Database",        "Oracle Database"),
    (1723,  "PPTP",         "HTTP", "VPN",             "Point-to-Point Tunneling"),
    (2049,  "NFS",          "HTTP", "File Transfer",   "Network File System"),
    (2121,  "FTP-Alt",      "FTP",  "File Transfer",   "FTP Alternate Port"),
    (2222,  "SSH-Alt",      "SSH",  "Remote Access",   "SSH Alternate Port"),
    (2375,  "Docker",       "HTTP", "Container",       "Docker API (unencrypted)"),
    (2376,  "Docker-TLS",   "HTTP", "Container",       "Docker API (TLS)"),
    (3000,  "Dev-HTTP",     "HTTP", "Web",             "Dev/Node.js HTTP"),
    (3306,  "MySQL",        "HTTP", "Database",        "MySQL Database"),
    (3389,  "RDP",          "HTTP", "Remote Access",   "Remote Desktop Protocol"),
    (4444,  "Metasploit",   "HTTP", "Exploit",         "Metasploit default listener"),
    (4445,  "Upnotifyp",    "HTTP", "Exploit",         "Common backdoor port"),
    (5000,  "Flask",        "HTTP", "Web",             "Flask/Dev HTTP Server"),
    (5432,  "PostgreSQL",   "HTTP", "Database",        "PostgreSQL Database"),
    (5900,  "VNC",          "HTTP", "Remote Access",   "Virtual Network Computing"),
    (5985,  "WinRM-HTTP",   "HTTP", "Windows",         "Windows Remote Management"),
    (5986,  "WinRM-HTTPS",  "HTTP", "Windows",         "Windows Remote Mgmt (TLS)"),
    (6379,  "Redis",        "HTTP", "Database",        "Redis In-Memory Database"),
    (6667,  "IRC",          "HTTP", "Chat",            "IRC (unencrypted)"),
    (7001,  "WebLogic",     "HTTP", "Web",             "Oracle WebLogic Server"),
    (8000,  "HTTP-Alt",     "HTTP", "Web",             "HTTP Alternate"),
    (8080,  "HTTP-Proxy",   "HTTP", "Web",             "HTTP Proxy / Alt Web"),
    (8443,  "HTTPS-Alt",    "HTTP", "Web",             "HTTPS Alternate"),
    (8888,  "Jupyter",      "HTTP", "Web",             "Jupyter Notebook"),
    (9000,  "PHP-FPM",      "HTTP", "Web",             "PHP FastCGI / SonarQube"),
    (9090,  "Prometheus",   "HTTP", "Monitoring",      "Prometheus Metrics"),
    (9200,  "Elasticsearch","HTTP", "Database",        "Elasticsearch REST API"),
    (9300,  "ES-Transport", "HTTP", "Database",        "Elasticsearch Transport"),
    (11211, "Memcached",    "HTTP", "Database",        "Memcached"),
    (27017, "MongoDB",      "HTTP", "Database",        "MongoDB Database"),
    (27018, "MongoDB-Shard","HTTP", "Database",        "MongoDB Shard"),
    (50000, "SAP",          "HTTP", "Enterprise",      "SAP Application Server"),
]

CATEGORIES = sorted(set(p[3] for p in ALL_PORTS))
CAT_COLORS = {
    "File Transfer": BLUE,
    "Remote Access": GREEN,
    "Web":           ORANGE,
    "Mail":          PINK,
    "Database":      PURPLE,
    "Windows":       CYAN,
    "Network":       TEAL,
    "Container":     "#f97316",
    "Exploit":       RED,
    "VPN":           "#a78bfa",
    "Proxy":         "#34d399",
    "Monitoring":    "#fb923c",
    "Print":         MUTED,
    "Chat":          "#e879f9",
    "Directory":     "#60a5fa",
    "Enterprise":    "#fbbf24",
    "News":          MUTED,
}

LOG_TAG_COLOR = {
    "LOGIN":   YELLOW,
    "PROBE":   PURPLE,
    "CLOSED":  BORDER,
    "SYSTEM":  MUTED,
    "FTP":     BLUE,
    "SSH":     GREEN,
    "HTTP":    ORANGE,
    "ERROR":   RED,
    "DEFAULT": FG2,
}

def make_btn(parent, text, color, cmd, fg=BG, font_size=9, padx=14, pady=5):
    return tk.Button(parent, text=text, font=("Consolas", font_size, "bold"),
                     bg=color, fg=fg, activebackground=color, activeforeground=fg,
                     relief="flat", bd=0, padx=padx, pady=pady,
                     cursor="hand2", command=cmd)


# ── Active instance tracker ──────────────────────────────────────────────────
class PortInstance:
    def __init__(self, port, module_key, instance_id):
        self.port        = port
        self.module_key  = module_key
        self.instance_id = instance_id
        self.conn_count  = 0
        self.running     = True


class HoneypotGUI:

    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("Honeypot Console v2.0")
        root.configure(bg=BG)
        root.geometry("1200x800")
        root.minsize(1000, 640)
        root.resizable(True, True)

        self._log_entries   = []
        self._total_conns   = 0
        self._active_tab    = tk.StringVar(value="ALL")
        self._instances: dict[str, PortInstance] = {}   # instance_id -> PortInstance
        self._port_rows: dict[str, tk.Frame] = {}       # instance_id -> row frame

        self._build_ui()
        self._wire_callbacks()
        self._update_clock()
        self._tick()

    # ═══════════════════════════════════════════════════════════════════════════
    def _build_ui(self):
        self._build_titlebar()

        # main paned layout: left=port panel, right=log
        pane = tk.PanedWindow(self.root, orient="horizontal",
                              bg=BG, sashwidth=4, sashrelief="flat",
                              sashpad=0, bd=0)
        pane.pack(fill="both", expand=True, padx=0, pady=0)

        left  = tk.Frame(pane, bg=BG, width=420)
        right = tk.Frame(pane, bg=BG)
        pane.add(left,  minsize=360)
        pane.add(right, minsize=400)

        self._build_port_panel(left)
        self._build_log_panel(right)
        self._build_statusbar()

    # ── title bar ─────────────────────────────────────────────────────────────
    def _build_titlebar(self):
        bar = tk.Frame(self.root, bg=PANEL,
                       highlightthickness=1, highlightbackground=BORDER)
        bar.pack(fill="x")
        tk.Frame(bar, bg=BLUE_D, height=2).pack(fill="x")

        inner = tk.Frame(bar, bg=PANEL, padx=18, pady=8)
        inner.pack(fill="x")

        left = tk.Frame(inner, bg=PANEL)
        left.pack(side="left")
        tk.Label(left, text="HONEYPOT", font=("Consolas", 15, "bold"),
                 fg=FG, bg=PANEL).pack(side="left")
        tk.Label(left, text="  CONSOLE  ", font=("Consolas", 15),
                 fg=MUTED, bg=PANEL).pack(side="left")
        tk.Label(left, text="v2.0", font=("Consolas", 8),
                 fg=BORDER, bg=PANEL).pack(side="left", pady=(4,0))

        right = tk.Frame(inner, bg=PANEL)
        right.pack(side="right", anchor="e")
        self.clock_lbl = tk.Label(right, text="", font=("Consolas", 8),
                                  fg=MUTED, bg=PANEL)
        self.clock_lbl.pack(anchor="e")
        tk.Label(right, text="⚠ Research use only — never deploy on production",
                 font=("Consolas", 8), fg=RED, bg=PANEL).pack(anchor="e")

    def _update_clock(self):
        self.clock_lbl.config(
            text=datetime.datetime.now().strftime("%Y-%m-%d  %H:%M:%S"))
        self.root.after(1000, self._update_clock)

    # ── LEFT: port panel ──────────────────────────────────────────────────────
    def _build_port_panel(self, parent):
        # top controls
        ctrl = tk.Frame(parent, bg=BG, padx=10, pady=8)
        ctrl.pack(fill="x")

        make_btn(ctrl, "▶ START ALL", GREEN_D, self._start_all,
                 fg=FG, padx=12, pady=5).pack(side="left", padx=(0,5))
        make_btn(ctrl, "■ STOP ALL", RED_D, self._stop_all,
                 fg=FG, padx=12, pady=5).pack(side="left")

        # search
        sf = tk.Frame(ctrl, bg=BG)
        sf.pack(side="right")
        tk.Label(sf, text="🔍", fg=MUTED, bg=BG,
                 font=("Consolas",9)).pack(side="left")
        self.port_search = tk.StringVar()
        self.port_search.trace_add("write", lambda *a: self._filter_ports())
        tk.Entry(sf, textvariable=self.port_search, width=12,
                 font=("Consolas",9), bg=PANEL2, fg=FG,
                 insertbackground=FG, relief="flat", bd=0,
                 highlightthickness=1, highlightbackground=BORDER
                 ).pack(side="left", padx=4)

        # category filter
        cat_frame = tk.Frame(parent, bg=BG, padx=10)
        cat_frame.pack(fill="x")
        tk.Label(cat_frame, text="Filter:", font=("Consolas",8),
                 fg=MUTED, bg=BG).pack(side="left")
        self.cat_var = tk.StringVar(value="All")
        cats = ["All"] + CATEGORIES
        cat_cb = ttk.Combobox(cat_frame, textvariable=self.cat_var,
                              values=cats, width=16,
                              font=("Consolas",8), state="readonly")
        cat_cb.pack(side="left", padx=6)
        cat_cb.bind("<<ComboboxSelected>>", lambda e: self._filter_ports())

        # port list header
        hdr = tk.Frame(parent, bg=PANEL2, padx=10, pady=4)
        hdr.pack(fill="x", pady=(6,0))
        for txt, w in [("PORT",6),("SERVICE",12),("CATEGORY",13),("ACTION",8)]:
            tk.Label(hdr, text=txt, font=("Consolas",8,"bold"),
                     fg=MUTED, bg=PANEL2, width=w, anchor="w").pack(side="left")

        # scrollable port list
        list_outer = tk.Frame(parent, bg=BG)
        list_outer.pack(fill="both", expand=True, pady=(0,0))

        canvas = tk.Canvas(list_outer, bg=BG, bd=0,
                           highlightthickness=0)
        scrollbar = tk.Scrollbar(list_outer, orient="vertical",
                                 command=canvas.yview, bg=PANEL2)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.port_list_frame = tk.Frame(canvas, bg=BG)
        canvas_window = canvas.create_window((0,0), window=self.port_list_frame,
                                              anchor="nw")

        def on_frame_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
        def on_canvas_configure(e):
            canvas.itemconfig(canvas_window, width=e.width)

        self.port_list_frame.bind("<Configure>", on_frame_configure)
        canvas.bind("<Configure>", on_canvas_configure)
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        self._port_canvas    = canvas
        self._all_port_rows  = {}  # port -> row_frame (for filtering)
        self._populate_ports()

        # active instances panel
        act_hdr = tk.Frame(parent, bg=PANEL, padx=10, pady=6,
                           highlightthickness=1, highlightbackground=BORDER)
        act_hdr.pack(fill="x")
        tk.Label(act_hdr, text="ACTIVE LISTENERS", font=("Consolas",9,"bold"),
                 fg=CYAN, bg=PANEL).pack(side="left")
        self.active_count_lbl = tk.Label(act_hdr, text="0 running",
                                         font=("Consolas",8), fg=MUTED, bg=PANEL)
        self.active_count_lbl.pack(side="right")

        self.active_frame = tk.Frame(parent, bg=PANEL2, pady=4)
        self.active_frame.pack(fill="x")
        self.no_active_lbl = tk.Label(self.active_frame,
                                      text="  No active listeners",
                                      font=("Consolas",8), fg=MUTED, bg=PANEL2)
        self.no_active_lbl.pack(anchor="w", padx=10, pady=4)

    def _populate_ports(self):
        for widget in self.port_list_frame.winfo_children():
            widget.destroy()
        self._all_port_rows.clear()

        search = self.port_search.get().lower()
        cat    = self.cat_var.get() if hasattr(self, "cat_var") else "All"

        for i, (port, svc, mod, category, desc) in enumerate(ALL_PORTS):
            if search and search not in str(port) and search not in svc.lower() and search not in desc.lower():
                continue
            if cat != "All" and cat != category:
                continue

            col = CAT_COLORS.get(category, MUTED)
            row_bg = PANEL if i % 2 == 0 else PANEL2

            row = tk.Frame(self.port_list_frame, bg=row_bg,
                           highlightthickness=0)
            row.pack(fill="x")

            # colored left bar
            tk.Frame(row, bg=col, width=3).pack(side="left", fill="y")

            inner = tk.Frame(row, bg=row_bg, padx=6, pady=3)
            inner.pack(side="left", fill="x", expand=True)

            tk.Label(inner, text=str(port), font=("Consolas",9,"bold"),
                     fg=col, bg=row_bg, width=6, anchor="w").pack(side="left")
            tk.Label(inner, text=svc, font=("Consolas",9),
                     fg=FG2, bg=row_bg, width=12, anchor="w").pack(side="left")
            tk.Label(inner, text=category, font=("Consolas",8),
                     fg=MUTED, bg=row_bg, width=13, anchor="w").pack(side="left")

            btn = tk.Button(inner, text="START",
                            font=("Consolas",8,"bold"),
                            bg=GREEN_D, fg=FG,
                            activebackground=GREEN, activeforeground=FG,
                            relief="flat", bd=0, padx=8, pady=2,
                            cursor="hand2",
                            command=lambda p=port, m=mod, s=svc: \
                                self._toggle_port(p, m, s))
            btn.pack(side="left")

            row._port    = port
            row._svc     = svc
            row._mod     = mod
            row._cat     = category
            row._btn     = btn
            row._running = False

            self._all_port_rows[port] = row

    def _filter_ports(self):
        self._populate_ports()

    def _toggle_port(self, port, mod_key, svc_name):
        row = self._all_port_rows.get(port)
        if row and row._running:
            self._stop_port(port)
        else:
            self._start_port(port, mod_key, svc_name)

    def _start_port(self, port, mod_key, svc_name):
        iid = f"{svc_name}_{port}_{uuid.uuid4().hex[:6]}"
        mod = SVC_MODULE.get(mod_key, HTTP)

        inst = PortInstance(port, mod_key, iid)
        self._instances[iid] = inst

        t = threading.Thread(
            target=mod.start,
            kwargs={"port": port, "instance_id": iid},
            daemon=True)
        t.start()

        # update row button
        row = self._all_port_rows.get(port)
        if row:
            row._running = True
            row._iid     = iid
            row._btn.config(text="STOP", bg=RED_D, activebackground=RED)

        self._add_active_row(iid, port, svc_name, mod_key)
        self._refresh_active_count()
        self._log_system(f"Started {svc_name} honeypot on port {port}")

    def _stop_port(self, port):
        row = self._all_port_rows.get(port)
        iid = getattr(row, "_iid", None) if row else None

        if iid and iid in self._instances:
            inst = self._instances[iid]
            mod  = SVC_MODULE.get(inst.module_key, HTTP)
            mod.stop(instance_id=iid)
            del self._instances[iid]

        if row:
            row._running = False
            row._btn.config(text="START", bg=GREEN_D, activebackground=GREEN)

        if iid and iid in self._port_rows:
            self._port_rows[iid].destroy()
            del self._port_rows[iid]

        self._refresh_active_count()
        self._log_system(f"Stopped port {port}")

    def _add_active_row(self, iid, port, svc_name, mod_key):
        # remove no-active label
        self.no_active_lbl.pack_forget()

        col = SVC_COLOR.get(mod_key, MUTED)
        r = tk.Frame(self.active_frame, bg=PANEL2)
        r.pack(fill="x", padx=4, pady=1)

        tk.Frame(r, bg=col, width=3).pack(side="left", fill="y")
        inner = tk.Frame(r, bg=PANEL2, padx=6, pady=3)
        inner.pack(side="left", fill="x", expand=True)

        tk.Label(inner, text=f":{port}", font=("Consolas",9,"bold"),
                 fg=col, bg=PANEL2, width=7, anchor="w").pack(side="left")
        tk.Label(inner, text=svc_name, font=("Consolas",8),
                 fg=FG2, bg=PANEL2, width=12, anchor="w").pack(side="left")

        r._conn_lbl = tk.Label(inner, text="0 conns",
                               font=("Consolas",8), fg=MUTED, bg=PANEL2)
        r._conn_lbl.pack(side="left")

        tk.Button(inner, text="✕",
                  font=("Consolas",8), bg=PANEL2, fg=MUTED,
                  activebackground=RED_D, activeforeground=FG,
                  relief="flat", bd=0, padx=4, pady=1,
                  cursor="hand2",
                  command=lambda p=port: self._stop_port(p)
                  ).pack(side="right", padx=4)

        self._port_rows[iid] = r

    def _refresh_active_count(self):
        n = len(self._instances)
        self.active_count_lbl.config(text=f"{n} running")
        if n == 0:
            self.no_active_lbl.pack(anchor="w", padx=10, pady=4)

    # ── FIXED: cleaned up, no more confusing nested list comprehension ──────
    def _start_all(self):
        """Start every port that isn't already running."""
        for port, svc, mod, cat, desc in ALL_PORTS:
            row = self._all_port_rows.get(port)
            if row and not row._running:
                self._start_port(port, mod, svc)

    def _stop_all(self):
        """Stop every port that is currently running."""
        for port in list(self._all_port_rows.keys()):
            row = self._all_port_rows.get(port)
            if row and row._running:
                self._stop_port(port)

    # ── RIGHT: log panel ──────────────────────────────────────────────────────
    def _build_log_panel(self, parent):
        # tab + search row
        top = tk.Frame(parent, bg=PANEL,
                       highlightthickness=1, highlightbackground=BORDER)
        top.pack(fill="x")

        tabs = tk.Frame(top, bg=PANEL)
        tabs.pack(side="left")
        for label in ("ALL", "FTP", "SSH", "HTTP"):
            col = SVC_COLOR.get(label, FG)
            tk.Radiobutton(
                tabs, text=f"  {label}  ",
                variable=self._active_tab, value=label,
                font=("Consolas",9,"bold"),
                fg=MUTED, bg=PANEL,
                selectcolor=PANEL2,
                activebackground=PANEL, activeforeground=col,
                indicatoron=False, relief="flat", bd=0,
                padx=4, pady=8, cursor="hand2",
                command=lambda l=label: self._switch_tab(l)
            ).pack(side="left")

        # search
        sf = tk.Frame(top, bg=PANEL, padx=8)
        sf.pack(side="right", pady=4)
        tk.Label(sf, text="🔍", fg=MUTED, bg=PANEL,
                 font=("Consolas",9)).pack(side="left")
        self.log_search_var = tk.StringVar()
        self.log_search_var.trace_add("write", lambda *a: self._redraw_log())
        tk.Entry(sf, textvariable=self.log_search_var, width=16,
                 font=("Consolas",9), bg=BG, fg=FG,
                 insertbackground=FG, relief="flat", bd=0,
                 highlightthickness=1, highlightbackground=BORDER
                 ).pack(side="left", padx=4)

        # control buttons
        ctrl = tk.Frame(parent, bg=BG, padx=8, pady=4)
        ctrl.pack(fill="x")
        make_btn(ctrl, "⬇ Export Log", PANEL, self._export_log,
                 fg=MUTED, padx=10, pady=4).pack(side="left", padx=(0,4))
        make_btn(ctrl, "🗑 Clear", PANEL, self._clear_log,
                 fg=MUTED, padx=10, pady=4).pack(side="left")

        self.log_count_lbl = tk.Label(ctrl, text="0 events",
                                      font=("Consolas",8), fg=MUTED, bg=BG)
        self.log_count_lbl.pack(side="right", padx=8)

        # log box
        lf = tk.Frame(parent, bg=PANEL,
                      highlightthickness=1, highlightbackground=BORDER)
        lf.pack(fill="both", expand=True, padx=8, pady=(0,4))

        self.log_box = scrolledtext.ScrolledText(
            lf, font=("Consolas",10),
            bg="#0a0d12", fg=FG2,
            insertbackground=FG,
            relief="flat", bd=0,
            state="disabled",
            wrap="none",
            padx=12, pady=8,
            spacing1=1, spacing3=1)
        self.log_box.pack(fill="both", expand=True)

        for tag, col in LOG_TAG_COLOR.items():
            self.log_box.tag_config(tag, foreground=col)
        self.log_box.tag_config("LOGIN_BG",
                                background="#2a2200",
                                foreground=YELLOW,
                                font=("Consolas",10,"bold"))
        self.log_box.tag_config("ERROR_BG",
                                background="#220808",
                                foreground=RED,
                                font=("Consolas",10,"bold"))

    def _switch_tab(self, label):
        self._active_tab.set(label)
        self._redraw_log()

    def _redraw_log(self):
        active = self._active_tab.get()
        search = self.log_search_var.get().lower()
        self.log_box.config(state="normal")
        self.log_box.delete("1.0", "end")
        for svc, tag, line in self._log_entries:
            if active != "ALL" and svc != active:
                continue
            if search and search not in line.lower():
                continue
            dtag = "LOGIN_BG" if tag=="LOGIN" else ("ERROR_BG" if tag=="ERROR" else tag)
            self.log_box.insert("end", line+"\n", dtag)
        self.log_box.see("end")
        self.log_box.config(state="disabled")

    def _clear_log(self):
        self._log_entries.clear()
        self.log_box.config(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.config(state="disabled")
        self.log_count_lbl.config(text="0 events")

    def _export_log(self):
        import tkinter.filedialog as fd
        path = fd.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text","*.txt"),("All","*.*")],
            initialfile=f"honeypot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        if not path:
            return
        try:
            with open(path,"w",encoding="utf-8") as f:
                for _,_,line in self._log_entries:
                    f.write(line+"\n")
            messagebox.showinfo("Exported", f"Saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _log_system(self, msg):
        ts  = datetime.datetime.now().strftime("%H:%M:%S")
        txt = f"[{ts}] [SYSTEM] {msg}"
        self._log_entries.append(("SYSTEM","SYSTEM",txt))
        self.log_count_lbl.config(text=f"{len(self._log_entries)} events")
        if self._active_tab.get() == "ALL":
            self.log_box.config(state="normal")
            self.log_box.insert("end", txt+"\n", "SYSTEM")
            self.log_box.see("end")
            self.log_box.config(state="disabled")

    # ── status bar ────────────────────────────────────────────────────────────
    def _build_statusbar(self):
        bar = tk.Frame(self.root, bg=PANEL2, pady=4, padx=14,
                       highlightthickness=1, highlightbackground=BORDER2)
        bar.pack(fill="x", side="bottom")
        self.status_msg = tk.Label(bar, text="Ready — Start any port to begin capturing",
                                   font=("Consolas",8), fg=MUTED, bg=PANEL2)
        self.status_msg.pack(side="left")
        self.status_conns = tk.Label(bar, text="Total: 0 connections",
                                     font=("Consolas",8), fg=MUTED, bg=PANEL2)
        self.status_conns.pack(side="right")

    # ── callbacks ─────────────────────────────────────────────────────────────
    def _wire_callbacks(self):
        FTP.set_log_callback(self._on_log)
        SSH.set_log_callback(self._on_log)
        HTTP.set_log_callback(self._on_log)

    def _on_log(self, service, message):
        self.root.after(0, self._append_log, service, message)

    def _append_log(self, service, message):
        upper = message.upper()
        if "LOGIN ATTEMPT" in upper or "BASICAUTH" in upper or "AUTH PROBE" in upper:
            tag = "LOGIN"
        elif "PROBE" in upper:
            tag = "PROBE"
        elif "BIND ERROR" in upper or "ERROR" in upper:
            tag = "ERROR"
        elif "CLOSED" in upper:
            tag = "CLOSED"
        elif "LISTENING" in upper or "STOPPED" in upper or "STOPPING" in upper:
            tag = "SYSTEM"
        else:
            tag = service

        self._log_entries.append((service, tag, message))
        self.log_count_lbl.config(text=f"{len(self._log_entries)} events")

        if "NEW CONNECTION" in upper or "CONNECTION FROM" in upper:
            self._total_conns += 1
            self.status_conns.config(text=f"Total: {self._total_conns} connections")
            # update active row conn count
            for iid, inst in self._instances.items():
                if inst.module_key == service or service in ("FTP","SSH","HTTP"):
                    inst.conn_count += 1
                    r = self._port_rows.get(iid)
                    if r:
                        r._conn_lbl.config(text=f"{inst.conn_count} conns")
                    break

        if tag == "LOGIN":
            self.status_msg.config(text=f"⚡ Credential captured on {service}!", fg=YELLOW)
        elif tag == "ERROR":
            self.status_msg.config(text=f"⚠ Port error on {service}", fg=RED)

        active = self._active_tab.get()
        search = self.log_search_var.get().lower()
        if active in ("ALL", service):
            if not search or search in message.lower():
                dtag = "LOGIN_BG" if tag=="LOGIN" else ("ERROR_BG" if tag=="ERROR" else tag)
                self.log_box.config(state="normal")
                self.log_box.insert("end", message+"\n", dtag)
                self.log_box.see("end")
                self.log_box.config(state="disabled")

    def _tick(self):
        self.root.after(2000, self._tick)


def main():
    root = tk.Tk()
    try:
        root.iconbitmap(default="")
    except:
        pass
    HoneypotGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()