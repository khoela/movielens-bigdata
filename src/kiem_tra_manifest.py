import json
import hashlib
from pathlib import Path


def tinh_sha256(duong_dan):
    bo_bam = hashlib.sha256()

    with open(duong_dan, "rb") as file:
        while True:
            khoi_du_lieu = file.read(1024 * 1024)

            if not khoi_du_lieu:
                break

            bo_bam.update(khoi_du_lieu)

    return bo_bam.hexdigest()


# 1. Chọn manifest mới nhất
thu_muc_goc = Path("data/raw/movielens25m")

cac_manifest = sorted(
    thu_muc_goc.glob("ingest_date=*/run_*/manifest.json")
)

if len(cac_manifest) == 0:
    raise RuntimeError("Chua tim thay manifest.")

file_manifest = cac_manifest[-1]
thu_muc_run = file_manifest.parent

print("Dang kiem tra:", file_manifest)

# 2. Đọc thông tin đã ghi trong manifest
with open(file_manifest, "r", encoding="utf-8") as file:
    manifest = json.load(file)

# 3. Đối chiếu từng file
for thong_tin in manifest["files"]:
    duong_dan = thu_muc_run / thong_tin["path"]

    if not duong_dan.is_file():
        raise RuntimeError(f"Thieu file: {duong_dan}")

    kich_thuoc = duong_dan.stat().st_size

    if kich_thuoc != thong_tin["bytes"]:
        raise RuntimeError(f"Sai kich thuoc: {duong_dan}")

    checksum = tinh_sha256(duong_dan)

    if checksum != thong_tin["sha256"]:
        raise RuntimeError(f"Noi dung da thay doi: {duong_dan}")

    print("PASS:", thong_tin["path"])

print("MANIFEST CHECK: PASS")