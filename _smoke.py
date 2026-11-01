import sys
import traceback
from pathlib import Path

root = Path(__file__).parent
sys.path.insert(0, str(root / "backend"))

try:
    import main  # noqa: F401
    print("IMPORT_OK")
except Exception:
    traceback.print_exc()
    print("IMPORT_FAIL")
