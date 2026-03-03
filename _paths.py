"""Import helper — adds all engine/shared src dirs to sys.path."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
_dirs = [
    ROOT / "engines" / "source" / "src",
    ROOT / "engines" / "normalization" / "src",
    ROOT / "engines" / "normalization" / "src" / "normalizers",
    ROOT / "engines" / "passaging" / "src",
    ROOT / "engines" / "atomization" / "src",
    ROOT / "engines" / "excerpting" / "src",
    ROOT / "engines" / "taxonomy" / "src",
    ROOT / "engines" / "synthesis" / "src",
    ROOT / "shared" / "consensus" / "src",
    ROOT / "shared" / "validation" / "src",
    ROOT / "shared" / "human_gate" / "src",
    ROOT / "shared" / "feedback" / "src",
    ROOT / "gold" / "tools",
]
for d in _dirs:
    s = str(d)
    if s not in sys.path:
        sys.path.insert(0, s)
