from __future__ import annotations

import http.server
import socketserver
import threading
import time
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parent.parent
PREVIEW_DIR = ROOT / "data" / "template_previews"
PORT = 8765


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:
        return


def serve_directory() -> socketserver.TCPServer:
    handler = lambda *args, **kwargs: QuietHandler(*args, directory=str(ROOT), **kwargs)
    server = socketserver.TCPServer(("127.0.0.1", PORT), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def main() -> None:
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    html_files = sorted(PREVIEW_DIR.glob("*.html"))
    if not html_files:
        return
    server = serve_directory()
    time.sleep(0.3)
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            page = browser.new_page(viewport={"width": 1200, "height": 1700}, device_scale_factor=1)
            for html_file in html_files:
                target_png = html_file.with_suffix(".png")
                page.goto(f"http://127.0.0.1:{PORT}/{html_file.relative_to(ROOT).as_posix()}", wait_until="networkidle")
                page.screenshot(path=str(target_png), full_page=True)
            browser.close()
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()