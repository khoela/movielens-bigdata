import json
import hashlib
from pathlib import Path


# Hàm tính SHA-256 bằng công cụ có sẵn trong Python 3.11
def tinh_sha256(duong_dan):
    with open(duong_dan, "rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest()


# 1. Tính checksum của ZIP nguồn
checksum_zip = tinh_sha256("incoming/ml-25m.zip")

# 2. Tìm các snapshot có manifest
thu_muc_goc = Path("data/raw/movielens25m")

cac_manifest = sorted(
    thu_muc_goc.glob("ingest_date=*/run_*/manifest.json")
)

if len(cac_manifest) < 3:
    raise RuntimeError("Can it nhat 3 snapshot co manifest.")

# Chỉ kiểm tra ba snapshot mới nhất
ba_manifest = cac_manifest[-3:]

checksum_lan_dau = None

# 3. Kiểm tra lần lượt từng snapshot
for file_manifest in ba_manifest:
    print("Dang kiem tra:", file_manifest.parent.name)

    with open(file_manifest, "r", encoding="utf-8") as file:
        manifest = json.load(file)

    if manifest["source_sha256"] != checksum_zip:
        raise RuntimeError("Snapshot khong cung ZIP nguon hien tai.")

    checksum_lan_nay = {}

    for thong_tin in manifest["files"]:
        duong_dan = file_manifest.parent / thong_tin["path"]

        if duong_dan.stat().st_size != thong_tin["bytes"]:
            raise RuntimeError(f"Sai kich thuoc: {duong_dan}")

        checksum = tinh_sha256(duong_dan)

        if checksum != thong_tin["sha256"]:
            raise RuntimeError(f"Sai checksum: {duong_dan}")

        checksum_lan_nay[thong_tin["path"]] = checksum
        print("  PASS:", thong_tin["path"])

    # Lấy snapshot đầu làm mốc so sánh
    if checksum_lan_dau is None:
        checksum_lan_dau = checksum_lan_nay
    elif checksum_lan_nay != checksum_lan_dau:
        raise RuntimeError("Noi dung giua cac snapshot khac nhau.")

print("RERUN CHECK: PASS")