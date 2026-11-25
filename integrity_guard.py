# ═══════════════════════════════════════════════════════════════
# integrity_guard.py — Full file protection for Nahid H4cks TCP Panel
# সব গুরুত্বপূর্ণ .py / .html / .json এ SHA-256 চেক
# কেউ এডিট করলে বট চলবে না
# হ্যাশ আপডেট:  python fix_hash.py
# ═══════════════════════════════════════════════════════════════
import hashlib
import sys
from pathlib import Path

EXPECTED = {
    "bot/Pb2/DEcwHisPErMsG_pb2.py": "65ee8d2bbe6158bf16867c53b7fc7f8d86780fbf89ef0b4e32a6fddc59dcf9c2",
    "bot/Pb2/Fo_pb2.py": "06dd94209c44d4e5236231730f6f1844f1f69c222900def064dc49ad0dbd4cfe",
    "bot/Pb2/GenWhisperMsg_pb2.py": "396f56694447175067d026e8f70c545245cbba47bf2f713f9b902c1901ec88af",
    "bot/Pb2/MajoRLoGinrEq_pb2.py": "60488e0751c626373ebb1d6ae00d74b779389e658a612c61c14253bbb9427901",
    "bot/Pb2/MajoRLoGinrEs_pb2.py": "e7b5aeabca76035011c40e6f9dc004fc5f2213ad476d31f9ce6d16f454328ae6",
    "bot/Pb2/PorTs_pb2.py": "7f6662bd5d0cb43b4a08e34db5e16c9a7bed94f1d1cef6d8d194893fda0e779e",
    "bot/Pb2/Team_msg_pb2.py": "b9a4bab47439986bc07c0340ecb0f6100a9e825e3ca0c20497b8f907bc33946f",
    "bot/Pb2/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "bot/Pb2/sQ_pb2.py": "09b7a33cba2a768d79f2940469e94fe5842cac444276e3974b9a1aae29d88df8",
    "bot/RemoveFriend_Req_pb2.py": "b25c477ba0e7d03946fa8072de6026c278e06c258360d45c26c58ecb2cd19433",
    "bot/byte.py": "41094367b1970020e0de2912ff81c907703bc4500941568554f038af6bfabdb2",
    "bot/emote_menu.json": "6a69f3bdbc6e383d2a4dbc6ca8d9f73413f28f9c7833a35b4833a3ceb043eda0",
    "bot/emotes.json": "b8573a9071d5578b304081db6f4a4abe7d3b7d874c5eea87c9a04a9b7632424e",
    "bot/main.py": "a8a2e04093e7415aef57267fd179747fd38474031e922ea5f20310cf73f3711c",
    "bot/thunderFF_pb2.py": "a0857d6310fbede9d44a3f36595e9985b6e70ae1b546ee71b746ee30060b4b70",
    "bot/xC4.py": "c29ca4a9b571221e71186db66f48faa8b4c78469f9d818ce73fd76de3b1aec23",
    "bot/xHeaders.py": "e26195e177f584701765ba3e5c05c80f85e114c73f379f14451f6147ac762be7",
    "bot/xP.py": "85a37e542b0f25b15748e2358524d67902c5c3cfe23e829afa76cf8279a23b25",
    "bot_main.py": "d398a483496be64ff8015b160683e3202e30e728726b6a186fba97e659b5e369",
    "main.py": "82adf28a75594b62f4dec66c995e7a1db053b730b0cb03f6d0ca72c865f57d78",
    "panel.html": "6225fc7eb5f2aef5cd3d4f151f70fd0575649fc5c504827e324c64d9f7e082f8",
}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_integrity(folder=None, silent=False):
    """Return True if all protected files match. Exit with error otherwise."""
    base = Path(folder) if folder else Path(__file__).resolve().parent
    failed = []
    for rel, expected in EXPECTED.items():
        if expected == "PLACEHOLDER":
            continue
        p = base / rel
        if not p.is_file():
            failed.append(f"MISSING: {rel}")
            continue
        got = _sha256(p)
        if got != expected:
            failed.append(f"TAMPERED: {rel}")
    if failed:
        if not silent:
            print("╔══════════════════════════════════════════╗")
            print("║   ⛔  FILE PROTECTION FAILED  ⛔         ║")
            print("║   কোড পরিবর্তন / চুরি করা হয়েছে      ║")
            print("╚══════════════════════════════════════════╝")
            for msg in failed:
                print("  →", msg)
            print("\nশুধুমাত্র অফিসিয়াল বিল্ড চালান। Contact: @NahidH4cks")
        sys.exit(1)
    return True


if __name__ == "__main__":
    verify_integrity()
    print("✅ All protected files OK")
