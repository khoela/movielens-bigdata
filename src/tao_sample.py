import csv
import json
from pathlib import Path

# 1. Chọn snapshot mới nhất có manifest
thu_muc_goc = Path("data/raw/movielens25m")

cac_manifest = sorted(
    thu_muc_goc.glob("ingest_date=*/run_*/manifest.json")
)

if len(cac_manifest) == 0:
    raise RuntimeError("Chua tim thay manifest.")

file_manifest = cac_manifest[-1]
thu_muc_run = file_manifest.parent

# 2. Tạo thư mục chứa sample
thu_muc_sample = Path("data/sample")
thu_muc_sample.mkdir(parents=True, exist_ok=True)

# 3. Lấy tối đa 100 record đầu của mỗi CSV
for ten_file in ["ratings.csv", "movies.csv"]:
    file_nguon = thu_muc_run / "ml-25m" / ten_file
    file_dich = thu_muc_sample / ten_file

    with open(file_nguon, "r", encoding="utf-8", newline="") as nguon:
        with open(file_dich, "w", encoding="utf-8", newline="") as dich:
            bo_doc = csv.reader(nguon)
            bo_ghi = csv.writer(dich)

            # Giữ dòng tiêu đề
            bo_ghi.writerow(next(bo_doc))

            so_dong = 0

            for dong in bo_doc:
                if so_dong == 100:
                    break

                bo_ghi.writerow(dong)
                so_dong += 1

    print("Da tao:", file_dich, "- So record:", so_dong)

# 4. Ghi rõ nguồn và mục đích của sample
thong_tin = {
    "source_manifest": str(file_manifest),
    "selection": "First 100 records of each CSV",
    "purpose": "Readability demo only; not a representative training sample"
}

with open(
    thu_muc_sample / "sample_info.json",
    "w",
    encoding="utf-8"
) as file:
    json.dump(thong_tin, file, indent=4)

print("SAMPLE: PASS")