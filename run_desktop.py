#!/usr/bin/env python
"""Run the PyWebView desktop application."""

import sys
import os

# Add the project root to the path
sys.path.insert(0, r'C:\Users\taras\OneDrive\Plocha\Projects\App\Causa')

from src.ui.desktop import PyWebViewApp

if __name__ == "__main__":
    app = PyWebViewApp(api_url="http://localhost:8000")
    print("Starting Causa Desktop application...")
    app.start()