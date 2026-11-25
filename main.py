# ═══════════════════════════════════════════════════════════════
# main.py — Nahid H4cks PANEL (localhost web panel)
# চালান:  python main.py   →  http://localhost:8000
# Contact  : Nahid H4cks
# Telegram : https://t.me/NahidH4cks
# YouTube  : https://youtube.com/@NahidH4cksIsBack
# ═══════════════════════════════════════════════════════════════
import base64, collections, json, os, re, secrets, shutil, signal, subprocess, sys, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

# ── File Protection ──
try:
    from integrity_guard import verify_integrity
    verify_integrity()
except SystemExit:
    raise
except Exception as e:
    print("Integrity module error:", e)
    raise SystemExit(1)

BASE = Path(__file__).resolve().parent
ACC_FILE = BASE / "accounts.json"
PORT = int(os.environ.get("PORT", "8000"))
PANEL_PASSWORD = os.environ.get("PANEL_PASSWORD", "")   # সেট করলে panel এ পাসওয়ার্ড লাগবে (user: admin)
PW_FILE = BASE / ".panel_password"
REGIONS = ["BD", "IND", "PK", "SG", "ID", "TH", "VN", "TW", "ME", "BR", "SAC", "CIS", "EU", "US", "LK"]
DEFAULT_ADMIN = "10914152209"
PUBLIC_URL = ""            # public link (tunnel / hosting থেকে পাওয়া)
_tunnel_proc = None
ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]|\x1b\][^\x07]*\x07")

lock = threading.Lock()
proc = None
started_at = 0.0
logs = collections.deque(maxlen=3000)
base_idx = 0      # মোট কত লাইন আগে মুছে গেছে / বাদ পড়েছে
total = 0


def add_log(line):
    global total
    with lock:
        logs.append(line); total += 1


def reader(p):
    for raw in iter(p.stdout.readline, b""):
        s = raw.decode("utf-8", "replace").rstrip("\r\n")
        if "\x1b[H\x1b[2J" in s or "\x1b[2J" in s or "\x1b[3J" in s:   # clear screen
            with lock:
                logs.clear()
        s = ANSI.sub("", s)
        if s.strip() != "":
            add_log(s)
    add_log("⛔ বট বন্ধ হয়েছে (exit code: %s)" % p.wait())


def is_running():
    return proc is not None and proc.poll() is None


def start_bot():
    global proc, started_at
    if is_running():
        return False, "বট আগে থেকেই চালু আছে"
    acc = load_acc()
    if not acc.get("uid") or not acc.get("password"):
        return False, "আগে Accounts পেজে UID ও Password Save করুন"
    env = dict(os.environ, PYTHONUNBUFFERED="1", TERM="xterm",
               NAHID_BOT_UID=acc.get("uid") or "",
               NAHID_BOT_PASSWORD=acc.get("password") or "",
               NAHID_REGION=acc.get("region") or "BD",
               NAHID_ADMIN_UID=acc.get("admin_uid") or DEFAULT_ADMIN)
    proc = subprocess.Popen([sys.executable, "-u", str(BASE / "bot_main.py")], cwd=str(BASE),
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env,
                            start_new_session=True)
    started_at = time.time()
    add_log("▶ বট চালু করা হচ্ছে...")
    threading.Thread(target=reader, args=(proc,), daemon=True).start()
    return True, "চালু হচ্ছে"


def stop_bot(force=False):
    global proc
    if not is_running():
        return False, "বট চালু নেই"
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGKILL if force else signal.SIGTERM)
    except Exception:
        proc.kill()
    try:
        proc.wait(timeout=5)
    except Exception:
        pass
    return True, "বন্ধ করা হয়েছে"


def load_acc():
    try:
        return json.loads(ACC_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


# ── Protected HTML (embedded + base64) ──
_HTML_B64 = """PCFkb2N0eXBlIGh0bWw+CjxodG1sIGxhbmc9ImJuIj4KPGhlYWQ+CjxtZXRhIGNoYXJzZXQ9InV0Zi04Ij4KPG1ldGEgbmFtZT0idmlld3BvcnQiIGNvbnRlbnQ9IndpZHRoPWRldmljZS13aWR0aCxpbml0aWFsLXNjYWxlPTEiPgo8dGl0bGU+TkFISUQgRlJFRSBGSVJFIFRDQiB2MTwvdGl0bGU+CjxsaW5rIGhyZWY9Imh0dHBzOi8vZm9udHMuZ29vZ2xlYXBpcy5jb20vY3NzMj9mYW1pbHk9QmxhY2srT3BzK09uZSZmYW1pbHk9T3JiaXRyb246d2dodEA5MDAmZmFtaWx5PVJ1c3NvK09uZSZkaXNwbGF5PXN3YXAiIHJlbD0ic3R5bGVzaGVldCI+CjxzdHlsZT4KLyogPT09PT09PT09PSBJTlRSTyBTVFlMRVMgPT09PT09PT09PSAqLwoqIHsgbWFyZ2luOiAwOyBwYWRkaW5nOiAwOyBib3gtc2l6aW5nOiBib3JkZXItYm94OyAtd2Via2l0LXRhcC1oaWdobGlnaHQtY29sb3I6IHRyYW5zcGFyZW50OyB9CmJvZHksIGh0bWwgeyB3aWR0aDogMTAwJTsgaGVpZ2h0OiAxMDAlOyBiYWNrZ3JvdW5kLWNvbG9yOiAjMDAwOyBvdmVyZmxvdzogaGlkZGVuOyBmb250LWZhbWlseTogJ09yYml0cm9uJywgc2Fucy1zZXJpZjsgfQoKQGtleWZyYW1lcyByZ2ItbGlnaHRpbmcgewogIDAlIHsgYm9yZGVyLWNvbG9yOiAjZmYwMDAwOyBib3gtc2hhZG93OiAwIDAgMTVweCAjZmYwMDAwOyB9CiAgMzMlIHsgYm9yZGVyLWNvbG9yOiAjMDBmZjAwOyBib3gtc2hhZG93OiAwIDAgMTVweCAjMDBmZjAwOyB9CiAgNjYlIHsgYm9yZGVyLWNvbG9yOiAjMDAwMGZmOyBib3gtc2hhZG93OiAwIDAgMTVweCAjMDAwMGZmOyB9CiAgMTAwJSB7IGJvcmRlci1jb2xvcjogI2ZmMDAwMDsgYm94LXNoYWRvdzogMCAwIDE1cHggI2ZmMDAwMDsgfQp9CgojaW50cm8tc2NyZWVuIHsKICBwb3NpdGlvbjogZml4ZWQ7IHRvcDogMDsgbGVmdDogMDsgd2lkdGg6IDEwMCU7IGhlaWdodDogMTAwJTsKICBiYWNrZ3JvdW5kOiAjMDAwOyBkaXNwbGF5OiBmbGV4OyBmbGV4LWRpcmVjdGlvbjogY29sdW1uOwogIGp1c3RpZnktY29udGVudDogY2VudGVyOyBhbGlnbi1pdGVtczogY2VudGVyOyB6LWluZGV4OiAyMDAwOwogIHRyYW5zaXRpb246IHRyYW5zZm9ybSAwLjhzIGN1YmljLWJlemllcigwLjcsIDAsIDAuMywgMSk7Cn0KLmVtYmVycyB7CiAgcG9zaXRpb246IGFic29sdXRlOyB3aWR0aDogMTAwJTsgaGVpZ2h0OiAxMDAlOwogIGJhY2tncm91bmQ6IHJhZGlhbC1ncmFkaWVudChjaXJjbGUgYXQgY2VudGVyLCAjMWEwMDAwIDAlLCAjMDAwIDgwJSk7CiAgei1pbmRleDogMTsKfQouY3Jvc3NoYWlyIHsKICBwb3NpdGlvbjogYWJzb2x1dGU7IHdpZHRoOiAxMDBweDsgaGVpZ2h0OiAxMDBweDsKICBib3JkZXI6IDJweCBzb2xpZCByZ2JhKDI1NSwgMCwgMCwgMC40KTsgYm9yZGVyLXJhZGl1czogNTAlOwogIGFuaW1hdGlvbjogdGFyZ2V0LWxvY2sgMS41cyBlYXNlLW91dCBmb3J3YXJkczsgb3BhY2l0eTogMDsgei1pbmRleDogMjsKfQpAa2V5ZnJhbWVzIHRhcmdldC1sb2NrIHsKICAwJSB7IHRyYW5zZm9ybTogc2NhbGUoNSk7IG9wYWNpdHk6IDA7IH0KICA4MCUgeyB0cmFuc2Zvcm06IHNjYWxlKDEpOyBvcGFjaXR5OiAxOyBib3JkZXItY29sb3I6ICNmZjAwMDA7IH0KICAxMDAlIHsgdHJhbnNmb3JtOiBzY2FsZSgxLjIpOyBvcGFjaXR5OiAwOyB9Cn0KLnRleHQtYm94IHsgcG9zaXRpb246IHJlbGF0aXZlOyB0ZXh0LWFsaWduOiBjZW50ZXI7IHotaW5kZXg6IDU7IG1hcmdpbi1ib3R0b206IDMwcHg7IH0KLm5hbWUtbmFoaWQgewogIGZvbnQtZmFtaWx5OiAnQmxhY2sgT3BzIE9uZScsIGN1cnNpdmU7IGZvbnQtc2l6ZTogNXJlbTsgY29sb3I6ICNmZmY7CiAgbGV0dGVyLXNwYWNpbmc6IDEwcHg7IHRleHQtdHJhbnNmb3JtOiB1cHBlcmNhc2U7IG9wYWNpdHk6IDA7CiAgYW5pbWF0aW9uOiBzbGFtLW5hbWUgMC41cyBmb3J3YXJkcyAxLjJzLCBnbG93LXB1bHNlIDNzIGluZmluaXRlIGVhc2UtaW4tb3V0IDEuN3M7Cn0KQGtleWZyYW1lcyBzbGFtLW5hbWUgewogIDAlIHsgdHJhbnNmb3JtOiBzY2FsZSg1KTsgb3BhY2l0eTogMDsgZmlsdGVyOiBibHVyKDIwcHgpOyB9CiAgMTAwJSB7IHRyYW5zZm9ybTogc2NhbGUoMSk7IG9wYWNpdHk6IDE7IGZpbHRlcjogYmx1cigwKTsgfQp9CkBrZXlmcmFtZXMgZ2xvdy1wdWxzZSB7CiAgMCUsIDEwMCUgeyB0ZXh0LXNoYWRvdzogNXB4IDVweCAwcHggI2ZmMDAwMDsgfQogIDUwJSB7IHRleHQtc2hhZG93OiA1cHggNXB4IDBweCAjZmYwMDAwLCAwIDAgMjBweCByZ2JhKDI1NSwwLDAsMC42KTsgfQp9Ci5mZi10aXRsZSB7CiAgZm9udC1zaXplOiAxLjhyZW07IGNvbG9yOiAjZmZiZDAwOyBsZXR0ZXItc3BhY2luZzogMTVweDsgbWFyZ2luLXRvcDogMTBweDsKICBvcGFjaXR5OiAwOyBhbmltYXRpb246IHNsaWRlLWluIDAuNXMgZm9yd2FyZHMgMS43czsKfQpAa2V5ZnJhbWVzIHNsaWRlLWluIHsKICBmcm9tIHsgdHJhbnNmb3JtOiB0cmFuc2xhdGVYKC0xMDBweCk7IG9wYWNpdHk6IDA7IH0KICB0byB7IG9wYWNpdHk6IDE7IHRyYW5zZm9ybTogdHJhbnNsYXRlWCgwKTsgfQp9Ci52ZXJzaW9uLXRhZyB7CiAgYmFja2dyb3VuZDogI2ZmMDAwMDsgY29sb3I6IHdoaXRlOyBwYWRkaW5nOiA1cHggMjJweDsgZm9udC1zaXplOiAxcmVtOwogIGRpc3BsYXk6IGlubGluZS1ibG9jazsgbWFyZ2luLXRvcDogMjBweDsKICBjbGlwLXBhdGg6IHBvbHlnb24oMTAlIDAsIDEwMCUgMCwgOTAlIDEwMCUsIDAgMTAwJSk7CiAgb3BhY2l0eTogMDsgYW5pbWF0aW9uOiBmYWRlLXVwIDAuNXMgZm9yd2FyZHMgMi4yczsgZm9udC13ZWlnaHQ6IGJvbGQ7Cn0KQGtleWZyYW1lcyBmYWRlLXVwIHsKICBmcm9tIHsgb3BhY2l0eTogMDsgdHJhbnNmb3JtOiB0cmFuc2xhdGVZKDIwcHgpOyB9CiAgdG8geyBvcGFjaXR5OiAxOyB0cmFuc2Zvcm06IHRyYW5zbGF0ZVkoMCk7IH0KfQojdGFwLXdyYXBwZXIgewogIHBvc2l0aW9uOiByZWxhdGl2ZTsgei1pbmRleDogMTA7IG9wYWNpdHk6IDA7CiAgYW5pbWF0aW9uOiBmYWRlSW5CdG4gMC44cyBmb3J3YXJkcyAzczsgY3Vyc29yOiBwb2ludGVyOyBtYXJnaW4tdG9wOiA0MHB4Owp9CkBrZXlmcmFtZXMgZmFkZUluQnRuIHsKICBmcm9tIHsgb3BhY2l0eTogMDsgdHJhbnNmb3JtOiBzY2FsZSgwLjUpOyB9CiAgdG8geyBvcGFjaXR5OiAxOyB0cmFuc2Zvcm06IHNjYWxlKDEpOyB9Cn0KLmVuZXJneS1idG4gewogIHdpZHRoOiAxNjBweDsgaGVpZ2h0OiAxNjBweDsgZGlzcGxheTogZmxleDsganVzdGlmeS1jb250ZW50OiBjZW50ZXI7IGFsaWduLWl0ZW1zOiBjZW50ZXI7IHBvc2l0aW9uOiByZWxhdGl2ZTsKfQoucmluZy1vdXRlciB7CiAgcG9zaXRpb246IGFic29sdXRlOyB3aWR0aDogMTAwJTsgaGVpZ2h0OiAxMDAlOwogIGJvcmRlcjogNHB4IHNvbGlkICNmZmY7IGJvcmRlci1yYWRpdXM6IDUwJTsKICBhbmltYXRpb246IHNwaW4gMnMgbGluZWFyIGluZmluaXRlLCByZ2ItbGlnaHRpbmcgM3MgbGluZWFyIGluZmluaXRlOwp9Ci5yaW5nLWlubmVyIHsKICBwb3NpdGlvbjogYWJzb2x1dGU7IHdpZHRoOiA4MCU7IGhlaWdodDogODAlOwogIGJvcmRlcjogM3B4IHNvbGlkICNmZmY7IGJvcmRlci1yYWRpdXM6IDUwJTsKICBhbmltYXRpb246IHNwaW4tcmV2ZXJzZSAxLjVzIGxpbmVhciBpbmZpbml0ZSwgcmdiLWxpZ2h0aW5nIDNzIGxpbmVhciBpbmZpbml0ZSByZXZlcnNlOwp9Ci5jb3JlIHsKICB3aWR0aDogNjUlOyBoZWlnaHQ6IDY1JTsgYmFja2dyb3VuZDogIzAwMDsgYm9yZGVyLXJhZGl1czogNTAlOwogIGRpc3BsYXk6IGZsZXg7IGp1c3RpZnktY29udGVudDogY2VudGVyOyBhbGlnbi1pdGVtczogY2VudGVyOwogIGJvcmRlcjogMXB4IHNvbGlkICNmZmY7IGFuaW1hdGlvbjogcHVsc2UgMXMgaW5maW5pdGUgYWx0ZXJuYXRlLCByZ2ItbGlnaHRpbmcgM3MgbGluZWFyIGluZmluaXRlOwp9Ci50YXAtdGV4dCB7IGNvbG9yOiAjZmZmOyBmb250LXNpemU6IDE0cHg7IGZvbnQtZmFtaWx5OiAnUnVzc28gT25lJzsgdGV4dC1hbGlnbjogY2VudGVyOyB9CkBrZXlmcmFtZXMgc3BpbiB7IGZyb20geyB0cmFuc2Zvcm06IHJvdGF0ZSgwZGVnKTsgfSB0byB7IHRyYW5zZm9ybTogcm90YXRlKDM2MGRlZyk7IH0gfQpAa2V5ZnJhbWVzIHNwaW4tcmV2ZXJzZSB7IGZyb20geyB0cmFuc2Zvcm06IHJvdGF0ZSgzNjBkZWcpOyB9IHRvIHsgdHJhbnNmb3JtOiByb3RhdGUoMGRlZyk7IH0gfQpAa2V5ZnJhbWVzIHB1bHNlIHsgZnJvbSB7IHRyYW5zZm9ybTogc2NhbGUoMC45NSk7IH0gdG8geyB0cmFuc2Zvcm06IHNjYWxlKDEuMDUpOyB9IH0KCi8qID09PT09PT09PT0gUEFORUwgU1RZTEVTID09PT09PT09PT0gKi8KI3BhbmVsLXdyYXBwZXIgeyBkaXNwbGF5OiBub25lOyB3aWR0aDogMTAwJTsgaGVpZ2h0OiAxMDAlOyBvdmVyZmxvdzogYXV0bzsgYmFja2dyb3VuZDogIzA1MDUwNTsgfQo6cm9vdHstLWJnOiMwNTA1MDU7LS1jYXJkOiMxMTExMTM7LS1saW5lOiMyNjI2MmI7LS1vcjojZWE1ODBjOy0tdHg6I2YzZjNmMzstLW11dDojOGI4Yjk0Oy0tZ3I6IzIyYzU1ZTstLXJkOiNlZjQ0NDR9CiNwYW5lbC13cmFwcGVyICp7Ym94LXNpemluZzpib3JkZXItYm94fQojcGFuZWwtd3JhcHBlciBib2R5LCAjcGFuZWwtd3JhcHBlciB7bWFyZ2luOjA7YmFja2dyb3VuZDp2YXIoLS1iZyk7Y29sb3I6dmFyKC0tdHgpO2ZvbnQtZmFtaWx5OnN5c3RlbS11aSxzYW5zLXNlcmlmfQojcGFuZWwtd3JhcHBlciBoZWFkZXJ7ZGlzcGxheTpmbGV4O2FsaWduLWl0ZW1zOmNlbnRlcjtnYXA6MTRweDtwYWRkaW5nOjE2cHggMjBweDtiYWNrZ3JvdW5kOiMwYzBjMGQ7Ym9yZGVyLWJvdHRvbToxcHggc29saWQgdmFyKC0tbGluZSl9CiNwYW5lbC13cmFwcGVyICNidXJnZXJ7YmFja2dyb3VuZDpub25lO2JvcmRlcjowO2NvbG9yOnZhcigtLW9yKTtmb250LXNpemU6MjhweDtjdXJzb3I6cG9pbnRlcn0KI3BhbmVsLXdyYXBwZXIgaDF7Zm9udC1zaXplOjIwcHg7bWFyZ2luOjA7ZmxleDoxO3RleHQtdHJhbnNmb3JtOnVwcGVyY2FzZX0KI3BhbmVsLXdyYXBwZXIgLmJhZGdle2JvcmRlcjoxcHggc29saWQgdmFyKC0tb3IpO2NvbG9yOnZhcigtLW9yKTtwYWRkaW5nOjhweCAxNHB4O2JvcmRlci1yYWRpdXM6MTJweDtmb250LXNpemU6MTJweDtmb250LXdlaWdodDo3MDA7bGV0dGVyLXNwYWNpbmc6MXB4fQojcGFuZWwtd3JhcHBlciBuYXZ7cG9zaXRpb246Zml4ZWQ7aW5zZXQ6MCBhdXRvIDAgMDt3aWR0aDoyNjBweDtiYWNrZ3JvdW5kOiMwZTBlMTA7Ym9yZGVyLXJpZ2h0OjJweCBzb2xpZCB2YXIoLS1vcik7cGFkZGluZzoyMHB4O3RyYW5zZm9ybTp0cmFuc2xhdGVYKC0xMDUlKTt0cmFuc2l0aW9uOi4yNXM7ei1pbmRleDo1fQojcGFuZWwtd3JhcHBlciBuYXYub3Blbnt0cmFuc2Zvcm06bm9uZX0KI3BhbmVsLXdyYXBwZXIgbmF2IGgye21hcmdpbjowIDAgMjRweDtmb250LXNpemU6MjBweH0KI3BhbmVsLXdyYXBwZXIgbmF2IGF7ZGlzcGxheTpibG9jaztwYWRkaW5nOjE0cHg7Ym9yZGVyLXJhZGl1czoxMnB4O2NvbG9yOnZhcigtLW11dCk7Y3Vyc29yOnBvaW50ZXI7bWFyZ2luLWJvdHRvbTo4cHh9CiNwYW5lbC13cmFwcGVyIG5hdiBhLm9ue2JhY2tncm91bmQ6IzJhMWExMDtjb2xvcjp2YXIoLS1vcik7Ym9yZGVyLWxlZnQ6M3B4IHNvbGlkIHZhcigtLW9yKX0KI3BhbmVsLXdyYXBwZXIgbWFpbntwYWRkaW5nOjIwcHg7bWF4LXdpZHRoOjcyMHB4O21hcmdpbjphdXRvfQojcGFuZWwtd3JhcHBlciAuY2FyZHtiYWNrZ3JvdW5kOnZhcigtLWNhcmQpO2JvcmRlcjoxcHggc29saWQgdmFyKC0tbGluZSk7Ym9yZGVyLXJhZGl1czoxOHB4O3BhZGRpbmc6MjBweDttYXJnaW4tYm90dG9tOjE2cHh9CiNwYW5lbC13cmFwcGVyIC5jYXJkIHNtYWxse2NvbG9yOnZhcigtLW11dCk7bGV0dGVyLXNwYWNpbmc6MnB4O2ZvbnQtd2VpZ2h0OjcwMDtmb250LXNpemU6MTJweH0KI3BhbmVsLXdyYXBwZXIgLmJpZ3tmb250LXNpemU6MjZweDtmb250LXdlaWdodDo3MDA7bWFyZ2luLXRvcDo2cHh9CiNwYW5lbC13cmFwcGVyIC5zdG9we2NvbG9yOnZhcigtLXJkKX0KI3BhbmVsLXdyYXBwZXIgLnJ1bntjb2xvcjp2YXIoLS1ncil9CiNwYW5lbC13cmFwcGVyIC5ncmlke2Rpc3BsYXk6Z3JpZDtncmlkLXRlbXBsYXRlLWNvbHVtbnM6cmVwZWF0KDMsMWZyKTtnYXA6MTBweH0KI3BhbmVsLXdyYXBwZXIgYnV0dG9uLmJ7cGFkZGluZzoxNHB4IDZweDtib3JkZXItcmFkaXVzOjEycHg7Ym9yZGVyOjFweCBzb2xpZCB2YXIoLS1saW5lKTtiYWNrZ3JvdW5kOiMxODE4MWI7Y29sb3I6dmFyKC0tdHgpO2ZvbnQtd2VpZ2h0OjcwMDtjdXJzb3I6cG9pbnRlcjtsZXR0ZXItc3BhY2luZzoxcHh9CiNwYW5lbC13cmFwcGVyIC5iLnN7Ym9yZGVyLWNvbG9yOiMxNDUzMmQ7YmFja2dyb3VuZDojMGMxZjE0O2NvbG9yOiM0YWRlODB9CiNwYW5lbC13cmFwcGVyIC5iLnR7Ym9yZGVyLWNvbG9yOiM0YzFkMWQ7YmFja2dyb3VuZDojMWQwZTBlO2NvbG9yOiNmODcxNzF9CiNwYW5lbC13cmFwcGVyIC5iLnJ7Ym9yZGVyLWNvbG9yOiM3YzJkMTI7YmFja2dyb3VuZDojMWYxMzBkO2NvbG9yOnZhcigtLW9yKX0KI3BhbmVsLXdyYXBwZXIgcHJle2JhY2tncm91bmQ6IzAwMDtjb2xvcjojMjJjNTVlO2JvcmRlcjoxcHggc29saWQgdmFyKC0tbGluZSk7Ym9yZGVyLXJhZGl1czoxMnB4O3BhZGRpbmc6MTJweDtoZWlnaHQ6NDIwcHg7b3ZlcmZsb3c6YXV0bztmb250OjEycHgvMS40IHVpLW1vbm9zcGFjZSxtb25vc3BhY2U7d2hpdGUtc3BhY2U6cHJlLXdyYXA7bWFyZ2luOjE0cHggMCAwfQojcGFuZWwtd3JhcHBlciBpbnB1dHt3aWR0aDoxMDAlO3BhZGRpbmc6MTZweDtib3JkZXItcmFkaXVzOjE0cHg7Ym9yZGVyOjFweCBzb2xpZCB2YXIoLS1saW5lKTtiYWNrZ3JvdW5kOiMwOTA5MGI7Y29sb3I6dmFyKC0tdHgpO2ZvbnQtc2l6ZToxNnB4O21hcmdpbi1ib3R0b206MTRweH0KI3BhbmVsLXdyYXBwZXIgLnNhdmV7d2lkdGg6MTAwJTtwYWRkaW5nOjE2cHg7Ym9yZGVyOjA7Ym9yZGVyLXJhZGl1czoxMnB4O2JhY2tncm91bmQ6dmFyKC0tb3IpO2NvbG9yOiNmZmY7Zm9udC13ZWlnaHQ6ODAwO2xldHRlci1zcGFjaW5nOjJweDtjdXJzb3I6cG9pbnRlcn0KI3BhbmVsLXdyYXBwZXIgI21zZ3ttYXJnaW4tdG9wOjEycHg7Y29sb3I6dmFyKC0tb3IpO21pbi1oZWlnaHQ6MjBweH0KI3BhbmVsLXdyYXBwZXIgLmhpZHtkaXNwbGF5Om5vbmV9CiNwYW5lbC13cmFwcGVyIGZvb3Rlcnt0ZXh0LWFsaWduOmNlbnRlcjtjb2xvcjp2YXIoLS1tdXQpO2ZvbnQtc2l6ZToxM3B4O3BhZGRpbmc6MjBweH0KI3BhbmVsLXdyYXBwZXIgZm9vdGVyIGF7Y29sb3I6dmFyKC0tb3IpO3RleHQtZGVjb3JhdGlvbjpub25lfQo8L3N0eWxlPgo8L2hlYWQ+Cjxib2R5PgoKPCEtLSA9PT09PT09PT09IElOVFJPIFNDUkVFTiA9PT09PT09PT09IC0tPgo8ZGl2IGlkPSJpbnRyby1zY3JlZW4iPgogIDxkaXYgY2xhc3M9ImVtYmVycyI+PC9kaXY+CiAgPGRpdiBjbGFzcz0iY3Jvc3NoYWlyIj48L2Rpdj4KICA8ZGl2IGNsYXNzPSJ0ZXh0LWJveCI+CiAgICA8aDEgY2xhc3M9Im5hbWUtbmFoaWQiPk5BSElEPC9oMT4KICAgIDxoMiBjbGFzcz0iZmYtdGl0bGUiPkZSRUUgRklSRTwvaDI+CiAgICA8ZGl2IGNsYXNzPSJ2ZXJzaW9uLXRhZyI+VENCIHYxPC9kaXY+CiAgPC9kaXY+CiAgPGRpdiBpZD0idGFwLXdyYXBwZXIiIG9uY2xpY2s9InN0YXJ0QXBwKCkiPgogICAgPGRpdiBjbGFzcz0iZW5lcmd5LWJ0biI+CiAgICAgIDxkaXYgY2xhc3M9InJpbmctb3V0ZXIiPjwvZGl2PgogICAgICA8ZGl2IGNsYXNzPSJyaW5nLWlubmVyIj48L2Rpdj4KICAgICAgPGRpdiBjbGFzcz0iY29yZSI+CiAgICAgICAgPGRpdiBjbGFzcz0idGFwLXRleHQiPlRBUCBUTzxicj5TVEFSVDwvZGl2PgogICAgICA8L2Rpdj4KICAgIDwvZGl2PgogIDwvZGl2Pgo8L2Rpdj4KCjwhLS0gPT09PT09PT09PSBQQU5FTCA9PT09PT09PT09IC0tPgo8ZGl2IGlkPSJwYW5lbC13cmFwcGVyIj4KICA8bmF2IGlkPSJuYXYiPgogICAgPGgyPvCfpJYgTmFoaWQgSDRja3MgUEFORUw8L2gyPgogICAgPGEgaWQ9Im4tY3RsIiBjbGFzcz0ib24iIG9uY2xpY2s9ImdvKCdjdGwnKSI+8J+OriBDb250cm9sIFBhbmVsPC9hPgogICAgPGEgaWQ9Im4tYWNjIiBvbmNsaWNrPSJnbygnYWNjJykiPvCfkaUgQWNjb3VudHM8L2E+CiAgPC9uYXY+CiAgPGhlYWRlcj4KICAgIDxidXR0b24gaWQ9ImJ1cmdlciIgb25jbGljaz0ibmF2LmNsYXNzTGlzdC50b2dnbGUoJ29wZW4nKSI+4piwPC9idXR0b24+CiAgICA8aDEgaWQ9InR0bCI+4pqhIENvbnRyb2wgUGFuZWw8L2gxPgogICAgPHNwYW4gY2xhc3M9ImJhZGdlIj5OYWhpZCBINGNrcyBQQU5FTDwvc3Bhbj4KICA8L2hlYWRlcj4KICA8bWFpbj4KICAgIDxzZWN0aW9uIGlkPSJjdGwiPgogICAgICA8ZGl2IGNsYXNzPSJjYXJkIj4KICAgICAgICA8c21hbGw+8J+MjSBQVUJMSUMgTElOSzwvc21hbGw+CiAgICAgICAgPGRpdiBpZD0icHViIiBjbGFzcz0iYmlnIiBzdHlsZT0iZm9udC1zaXplOjE2cHg7d29yZC1icmVhazpicmVhay1hbGwiPuCmpOCniOCmsOCmvyDgprngpprgp43gppvgp4cuLi48L2Rpdj4KICAgICAgICA8YnV0dG9uIGNsYXNzPSJiIHIiIHN0eWxlPSJtYXJnaW4tdG9wOjEycHg7d2lkdGg6MTAwJSIgb25jbGljaz0iY29weVB1YigpIj7wn5OLIENPUFkgTElOSzwvYnV0dG9uPgogICAgICA8L2Rpdj4KICAgICAgPGRpdiBjbGFzcz0iY2FyZCI+CiAgICAgICAgPGRpdiBzdHlsZT0iZGlzcGxheTpmbGV4O2p1c3RpZnktY29udGVudDpzcGFjZS1iZXR3ZWVuO2FsaWduLWl0ZW1zOmNlbnRlciI+CiAgICAgICAgICA8ZGl2PgogICAgICAgICAgICA8c21hbGw+Qk9UIFNUQVRVUzwvc21hbGw+CiAgICAgICAgICAgIDxkaXYgaWQ9InN0IiBjbGFzcz0iYmlnIHN0b3AiPlNUT1BQRUQ8L2Rpdj4KICAgICAgICAgIDwvZGl2PgogICAgICAgICAgPGRpdiBzdHlsZT0idGV4dC1hbGlnbjpyaWdodCI+CiAgICAgICAgICAgIDxzbWFsbD5VUFRJTUU8L3NtYWxsPgogICAgICAgICAgICA8ZGl2IGlkPSJ1cCIgY2xhc3M9ImJpZyIgc3R5bGU9ImZvbnQtc2l6ZToxOHB4Ij4waCAwbSAwczwvZGl2PgogICAgICAgICAgPC9kaXY+CiAgICAgICAgPC9kaXY+CiAgICAgICAgPGRpdiBzdHlsZT0ibWFyZ2luLXRvcDoxMnB4Ij4KICAgICAgICAgIDxzbWFsbD5BQ0NPVU5UPC9zbWFsbD4KICAgICAgICAgIDxkaXYgaWQ9IndobyIgc3R5bGU9Im1hcmdpbi10b3A6NHB4O2NvbG9yOnZhcigtLW11dCkiPuKAlDwvZGl2PgogICAgICAgICAgPGRpdiBpZD0iY2ZnIiBzdHlsZT0ibWFyZ2luLXRvcDo0cHg7Zm9udC1zaXplOjEzcHg7Y29sb3I6dmFyKC0tbXV0KSI+PC9kaXY+CiAgICAgICAgPC9kaXY+CiAgICAgIDwvZGl2PgogICAgICA8ZGl2IGNsYXNzPSJjYXJkIj4KICAgICAgICA8c21hbGw+8J+OriBCT1QgT1BFUkFUSU9OUzwvc21hbGw+CiAgICAgICAgPGRpdiBjbGFzcz0iZ3JpZCIgc3R5bGU9Im1hcmdpbi10b3A6MTJweCI+CiAgICAgICAgICA8YnV0dG9uIGNsYXNzPSJiIHMiIG9uY2xpY2s9ImFjdCgnc3RhcnQnKSI+4pa2IFNUQVJUPC9idXR0b24+CiAgICAgICAgICA8YnV0dG9uIGNsYXNzPSJiIHQiIG9uY2xpY2s9ImFjdCgnc3RvcCcpIj7ilqAgU1RPUDwvYnV0dG9uPgogICAgICAgICAgPGJ1dHRvbiBjbGFzcz0iYiByIiBvbmNsaWNrPSJhY3QoJ3Jlc3RhcnQnKSI+8J+UhCBSRVNUQVJUPC9idXR0b24+CiAgICAgICAgICA8YnV0dG9uIGNsYXNzPSJiIHQiIG9uY2xpY2s9ImFjdCgna2lsbCcpIj7im5QgRk9SQ0UgS0lMTDwvYnV0dG9uPgogICAgICAgICAgPGJ1dHRvbiBjbGFzcz0iYiIgb25jbGljaz0iYWN0KCdjbGVhcicpIj7wn5eRIENMRUFSPC9idXR0b24+CiAgICAgICAgICA8YnV0dG9uIGNsYXNzPSJiIiBvbmNsaWNrPSJhdXRvPSFhdXRvOyQoJ21zZzInKS50ZXh0Q29udGVudD1hdXRvPyfihpUgU0NST0xMIE9OJzon4oaVIFNDUk9MTCBPRkYnIj7ihpUgU0NST0xMPC9idXR0b24+CiAgICAgICAgPC9kaXY+CiAgICAgICAgPGRpdiBpZD0ibXNnMiIgc3R5bGU9Im1hcmdpbi10b3A6MTBweDtjb2xvcjp2YXIoLS1vcik7bWluLWhlaWdodDoxOHB4Ij48L2Rpdj4KICAgICAgICA8cHJlIGlkPSJjb24iPkNvbnNvbGUgSW5pdGlhbGl6ZWQuLi48L3ByZT4KICAgICAgPC9kaXY+CiAgICA8L3NlY3Rpb24+CiAgICA8c2VjdGlvbiBpZD0iYWNjIiBjbGFzcz0iaGlkIj4KICAgICAgPGRpdiBjbGFzcz0iY2FyZCI+CiAgICAgICAgPHNtYWxsPkFDQ09VTlQgU0VUVVA8L3NtYWxsPgogICAgICAgIDxpbnB1dCBpZD0ibmljayIgcGxhY2Vob2xkZXI9Ik5pY2tuYW1lIChvcHRpb25hbCkiPgogICAgICAgIDxpbnB1dCBpZD0idWlkIiBwbGFjZWhvbGRlcj0iVUlEIj4KICAgICAgICA8aW5wdXQgaWQ9InB3IiB0eXBlPSJwYXNzd29yZCIgcGxhY2Vob2xkZXI9IlBhc3N3b3JkIj4KICAgICAgICA8aW5wdXQgaWQ9ImFkbWluIiBwbGFjZWhvbGRlcj0iQWRtaW4gVUlEIj4KICAgICAgICA8c2VsZWN0IGlkPSJyZWdpb24iIHN0eWxlPSJ3aWR0aDoxMDAlO3BhZGRpbmc6MTZweDtib3JkZXItcmFkaXVzOjE0cHg7Ym9yZGVyOjFweCBzb2xpZCB2YXIoLS1saW5lKTtiYWNrZ3JvdW5kOiMwOTA5MGI7Y29sb3I6dmFyKC0tdHgpO2ZvbnQtc2l6ZToxNnB4O21hcmdpbi1ib3R0b206MTRweCI+CiAgICAgICAgICA8b3B0aW9uIHZhbHVlPSIiPvCfjI0gUkVHSU9OIOCmuOCmv+CmsuCnh+CmleCnjeCmnyDgppXgprDgp4Hgpqg8L29wdGlvbj4KICAgICAgICA8L3NlbGVjdD4KICAgICAgICA8YnV0dG9uIGNsYXNzPSJzYXZlIiBvbmNsaWNrPSJzYXZlKCkiPlNBVkUgQ09ORklHVVJBVElPTjwvYnV0dG9uPgogICAgICAgIDxkaXYgaWQ9Im1zZyI+PC9kaXY+CiAgICAgIDwvZGl2PgogICAgPC9zZWN0aW9uPgogIDwvbWFpbj4KICA8Zm9vdGVyPmJ5IDxiPk5haGlkIEg0Y2tzPC9iPiDCtyA8YSBocmVmPSJodHRwczovL3QubWUvTmFoaWRINGNrcyIgdGFyZ2V0PSJfYmxhbmsiPkBOYWhpZEg0Y2tzPC9hPiDCtyA8YSBocmVmPSJodHRwczovL3QubWUvbmFoaWRoNGNrcyIgdGFyZ2V0PSJfYmxhbmsiPkBuYWhpZGg0Y2tzPC9hPiDCtyA8YSBocmVmPSJodHRwczovL3lvdXR1YmUuY29tL0BOYWhpZEg0Y2tzSXNCYWNrIiB0YXJnZXQ9Il9ibGFuayI+WW91VHViZTwvYT48L2Zvb3Rlcj4KPC9kaXY+Cgo8YXVkaW8gaWQ9ImJnLW11c2ljIiBsb29wPgogIDxzb3VyY2Ugc3JjPSJodHRwczovL2ltYWdlMnVybC5jb20vcjIvZGVmYXVsdC9hdWRpby8xNzcwMzgwMTg2MzcwLTc4OTFiNTVlLWU0MDEtNDE4YS1iOWFjLTc5OTI2ZDZlZGRhZC5tcDMiIHR5cGU9ImF1ZGlvL21wZWciPgo8L2F1ZGlvPgoKPHNjcmlwdD4KY29uc3QgbXVzaWMgPSBkb2N1bWVudC5nZXRFbGVtZW50QnlJZCgnYmctbXVzaWMnKTsKY29uc3QgaW50cm8gPSBkb2N1bWVudC5nZXRFbGVtZW50QnlJZCgnaW50cm8tc2NyZWVuJyk7CmNvbnN0IHBhbmVsID0gZG9jdW1lbnQuZ2V0RWxlbWVudEJ5SWQoJ3BhbmVsLXdyYXBwZXInKTsKCmZ1bmN0aW9uIHN0YXJ0QXBwKCkgewogIG11c2ljLnBsYXkoKS5jYXRjaChlID0+IGNvbnNvbGUubG9nKCJBdWRpbyBFcnJvciIpKTsKICBpbnRyby5zdHlsZS50cmFuc2Zvcm0gPSAndHJhbnNsYXRlWSgtMTAwJSknOwogIHNldFRpbWVvdXQoKCkgPT4gewogICAgaW50cm8uc3R5bGUuZGlzcGxheSA9ICdub25lJzsKICAgIHBhbmVsLnN0eWxlLmRpc3BsYXkgPSAnYmxvY2snOwogICAgZG9jdW1lbnQuYm9keS5zdHlsZS5vdmVyZmxvdyA9ICdhdXRvJzsKICB9LCA4MDApOwp9CgovLyA9PT09PT09PT09IE9SSUdJTkFMIFBBTkVMIEpTID09PT09PT09PT0KY29uc3QgJCA9IGkgPT4gZG9jdW1lbnQuZ2V0RWxlbWVudEJ5SWQoaSk7CmxldCBuZXh0ID0gMCwgYXV0byA9IHRydWU7CgpmdW5jdGlvbiBnbyhwKSB7CiAgZm9yIChjb25zdCB4IG9mIFsnY3RsJywgJ2FjYyddKSB7CiAgICAkKHgpLmNsYXNzTGlzdC50b2dnbGUoJ2hpZCcsIHggIT09IHApOwogICAgJCgnbi0nICsgeCkuY2xhc3NMaXN0LnRvZ2dsZSgnb24nLCB4ID09PSBwKTsKICB9CiAgJCgndHRsJykudGV4dENvbnRlbnQgPSBwID09PSAnY3RsJyA/ICfimqEgQ29udHJvbCBQYW5lbCcgOiAn4pqhIEFjY291bnRzJzsKICAkKCduYXYnKS5jbGFzc0xpc3QucmVtb3ZlKCdvcGVuJyk7Cn0KCmFzeW5jIGZ1bmN0aW9uIGFwaShwLCBiKSB7CiAgY29uc3QgciA9IGF3YWl0IGZldGNoKCcvYXBpLycgKyBwLCBiID8gewogICAgbWV0aG9kOiAnUE9TVCcsCiAgICBoZWFkZXJzOiB7ICdDb250ZW50LVR5cGUnOiAnYXBwbGljYXRpb24vanNvbicgfSwKICAgIGJvZHk6IEpTT04uc3RyaW5naWZ5KGIpCiAgfSA6IHsgbWV0aG9kOiAnUE9TVCcsIGJvZHk6ICd7fScgfSk7CiAgcmV0dXJuIHIuanNvbigpOwp9Cgphc3luYyBmdW5jdGlvbiBhY3QoYSkgewogIGNvbnN0IHIgPSBhd2FpdCBhcGkoYSk7CiAgJCgnbXNnMicpLnRleHRDb250ZW50ID0gci5tc2cgfHwgJyc7CiAgaWYgKGEgPT09ICdjbGVhcicpIHsgJCgnY29uJykudGV4dENvbnRlbnQgPSAnJzsgfQogIHRpY2soKTsKfQoKYXN5bmMgZnVuY3Rpb24gc2F2ZSgpIHsKICBjb25zdCByID0gYXdhaXQgYXBpKCdhY2NvdW50JywgewogICAgbmlja25hbWU6ICQoJ25pY2snKS52YWx1ZSwKICAgIHVpZDogJCgndWlkJykudmFsdWUsCiAgICBwYXNzd29yZDogJCgncHcnKS52YWx1ZSwKICAgIHJlZ2lvbjogJCgncmVnaW9uJykudmFsdWUsCiAgICBhZG1pbl91aWQ6ICQoJ2FkbWluJykudmFsdWUKICB9KTsKICAkKCdtc2cnKS50ZXh0Q29udGVudCA9IHIubXNnOwogICQoJ3B3JykudmFsdWUgPSAnJzsKICB0aWNrKCk7Cn0KCmZ1bmN0aW9uIGNvcHlQdWIoKSB7CiAgY29uc3QgdSA9ICQoJ3B1YicpLnRleHRDb250ZW50OwogIGlmICh1LnN0YXJ0c1dpdGgoJ2h0dHAnKSkgewogICAgbmF2aWdhdG9yLmNsaXBib2FyZCAmJiBuYXZpZ2F0b3IuY2xpcGJvYXJkLndyaXRlVGV4dCh1KTsKICAgICQoJ21zZzInKS50ZXh0Q29udGVudCA9ICfinIUg4Kay4Ka/4KaC4KaVIOCmleCmquCmvyDgprngpq/gprzgp4fgppvgp4cnOwogIH0KfQoKZnVuY3Rpb24gZm10KHMpIHsKICByZXR1cm4gTWF0aC5mbG9vcihzIC8gMzYwMCkgKyAnaCAnICsgTWF0aC5mbG9vcihzICUgMzYwMCAvIDYwKSArICdtICcgKyBzICUgNjAgKyAncyc7Cn0KCmFzeW5jIGZ1bmN0aW9uIHRpY2soKSB7CiAgdHJ5IHsKICAgIGNvbnN0IHMgPSBhd2FpdCAoYXdhaXQgZmV0Y2goJy9hcGkvc3RhdHVzJykpLmpzb24oKTsKICAgICQoJ3N0JykudGV4dENvbnRlbnQgPSBzLnJ1bm5pbmcgPyAnUlVOTklORycgOiAnU1RPUFBFRCc7CiAgICAkKCdzdCcpLmNsYXNzTmFtZSA9ICdiaWcgJyArIChzLnJ1bm5pbmcgPyAncnVuJyA6ICdzdG9wJyk7CiAgICAkKCd1cCcpLnRleHRDb250ZW50ID0gZm10KHMudXB0aW1lKTsKICAgICQoJ3dobycpLnRleHRDb250ZW50ID0gcy51aWQgPyAoKHMubmlja25hbWUgfHwgJ0JvdCcpICsgJyDCtyAnICsgcy51aWQpIDogJ+CmleCni+CmqOCniyBhY2NvdW50IOCmuOCnh+CmrSDgpqjgp4fgpocnOwogICAgJCgncHViJykudGV4dENvbnRlbnQgPSBzLnB1YmxpY191cmwgfHwgJ+CmpOCniOCmsOCmvyDgprngpprgp43gppvgp4cuLi4gLyDgprbgp4Hgpqfgp4EgbG9jYWxob3N0JzsKICAgICQoJ2NmZycpLnRleHRDb250ZW50ID0gJ1JlZ2lvbjogJyArIHMucmVnaW9uICsgJyAgwrcgIEFkbWluIFVJRDogJyArIHMuYWRtaW5fdWlkOwogICAgY29uc3QgcmcgPSAkKCdyZWdpb24nKTsKICAgIGlmICghcmcub3B0aW9ucy5sZW5ndGggfHwgcmcub3B0aW9ucy5sZW5ndGggPD0gMSkgewogICAgICBzLnJlZ2lvbnMuZm9yRWFjaChyID0+IHJnLmFkZChuZXcgT3B0aW9uKHIsIHIpKSk7CiAgICAgIHJnLnZhbHVlID0gcy5yZWdpb247CiAgICAgICQoJ2FkbWluJykudmFsdWUgPSBzLmFkbWluX3VpZDsKICAgIH0KICAgIGlmICghJCgndWlkJykudmFsdWUgJiYgcy51aWQpIHsKICAgICAgJCgndWlkJykudmFsdWUgPSBzLnVpZDsKICAgICAgJCgnbmljaycpLnZhbHVlID0gcy5uaWNrbmFtZTsKICAgIH0KICAgIGNvbnN0IGwgPSBhd2FpdCAoYXdhaXQgZmV0Y2goJy9hcGkvbG9ncz9zaW5jZT0nICsgbmV4dCkpLmpzb24oKTsKICAgIGlmIChsLnJlc2V0KSB7IG5leHQgPSAwOyAkKCdjb24nKS50ZXh0Q29udGVudCA9ICcnOyB9CiAgICBpZiAobC5saW5lcy5sZW5ndGgpIHsKICAgICAgY29uc3QgYyA9ICQoJ2NvbicpOwogICAgICBpZiAobmV4dCA9PT0gMCkgYy50ZXh0Q29udGVudCA9ICcnOwogICAgICBjLnRleHRDb250ZW50ICs9IGwubGluZXMuam9pbignXG4nKSArICdcbic7CiAgICAgIGlmIChjLnRleHRDb250ZW50Lmxlbmd0aCA+IDIwMDAwMCkgYy50ZXh0Q29udGVudCA9IGMudGV4dENvbnRlbnQuc2xpY2UoLTEwMDAwMCk7CiAgICAgIGlmIChhdXRvKSBjLnNjcm9sbFRvcCA9IGMuc2Nyb2xsSGVpZ2h0OwogICAgfQogICAgbmV4dCA9IGwubmV4dDsKICB9IGNhdGNoIChlKSB7fQp9CgpzZXRJbnRlcnZhbCh0aWNrLCAxMDAwKTsKdGljaygpOwo8L3NjcmlwdD4KCjxzY3JpcHQ+Ci8vIEJhc2ljIHByb3RlY3Rpb24KZG9jdW1lbnQuYWRkRXZlbnRMaXN0ZW5lcignY29udGV4dG1lbnUnLCBlID0+IGUucHJldmVudERlZmF1bHQoKSk7CmRvY3VtZW50LmFkZEV2ZW50TGlzdGVuZXIoJ2tleWRvd24nLCBlID0+IHsKICBpZiAoZS5rZXkgPT09ICdGMTInIHx8IChlLmN0cmxLZXkgJiYgZS5zaGlmdEtleSAmJiAoZS5rZXkgPT09ICdJJyB8fCBlLmtleSA9PT0gJ0onIHx8IGUua2V5ID09PSAnQycpKSB8fCAoZS5jdHJsS2V5ICYmIGUua2V5ID09PSAnVScpKSB7CiAgICBlLnByZXZlbnREZWZhdWx0KCk7CiAgICByZXR1cm4gZmFsc2U7CiAgfQp9KTsKPC9zY3JpcHQ+CjwvYm9keT4KPC9odG1sPgo="""
HTML = base64.b64decode(_HTML_B64).decode("utf-8")



class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def _auth(self):
        if not PANEL_PASSWORD:
            return True
        h = self.headers.get("Authorization", "")
        try:
            u, _, p = base64.b64decode(h.split(" ", 1)[1]).decode().partition(":")
            if p == PANEL_PASSWORD:
                return True
        except Exception:
            pass
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="Nahid H4cks PANEL"')
        self.end_headers()
        return False

    def _json(self, obj, code=200):
        b = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers(); self.wfile.write(b)

    def do_GET(self):
        if not self._auth(): return
        u = urlparse(self.path)
        if u.path == "/":
            b = HTML.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(b)))
            self.end_headers(); self.wfile.write(b)
        elif u.path == "/api/status":
            a = load_acc()
            self._json({"running": is_running(),
                        "uptime": int(time.time() - started_at) if is_running() else 0,
                        "nickname": a.get("nickname", ""), "uid": a.get("uid", ""),
                        "region": a.get("region") or "BD",
                        "admin_uid": a.get("admin_uid") or DEFAULT_ADMIN,
                        "regions": REGIONS, "public_url": PUBLIC_URL,
                        "has_password": bool(a.get("password"))})
        elif u.path == "/api/logs":
            since = int(parse_qs(u.query).get("since", ["0"])[0])
            with lock:
                first = total - len(logs)
                start = max(since, first)
                out = list(logs)[start - first:]
                self._json({"lines": out, "next": total, "reset": since > total})
        else:
            self.send_response(404); self.end_headers()

    def do_POST(self):
        if not self._auth(): return
        n = int(self.headers.get("Content-Length", 0) or 0)
        try:
            data = json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            data = {}
        p = urlparse(self.path).path
        if p == "/api/start":
            ok, m = start_bot(); self._json({"ok": ok, "msg": m})
        elif p == "/api/stop":
            ok, m = stop_bot(); self._json({"ok": ok, "msg": m})
        elif p == "/api/kill":
            ok, m = stop_bot(True); self._json({"ok": ok, "msg": m})
        elif p == "/api/restart":
            stop_bot(); time.sleep(1); ok, m = start_bot(); self._json({"ok": ok, "msg": m})
        elif p == "/api/clear":
            with lock: logs.clear()
            self._json({"ok": True, "msg": "পরিষ্কার"})
        elif p == "/api/account":
            uid = str(data.get("uid", "")).strip(); pw = str(data.get("password", "")).strip()
            old = load_acc()
            if not pw: pw = old.get("password", "")
            if not uid.isdigit() or not pw:
                return self._json({"ok": False, "msg": "সঠিক UID (শুধু সংখ্যা) ও Password দিন"})
            region = str(data.get("region", "BD")).strip().upper()
            if region not in REGIONS:
                return self._json({"ok": False, "msg": "সঠিক Region সিলেক্ট করুন"})
            admin_uid = str(data.get("admin_uid", "")).strip() or DEFAULT_ADMIN
            if not admin_uid.isdigit():
                return self._json({"ok": False, "msg": "Admin UID শুধু সংখ্যা হতে হবে"})
            ACC_FILE.write_text(json.dumps({"nickname": str(data.get("nickname", "")).strip()[:30],
                                            "uid": uid, "password": pw,
                                            "region": region, "admin_uid": admin_uid}, ensure_ascii=False), encoding="utf-8")
            try: os.chmod(ACC_FILE, 0o600)
            except Exception: pass
            self._json({"ok": True, "msg": "✅ সেভ হয়েছে — এখন Control Panel এ গিয়ে Start চাপুন"})
        else:
            self.send_response(404); self.end_headers()


def _ensure_password():
    """public হলে পাসওয়ার্ড বাধ্যতামূলক — না দিলে নিজে বানিয়ে সেভ করে (user: admin)"""
    global PANEL_PASSWORD
    if PANEL_PASSWORD:
        return PANEL_PASSWORD
    try:
        PANEL_PASSWORD = PW_FILE.read_text().strip()
    except Exception:
        PANEL_PASSWORD = ""
    if not PANEL_PASSWORD:
        PANEL_PASSWORD = secrets.token_urlsafe(9)
        try:
            PW_FILE.write_text(PANEL_PASSWORD); os.chmod(PW_FILE, 0o600)
        except Exception:
            pass
    return PANEL_PASSWORD


def _hosted_url():
    for k in ("PUBLIC_URL", "RENDER_EXTERNAL_URL", "RAILWAY_STATIC_URL", "KOYEB_PUBLIC_DOMAIN"):
        v = os.environ.get(k, "").strip()
        if v:
            return v if v.startswith("http") else "https://" + v
    cs = os.environ.get("CODESPACE_NAME")
    if cs:
        return f"https://{cs}-{PORT}.{os.environ.get('GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN', 'app.github.dev')}"
    return ""


def _find_cloudflared():
    p = shutil.which("cloudflared")
    if p:
        return p
    win = sys.platform.startswith("win")
    local = BASE / ("cloudflared.exe" if win else "cloudflared")
    if local.exists():
        return str(local)
    if sys.platform == "darwin":
        return None
    try:
        import platform, urllib.request
        m = platform.machine().lower()
        arch = "arm64" if m in ("aarch64", "arm64") else ("arm" if m.startswith("arm") else "amd64")
        name = "cloudflared-windows-amd64.exe" if win else f"cloudflared-linux-{arch}"
        add_log("🌐 cloudflared ডাউনলোড হচ্ছে (প্রথমবার)...")
        urllib.request.urlretrieve(f"https://github.com/cloudflare/cloudflared/releases/latest/download/{name}", str(local))
        os.chmod(local, 0o755)
        return str(local)
    except Exception as e:
        print("⚠️  cloudflared ডাউনলোড হয়নি:", e)
        return None


def _watch_url(p, pattern):
    global PUBLIC_URL
    rx = re.compile(pattern)
    for raw in iter(p.stdout.readline, b""):
        m = rx.search(raw.decode("utf-8", "replace"))
        if m and not PUBLIC_URL:
            PUBLIC_URL = m.group(0)
            print("=" * 50)
            print(f"🌍 PUBLIC LINK : {PUBLIC_URL}")
            print(f"🔐 Login       : username = admin  |  password = {PANEL_PASSWORD}")
            print("=" * 50)
            add_log(f"🌍 Public link: {PUBLIC_URL}")


def start_tunnel():
    """localhost এর বদলে public link: cloudflared (না থাকলে ssh → localhost.run)"""
    global _tunnel_proc
    cf = _find_cloudflared()
    attempts = []
    if cf:
        attempts.append(([cf, "tunnel", "--url", f"http://localhost:{PORT}", "--no-autoupdate"],
                         r"https://[a-z0-9-]+\.trycloudflare\.com"))
    if shutil.which("ssh"):
        attempts.append((["ssh", "-o", "StrictHostKeyChecking=no", "-o", "ServerAliveInterval=30",
                          "-R", f"80:localhost:{PORT}", "nokey@localhost.run"], r"https://[a-z0-9]+\.lhr\.life"))
    for cmd, pat in attempts:
        try:
            _tunnel_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except Exception:
            continue
        threading.Thread(target=_watch_url, args=(_tunnel_proc, pat), daemon=True).start()
        for _ in range(40):
            if PUBLIC_URL: return
            if _tunnel_proc.poll() is not None: break
            time.sleep(0.5)
        if PUBLIC_URL: return
        try: _tunnel_proc.kill()
        except Exception: pass
    print("⚠️  Public link তৈরি হয়নি — শুধু http://localhost:%s এ খুলবে।" % PORT)
    print("    (Termux: pkg install cloudflared  |  Mac: brew install cloudflared)")


if __name__ == "__main__":
    hosted = _hosted_url()
    want_tunnel = os.environ.get("NAHID_TUNNEL", "1") != "0" and not hosted
    if hosted:
        PUBLIC_URL = hosted
    if hosted or want_tunnel:
        _ensure_password()          # public হলে পাসওয়ার্ড বাধ্যতামূলক
    srv = ThreadingHTTPServer(("0.0.0.0", PORT), H)
    print("=" * 50)
    print("🤖 Nahid H4cks PANEL চালু হয়েছে")
    print("=" * 50)
    print(f"🌐 Local : http://localhost:{PORT}")
    if hosted:
        print(f"🌍 PUBLIC LINK : {hosted}")
        print(f"🔐 Login       : username = admin  |  password = {PANEL_PASSWORD}")
    elif want_tunnel:
        print("🌍 Public link তৈরি হচ্ছে... (কয়েক সেকেন্ড অপেক্ষা করুন)")
    print("📌 Accounts পেজে Region + Admin UID + UID/Password দিন → SAVE → Start চাপুন")
    print("💬 Contact  : Nahid H4cks")
    print("✈️  Telegram : https://t.me/NahidH4cks")
    print("▶️  YouTube  : https://youtube.com/@NahidH4cksIsBack")
    print("=" * 50)
    if want_tunnel:
        threading.Thread(target=start_tunnel, daemon=True).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        stop_bot(True)
        try: _tunnel_proc.kill()
        except Exception: pass
        print("\nপ্যানেল বন্ধ।")
