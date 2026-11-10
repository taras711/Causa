"""Web UI module – React + Vite obal pro Causa core."""

from pathlib import Path
import shutil


__all__ = ["ReactViteApp"]


class ReactViteApp:
    """React + Vite web application wrapper for Causa platform."""

    def __init__(self, title: str = "Causa", api_url: str = "http://localhost:8000") -> None:
        self.title = title
        self.api_url = api_url
        self.dev_server_process = None

    def check_node_available(self) -> bool:
        """Check if Node.js/npm is available on the system.

        Returns:
            True if npm is found, False otherwise.
        """
        return shutil.which("npm") is not None

    def start_dev_server(self) -> None:
        """Start the React + Vite development server.

        Raises:
            RuntimeError: If npm is not available or the development server fails to start.
        """
        # Check if Node.js/npm is available
        if not self.check_node_available():
            raise RuntimeError(
                "Node.js/npm is not available on this system. "
                "Please install Node.js (https://nodejs.org/) to use the web UI. "
                "The desktop UI (PyWebView) does not require Node.js."
            )

        import subprocess
        import sys
        import webbrowser
        import time

        web_dir = Path(__file__).parent.parent / "ui" / "web"

        # Check if package.json exists, if not create a basic one
        if not (web_dir / "package.json").exists():
            self._create_basic_package_json(web_dir)

        # Install dependencies if node_modules doesn't exist
        if not (web_dir / "node_modules").exists():
            print("Installing web UI npm dependencies...")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", "npm"],
                check=True,
            )
            result = subprocess.run(
                ["npm", "install"],
                cwd=str(web_dir),
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                raise RuntimeError(f"npm install failed: {result.stderr}")

        # Start the Vite development server
        print("Starting React Vite development server...")
        self.dev_server_process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=str(web_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        # Wait for server to start and open browser
        time.sleep(3)

        # Open the browser to the app
        webbrowser.open(f"{self.api_url}/")

    def stop_dev_server(self) -> None:
        """Stop the React development server."""
        if self.dev_server_process:
            self.dev_server_process.terminate()
            self.dev_server_process.wait()
            self.dev_server_process = None
            print("React development server stopped.")

    def _create_basic_package_json(self, web_dir: Path) -> None:
        """Create a basic package.json for the web UI if one doesn't exist.

        Args:
            web_dir: Path to the web UI directory.
        """
        package_json = {
            "name": "causa-web",
            "version": "1.0.0",
            "private": True,
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "vite build",
                "preview": "vite preview",
            },
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "vite": "^5.0.0",
            },
        }

        with open(web_dir / "package.json", "w") as f:
            import json

            json.dump(package_json, f, indent=2)

        print(f"Created basic package.json at {web_dir / 'package.json'}")
    """React + Vite web application wrapper for Causa platform.

    This module provides the web frontend interface that connects to the
    Causa backend API. It uses React + Vite for the modern web interface.

    The web UI can be started standalone or as part of the desktop application.
    """

    def __init__(self, title: str = "Causa", api_url: str = "http://localhost:8000") -> None:
        self.title = title
        self.api_url = api_url
        self.dev_server_process = None

    def start_dev_server(self) -> None:
        """Start the React + Vite development server.

        Launches the Vite dev server for the web UI. The server will be
        accessible at the configured API URL.

        Raises:
            RuntimeError: If the development server fails to start.
        """
        import subprocess
        import sys
        import webbrowser
        import time

        web_dir = Path(__file__).parent.parent / "ui" / "web"

        # Check if package.json exists, if not create a basic one
        if not (web_dir / "package.json").exists():
            self._create_basic_package_json(web_dir)

        # Install dependencies if node_modules doesn't exist
        if not (web_dir / "node_modules").exists():
            print("Installing web UI npm dependencies...")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", "npm"],
                check=True,
            )
            result = subprocess.run(
                ["npm", "install"],
                cwd=str(web_dir),
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                raise RuntimeError(f"npm install failed: {result.stderr}")

        # Start the Vite development server
        print("Starting React Vite development server...")
        self.dev_server_process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=str(web_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        # Wait for server to start and open browser
        time.sleep(3)

        # Open the browser to the app
        webbrowser.open(f"{self.api_url}/")

    def stop_dev_server(self) -> None:
        """Stop the React development server."""
        if self.dev_server_process:
            self.dev_server_process.terminate()
            self.dev_server_process.wait()
            self.dev_server_process = None
            print("React development server stopped.")

    def _create_basic_package_json(self, web_dir: Path) -> None:
        """Create a basic package.json for the web UI if one doesn't exist.

        Args:
            web_dir: Path to the web UI directory.
        """
        package_json = {
            "name": "causa-web",
            "version": "1.0.0",
            "private": True,
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "vite build",
                "preview": "vite preview",
            },
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "vite": "^5.0.0",
            },
        }

        with open(web_dir / "package.json", "w") as f:
            import json

            json.dump(package_json, f, indent=2)

        print(f"Created basic package.json at {web_dir / 'package.json'}")