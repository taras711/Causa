"""PyWebView desktop application for Causa platform."""

import asyncio
from pathlib import Path

from pywebview import create_window, App


class PyWebViewApp:
    """Desktop application wrapper using PyWebView."""

    def __init__(self, title: str = "Causa", api_url: str = "http://localhost:8000") -> None:
        self.title = title
        self.api_url = api_url
        self.window = None

    def start(self) -> None:
        """Start the desktop application."""
        webview_dir = Path(__file__).parent.parent / "ui" / "web" / "dist"

        # If dist doesn't exist, start in API-only mode
        if not webview_dir.exists():
            webview_dir = None

        self.window = create_window(
            title=self.title,
            url=self.api_url if webview_dir is None else f"file://{webview_dir / 'index.html'}",
            width=1200,
            height=800,
            resizable=True,
        )

        # Start the event loop
        import webview
        webview.start()

    def stop(self) -> None:
        """Stop the desktop application."""
        if self.window:
            self.window.destroy()


if __name__ == "__main__":
    app = PyWebViewApp()
    app.start()