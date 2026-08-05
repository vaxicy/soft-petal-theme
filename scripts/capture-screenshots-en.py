#!/usr/bin/env python3
"""Render two English Chrome Web Store screenshots (1280x800) by loading HTML
mockups in headless Chromium and capturing the viewport.

Output:
  store-assets/screenshots/en/soft-petal-ntp.png
  store-assets/screenshots/en/soft-petal-reading.png
"""
import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
MOCKUPS = ROOT / "scripts" / "mockups"
OUT = ROOT / "store-assets" / "screenshots" / "en"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1280, 800


def shoot(page, html_path: Path, out_path: Path):
    page.set_viewport_size({"width": W, "height": H})
    page.goto(html_path.as_uri(), wait_until="networkidle")
    page.wait_for_timeout(400)
    page.screenshot(path=str(out_path), full_page=False, type="png")
    print(f"saved {out_path.relative_to(ROOT)}")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            viewport={"width": W, "height": H},
            device_scale_factor=1,
        )
        page = context.new_page()

        shoot(page, MOCKUPS / "ntp.html",     OUT / "soft-petal-ntp.png")
        shoot(page, MOCKUPS / "reading.html", OUT / "soft-petal-reading.png")

        browser.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"FAIL: {e}", file=sys.stderr)
        sys.exit(1)
