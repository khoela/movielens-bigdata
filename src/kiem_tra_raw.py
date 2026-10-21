from pathlib import Path
from pyspark.sql import SparkSession

# 1. Tìm các manifest đã tạo
thu_muc_goc = Path("data/raw/movielens25m")

cac_manifest = sorted(
    thu_muc_goc.glob("ingest_date=*/run_*/manifest.json")
)

if len(cac_manifest) == 0:
    raise RuntimeError("Chua tim thay manifest. Hay chay ingestion truoc.")

# 2. Chọn lần chạy mới nhất theo tên thư mục thời gian
file_manifest = cac_manifest[-1]
thu_muc_run = file_manifest.parent

print("Dang kiem tra:", thu_muc_run)

# 3. Khởi động Spark
spark = SparkSession.builder \
    .master("local[2]") \
    .appName("KiemTraMovieLensRaw") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# 4. Đọc hai CSV trong đúng lần chạy đã chọn
ratings = spark.read.csv(
    str(thu_muc_run / "ml-25m/ratings.csv"),
    header=True
)

movies = spark.read.csv(
    str(thu_muc_run / "ml-25m/movies.csv"),
    header=True
)

# 5. Xem cấu trúc và một số dòng dữ liệu
print("=== RATINGS ===")
ratings.printSchema()
ratings.show(5, truncate=False)

print("=== MOVIES ===")
movies.printSchema()
movies.show(5, truncate=False)

# 6. Đếm toàn bộ số dòng
so_ratings = ratings.count()
so_movies = movies.count()

print("So ratings:", so_ratings)
print("So movies:", so_movies)

# 7. Đóng Spark
spark.stop()

# 8. Đối chiếu với số dòng kỳ vọng của MovieLens 25M
if so_ratings != 25000095 or so_movies != 62423:
    raise RuntimeError("So dong khong khop. Can kiem tra lai snapshot.")

print("RAW CHECK: PASS")