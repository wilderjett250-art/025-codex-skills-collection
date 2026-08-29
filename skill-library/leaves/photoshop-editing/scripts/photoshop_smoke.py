from pathlib import Path

import win32com.client


OUT_DIR = Path(r"E:\workproject\photoshop_workspace\output")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    png_path = OUT_DIR / "codex_skill_photoshop_smoke.png"
    psd_path = OUT_DIR / "codex_skill_photoshop_smoke.psd"

    app = win32com.client.Dispatch("Photoshop.Application")
    app.Visible = True
    js = f"""
var doc = app.documents.add(900, 520, 72, "Codex Skill Smoke", NewDocumentMode.RGB, DocumentFill.WHITE);
var bg = new SolidColor();
bg.rgb.red = 32;
bg.rgb.green = 42;
bg.rgb.blue = 58;
app.foregroundColor = bg;
doc.selection.selectAll();
doc.selection.fill(app.foregroundColor);
doc.selection.deselect();

var textLayer = doc.artLayers.add();
textLayer.kind = LayerKind.TEXT;
textLayer.textItem.contents = "Codex Photoshop skill OK";
textLayer.textItem.position = [90, 220];
textLayer.textItem.size = 48;
var white = new SolidColor();
white.rgb.red = 255;
white.rgb.green = 255;
white.rgb.blue = 255;
textLayer.textItem.color = white;

var pngFile = new File("{str(png_path).replace(chr(92), "/")}");
var pngOptions = new PNGSaveOptions();
doc.saveAs(pngFile, pngOptions, true, Extension.LOWERCASE);

var psdFile = new File("{str(psd_path).replace(chr(92), "/")}");
var psdOptions = new PhotoshopSaveOptions();
doc.saveAs(psdFile, psdOptions, true, Extension.LOWERCASE);
doc.close(SaveOptions.DONOTSAVECHANGES);
"""
    app.DoJavaScript(js)

    print(f"Photoshop={app.Version}")
    print(f"PNG={png_path} size={png_path.stat().st_size}")
    print(f"PSD={psd_path} size={psd_path.stat().st_size}")


if __name__ == "__main__":
    main()
