from pathlib import Path
from zipfile import ZipFile
from datetime import datetime, timezone
import json
import hashlib

# 1. Vị trí ZIP đã tải
file_zip = Path("incoming/ml-25m.zip")

# 2. Lấy thời gian UTC để đặt tên lần chạy
thoi_gian = datetime.now(timezone.utc)

ngay = thoi_gian.strftime("%Y-%m-%d")
ma_lan_chay = thoi_gian.strftime("%Y%m%dT%H%M%S%fZ")

# 3. Tạo đường dẫn lưu dữ liệu
thu_muc_raw = (
    Path("data/raw/movielens25m")
    / f"ingest_date={ngay}"
    / f"run_{ma_lan_chay}"
)

# 4. Những file cần lấy từ ZIP
danh_sach_file = [
    "ml-25m/ratings.csv",
    "ml-25m/movies.csv",
    "ml-25m/README.txt"
]

# 5. Mở ZIP và trích xuất từng file
with ZipFile(file_zip, "r") as zip_data:
    for ten_file in danh_sach_file:
        duong_dan = zip_data.extract(ten_file, path=thu_muc_raw)
        print("Da luu:", duong_dan)

print("Hoan thanh trich xuat!")
print("Thu muc raw:", thu_muc_raw)
# 6. Hàm tính SHA-256 của một file
def tinh_sha256(duong_dan):
    bo_bam = hashlib.sha256()

    with open(duong_dan, "rb") as file:
        while True:
            khoi_du_lieu = file.read(1024 * 1024)

            if not khoi_du_lieu:
                break

            bo_bam.update(khoi_du_lieu)

    return bo_bam.hexdigest()


# 7. Thu thập thông tin các file đã trích xuất
thong_tin_cac_file = []

for ten_file in danh_sach_file:
    duong_dan = thu_muc_raw / ten_file
    kich_thuoc = duong_dan.stat().st_size

    if kich_thuoc == 0:
        raise RuntimeError(f"File rong: {ten_file}")

    thong_tin = {
        "path": ten_file,
        "bytes": kich_thuoc,
        "sha256": tinh_sha256(duong_dan)
    }

    thong_tin_cac_file.append(thong_tin)


# 8. Tạo thông tin cho lần nạp
manifest = {
    "dataset": "MovieLens 25M",
    "run_id": ma_lan_chay,
    "ingested_at_utc": thoi_gian.isoformat(),
    "source_url": "https://files.grouplens.org/datasets/movielens/ml-25m.zip",
    "source_zip": str(file_zip),
    "source_sha256": tinh_sha256(file_zip),
    "status": "success",
    "validation_scope": "extracted files exist and are non-empty",
    "files": thong_tin_cac_file
}


# 9. Lưu manifest bên cạnh thư mục dữ liệu
file_manifest = thu_muc_raw / "manifest.json"

with open(file_manifest, "w", encoding="utf-8") as file:
    json.dump(manifest, file, ensure_ascii=False, indent=4)

print("Da tao manifest:", file_manifest)