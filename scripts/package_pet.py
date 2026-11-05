"""Create a verified portable ZIP without silently replacing older packages."""
from pathlib import Path
import argparse
import zipfile
from validate_pet import ROOT, validate

parser=argparse.ArgumentParser()
parser.add_argument("--output",default="dist/emma-pet-2627.zip")
args=parser.parse_args()
report=validate()
if not report["ok"]: raise SystemExit(str(report["errors"]))
target=Path(args.output)
if not target.is_absolute(): target=ROOT/target
files={f"bvb-emma-2627/{name}":(ROOT/"package"/name).read_bytes() for name in ("pet.json","spritesheet.png")}
if target.exists():
    with zipfile.ZipFile(target) as archive:
        if set(archive.namelist()) != set(files) or any(archive.read(name)!=data for name,data in files.items()):
            raise SystemExit("Existing ZIP differs; specify a new --output filename")
else:
    target.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(target,"x",zipfile.ZIP_DEFLATED) as archive:
        for name,data in files.items(): archive.writestr(name,data)
with zipfile.ZipFile(target) as archive:
    if archive.testzip() is not None: raise SystemExit("ZIP CRC check failed")
print(f"Verified {target.name}")
