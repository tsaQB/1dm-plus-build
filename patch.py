#!/usr/bin/env python3
"""
1DM+ 18.2 — license-link bypass (offline, no Google account needed)

Mechanism in the APK:
  LinkApp.isLinked() -> cached "LINKED" state, set only after Play licensing handshake
  AppLinker.isLinked()/link() -> delegates to AppTypee (LinkApp instance)
  MainActivity.ۦۤۢ(Z)V    -> shows "not licensed / buy" dialog when Z == false

Patches:
  A) LinkApp.isLinked()Z  -> always true  (chain reports LINKED, no remote call)
  B) MainActivity.ۦۤۢ(Z)V -> no-op        (no dialog even if something calls it with false)
"""
import re
import sys
from pathlib import Path

LINKAPP = "smali/com/google/android/vending/licensing/LinkApp.smali"
MAINACT = "smali_classes3/idm/internet/download/manager/MainActivity.smali"

NEW_ISLINKED = """.method public isLinked()Z
    .locals 1

    const/4 v0, 0x1

    return v0
.end method
"""

NEW_DIALOG = """.method public final synthetic ۦۤۢ(Z)V
    .locals 0

    return-void
.end method
"""


def patch_method(text, signature, replacement, label):
    idx = text.find(signature)
    if idx == -1:
        raise SystemExit(f"[FAIL] signature not found: {label}")
    end = text.find(".end method", idx)
    if end == -1:
        raise SystemExit(f"[FAIL] no .end method for {label}")
    end += len(".end method")
    old = text[idx:end]
    out = text[:idx] + replacement.rstrip("\n") + text[end:]
    print(f"[OK] {label}: {len(old)} bytes -> {len(replacement)} bytes")
    return out


def main(root="dec"):
    root = Path(root)

    p = root / LINKAPP
    src = p.read_text(encoding="utf-8")
    src = patch_method(src, ".method public isLinked()Z", NEW_ISLINKED, "LinkApp.isLinked()Z")
    p.write_text(src, encoding="utf-8")

    p = root / MAINACT
    src = p.read_text(encoding="utf-8")
    src = patch_method(src, ".method public final synthetic ۦۤۢ(Z)V", NEW_DIALOG, "MainActivity.licenseDialog(Z)V")
    p.write_text(src, encoding="utf-8")
    print("[DONE] patches applied")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "dec")
