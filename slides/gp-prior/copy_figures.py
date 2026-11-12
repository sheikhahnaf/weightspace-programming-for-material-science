"""Copy the deck's figures from their source (a paper, a report, a results folder) into figures/.

Edit FIGS: source path -> name under figures/. PDFs are rasterized at 300 dpi
with pdftoppm; everything else is copied. deck_lib.norm() then flattens each
placed figure to 8-bit RGB PNG under figures/deck/.
"""
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIG = HERE / "figures"
SRC = HERE.parent / "figures"   # change to the deck's source folder

FIGS = {
    # "ch02/parity_yield.png": "ch02_parity_yield.png",
    # "ch05/hv_panel.pdf": "ch05_hv_panel.png",
}


def main():
    FIG.mkdir(exist_ok=True)
    for src, dst in FIGS.items():
        s, d = SRC / src, FIG / dst
        if s.suffix.lower() == ".pdf":
            subprocess.run(["pdftoppm", "-r", "300", "-png", "-singlefile", str(s), str(d.with_suffix(""))], check=True)
        else:
            shutil.copyfile(s, d)
        print("copied", dst)


if __name__ == "__main__":
    main()
