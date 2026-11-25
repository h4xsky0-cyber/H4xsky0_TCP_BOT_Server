# ═══════════════════════════════════════════════════════════════
# bot_main.py — Nahid H4cks  |  Owner: Nahid H4cks
# Run system = V2 Panel  |  Bot core = V1 (rebranded to Nahid H4cks)
# TG: @NahidH4cks  |  Channel: @nahidh4cks  |  YT: @NahidH4cksIsBack
# ═══════════════════════════════════════════════════════════════

import os
import sys
import json
import runpy
from pathlib import Path

BASE = Path(__file__).resolve().parent
BOT_DIR = BASE / "bot"
ACC_FILE = BASE / "accounts.json"

# Load accounts.json if env not fully set (panel should set them)
def ensure_env():
    uid = os.environ.get("NAHID_BOT_UID", "").strip()
    pw  = os.environ.get("NAHID_BOT_PASSWORD", "").strip()
    region = os.environ.get("NAHID_REGION", "").strip()
    admin  = os.environ.get("NAHID_ADMIN_UID", "").strip()
    if (not uid or not pw) and ACC_FILE.is_file():
        try:
            d = json.loads(ACC_FILE.read_text(encoding="utf-8"))
            if not uid:
                uid = str(d.get("uid", "")).strip()
                os.environ["NAHID_BOT_UID"] = uid
            if not pw:
                pw = str(d.get("password", "")).strip()
                os.environ["NAHID_BOT_PASSWORD"] = pw
            if not region:
                region = str(d.get("region", "BD") or "BD").strip().upper()
                os.environ["NAHID_REGION"] = region
            if not admin:
                admin = str(d.get("admin_uid", "") or "").strip()
                if admin:
                    os.environ["NAHID_ADMIN_UID"] = admin
        except Exception:
            pass
    if not os.environ.get("NAHID_REGION"):
        os.environ["NAHID_REGION"] = "BD"

ensure_env()

# Make bot package importable
sys.path.insert(0, str(BOT_DIR))
os.chdir(BOT_DIR)

print(f"▶ Nahid H4cks starting | UID={os.environ.get('NAHID_BOT_UID','?')} | Region={os.environ.get('NAHID_REGION','BD')} | Admin={os.environ.get('NAHID_ADMIN_UID','default')}")

try:
    runpy.run_path(str(BOT_DIR / "main.py"), run_name="__main__")
except KeyboardInterrupt:
    print("\n▌ Bot stopped — Nahid H4cks ▌")
except SystemExit:
    raise
except Exception as e:
    print(f"Bot error: {e}")
    import traceback
    traceback.print_exc()
    raise
