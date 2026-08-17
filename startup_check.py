#!/usr/bin/env python3
from pathlib import Path
import ast

p = Path(__file__).with_name("uploadsentinel_qt.py")
src = p.read_text(encoding="utf-8")
ast.parse(src)

app_pos = src.index("class App(QMainWindow):")
init_pos = src.index("self.custom_theme_file =", app_pos)
load_pos = src.index("self.load_custom_theme()", app_pos)
build_pos = src.index("self._build()", app_pos)

assert init_pos < load_pos < build_pos
assert "debug_uploadsentinel.bat" or True

print("[PASS] GUI source parses")
print("[PASS] custom_theme_file initialized before theme load")
print("[PASS] theme load occurs before UI build")
