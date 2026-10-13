import sys
from pathlib import Path
import uvicorn

if __name__ == "__main__":
    backend_path = Path(__file__).resolve().parent / "backend"
    sys.path.insert(0, str(backend_path))
    print("==================================================")
    print("  D&D 5e AI Dungeon Master System")
    print("  Deterministic Engine + Ollama Multi-Model DM")
    print("  Local URL:   http://localhost:8000")
    print("  Network URL: http://192.168.1.3:8000")
    print("==================================================")
    uvicorn.run("app.main:app", app_dir=str(backend_path), host="0.0.0.0", port=8000, reload=False)

