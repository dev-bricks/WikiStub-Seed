"""Generiert PWA-Icons aus MetaWiki.ico via Pillow."""
from pathlib import Path
from PIL import Image

ICO = Path(__file__).parent.parent / "MetaWiki.ico"
OUT = Path(__file__).parent / "icons"
OUT.mkdir(exist_ok=True)

ico = Image.open(ICO)
# Grösstes Frame wählen (256x256 RGBA)
best = None
for frame in range(getattr(ico, "n_frames", 1)):
    ico.seek(frame)
    if best is None or ico.size[0] > best.size[0]:
        best = ico.copy().convert("RGBA")

for size in (192, 512):
    img = best.resize((size, size), Image.LANCZOS)
    img.save(OUT / f"Icon-{size}.png", "PNG")
    # Maskable: 10 % safe-zone padding (weiß/transparent)
    canvas = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    pad = int(size * 0.10)
    inner = img.resize((size - 2 * pad, size - 2 * pad), Image.LANCZOS)
    canvas.paste(inner, (pad, pad), inner)
    canvas.save(OUT / f"Icon-maskable-{size}.png", "PNG")
    print(f"[icons] Icon-{size}.png + Icon-maskable-{size}.png")

print("[icons] OK")
