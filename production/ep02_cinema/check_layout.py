"""Validate every distinct UI state before video encoding (no 3D frame modification)."""
from pathlib import Path
import ast
from PIL import ImageFont
ROOT=Path(__file__).resolve().parent
tree=ast.parse((ROOT/'compose.py').read_text(encoding='utf-8'))
font=ImageFont.truetype(str(ROOT/'fonts/Jua-Regular.ttf'),32)
lines=[]
for n in ast.walk(tree):
    if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='lines' for t in n.targets) and isinstance(n.value,ast.List):
        lines.extend(e.value for e in n.value.elts if isinstance(e,ast.Constant) and isinstance(e.value,str))
for line in lines:
    normalized=line.replace('…','...').replace('“','"').replace('”','"')
    assert font.getlength(normalized)<590,normalized
print(f'{len(lines)} caption lines fit the 590px text area')
