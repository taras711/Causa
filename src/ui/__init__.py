"""UI vrstva – webové rozhraní (React + TypeScript + Vite) napojené na FastAPI backend.

Živý kód aplikace je v `src/ui/web/`; sestavené statické soubory se servírují přes Nginx
(port 3000, proxy `/api` → backend:8000).
"""