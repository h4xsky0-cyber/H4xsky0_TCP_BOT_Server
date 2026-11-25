# ═══════════════════════════════════════════════════════════════
# fix_hash.py — Update integrity hashes after you edit protected files
# Run:  python fix_hash.py
# ═══════════════════════════════════════════════════════════════
import hashlib
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
GUARD = BASE / "integrity_guard.py"

PROTECTED = [
    "bot/Pb2/DEcwHisPErMsG_pb2.py",
    "bot/Pb2/Fo_pb2.py",
    "bot/Pb2/GenWhisperMsg_pb2.py",
    "bot/Pb2/MajoRLoGinrEq_pb2.py",
    "bot/Pb2/MajoRLoGinrEs_pb2.py",
    "bot/Pb2/PorTs_pb2.py",
    "bot/Pb2/Team_msg_pb2.py",
    "bot/Pb2/__init__.py",
    "bot/Pb2/sQ_pb2.py",
    "bot/RemoveFriend_Req_pb2.py",
    "bot/byte.py",
    "bot/emote_menu.json",
    "bot/emotes.json",
    "bot/main.py",
    "bot/thunderFF_pb2.py",
    "bot/xC4.py",
    "bot/xHeaders.py",
    "bot/xP.py",
    "bot_main.py",
    "main.py",
    "panel.html",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    text = GUARD.read_text(encoding="utf-8")
    for rel in PROTECTED:
        p = BASE / rel
        if not p.is_file():
            print(f"⚠ missing: {rel}")
            continue
        h = sha256(p)
        pattern = re.compile(r'("%s":\s*")(?:[0-9a-fA-F]{64}|PLACEHOLDER)(")' % re.escape(rel))
        new_text, n = pattern.subn(r'\g<1>' + h + r'\g<2>', text)
        if n:
            text = new_text
            print(f"✅ {rel}  →  {h[:16]}…")
        else:
            print(f"❌ could not update entry for {rel}")
    GUARD.write_text(text, encoding="utf-8")
    print("\n🔒 integrity_guard.py updated. All files protected.")


if __name__ == "__main__":
    main()
